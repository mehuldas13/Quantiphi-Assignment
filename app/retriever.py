"""BM25 keyword search with a mandatory access-control pre-filter.

Why BM25? It needs no model download or API key, it is deterministic (good for
a demo and for tests), and it works very well on earnings calls, where the
questions use the same vocabulary as the documents (revenue, margin, Q4...).
The Retriever interface is small, so it can be swapped for a vector store
(FAISS, Chroma, pgvector) later without touching the rest of the system.

Security property: search() takes the set of company ids the caller may read
and only scores chunks owned by those companies. Unauthorised chunks are never
scored, so they can never be ranked, returned, or leaked into an answer.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .ingest import Chunk
from .text import query_terms, tokenize


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class BM25Retriever:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self._tf = [Counter(tokenize(c.text + " " + c.title)) for c in chunks]
        self._len = [sum(tf.values()) for tf in self._tf]
        self._avg = (sum(self._len) / len(self._len)) if chunks else 0.0
        df = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(chunks)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        # Index chunks by company so the filter is a cheap lookup, not a scan.
        self._by_company: dict[str, list[int]] = {}
        for i, c in enumerate(chunks):
            self._by_company.setdefault(c.company_id, []).append(i)

    def search(self, query: str, allowed_companies: frozenset[str] | set[str], k: int = 4) -> list[Hit]:
        if not allowed_companies:
            return []
        terms = query_terms(query)
        if not terms:
            return []
        candidates = [i for cid in sorted(allowed_companies) for i in self._by_company.get(cid, [])]
        hits = []
        for i in candidates:
            tf, dl = self._tf[i], self._len[i]
            score = 0.0
            for t in terms:
                f = tf.get(t)
                if f:
                    score += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self._avg))
            if score > 0:
                hits.append(Hit(self.chunks[i], score))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]
