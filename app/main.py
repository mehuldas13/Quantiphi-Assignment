"""FastAPI app: JSON API + the single-page web UI.

Run:  python -m uvicorn app.main:app --reload     then open http://127.0.0.1:8000

FastAPI runs the plain `def` endpoints below in a thread pool, so many users
can query at the same time. Shared state is either read-only after start-up
(the index, the policy) or protected by a lock (sessions, conversations,
audit log).
"""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .access import User
from .auth import SessionManager
from .service import QAService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

service = QAService.from_config()
sessions = SessionManager(service.policy)
app = FastAPI(title="Multi-User Document Q&A", version="1.0.0")
STATIC = config.ROOT / "app" / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class LoginIn(BaseModel):
    email: str = Field(..., examples=["alice@email.com"])


class ChatIn(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_id: str | None = None


def current_user(authorization: str | None = Header(default=None)) -> User:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    user = sessions.user_for(token)
    if not user:
        raise HTTPException(401, "Not logged in or session expired")
    return user


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "chunks": len(service.retriever.chunks), "answer_mode": service.answerer.name}


@app.get("/api/demo-users")
def demo_users():
    """Lists the dummy accounts so the login screen can offer them. Demo only."""
    return [{"email": u.email, "name": u.name,
             "companies": sorted(service.policy.company_name(c) for c in u.companies)}
            for u in service.policy.users.values()]


@app.post("/api/login")
def login(body: LoginIn):
    result = sessions.login(body.email)
    if not result:
        raise HTTPException(403, "Unknown user. Use one of the demo emails.")
    token, user = result
    return {"token": token, "user": {"email": user.email, "name": user.name},
            "library": service.library_for(user), "conversation_id": service.memory.new(user.email)}


@app.post("/api/logout")
def logout(authorization: str | None = Header(default=None), user: User = Depends(current_user)):
    sessions.logout(authorization.removeprefix("Bearer ").strip())
    return {"ok": True}


@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"email": user.email, "name": user.name, "library": service.library_for(user)}


@app.post("/api/conversations")
def new_conversation(user: User = Depends(current_user)):
    return {"conversation_id": service.memory.new(user.email)}


@app.get("/api/conversations/{cid}")
def get_conversation(cid: str, user: User = Depends(current_user)):
    if not service.memory.exists(user.email, cid):
        raise HTTPException(404, "Conversation not found")  # also what another user's id looks like
    return [t.__dict__ for t in service.memory.history(user.email, cid)]


@app.post("/api/chat")
def chat(body: ChatIn, user: User = Depends(current_user)):
    cid = body.conversation_id
    if not cid or not service.memory.exists(user.email, cid):
        cid = service.memory.new(user.email)
    return service.ask(user, cid, body.question)


@app.get("/api/documents/{name}")
def get_document(name: str, user: User = Depends(current_user)):
    if not service.policy.can_read(user.email, name):
        raise HTTPException(403, "You are not authorised to view this document")
    return FileResponse(config.PDF_DIR / name, media_type="application/pdf")
