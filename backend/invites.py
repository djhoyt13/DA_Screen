"""Exam invite persistence and status helpers."""
from datetime import datetime

from backend.database import get_session
from backend.models import Answer, Submission
from backend.models_invites import ExamInvite, new_invite_token


STATUS_SENT = "sent"
STATUS_OPENED = "opened"
STATUS_OPENED_NOT_COMPLETED = "opened_but_not_completed"
STATUS_COMPLETED = "completed"

STATUS_LABELS = {
    STATUS_SENT: "Sent",
    STATUS_OPENED: "Opened",
    STATUS_OPENED_NOT_COMPLETED: "Opened but not completed",
    STATUS_COMPLETED: "Completed",
}


def compute_status(invite):
    if invite.completed_at or invite.submission_id:
        return STATUS_COMPLETED
    if invite.acknowledged_at:
        return STATUS_OPENED_NOT_COMPLETED
    if invite.opened_at:
        return STATUS_OPENED
    return STATUS_SENT


def _iso(value):
    return value.isoformat(sep=" ") if value else None


def invite_to_dict(invite, *, include_token=False, public_app_url=None):
    status = compute_status(invite)
    path = "/data-scientist" if invite.assessment == "ds" else "/data-engineer"
    invite_url = None
    if public_app_url and invite.token:
        base = public_app_url.rstrip("/")
        invite_url = f"{base}{path}?invite={invite.token}"
    data = {
        "id": invite.id,
        "name": invite.name,
        "email": invite.email,
        "phone": invite.phone or "",
        "recruiter_email": invite.recruiter_email or "",
        "assessment": invite.assessment,
        "status": status,
        "status_label": STATUS_LABELS[status],
        "sent_at": _iso(invite.sent_at or invite.created_at),
        "opened_at": _iso(invite.opened_at),
        "acknowledged_at": _iso(invite.acknowledged_at),
        "completed_at": _iso(invite.completed_at),
        "submission_id": invite.submission_id,
        "invite_url": invite_url,
    }
    if include_token:
        data["token"] = invite.token
    return data


def create_invite(
    name,
    email,
    assessment,
    phone=None,
    recruiter_email=None,
    sent_at=None,
    public_app_url=None,
):
    session = get_session()
    try:
        invite = ExamInvite(
            token=new_invite_token(),
            name=name,
            email=email,
            phone=phone or None,
            recruiter_email=recruiter_email or None,
            assessment=assessment,
            sent_at=sent_at or datetime.now(),
            created_at=datetime.now(),
        )
        session.add(invite)
        session.commit()
        session.refresh(invite)
        return invite_to_dict(invite, include_token=True, public_app_url=public_app_url)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_invites(public_app_url=None):
    session = get_session()
    try:
        rows = (
            session.query(ExamInvite)
            .order_by(ExamInvite.sent_at.desc(), ExamInvite.id.desc())
            .all()
        )
        return [
            invite_to_dict(row, include_token=True, public_app_url=public_app_url)
            for row in rows
        ]
    finally:
        session.close()


def get_invite_public(token):
    """Candidate-facing invite payload (no admin token leakage beyond the URL token)."""
    session = get_session()
    try:
        invite = (
            session.query(ExamInvite)
            .filter(ExamInvite.token == str(token).strip())
            .one_or_none()
        )
        if invite is None:
            return None
        return {
            "token": invite.token,
            "name": invite.name,
            "email": invite.email,
            "phone": invite.phone or "",
            "recruiter_email": invite.recruiter_email or "",
            "assessment": invite.assessment,
            "status": compute_status(invite),
            "completed": compute_status(invite) == STATUS_COMPLETED,
        }
    finally:
        session.close()


def mark_opened(token, opened_at=None):
    session = get_session()
    try:
        invite = (
            session.query(ExamInvite)
            .filter(ExamInvite.token == str(token).strip())
            .one_or_none()
        )
        if invite is None:
            return None
        if invite.opened_at is None:
            invite.opened_at = opened_at or datetime.now()
            session.commit()
            session.refresh(invite)
        return invite_to_dict(invite)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def mark_acknowledged(token, acknowledged_at=None):
    session = get_session()
    try:
        invite = (
            session.query(ExamInvite)
            .filter(ExamInvite.token == str(token).strip())
            .one_or_none()
        )
        if invite is None:
            return None
        now = acknowledged_at or datetime.now()
        if invite.opened_at is None:
            invite.opened_at = now
        if invite.acknowledged_at is None:
            invite.acknowledged_at = now
        session.commit()
        session.refresh(invite)
        return invite_to_dict(invite)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def mark_completed(token, submission_id, completed_at=None):
    if not token:
        return None
    session = get_session()
    try:
        invite = (
            session.query(ExamInvite)
            .filter(ExamInvite.token == str(token).strip())
            .one_or_none()
        )
        if invite is None:
            return None
        now = completed_at or datetime.now()
        invite.submission_id = submission_id
        invite.completed_at = now
        if invite.opened_at is None:
            invite.opened_at = now
        if invite.acknowledged_at is None:
            invite.acknowledged_at = now
        session.commit()
        session.refresh(invite)
        return invite_to_dict(invite)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_invite_detail(invite_id):
    """Invite summary plus graded results when completed."""
    session = get_session()
    try:
        invite = session.get(ExamInvite, invite_id)
        if invite is None:
            return None
        detail = invite_to_dict(invite, include_token=True)
        if invite.submission_id:
            submission = session.get(Submission, invite.submission_id)
            if submission:
                answers = (
                    session.query(Answer)
                    .filter(Answer.submission_id == submission.id)
                    .order_by(Answer.id)
                    .all()
                )
                detail["results"] = {
                    "submission_id": submission.id,
                    "score_percentage": submission.score_percentage,
                    "correct_count": submission.correct_count,
                    "total_questions": submission.total_questions,
                    "email_sent": bool(submission.email_sent),
                    "opened_at": _iso(submission.opened_at),
                    "acknowledged_at": _iso(submission.acknowledged_at),
                    "submitted_at": _iso(submission.submitted_at or submission.created_at),
                    "detailed_results": [
                        {
                            "key": row.question_key,
                            "status": "correct" if row.is_correct else "incorrect",
                            "user_answer": row.user_answer,
                            "correct_answer": row.correct_answer,
                            "answered_at": _iso(row.answered_at),
                        }
                        for row in answers
                    ],
                }
        return detail
    finally:
        session.close()
