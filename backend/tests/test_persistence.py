from backend.grading import get_answer_key, grade_quiz
from backend.models import Answer, Submission
from backend.persistence import count_answers, save_submission
from backend.questions import QUESTION_KEYS
from backend.tests.data import PERFECT_ANSWERS, VALID_CANDIDATE

ACTIVE_COUNT = len(get_answer_key())


def test_save_submission_inserts_row_and_all_answers(db_path):
    grading_results = grade_quiz(PERFECT_ANSWERS)
    submission_id = save_submission(
        name=VALID_CANDIDATE["name"],
        email=VALID_CANDIDATE["email"],
        phone=VALID_CANDIDATE["phone"],
        recruiter_email=VALID_CANDIDATE["recruiter_email"],
        grading_results=grading_results,
        email_sent=False,
    )
    assert submission_id >= 1
    assert count_answers(submission_id) == ACTIVE_COUNT
    assert db_path.exists()

    from backend.database import get_session

    session = get_session()
    try:
        row = session.get(Submission, submission_id)
        assert row is not None
        assert row.name == "Jane Doe"
        assert row.score_percentage == 100.0
        assert row.correct_count == ACTIVE_COUNT
        assert row.total_questions == ACTIVE_COUNT
        assert row.email_sent is False
        keys = {
            a.question_key
            for a in session.query(Answer).filter_by(submission_id=submission_id).all()
        }
        assert keys == set(QUESTION_KEYS)
    finally:
        session.close()


def test_submit_endpoint_writes_sqlite_row(client, db_path):
    response = client.post(
        "/api/submit",
        json={**VALID_CANDIDATE, "answers": PERFECT_ANSWERS},
    )
    assert response.status_code == 200
    assert db_path.exists()

    from backend.database import get_session

    session = get_session()
    try:
        submissions = session.query(Submission).all()
        assert len(submissions) == 1
        assert session.query(Answer).count() == ACTIVE_COUNT
    finally:
        session.close()
