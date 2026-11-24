"""Access-control policy: which user may read which company's documents.

The policy is the single source of truth for authorisation. Every query is
resolved to a set of allowed company ids here BEFORE any search happens, so a
user's query can never score, retrieve or display a chunk from a document
they are not entitled to.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Company:
    id: str
    name: str
    aliases: tuple[str, ...]
    documents: tuple[str, ...]


@dataclass(frozen=True)
class User:
    email: str
    name: str
    companies: frozenset[str] = field(default_factory=frozenset)


class AccessPolicy:
    def __init__(self, companies: dict[str, Company], users: dict[str, User]):
        self.companies = companies
        self.users = users  # keyed by lower-cased email
        self._doc_owner = {doc: c.id for c in companies.values() for doc in c.documents}
        # One regex per company that matches any alias as a whole word.
        self._alias_patterns = {
            c.id: re.compile(r"\b(" + "|".join(re.escape(a.lower()) for a in sorted(
                set(c.aliases) | {c.name.lower()}, key=len, reverse=True)) + r")('s)?\b")
            for c in companies.values()
        }

    @classmethod
    def load(cls, path: Path) -> "AccessPolicy":
        raw = json.loads(Path(path).read_text())
        companies = {
            cid: Company(cid, c["name"], tuple(a.lower() for a in c.get("aliases", [])), tuple(c["documents"]))
            for cid, c in raw["companies"].items()
        }
        users = {}
        for email, u in raw["users"].items():
            unknown = set(u["companies"]) - companies.keys()
            if unknown:
                raise ValueError(f"User {email} references unknown companies: {unknown}")
            users[email.lower()] = User(email.lower(), u.get("name", email), frozenset(u["companies"]))
        return cls(companies, users)

    # -- lookups -------------------------------------------------------------
    def get_user(self, email: str) -> User | None:
        return self.users.get(email.strip().lower())

    def allowed_companies(self, email: str) -> frozenset[str]:
        user = self.get_user(email)
        return user.companies if user else frozenset()

    def owner_of(self, document: str) -> str | None:
        return self._doc_owner.get(document)

    def can_read(self, email: str, document: str) -> bool:
        owner = self.owner_of(document)
        return owner is not None and owner in self.allowed_companies(email)

    def mentioned_companies(self, text: str) -> set[str]:
        """Company ids whose name or alias appears in the text."""
        lowered = text.lower()
        return {cid for cid, pat in self._alias_patterns.items() if pat.search(lowered)}

    def company_name(self, cid: str) -> str:
        return self.companies[cid].name
