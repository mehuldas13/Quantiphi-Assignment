"""Fire questions from several users at the same time against a running server
and show that every user only ever gets answers from their own companies.

Start the server first (uvicorn app.main:app), then:
    python scripts/concurrency_demo.py            # default http://127.0.0.1:8000
    python scripts/concurrency_demo.py http://host:port
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
USERS = ["alice@email.com", "bob@email.com", "charlie@email.com", "userA@email.com", "userB@email.com", "userC@email.com"]
QUESTIONS = ["What was the revenue reported in Q4?", "And the gross margin?", "What was Zentrix Cloud's revenue?"]


def run_user(email: str) -> list[str]:
    with httpx.Client(base_url=BASE, timeout=30) as c:
        login = c.post("/api/login", json={"email": email}).json()
        headers = {"Authorization": f"Bearer {login['token']}"}
        allowed = {x["company"] for x in login["library"]}
        cid, lines = login["conversation_id"], []
        for q in QUESTIONS:
            r = c.post("/api/chat", json={"question": q, "conversation_id": cid}, headers=headers).json()
            used = {s["company"] for s in r["sources"]}
            ok = used <= allowed
            first = next(l for l in r["answer"].splitlines() if l.startswith(("- ", "Access", "I couldn")))[:95]
            lines.append(f"  {'OK  ' if ok else 'LEAK'} {q:<38} sources={sorted(used) or '-'}\n        {first}")
        return [f"{email}  (allowed: {', '.join(sorted(allowed))})"] + lines


if __name__ == "__main__":
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(USERS)) as pool:
        results = list(pool.map(run_user, USERS))
    for block in results:
        print("\n".join(block), end="\n\n")
    leaks = sum(line.strip().startswith("LEAK") for block in results for line in block)
    print(f"{len(USERS)} users x {len(QUESTIONS)} questions in parallel, {time.time() - t0:.2f}s, leaks: {leaks}")
