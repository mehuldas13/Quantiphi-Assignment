"""Builds an answer by picking the sentences from the retrieved chunks that best
match the query, each labelled with its company and source number."""
from __future__ import annotations

import re

from .ingest import split_sentences
from .retriever import Hit
from .text import query_terms, tokenize

NOT_FOUND = ("I couldn't find anything about that in the documents you have access to. "
             "Try rephrasing, or ask about one of the companies listed on the left.")


class ExtractiveAnswerer:
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
