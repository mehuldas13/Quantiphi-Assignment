"""Tokenisation shared by the search index and the answer extractor."""
from __future__ import annotations

import re

STOPWORDS = set("""
a an the and or but if of to in on for with at by from as is are was were be been being this that these those
it its it's they them their there here what which who whom whose when where why how do does did done can could
would should will shall may might must say said talk i we you he she our your his her my me us about into over than then so
such not no yes also any all some more most very just tell give show please reported report much many
""".split())

# Small finance-domain synonym map. A query term is expanded with its synonyms
# so "revenue" also finds "net sales" and "Q4" also finds "fourth quarter".
SYNONYMS = {
    "q1": ["first", "quarter"], "q2": ["second", "quarter"],
    "q3": ["third", "quarter"], "q4": ["fourth", "quarter"],
    "revenue": ["sales"], "sales": ["revenue"],
    "profit": ["income", "earnings"], "earnings": ["income"],
    "eps": ["earnings", "share"],
    "outlook": ["guidance", "expect"], "guidance": ["expect", "outlook"], "forecast": ["guidance", "expect"],
    "cash": ["cash"], "fcf": ["free", "cash", "flow"],
    "risk": ["risks"], "risks": ["risk"],
    "headcount": ["employees"],
    "next": ["2026", "expect"],
    "margin": ["margin"], "deliveries": ["delivered"], "delivery": ["delivered"],
}

_TOKEN = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")


def stem(word: str) -> str:
    """Very light suffix stripping, enough to match margin/margins, deliver/delivered."""
    for suffix in ("ing", "ies", "ed", "es", "s"):
        if len(word) > 4 and word.endswith(suffix):
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def tokenize(text: str) -> list[str]:
    return [stem(t) for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]


def query_terms(text: str) -> list[str]:
    """Tokens for a query, with synonym expansion."""
    terms = []
    for raw in _TOKEN.findall(text.lower()):
        if raw in STOPWORDS:
            continue
        terms.append(stem(raw))
        terms.extend(stem(s) for s in SYNONYMS.get(raw, []))
    return terms
