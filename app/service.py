"""The Q&A pipeline. Each call to ask() runs these steps:

  1. Look up the companies the user can access.
  2. Rewrite a follow-up into a full query using the user's history.
  3. Refuse any company the question names that the user can't access.
  4. Search only the allowed companies.
  5. Build the answer from the retrieved excerpts.
  6. Save the turn and write an audit log line.
"""
from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .access import AccessPolicy, User
from .answer import ExtractiveAnswerer
from .contextualizer import Resolved, resolve
from .ingest import load_corpus
from .memory import ConversationStore, Turn
from .retriever import BM25Retriever, Hit

log = logging.getLogger(__name__)


class QAService:
    def __init__(
        self,
        policy: AccessPolicy,
        retriever: BM25Retriever,
        audit_path: Path | None = None,
        top_k: int = 4,
        max_turns: int = 10,
    ):
        self.policy = policy
        self.retriever = retriever
        self.memory = ConversationStore(max_turns)
        self.top_k = top_k
        self.audit_path = audit_path
        self._audit_lock = threading.Lock()

        company_names = {c.id: c.name for c in policy.companies.values()}
        self.answerer = ExtractiveAnswerer(retriever.idf, company_names)

    @classmethod
    def from_config(cls) -> "QAService":
        policy = AccessPolicy.load(config.ACCESS_FILE)
        chunks = load_corpus(config.PDF_DIR, policy, config.CHUNK_WORDS, config.OVERLAP_SENTENCES)
        log.info("Indexed %d chunks from %d documents", len(chunks), len({c.document for c in chunks}))

        return cls(
            policy,
            BM25Retriever(chunks),
            audit_path=config.LOG_DIR / "audit.jsonl",
            top_k=config.TOP_K,
            max_turns=config.MAX_HISTORY_TURNS,
        )

    # ---------------------------------------------------------------- main entry point

    def ask(self, user: User, conversation_id: str, question: str) -> dict:
        question = question.strip()

        # Steps 1-2: permissions and follow-up rewriting
        allowed = user.companies
        history = self.memory.history(user.email, conversation_id)
        resolved = resolve(question, history, self.policy)

        # Step 3: split the companies the question names into allowed and denied
        denied = [c for c in resolved.companies if c not in allowed]
        focus = [c for c in resolved.companies if c in allowed]

        if denied and not focus:
            # Only restricted companies were named: refuse without searching.
            hits: list[Hit] = []
            searched: list[str] = []
            answer = self._denied_message(denied, allowed)
        else:
            # Steps 4-5: search the named companies, or all allowed ones if none were named
            searched = sorted(focus or allowed)
            hits = self._search(user, resolved.search_query, frozenset(searched))
            answer = self.answerer.answer(question, resolved.search_query, hits, history)
            if denied:
                answer = self._denied_message(denied, allowed) + "\n\n" + answer

        # Step 6: remember the turn and audit it
        sources = self._sources(hits)
        self.memory.append(user.email, conversation_id, Turn(
            question=question,
            standalone_query=resolved.standalone_query,
            companies=focus,
            topic=resolved.topic,
            period=resolved.period,
            answer=answer,
            sources=sources,
        ))

        result = {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "trace": self._trace(resolved, searched, denied),
        }
        self._audit(user, result)
        return result

    def library_for(self, user: User) -> list[dict]:
        return [
            {"company": self.policy.company_name(cid), "documents": list(self.policy.companies[cid].documents)}
            for cid in sorted(user.companies)
        ]

    # ---------------------------------------------------------------- helpers

    def _search(self, user: User, query: str, scope: frozenset[str]) -> list[Hit]:
        hits = self.retriever.search(query, scope, self.top_k)
        # Re-check every hit against the access rules before it leaves the service.
        return [h for h in hits if self.policy.can_read(user.email, h.chunk.document)]

    def _sources(self, hits: list[Hit]) -> list[dict]:
        return [
            {
                "n": n,
                "company": self.policy.company_name(h.chunk.company_id),
                "document": h.chunk.document,
                "title": h.chunk.title,
                "page": h.chunk.page,
                "score": round(h.score, 2),
                "excerpt": h.chunk.text,
            }
            for n, h in enumerate(hits, start=1)
        ]

    def _trace(self, resolved: Resolved, searched: list[str], denied: list[str]) -> dict:
        names = self.policy.company_name
        return {
            "standalone_query": resolved.standalone_query,
            "is_followup": resolved.is_followup,
            "slots": {
                "companies": [names(c) for c in resolved.companies],
                "topic": resolved.topic,
                "period": resolved.period,
            },
            "searched_companies": [names(c) for c in searched],
            "denied_companies": [names(c) for c in denied],
        }

    def _denied_message(self, denied: list[str], allowed) -> str:
        names = ", ".join(self.policy.company_name(c) for c in denied)
        mine = ", ".join(sorted(self.policy.company_name(c) for c in allowed)) or "no companies"
        return f"Access denied: you are not authorised to view documents for {names}. Your access covers: {mine}."

    def _audit(self, user: User, result: dict) -> None:
        if not self.audit_path:
            return

        trace = result["trace"]
        line = json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user.email,
            "conversation_id": result["conversation_id"],
            "question": result["question"],
            "standalone_query": trace["standalone_query"],
            "searched": trace["searched_companies"],
            "denied": trace["denied_companies"],
            "documents_returned": sorted({s["document"] for s in result["sources"]}),
        })

        with self._audit_lock:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.audit_path, "a") as f:
                f.write(line + "\n")
