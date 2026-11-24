"""The Q&A pipeline. One call to ask() runs these steps:

  1. Resolve permissions   - allowed companies for this user, from the policy
  2. Contextualise         - rewrite a follow-up into a standalone query using this user's history
  3. Authorisation check   - if the question names companies the user may not read, refuse those
  4. Retrieve              - BM25 search restricted to the allowed (and focused) companies
  5. Answer                - extractive or Claude, from the retrieved excerpts only
  6. Remember + audit      - store the turn in the user's conversation, write an audit log line
"""
from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .access import AccessPolicy, User
from .answer import ClaudeAnswerer, ExtractiveAnswerer
from .contextualizer import resolve
from .ingest import load_corpus
from .memory import ConversationStore, Turn
from .retriever import BM25Retriever

log = logging.getLogger(__name__)


class QAService:
    def __init__(self, policy: AccessPolicy, retriever: BM25Retriever, answer_mode: str = "auto",
                 audit_path: Path | None = None, top_k: int = 4, max_turns: int = 10):
        self.policy = policy
        self.retriever = retriever
        self.memory = ConversationStore(max_turns)
        self.top_k = top_k
        self.audit_path = audit_path
        self._audit_lock = threading.Lock()
        extractive = ExtractiveAnswerer(retriever.idf, {c.id: c.name for c in policy.companies.values()})
        use_claude = answer_mode == "claude" or (answer_mode == "auto" and os.getenv("ANTHROPIC_API_KEY"))
        self.answerer = ClaudeAnswerer(config.CLAUDE_MODEL, extractive) if use_claude else extractive
        log.info("Answer mode: %s", self.answerer.name)

    @classmethod
    def from_config(cls) -> "QAService":
        policy = AccessPolicy.load(config.ACCESS_FILE)
        chunks = load_corpus(config.PDF_DIR, policy, config.CHUNK_WORDS, config.OVERLAP_SENTENCES)
        log.info("Indexed %d chunks from %d documents", len(chunks), len({c.document for c in chunks}))
        return cls(policy, BM25Retriever(chunks), config.ANSWER_MODE, config.LOG_DIR / "audit.jsonl",
                   config.TOP_K, config.MAX_HISTORY_TURNS)

    # ------------------------------------------------------------------
    def ask(self, user: User, conversation_id: str, question: str) -> dict:
        question = question.strip()
        allowed = user.companies                                         # step 1
        history = self.memory.history(user.email, conversation_id)
        r = resolve(question, history, self.policy)                      # step 2

        denied = [c for c in r.companies if c not in allowed]            # step 3
        focus = [c for c in r.companies if c in allowed]
        search_scope_list: list[str] = []
        if denied and not focus:
            answer = self._denied_message(denied, allowed)
            hits = []
        else:
            search_scope = frozenset(focus) if focus else allowed
            hits = self.retriever.search(r.search_query, search_scope, self.top_k)   # step 4
            # Defence in depth: re-check every hit against the policy before it leaves the service.
            hits = [h for h in hits if self.policy.can_read(user.email, h.chunk.document)]
            answer = self.answerer.answer(question, r.search_query, hits, history)  # step 5
            if denied:
                answer = self._denied_message(denied, allowed) + "\n\n" + answer
            search_scope_list = sorted(search_scope)

        sources = [{
            "n": n, "company": self.policy.company_name(h.chunk.company_id), "document": h.chunk.document,
            "title": h.chunk.title, "page": h.chunk.page, "score": round(h.score, 2), "excerpt": h.chunk.text,
        } for n, h in enumerate(hits, start=1)]

        self.memory.append(user.email, conversation_id, Turn(                     # step 6
            question, r.standalone_query, focus,
            r.topic, r.period, answer, sources))
        result = {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "trace": {
                "standalone_query": r.standalone_query,
                "is_followup": r.is_followup,
                "slots": {"companies": [self.policy.company_name(c) for c in r.companies],
                          "topic": r.topic, "period": r.period},
                "searched_companies": [self.policy.company_name(c) for c in search_scope_list],
                "denied_companies": [self.policy.company_name(c) for c in denied],
                "answer_mode": self.answerer.name,
            },
        }
        self._audit(user, result)
        return result

    def _denied_message(self, denied: list[str], allowed) -> str:
        names = ", ".join(self.policy.company_name(c) for c in denied)
        mine = ", ".join(sorted(self.policy.company_name(c) for c in allowed)) or "no companies"
        return (f"Access denied: you are not authorised to view documents for {names}. "
                f"Your access covers: {mine}.")

    def _audit(self, user: User, result: dict) -> None:
        if not self.audit_path:
            return
        line = json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user.email,
            "conversation_id": result["conversation_id"],
            "question": result["question"],
            "standalone_query": result["trace"]["standalone_query"],
            "searched": result["trace"]["searched_companies"],
            "denied": result["trace"]["denied_companies"],
            "documents_returned": sorted({s["document"] for s in result["sources"]}),
        })
        with self._audit_lock:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.audit_path, "a") as f:
                f.write(line + "\n")

    # ------------------------------------------------------------------
    def library_for(self, user: User) -> list[dict]:
        return [{"company": self.policy.company_name(cid),
                 "documents": list(self.policy.companies[cid].documents)}
                for cid in sorted(user.companies)]
