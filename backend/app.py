"""
DA Screen FastAPI backend.

Start from the repository root:

    uvicorn backend.app:app --reload --port 8000

Database: SQLite at ``<repo_root>/quiz_results.db`` by default.
Override with ``DATABASE_URL`` (e.g. ``sqlite:///./quiz_results.db``).
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from typing import Optional
from fastapi import Body, FastAPI, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import assessments, emailer, invites, persistence
from backend.admin_auth import require_admin
from backend.database import init_db
from backend.timing import extract_timing, parse_iso_datetime
from backend.validation import is_valid_email, is_valid_name, is_valid_phone

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


def _public_app_url():
    return (os.getenv("PUBLIC_APP_URL") or "http://127.0.0.1:5173").rstrip("/")


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


def validate_submit(payload, assessment_id="ds"):
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
        for key in assessments.get_answer_key_for(assessment_id):
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


@app.get("/api/assessments")
def get_assessments():
    return {"assessments": assessments.list_assessments()}


@app.get("/api/questions")
def get_questions(assessment: str = Query(default="ds")):
    normalized = assessments.normalize_assessment_id(assessment)
    if normalized is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Unknown assessment: {assessment}"},
        )
    return assessments.build_questions_payload(normalized)


@app.get("/api/invite/{token}")
def get_invite(token: str):
    data = invites.get_invite_public(token)
    if data is None:
        return JSONResponse(status_code=404, content={"error": "Invite not found"})
    return data


@app.post("/api/invite/{token}/open")
def open_invite(token: str, payload: dict = Body(default=None)):
    opened_at = None
    if isinstance(payload, dict) and payload.get("opened_at"):
        opened_at = parse_iso_datetime(payload.get("opened_at"))
    data = invites.mark_opened(token, opened_at=opened_at)
    if data is None:
        return JSONResponse(status_code=404, content={"error": "Invite not found"})
    return data


@app.post("/api/invite/{token}/acknowledge")
def acknowledge_invite(token: str, payload: dict = Body(default=None)):
    acknowledged_at = None
    if isinstance(payload, dict) and payload.get("acknowledged_at"):
        acknowledged_at = parse_iso_datetime(payload.get("acknowledged_at"))
    data = invites.mark_acknowledged(token, acknowledged_at=acknowledged_at)
    if data is None:
        return JSONResponse(status_code=404, content={"error": "Invite not found"})
    return data


@app.get("/api/admin/exams")
def admin_list_exams(
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    admin_key: Optional[str] = Query(default=None),
):
    auth_error = require_admin(x_admin_key=x_admin_key, admin_key=admin_key)
    if auth_error is not None:
        return auth_error
    rows = invites.list_exams(public_app_url=_public_app_url())
    return {"exams": rows}


@app.post("/api/admin/exams")
def admin_create_exam(
    payload: dict = Body(default=None),
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    admin_key: Optional[str] = Query(default=None),
):
    auth_error = require_admin(x_admin_key=x_admin_key, admin_key=admin_key)
    if auth_error is not None:
        return auth_error
    if payload is None:
        payload = {}

    name = _as_str(payload.get("name")).strip()
    email = _as_str(payload.get("email")).strip()
    phone = _as_str(payload.get("phone")).strip()
    recruiter_email = _as_str(payload.get("recruiter_email")).strip()
    assessment_id = assessments.normalize_assessment_id(payload.get("assessment", "ds"))

    fields = {}
    if not name:
        fields["name"] = "Name is required"
    elif not is_valid_name(name):
        fields["name"] = "Please enter a valid name (letters, spaces, hyphens, and apostrophes only)"
    if not email:
        fields["email"] = "Email is required"
    elif not is_valid_email(email):
        fields["email"] = "Please enter a valid email address"
    if phone and not is_valid_phone(phone):
        fields["phone"] = "Please enter a valid phone number (10-14 digits, can include country code)"
    if recruiter_email and not is_valid_email(recruiter_email):
        fields["recruiter_email"] = "Please enter a valid recruiter email address"
    if assessment_id is None:
        fields["assessment"] = "Assessment must be ds or de"
    if fields:
        return _validation_error(fields)

    created = invites.create_invite(
        name=name,
        email=email,
        assessment=assessment_id,
        phone=phone or None,
        recruiter_email=recruiter_email or None,
        public_app_url=_public_app_url(),
    )
    return created


@app.get("/api/admin/exams/{exam_key}")
def admin_exam_detail(
    exam_key: str,
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    admin_key: Optional[str] = Query(default=None),
):
    auth_error = require_admin(x_admin_key=x_admin_key, admin_key=admin_key)
    if auth_error is not None:
        return auth_error
    detail = invites.get_exam_detail(exam_key, public_app_url=_public_app_url())
    if detail is None:
        return JSONResponse(status_code=404, content={"error": "Exam not found"})
    return detail


@app.post("/api/submit")
def submit_quiz(payload: dict = Body(default=None)):
    if payload is None:
        payload = {}
    try:
        assessment_raw = payload.get("assessment", "ds")
        assessment_id = assessments.normalize_assessment_id(assessment_raw)
        if assessment_id is None:
            return _validation_error(
                {"assessment": f"Unknown assessment: {assessment_raw}"},
                message="Validation failed",
            )

        fields = validate_submit(payload, assessment_id=assessment_id)
        if fields:
            return _validation_error(fields)

        meta = assessments.get_assessment_meta(assessment_id)
        name = _as_str(payload.get("name")).strip()
        email = _as_str(payload.get("email")).strip()
        phone = _as_str(payload.get("phone")).strip()
        recruiter_email = _as_str(payload.get("recruiter_email")).strip()
        invite_token = _as_str(payload.get("invite_token")).strip()
        raw_answers = payload.get("answers") or {}
        answers = {}
        for key in assessments.question_keys_for(assessment_id):
            answers[key] = (
                _as_str(raw_answers.get(key, "")).strip()
                if raw_answers.get(key) is not None
                else ""
            )

        grading_results = assessments.grade_assessment(assessment_id, answers)
        server_now = datetime.now()
        timing = extract_timing(payload)
        submitted_at = timing["submitted_at"] or server_now

        submission_id = persistence.save_submission(
            name=name,
            email=email,
            phone=phone,
            recruiter_email=recruiter_email,
            grading_results=grading_results,
            email_sent=False,
            created_at=server_now,
            assessment=assessment_id,
            opened_at=timing["opened_at"],
            acknowledged_at=timing["acknowledged_at"],
            submitted_at=submitted_at,
            answer_timestamps=timing["answer_timestamps"],
        )

        if invite_token:
            invites.mark_completed(
                invite_token,
                submission_id=submission_id,
                completed_at=submitted_at,
            )

        email_sent, email_warning = emailer.send_results_email(
            name=name,
            email=email,
            phone=phone,
            recruiter_email=recruiter_email,
            grading_results=grading_results,
            submitted_at=submitted_at,
            assessment_title=meta["display_name"],
        )
        if email_sent:
            persistence.update_email_sent(submission_id, True)

        return {
            "assessment": assessment_id,
            "score_percentage": grading_results["score_percentage"],
            "correct_count": grading_results["correct_count"],
            "total_questions": grading_results["total_questions"],
            "detailed_results": _detailed_results_list(grading_results["detailed_results"]),
            "email_sent": bool(email_sent),
            "email_warning": email_warning,
            "timing": {
                "opened_at": timing["opened_at"].isoformat(sep=" ") if timing["opened_at"] else None,
                "acknowledged_at": (
                    timing["acknowledged_at"].isoformat(sep=" ")
                    if timing["acknowledged_at"]
                    else None
                ),
                "submitted_at": submitted_at.isoformat(sep=" "),
            },
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
