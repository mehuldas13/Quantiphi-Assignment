"""Follow-up questions keep the context of the conversation."""
from conftest import login


def ask(client, headers, cid, q):
    r = client.post("/api/chat", json={"question": q, "conversation_id": cid}, headers=headers)
    assert r.status_code == 200
    return r.json()


def test_alice_q4_revenue_then_follow_ups(client):
    h, cid = login(client, "alice@email.com")
    r1 = ask(client, h, cid, "What was the revenue reported in Q4?")
    assert "612 million" in r1["answer"]
    r2 = ask(client, h, cid, "And the gross margin?")
    assert r2["trace"]["is_followup"]
    assert r2["trace"]["slots"]["period"].lower() == "q4"   # period carried over
    assert "78.4 percent" in r2["answer"]


def test_bob_follow_ups_on_company_b(client):
    h, cid = login(client, "bob@email.com")
    r1 = ask(client, h, cid, "What was Voltara's revenue in Q4?")
    assert "4.12 billion" in r1["answer"]
    r2 = ask(client, h, cid, "How did the automotive gross margin compare to Q3?")
    assert r2["trace"]["slots"]["companies"] == ["Voltara Motors"]   # company carried over
    assert "15.1 percent" in r2["answer"]
    r3 = ask(client, h, cid, "What drove the improvement?")
    assert "battery cost" in r3["answer"]


def test_switching_company_keeps_the_topic(client):
    h, cid = login(client, "bob@email.com")
    ask(client, h, cid, "What was Voltara's revenue in Q4?")
    r = ask(client, h, cid, "What about Medivane?")
    assert r["trace"]["slots"]["topic"] == "revenue"
    assert r["trace"]["searched_companies"] == ["Medivane Therapeutics"]
    assert "842 million" in r["answer"]


def test_new_conversation_has_no_memory(client):
    h, cid = login(client, "alice@email.com")
    ask(client, h, cid, "What was the gross margin in Q4?")
    new_cid = client.post("/api/conversations", headers=h).json()["conversation_id"]
    r = ask(client, h, new_cid, "And the free cash flow?")
    assert r["trace"]["is_followup"] is False
    assert r["trace"]["slots"]["period"] == ""


def test_follow_up_cannot_reach_a_restricted_company(client):
    """Context carried from history is re-checked against the policy every turn."""
    h, cid = login(client, "userB@email.com")
    ask(client, h, cid, "What was Zentrix revenue?")          # denied
    r = ask(client, h, cid, "And their gross margin?")
    assert {s["company"] for s in r["sources"]} <= {"Voltara Motors"}
