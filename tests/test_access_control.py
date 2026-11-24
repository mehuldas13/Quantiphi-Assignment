"""Query isolation: a user can never get content from a company they are not entitled to."""
import itertools

import pytest

from conftest import login

EXPECTED = {
    "alice@email.com": {"Zentrix Cloud"},
    "bob@email.com": {"Voltara Motors", "Medivane Therapeutics"},
    "charlie@email.com": {"Solvane Energy", "Brightmart Retail"},
    "usera@email.com": {"Zentrix Cloud"},
    "userb@email.com": {"Voltara Motors"},
    "userc@email.com": {"Zentrix Cloud", "Voltara Motors"},
}

QUESTIONS = [
    "What was the revenue reported in Q4?", "gross margin", "free cash flow", "guidance for 2026",
    "deliveries", "dividend", "membership programme", "Cardiolex patents", "Copilot adoption",
    "What was Zentrix Cloud's revenue?", "Tell me about Voltara deliveries", "Medivane Neurovane trial",
    "Solvane capacity gigawatts", "Brightmart comparable store sales", "risks",
]


def test_policy_matches_assignment(service):
    for email, companies in EXPECTED.items():
        got = {service.policy.company_name(c) for c in service.policy.allowed_companies(email)}
        assert got == companies, email


@pytest.mark.parametrize("email", EXPECTED)
def test_retriever_never_returns_unauthorised_chunks(service, email):
    allowed = service.policy.allowed_companies(email)
    for q in QUESTIONS:
        for hit in service.retriever.search(q, allowed, k=10):
            assert hit.chunk.company_id in allowed, (email, q, hit.chunk.document)


@pytest.mark.parametrize("email,question", list(itertools.product(EXPECTED, QUESTIONS)))
def test_api_answers_only_from_allowed_documents(client, email, question):
    headers, cid = login(client, email)
    r = client.post("/api/chat", json={"question": question, "conversation_id": cid}, headers=headers).json()
    assert {s["company"] for s in r["sources"]} <= EXPECTED[email]


def test_example_scenario_charlie_cannot_see_company_a_or_b(client):
    headers, cid = login(client, "charlie@email.com")
    for q in ["What was Zentrix Cloud's revenue in Q4?", "What did Voltara Motors report?",
              "What about Medivane's Cardiolex sales?"]:
        r = client.post("/api/chat", json={"question": q, "conversation_id": cid}, headers=headers).json()
        assert r["answer"].startswith("Access denied")
        assert r["sources"] == []
        # and none of the restricted figures leak into the text
        for secret in ["612 million", "4.12 billion", "301 million"]:
            assert secret not in r["answer"]


def test_mixed_question_answers_allowed_part_and_blocks_the_rest(client):
    headers, cid = login(client, "alice@email.com")
    r = client.post("/api/chat", json={"question": "Compare Zentrix and Voltara revenue", "conversation_id": cid},
                    headers=headers).json()
    assert "Voltara Motors" in r["trace"]["denied_companies"]
    assert {s["company"] for s in r["sources"]} == {"Zentrix Cloud"}


def test_document_download_is_authorised(client):
    headers, _ = login(client, "alice@email.com")
    assert client.get("/api/documents/zentrix_cloud_q4_fy2025.pdf", headers=headers).status_code == 200
    assert client.get("/api/documents/voltara_motors_q4_fy2025.pdf", headers=headers).status_code == 403
    assert client.get("/api/documents/../access_control.json", headers=headers).status_code in (403, 404)


def test_requires_login(client):
    assert client.post("/api/chat", json={"question": "revenue"}).status_code == 401
    assert client.post("/api/chat", json={"question": "revenue"},
                       headers={"Authorization": "Bearer forged-token"}).status_code == 401
    assert client.post("/api/login", json={"email": "mallory@email.com"}).status_code == 403


def test_conversations_are_private(client):
    a_headers, a_cid = login(client, "alice@email.com")
    b_headers, _ = login(client, "bob@email.com")
    client.post("/api/chat", json={"question": "What was the revenue in Q4?", "conversation_id": a_cid}, headers=a_headers)
    # Bob cannot read Alice's conversation even with its id...
    assert client.get(f"/api/conversations/{a_cid}", headers=b_headers).status_code == 404
    # ...and cannot write into it: the server starts a fresh conversation for him instead.
    r = client.post("/api/chat", json={"question": "And the gross margin?", "conversation_id": a_cid}, headers=b_headers).json()
    assert r["conversation_id"] != a_cid
    assert len(client.get(f"/api/conversations/{a_cid}", headers=a_headers).json()) == 1
