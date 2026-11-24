# Demo script (about 8 minutes)

Use this for the interview walkthrough or to record the video. Each step lists **what to do** and **what to say**. The four points the assignment asks you to demonstrate are marked ①②③④:

① logging in as different users · ② submitting queries and getting answers · ③ query isolation · ④ conversational follow-ups

## Before you start

```bash
./run.sh            # or: uvicorn app.main:app
```

* Open **http://localhost:8000** in two browser tabs side by side (or two windows).
* Optional: a terminal ready for `pytest -q` and `python scripts/concurrency_demo.py`.
* Optional: `logs/audit.jsonl` open in an editor (`tail -f logs/audit.jsonl`).

---

## 1. Introduce the setup (1 min)

**Show:** the login screen.

**Say:** "There are five companies' earnings-call transcripts. Each demo user is entitled to one or two companies, matching the assignment: Alice has Company A, Bob has B and C, Charlie has D and E, and User A/B/C follow the first example. The policy is one JSON file, `data/access_control.json`."

## 2. Alice: login, query, follow-ups (2 min) ①②④

**Do (tab 1):** click **Alice**.

**Say:** "Login is simulated with a dummy email. The server issues a random token and identifies Alice from it on every request. On the left is everything she's allowed to see: only Zentrix Cloud."

**Do:** ask **"What was the revenue reported in Q4?"**

**Expect:** *Total revenue for the fourth quarter was 612 million dollars, up 26 percent…*

**Do:** open **Sources**.

**Say:** "The answer is grounded in these excerpts, with document and page. All of them are from Zentrix Cloud."

**Do:** ask **"And the gross margin?"**, then open **How this answer was built**.

**Expect:** *Non-GAAP gross margin was 78.4 percent in Q4…* · Rewritten query `gross margin Q4` · Follow-up: yes.

**Say:** "'And the gross margin?' has no period in it. The system recognised a follow-up and carried 'Q4' over from the previous turn. The rewritten query is what's actually searched."

**Do:** ask **"How did that compare to last year?"**

**Expect:** *…78.4 percent in Q4, up from 76.9 percent in the prior-year quarter…* The topic "gross margin" was carried over from the previous turn.

## 3. Alice can't see other companies (1 min) ③

**Do:** ask **"What was Voltara Motors' revenue?"**

**Expect:** a red **Access denied: you are not authorised to view documents for Voltara Motors. Your access covers: Zentrix Cloud.** No sources.

**Say:** "Isolation is enforced before search. The search engine only scores chunks from companies the user is entitled to, so restricted content can't be retrieved, ranked or quoted. When a question names a restricted company, the user gets an explicit refusal."

**Do (optional):** ask **"Compare Zentrix and Voltara revenue"**. Zentrix is answered, Voltara is listed as blocked.

## 4. Bob in parallel: follow-ups on Company B (2 min) ①④

**Do (tab 2):** sign in as **Bob**. Point out that tab 1 is still Alice.

**Say:** "Each tab has its own session, so two users are using the system at the same time."

**Do:** ask, in order:

| Question | Expected answer | Point to make |
|---|---|---|
| What was Voltara's revenue in Q4? | 4.12 billion dollars, up 29% | |
| How did the automotive gross margin compare to Q3? | 17.8% in Q4 vs 15.1% in Q3 | Company carried over; draws on both the Q4 and the Q3 transcript |
| What drove the improvement? | Battery cost reductions, Aria reaching scale, lower logistics costs | "The improvement" is resolved from context; the answer comes from the analyst Q&A |
| What about Medivane? | Bob's second company is now searched | Topic kept, company switched; still within Bob's access |

**Do:** switch back to Alice's tab and ask **"What are the biggest risks?"**

**Say:** "Alice's conversation wasn't affected by Bob's. Conversations are stored per user and per conversation."

## 5. Charlie: the example scenario from the assignment (1 min) ③

**Do:** sign out in tab 2 and sign in as **Charlie**.

| Question | Expected |
|---|---|
| What was the revenue reported in Q4? | Brightmart 18.9 billion and Solvane 1.38 billion, each labelled with the company |
| What was Zentrix Cloud's revenue in Q4? | Access denied (Company A) |
| What did Voltara say about deliveries? | Access denied (Company B) |
| Try to open a Voltara PDF | Not possible: only his own PDFs are listed, and the download endpoint returns 403 for others |

## 6. Proof (1 min) ③ and concurrency

**Do (terminal):**

```bash
pytest -q
# 108 passed
python scripts/concurrency_demo.py
# 6 users x 3 questions in parallel, ... leaks: 0
```

**Say:** "The tests run every user against fifteen questions, including ones that name other companies, and check that nothing from another company ever comes back. The concurrency test runs eighteen sessions in parallel and checks that every conversation contains only its own turns."

**Do (optional):** show `logs/audit.jsonl`. "Every question is logged with the user, what was searched, what was blocked and which documents were returned."

## 7. Wrap-up (30 s)

**Say:**
* "Python, FastAPI and a plain web UI; runs with one command and no API key."
* "Access is enforced in code at several layers: token identity, pre-filtered search, a post-filter re-check, per-user conversations and authorised downloads. It doesn't rely on an LLM following instructions."
* "With an Anthropic API key, Claude writes the answer, but it only ever sees excerpts that already passed the filter."
* "For production: SSO, Redis or a database for state, hybrid vector search with metadata filters, and LLM query rewriting. All of these are covered in `docs/ARCHITECTURE.md`."

---

## Likely questions and short answers

**Why not a vector database?**
For earnings calls, the questions use the documents' own vocabulary, so BM25 is accurate, needs no downloads and is deterministic. The retriever has a one-method interface, so a vector or hybrid store slots in; the access filter becomes a metadata filter.

**Couldn't the LLM leak data from other users?**
No. The model only receives the excerpts retrieved under the user's filter and that user's own history. It never sees the corpus.

**What if a user guesses another user's conversation id?**
Conversations are keyed by the authenticated user plus the id. Another user gets a 404 on read, and a fresh conversation on write. Covered by `test_conversations_are_private`.

**How does it handle many users?**
FastAPI serves requests on a thread pool. The index is read-only, and the three pieces of shared mutable state (sessions, conversations, audit log) each have a lock. For multiple servers, move sessions and conversations to Redis.

**Why are the companies fictional?**
So the repository can be public with the PDFs included. Real investor-relations PDFs drop in by copying them into `data/pdfs/` and adding them to `access_control.json` (README section 9).
