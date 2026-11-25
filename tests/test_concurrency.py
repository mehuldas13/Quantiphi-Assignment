"""Several users querying at the same time must not affect each other."""
from concurrent.futures import ThreadPoolExecutor

from conftest import login

# Expected access per user (company display names).
USERS = {
    "alice@email.com": {"Zentrix Cloud"},
    "bob@email.com": {"Voltara Motors", "Medivane Therapeutics"},
    "charlie@email.com": {"Solvane Energy", "Brightmart Retail"},
    "userA@email.com": {"Zentrix Cloud"},
    "userB@email.com": {"Voltara Motors"},
    "userC@email.com": {"Zentrix Cloud", "Voltara Motors"},
}

QUESTIONS = [
    "What was the revenue reported in Q4?",
    "And the gross margin?",
    "What about free cash flow?",
    "What guidance did they give for 2026?",
    "What are the risks?",
]

SESSIONS_PER_USER = 3


def run_session(client, email):
    """Log in, ask every question in one conversation, then read the conversation back."""
    headers, cid = login(client, email)

    companies_per_answer = []
    for question in QUESTIONS:
        response = client.post("/api/chat", json={"question": question, "conversation_id": cid}, headers=headers)
        companies_per_answer.append({s["company"] for s in response.json()["sources"]})

    history = client.get(f"/api/conversations/{cid}", headers=headers).json()
    return email, companies_per_answer, history


def run_all_sessions_in_parallel(client):
    emails = [email for email in USERS for _ in range(SESSIONS_PER_USER)]
    with ThreadPoolExecutor(max_workers=len(emails)) as pool:
        return list(pool.map(lambda email: run_session(client, email), emails))


def test_parallel_answers_stay_within_each_users_access(client):
    for email, companies_per_answer, _ in run_all_sessions_in_parallel(client):
        for companies in companies_per_answer:
            assert companies <= USERS[email], email


def test_parallel_conversations_contain_only_their_own_turns(client):
    for email, _, history in run_all_sessions_in_parallel(client):
        assert [turn["question"] for turn in history] == QUESTIONS, email
