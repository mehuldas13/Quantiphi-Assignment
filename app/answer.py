"""Answer generation from retrieved excerpts.

Two interchangeable answerers:

* ExtractiveAnswerer (default, no API key): picks the sentences from the
  retrieved chunks that best match the query and quotes them with citations.
  Fully offline and deterministic.
* ClaudeAnswerer (optional): sends ONLY the retrieved, access-filtered excerpts
  plus the user's own conversation history to Claude, which writes a fluent
  answer with [n] citations. The model never sees the full corpus, so it
  cannot leak a document the user is not allowed to read.
"""
from __future__ import annotations

import logging
import re

from .ingest import split_sentences
from .retriever import Hit
from .text import query_terms, tokenize

log = logging.getLogger(__name__)

NOT_FOUND = ("I couldn't find anything about that in the documents you have access to. "
             "Try rephrasing, or ask about one of the companies listed on the left.")


class ExtractiveAnswerer:
    name = "extractive"

    def __init__(self, idf: dict[str, float], company_names: dict[str, str] | None = None):
        self.idf = idf
        self.company_names = company_names or {}

    def _score(self, sentence: str, terms: set[str]) -> float:
        toks = set(tokenize(sentence))
        score = sum(self.idf.get(t, 0.0) for t in terms & toks)
        if score and re.search(r"\d", sentence):
            score *= 1.3   # earnings questions are usually about numbers
        if "welcome to" in sentence.lower():
            score *= 0.3   # operator boilerplate
        if sentence.rstrip().endswith("?"):
            score *= 0.5   # an analyst's question is rarely the answer
        return score

    def answer(self, question: str, standalone: str, hits: list[Hit], history=None) -> str:
        if not hits:
            return NOT_FOUND
        terms = set(query_terms(standalone))
        scored = []
        for n, hit in enumerate(hits, start=1):
            sentences = split_sentences(hit.chunk.text)
            for i, s in enumerate(sentences):
                sc = self._score(s, terms)
                if sc <= 0:
                    continue
                if s.rstrip().endswith("?") and i + 1 < len(sentences):
                    # Transcripts are Q&A: when an analyst's question matches,
                    # the answer is the sentence that follows it.
                    s, sc = sentences[i + 1], sc * 1.6
                scored.append((sc, n, s, hit.chunk))
        if not scored:
            return NOT_FOUND
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][0]
        picked, seen = [], set()
        for sc, n, s, chunk in scored:
            if sc < 0.6 * best or len(picked) == 3:
                break
            if s not in seen:
                seen.add(s)
                company = self.company_names.get(chunk.company_id, chunk.company_id)
                picked.append(f"- **{company}:** {s} [{n}]")
        return "Here is what the documents you can access say:\n\n" + "\n".join(picked)


SYSTEM_PROMPT = """You answer questions about company earnings-call transcripts for one user.
You are given numbered excerpts that this user is authorised to read. Use only those excerpts.
Cite the excerpts you rely on with their number in square brackets, like [1].
If the excerpts do not contain the answer, say you could not find it in the documents the user has access to; do not use outside knowledge.
Use the conversation history to understand follow-up questions such as "how did that compare to Q3?".
Keep answers short: two to five sentences, with the key figures stated exactly as they appear in the excerpts."""


class ClaudeAnswerer:
    name = "claude"

    def __init__(self, model: str, fallback: ExtractiveAnswerer):
        import anthropic  # imported lazily so the extractive mode needs no extra package

        self._anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model = model
        self.fallback = fallback

    def answer(self, question: str, standalone: str, hits: list[Hit], history=None) -> str:
        if not hits:
            return NOT_FOUND
        excerpts = "\n\n".join(
            f"[{n}] {h.chunk.title}, page {h.chunk.page}:\n{h.chunk.text}" for n, h in enumerate(hits, start=1))
        messages = []
        for turn in (history or [])[-4:]:
            messages.append({"role": "user", "content": turn.question})
            messages.append({"role": "assistant", "content": turn.answer})
        messages.append({"role": "user", "content": f"Excerpts:\n\n{excerpts}\n\nQuestion: {question}"})
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                messages=messages,
            )
        except self._anthropic.APIConnectionError as e:
            log.warning("Claude unreachable, using extractive answer: %s", e)
            return self.fallback.answer(question, standalone, hits, history)
        except self._anthropic.APIStatusError as e:
            log.warning("Claude API error %s, using extractive answer", e.status_code)
            return self.fallback.answer(question, standalone, hits, history)
        if response.stop_reason == "refusal":
            return self.fallback.answer(question, standalone, hits, history)
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or self.fallback.answer(question, standalone, hits, history)
