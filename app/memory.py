"""Per-user conversation memory.

Conversations are keyed by (user email, conversation id). The email always
comes from the authenticated session, never from the request body, so one
user cannot read or append to another user's conversation even if they guess
its id. A single lock keeps concurrent requests from corrupting the store.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Turn:
    question: str
    standalone_query: str
    companies: list[str]
    topic: str
    period: str
    answer: str
    sources: list[dict]
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


class ConversationStore:
    def __init__(self, max_turns: int = 10):
        self._max = max_turns
        self._lock = threading.Lock()
        self._data: dict[tuple[str, str], list[Turn]] = {}

    def new(self, email: str) -> str:
        cid = uuid.uuid4().hex[:12]
        with self._lock:
            self._data[(email, cid)] = []
        return cid

    def history(self, email: str, cid: str) -> list[Turn]:
        with self._lock:
            return list(self._data.get((email, cid), []))

    def exists(self, email: str, cid: str) -> bool:
        with self._lock:
            return (email, cid) in self._data

    def append(self, email: str, cid: str, turn: Turn) -> None:
        with self._lock:
            turns = self._data.setdefault((email, cid), [])
            turns.append(turn)
            del turns[:-self._max]

    def list_for(self, email: str) -> list[str]:
        with self._lock:
            return [cid for (e, cid) in self._data if e == email]

    def clear_user(self, email: str) -> None:
        with self._lock:
            for key in [k for k in self._data if k[0] == email]:
                del self._data[key]
