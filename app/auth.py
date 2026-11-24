"""Simulated authentication: log in with a demo email, get a random bearer token.

The assignment allows dummy emails instead of real user management. Tokens are
random (secrets.token_urlsafe), held in memory, and expire after a few hours.
Every API call resolves the user from the token, so the user's identity, and
therefore their permissions, can never be supplied by the client directly.
"""
from __future__ import annotations

import secrets
import threading
import time

from .access import AccessPolicy, User


class SessionManager:
    def __init__(self, policy: AccessPolicy, ttl_seconds: int = 8 * 3600):
        self.policy = policy
        self.ttl = ttl_seconds
        self._lock = threading.Lock()
        self._sessions: dict[str, tuple[str, float]] = {}

    def login(self, email: str) -> tuple[str, User] | None:
        user = self.policy.get_user(email)
        if not user:
            return None
        token = secrets.token_urlsafe(24)
        with self._lock:
            self._sessions[token] = (user.email, time.time() + self.ttl)
        return token, user

    def user_for(self, token: str | None) -> User | None:
        if not token:
            return None
        with self._lock:
            entry = self._sessions.get(token)
            if not entry:
                return None
            email, expires = entry
            if time.time() > expires:
                del self._sessions[token]
                return None
        return self.policy.get_user(email)

    def logout(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)
