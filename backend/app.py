"""
DA Screen FastAPI backend.

Start from the repository root:

    uvicorn backend.app:app --reload --port 8000

Database: SQLite at ``<repo_root>/quiz_results.db`` by default.
Override with ``DATABASE_URL`` (e.g. ``sqlite:///./quiz_results.db``).
"""
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import emailer, persistence
from backend.database import init_db
from backend.grading import get_answer_key, grade_quiz
from backend.questions import QUESTION_KEYS, build_questions_payload
from backend.validation import is_valid_email, is_valid_name, is_valid_phone

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(title="DA Screen API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validation_error(fields, message="Validation failed"):
    return JSONResponse(status_code=400, content={"error": message, "fields": fields})


def _as_str(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)


def validate_submit(payload):
    """Return a fields dict of errors, or empty dict if valid."""
    fields = {}
    name = _as_str(payload.get("name")).strip() if isinstance(payload, dict) else ""
    email = _as_str(payload.get("email")).strip() if isinstance(payload, dict) else ""
    phone = _as_str(payload.get("phone")).strip() if isinstance(payload, dict) else ""
    recruiter_email = (
        _as_str(payload.get("recruiter_email")).strip() if isinstance(payload, dict) else ""
    )

    if not name:
        fields["name"] = "Name is required"
    elif not is_valid_name(name):
        fields["name"] = "Please enter a valid name (letters, spaces, hyphens, and apostrophes only)"

    if not email:
        fields["email"] = "Email is required"
    elif not is_valid_email(email):
        fields["email"] = "Please enter a valid email address"

    if not phone:
        fields["phone"] = "Phone number is required"
    elif not is_valid_phone(phone):
        fields["phone"] = "Please enter a valid phone number (10-14 digits, can include country code)"

    if not recruiter_email:
        fields["recruiter_email"] = "Recruiter's email is required"
    elif not is_valid_email(recruiter_email):
        fields["recruiter_email"] = "Please enter a valid recruiter email address"

    answers = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(answers, dict):
        fields["answers"] = "Please make sure you have answered all of the questions"
    else:
        missing = False
        for key in get_answer_key():
            value = answers.get(key, "")
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing = True
                break
        if missing:
            fields["answers"] = "Please make sure you have answered all of the questions"

    return fields


def _detailed_results_list(detailed_results):
    rows = []
    for key, result in detailed_results.items():
        rows.append(
            {
                "key": key,
                "status": "correct" if result["is_correct"] else "incorrect",
                "user_answer": result["user_answer"],
                "correct_answer": result["correct_answer"],
            }
        )
    return rows


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/questions")
def get_questions():
    return build_questions_payload()


@app.post("/api/submit")
def submit_quiz(payload: dict = Body(default=None)):
    if payload is None:
        payload = {}
    try:
        fields = validate_submit(payload)
        if fields:
            return _validation_error(fields)

        name = _as_str(payload.get("name")).strip()
        email = _as_str(payload.get("email")).strip()
        phone = _as_str(payload.get("phone")).strip()
        recruiter_email = _as_str(payload.get("recruiter_email")).strip()
        raw_answers = payload.get("answers") or {}
        answers = {}
        for key in QUESTION_KEYS:
            answers[key] = _as_str(raw_answers.get(key, "")).strip() if raw_answers.get(key) is not None else ""

        grading_results = grade_quiz(answers)
        submitted_at = datetime.now()

        submission_id = persistence.save_submission(
            name=name,
            email=email,
            phone=phone,
            recruiter_email=recruiter_email,
            grading_results=grading_results,
            email_sent=False,
            created_at=submitted_at,
        )

        email_sent, email_warning = emailer.send_results_email(
            name=name,
            email=email,
            phone=phone,
            recruiter_email=recruiter_email,
            grading_results=grading_results,
            submitted_at=submitted_at,
        )
        if email_sent:
            persistence.update_email_sent(submission_id, True)

        return {
            "score_percentage": grading_results["score_percentage"],
            "correct_count": grading_results["correct_count"],
            "total_questions": grading_results["total_questions"],
            "detailed_results": _detailed_results_list(grading_results["detailed_results"]),
            "email_sent": bool(email_sent),
            "email_warning": email_warning,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
