# Multi-User Document Search and Q&A

A Python web app for searching earnings-call PDFs. Each user only gets answers from the companies they have access to, and follow-up questions keep the conversation's context.

![Alice asks a question and a follow-up](docs/screenshots/02_alice_followup.png)

Stack: Python, FastAPI, BM25 search, plain HTML/JS UI.

More: [Architecture](docs/ARCHITECTURE.md) · [Reviewer walkthrough](docs/REVIEWER_WALKTHROUGH.md)

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/mehuldas13/Quantiphi-Assignment.git
cd Quantiphi-Assignment
./run.sh        # macOS / Linux
run.bat         # Windows
```

Open **http://127.0.0.1:8000** and keep the terminal running.

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'app'` | Run the command from the project folder |
| Syntax or type errors on start | Use Python 3.10 or newer |
| Port 8000 in use | `PORT=8001 ./run.sh`, then open port 8001 |
| Browser can't reach the page | Check the terminal; the server must be running |

## Demo users and documents

`data/pdfs/` has six transcripts from five fictional companies.

| User | Email | Access |
|---|---|---|
| Alice | `alice@email.com` | Zentrix Cloud (Company A) |
| Bob | `bob@email.com` | Voltara Motors (B), Medivane Therapeutics (C) |
| Charlie | `charlie@email.com` | Solvane Energy (D), Brightmart Retail (E) |
| User A | `userA@email.com` | Zentrix Cloud |
| User B | `userB@email.com` | Voltara Motors |
| User C | `userC@email.com` | Zentrix Cloud, Voltara Motors |

Access rules: [`data/access_control.json`](data/access_control.json).

## Using the app

1. Pick a user. The left panel lists their documents.
2. Ask "What was the revenue reported in Q4?", then "And the gross margin?".
3. Expand **Sources** and **How this answer was built** under an answer.
4. Ask about a company the user can't access to see the access-denied response.

Each browser tab is a separate session, so you can use two users side by side.

| Access denied | Follow-up questions |
|---|---|
| ![Charlie](docs/screenshots/05_charlie_isolation.png) | ![Bob](docs/screenshots/04_bob_followups.png) |

## Requirements coverage

| Requirement | Implementation |
|---|---|
| Earnings-call PDFs from 4–5 companies | `data/pdfs/` (5 companies, 6 PDFs) |
| Users with access to one or two companies | `data/access_control.json` |
| Retrieve relevant excerpts | `app/retriever.py`, `app/answer.py` |
| Follow-ups keep context | `app/contextualizer.py`, `app/memory.py` |
| Users can't see others' documents | Search is filtered by the user's companies (`app/retriever.py`, `app/service.py`) |
| UI: log in, ask, follow up | `app/static/` |
| Multiple users at the same time | `tests/test_concurrency.py`, `scripts/concurrency_demo.py` |

## Project structure

```
app/
  main.py            API endpoints, serves the UI
  service.py         Q&A pipeline
  access.py          Access rules
  auth.py            Login and tokens
  ingest.py          PDF loading and chunking
  retriever.py       BM25 search
  contextualizer.py  Follow-up handling
  memory.py          Conversation history
  answer.py          Answer generation
  text.py            Tokenizer and synonyms
  config.py          Settings
  static/            Web UI
data/
  access_control.json
  pdfs/
scripts/             Sample PDF generator, concurrency demo
tests/
docs/
```

## Tests

```bash
pytest -q
```

Covers access isolation, follow-up context and parallel users. With the app running, `python scripts/concurrency_demo.py` runs six users in parallel and reports any leaks.

## API (Swagger)

Open **http://127.0.0.1:8000/docs**.

1. Call `POST /api/login` with `{"email": "alice@email.com"}` and copy the `token` and `conversation_id`.
2. Click **Authorize** and paste the token (without `Bearer`).
3. Call `POST /api/chat` with `{"question": "What was the revenue reported in Q4?", "conversation_id": "..."}`.

Screenshots: [reviewer walkthrough](docs/REVIEWER_WALKTHROUGH.md#7-api-in-swagger).

## Adding PDFs

Copy the PDF into `data/pdfs/`, list it under a company in `data/access_control.json`, give that company to the right users, and restart.
