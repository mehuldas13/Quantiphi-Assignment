"""FastAPI app: JSON API and the web UI.

Run:  python -m uvicorn app.main:app --reload   (then open http://127.0.0.1:8000)

Endpoints are plain `def` functions, so FastAPI runs them in a thread pool and
several users can be served at the same time.
"""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .access import User
from .auth import SessionManager
from .service import QAService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

STATIC_DIR = config.ROOT / "app" / "static"

service = QAService.from_config()
sessions = SessionManager(service.policy)

app = FastAPI(title="Multi-User Document Q&A", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------- request models

class LoginIn(BaseModel):
    email: str = Field(..., examples=["alice@email.com"])


class ChatIn(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_id: str | None = None


# ---------------------------------------------------------------- authentication

# Reads "Authorization: Bearer <token>" and adds the Authorize button to /docs.
# auto_error=False so a missing token returns 401 instead of FastAPI's default 403.
bearer = HTTPBearer(auto_error=False, description="Paste the token returned by POST /api/login")


def token_from(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str | None:
    return creds.credentials.strip() if creds else None


def current_user(token: str | None = Depends(token_from)) -> User:
    user = sessions.user_for(token)
    if not user:
        raise HTTPException(401, "Not logged in or session expired")
    return user


# ---------------------------------------------------------------- public endpoints

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "chunks": len(service.retriever.chunks)}


@app.get("/api/demo-users")
def demo_users():
    """Demo accounts shown on the login screen."""
    return [
        {
            "email": user.email,
            "name": user.name,
            "companies": sorted(service.policy.company_name(c) for c in user.companies),
        }
        for user in service.policy.users.values()
    ]


@app.post("/api/login")
def login(body: LoginIn):
    result = sessions.login(body.email)
    if not result:
        raise HTTPException(403, "Unknown user. Use one of the demo emails.")

    token, user = result
    return {
        "token": token,
        "user": {"email": user.email, "name": user.name},
        "library": service.library_for(user),
        "conversation_id": service.memory.new(user.email),
    }


# ---------------------------------------------------------------- authenticated endpoints

@app.post("/api/logout")
def logout(token: str | None = Depends(token_from), user: User = Depends(current_user)):
    sessions.logout(token)
    return {"ok": True}


@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"email": user.email, "name": user.name, "library": service.library_for(user)}


@app.post("/api/conversations")
def new_conversation(user: User = Depends(current_user)):
    return {"conversation_id": service.memory.new(user.email)}


@app.get("/api/conversations/{cid}")
def get_conversation(cid: str, user: User = Depends(current_user)):
    # Another user's conversation id is indistinguishable from one that doesn't exist.
    if not service.memory.exists(user.email, cid):
        raise HTTPException(404, "Conversation not found")
    return [turn.__dict__ for turn in service.memory.history(user.email, cid)]


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
