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

SOURCE_INVITE = "invite"
SOURCE_SUBMISSION = "submission"


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


def _score_fields(submission):
    if submission is None:
        return {
            "score_percentage": None,
            "correct_count": None,
            "total_questions": None,
        }
    return {
        "score_percentage": submission.score_percentage,
        "correct_count": submission.correct_count,
        "total_questions": submission.total_questions,
    }


def _results_payload(submission, answers):
    return {
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


def invite_to_dict(invite, *, include_token=False, public_app_url=None, submission=None):
    status = compute_status(invite)
    path = "/data-scientist" if invite.assessment == "ds" else "/data-engineer"
    invite_url = None
    if public_app_url and invite.token:
        base = public_app_url.rstrip("/")
        invite_url = f"{base}{path}?invite={invite.token}"
    data = {
        "row_id": f"invite-{invite.id}",
        "source": SOURCE_INVITE,
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
        **_score_fields(submission),
    }
    if include_token:
        data["token"] = invite.token
    return data


def submission_to_exam_row(submission):
    completed = submission.submitted_at or submission.created_at
    return {
        "row_id": f"submission-{submission.id}",
        "source": SOURCE_SUBMISSION,
        "id": submission.id,
        "name": submission.name,
        "email": submission.email,
        "phone": submission.phone or "",
        "recruiter_email": submission.recruiter_email or "",
        "assessment": submission.assessment or "ds",
        "status": STATUS_COMPLETED,
        "status_label": STATUS_LABELS[STATUS_COMPLETED],
        "sent_at": None,
        "opened_at": _iso(submission.opened_at),
        "acknowledged_at": _iso(submission.acknowledged_at),
        "completed_at": _iso(completed),
        "submission_id": submission.id,
        "invite_url": None,
        **_score_fields(submission),
    }


def _exam_sort_key(row):
    """Newest sent_at first; rows with null sent_at sort last."""
    sent = row.get("sent_at") or ""
    has_sent = 1 if sent else 0
    return (has_sent, sent, row.get("id") or 0)


def create_invite(
    name,
    email,
    assessment,
    phone=None,
    phone_normalized=None,
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
            phone_normalized=phone_normalized or None,
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


def has_incomplete_invite_for_phone(phone_normalized, exclude_token=None):
    """True if an incomplete invite already uses this normalized phone.

    When ``exclude_token`` is set (e.g. the invite being submitted), that row is
    ignored so a candidate can keep or re-submit their own phone.
    """
    if not phone_normalized:
        return False
    session = get_session()
    try:
        query = (
            session.query(ExamInvite)
            .filter(ExamInvite.phone_normalized == phone_normalized)
            .filter(ExamInvite.completed_at.is_(None))
            .filter(ExamInvite.submission_id.is_(None))
        )
        if exclude_token:
            query = query.filter(ExamInvite.token != str(exclude_token).strip())
        invite = query.first()
        return invite is not None
    finally:
        session.close()


def list_invites(public_app_url=None):
    """Backward-compatible alias for unified exam list."""
    return list_exams(public_app_url=public_app_url)


def list_exams(public_app_url=None):
    """All invites plus orphan submissions (not linked from any invite)."""
    session = get_session()
    try:
        invites = session.query(ExamInvite).all()
        linked_ids = {inv.submission_id for inv in invites if inv.submission_id}

        submissions_by_id = {}
        if linked_ids:
            for sub in session.query(Submission).filter(Submission.id.in_(linked_ids)):
                submissions_by_id[sub.id] = sub

        rows = []
        for invite in invites:
            linked = (
                submissions_by_id.get(invite.submission_id)
                if invite.submission_id
                else None
            )
            rows.append(
                invite_to_dict(
                    invite,
                    include_token=True,
                    public_app_url=public_app_url,
                    submission=linked,
                )
            )

        orphan_query = session.query(Submission)
        if linked_ids:
            orphan_query = orphan_query.filter(~Submission.id.in_(linked_ids))
        for submission in orphan_query.all():
            rows.append(submission_to_exam_row(submission))

        rows.sort(key=_exam_sort_key, reverse=True)
        return rows
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
        return _public_invite_payload(invite)
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


def _public_invite_payload(invite):
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


def update_candidate_contact(
    token,
    *,
    name=None,
    email=None,
    phone=None,
    phone_normalized=None,
):
    """Partial upsert of candidate contact on an incomplete invite.

    Does not overwrite ``recruiter_email``.

    Returns:
        ``("ok", public_payload)`` on success,
        ``("not_found", None)`` if token is unknown,
        ``("completed", None)`` if the invite is already completed.
    """
    if not token:
        return ("not_found", None)
    session = get_session()
    try:
        invite = (
            session.query(ExamInvite)
            .filter(ExamInvite.token == str(token).strip())
            .one_or_none()
        )
        if invite is None:
            return ("not_found", None)
        if compute_status(invite) == STATUS_COMPLETED:
            return ("completed", None)
        if name is not None:
            invite.name = name
        if email is not None:
            invite.email = email
        if phone is not None:
            invite.phone = phone or None
        if phone_normalized is not None:
            invite.phone_normalized = phone_normalized or None
        session.commit()
        session.refresh(invite)
        return ("ok", _public_invite_payload(invite))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def mark_completed(
    token,
    submission_id,
    completed_at=None,
    name=None,
    email=None,
    phone=None,
    phone_normalized=None,
):
    """Mark invite completed and optionally upsert candidate contact fields.

    Does not overwrite ``recruiter_email`` — that stays recruiter-provided.
    """
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
        if name is not None:
            invite.name = name
        if email is not None:
            invite.email = email
        if phone is not None:
            invite.phone = phone or None
        if phone_normalized is not None:
            invite.phone_normalized = phone_normalized or None
        session.commit()
        session.refresh(invite)
        return invite_to_dict(invite)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def parse_exam_key(exam_key):
    """Parse legacy invite id or row_id into (source, pk). Returns None if invalid."""
    key = str(exam_key).strip()
    if not key:
        return None
    if key.isdigit():
        return (SOURCE_INVITE, int(key))
    if key.startswith("invite-"):
        rest = key[len("invite-") :]
        if rest.isdigit():
            return (SOURCE_INVITE, int(rest))
        return None
    if key.startswith("submission-"):
        rest = key[len("submission-") :]
        if rest.isdigit():
            return (SOURCE_SUBMISSION, int(rest))
        return None
    return None


def get_invite_detail(invite_id):
    """Invite summary plus graded results when completed."""
    session = get_session()
    try:
        invite = session.get(ExamInvite, invite_id)
        if invite is None:
            return None
        submission = None
        answers = []
        if invite.submission_id:
            submission = session.get(Submission, invite.submission_id)
            if submission:
                answers = (
                    session.query(Answer)
                    .filter(Answer.submission_id == submission.id)
                    .order_by(Answer.id)
                    .all()
                )
        detail = invite_to_dict(
            invite, include_token=True, submission=submission
        )
        if submission:
            detail["results"] = _results_payload(submission, answers)
        return detail
    finally:
        session.close()


def get_submission_exam_detail(submission_id):
    """Orphan (or any) submission as an admin exam detail row."""
    session = get_session()
    try:
        submission = session.get(Submission, submission_id)
        if submission is None:
            return None
        answers = (
            session.query(Answer)
            .filter(Answer.submission_id == submission.id)
            .order_by(Answer.id)
            .all()
        )
        detail = submission_to_exam_row(submission)
        detail["results"] = _results_payload(submission, answers)
        return detail
    finally:
        session.close()


def get_exam_detail(exam_key, public_app_url=None):
    """Detail for invite-{n}, submission-{n}, or legacy numeric invite id."""
    parsed = parse_exam_key(exam_key)
    if parsed is None:
        return None
    source, pk = parsed
    if source == SOURCE_INVITE:
        detail = get_invite_detail(pk)
        if detail is None:
            return None
        if public_app_url and detail.get("token"):
            path = (
                "/data-scientist"
                if detail.get("assessment") == "ds"
                else "/data-engineer"
            )
            detail["invite_url"] = (
                f"{public_app_url.rstrip('/')}{path}?invite={detail['token']}"
            )
        return detail
    return get_submission_exam_detail(pk)
