# DA Screen API

FastAPI backend for the Data Scientist Technical Review. The React client
calls this API; root `app.py` remains the legacy Streamlit app.

## Start

From the repository root (with `.venv` activated):

```bash
uvicorn backend.app:app --reload --port 8000
```

- Health: `GET http://127.0.0.1:8000/api/health`
- Questions: `GET http://127.0.0.1:8000/api/questions`
- Submit: `POST http://127.0.0.1:8000/api/submit`

CORS allows `http://127.0.0.1:5173` and `http://localhost:5173`.

## Database

Default: SQLite file **`<repo_root>/quiz_results.db`**.

That matches `sqlite:///./quiz_results.db` when uvicorn is started from the
repo root. Override with:

```bash
export DATABASE_URL=sqlite:///./quiz_results.db
```

Tables: `submissions`, `answers`. Created on API startup.

SMTP uses `SENDER_EMAIL` / `SENDER_PASSWORD` from the repo-root `.env`.
Missing credentials or SMTP errors still return HTTP 200 with `email_sent: false`;
the row is always written to SQLite.

## Tests

```bash
pytest backend/tests -v
```
