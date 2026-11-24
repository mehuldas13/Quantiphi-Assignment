"""Turns a follow-up question into a standalone search query.

A conversation keeps three "slots" from the previous turn:
  * companies - which company the user is talking about
  * topic     - what they are asking about (revenue, gross margin, guidance...)
  * period    - which period (Q3, Q4, full year, 2026...)

When a new question is a follow-up ("And the gross margin?", "How did that
compare to Q3?", "What about Medivane?"), any slot it does not fill is carried
over from the previous turn. The result is a standalone query that the search
engine can answer without knowing the history, and it is shown in the UI so
the behaviour is easy to explain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .access import AccessPolicy
from .memory import Turn
from .text import STOPWORDS

_PERIOD = re.compile(
    r"\b(q[1-4]|(?:first|second|third|fourth) quarter|full[- ]year|fiscal (?:year )?20\d\d|fy ?20\d\d|20\d\d|"
    r"next year|last year|this year)\b", re.I)
_FOLLOWUP_START = re.compile(r"^\s*(and|also|what about|how about|and what about|compared|vs\.?|versus|same)\b", re.I)
_ANAPHORA = re.compile(r"\b(it|its|that|this|those|these|they|them|their|there|he|she|same|previous|prior|above)\b", re.I)
# Words that only steer the conversation and carry no topic of their own.
_FILLER = set("""
and also what about how did does do was were is are the a an that this it its those these they them their compare compared
comparison change changed vs versus previous prior last same again then more detail details tell me please explain
quarter period year to with of in for on figure number numbers there company companies one look like
""".split()) | STOPWORDS


@dataclass
class Resolved:
    standalone_query: str     # human-readable rewritten question, shown in the UI
    search_query: str         # what is sent to the search engine (company names removed: they become a filter)
    companies: list[str]      # every company the question refers to (may include unauthorised ones)
    topic: str
    period: str
    is_followup: bool


def _strip(text: str, policy: AccessPolicy) -> str:
    lowered = text.lower()
    for c in policy.companies.values():
        for alias in sorted(set(c.aliases) | {c.name.lower()}, key=len, reverse=True):
            lowered = re.sub(rf"\b{re.escape(alias)}('s)?\b", " ", lowered)
    lowered = _PERIOD.sub(" ", lowered)
    return lowered


def _topic(text: str, policy: AccessPolicy) -> str:
    words = re.findall(r"[a-z0-9][a-z0-9\-\.]*", _strip(text, policy))
    return " ".join(w for w in words if w not in _FILLER and len(w) > 1).strip(" ?.")


def resolve(question: str, history: list[Turn], policy: AccessPolicy) -> Resolved:
    companies = sorted(policy.mentioned_companies(question))
    m = _PERIOD.search(question)
    period = m.group(0) if m else ""
    topic = _topic(question, policy)
    prev = history[-1] if history else None

    # A question is treated as a follow-up when there is a previous turn and it
    # either starts like one ("and...", "what about..."), points back with a
    # pronoun ("that", "it", "their"), has no topic of its own, or names no
    # company and is short.
    is_followup = prev is not None and (
        bool(_FOLLOWUP_START.search(question))
        or bool(_ANAPHORA.search(question))
        or not topic
        or (not companies and len(topic.split()) <= 3)
    )

    if is_followup and prev:
        companies = companies or list(prev.companies)
        topic = topic or prev.topic
        period = period or prev.period

    names = [policy.company_name(c) for c in companies]
    standalone = " ".join(x for x in [" ".join(names), topic, period] if x).strip() or question
    search = " ".join(x for x in [topic, period] if x).strip() or standalone
    return Resolved(standalone, search, companies, topic, period, is_followup)
