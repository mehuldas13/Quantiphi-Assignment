"""Many users at once: answers and conversations do not bleed between users."""
from concurrent.futures import ThreadPoolExecutor

from conftest import login

USERS = {
    "alice@email.com": {"Zentrix Cloud"},
    "bob@email.com": {"Voltara Motors", "Medivane Therapeutics"},
    "charlie@email.com": {"Solvane Energy", "Brightmart Retail"},
    "userA@email.com": {"Zentrix Cloud"},
    "userB@email.com": {"Voltara Motors"},
    "userC@email.com": {"Zentrix Cloud", "Voltara Motors"},
}
QUESTIONS = ["What was the revenue reported in Q4?", "And the gross margin?", "What about free cash flow?",
             "What guidance did they give for 2026?", "What are the risks?"]


def session(client, email):
    headers, cid = login(client, email)
    seen = []
    for q in QUESTIONS:
        r = client.post("/api/chat", json={"question": q, "conversation_id": cid}, headers=headers).json()
        seen.append({s["company"] for s in r["sources"]})
    history = client.get(f"/api/conversations/{cid}", headers=headers).json()
    return email, seen, history


def test_parallel_users_are_isolated(client):
    jobs = [email for email in USERS for _ in range(3)]  # 18 sessions, 90 questions, all in parallel
    with ThreadPoolExecutor(max_workers=18) as pool:
        results = list(pool.map(lambda e: session(client, e), jobs))
    for email, seen, history in results:
        for companies in seen:
            assert companies <= USERS[email], email
        assert [t["question"] for t in history] == QUESTIONS   # each conversation has exactly its own turns
