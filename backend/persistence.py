"""Persist graded quiz submissions in SQLite (or DATABASE_URL)."""
from datetime import datetime

from backend.database import get_session
from backend.models import Answer, Submission


def save_submission(
    name,
    email,
    phone,
    recruiter_email,
    grading_results,
    email_sent=False,
    created_at=None,
    assessment="ds",
    opened_at=None,
    acknowledged_at=None,
    submitted_at=None,
    answer_timestamps=None,
):
    """Insert a submission row plus one answers row per question. Returns the new id."""
    answer_timestamps = answer_timestamps or {}
    session = get_session()
    try:
        submission = Submission(
            created_at=created_at or datetime.now(),
            name=name,
            email=email,
            phone=phone,
            recruiter_email=recruiter_email,
            score_percentage=grading_results["score_percentage"],
            correct_count=grading_results["correct_count"],
            total_questions=grading_results["total_questions"],
            email_sent=bool(email_sent),
            assessment=assessment or "ds",
            opened_at=opened_at,
            acknowledged_at=acknowledged_at,
            submitted_at=submitted_at or created_at or datetime.now(),
        )
        session.add(submission)
        session.flush()

        for question_key, result in grading_results["detailed_results"].items():
            session.add(
                Answer(
                    submission_id=submission.id,
                    question_key=question_key,
                    user_answer=str(result.get("user_answer", "")),
                    correct_answer=str(result.get("correct_answer", "")),
                    is_correct=bool(result.get("is_correct")),
                    answered_at=answer_timestamps.get(question_key),
                )
            )

        session.commit()
        return submission.id
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_email_sent(submission_id, email_sent):
    session = get_session()
    try:
        submission = session.get(Submission, submission_id)
        if submission is None:
            return
        submission.email_sent = bool(email_sent)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_submission(submission_id):
    session = get_session()
    try:
        return session.get(Submission, submission_id)
    finally:
        session.close()


def count_answers(submission_id):
    session = get_session()
    try:
        return (
            session.query(Answer)
            .filter(Answer.submission_id == submission_id)
            .count()
        )
    finally:
        session.close()
