import json

from backend.grading import get_answer_key
from backend.questions import QUESTION_KEYS, collect_question_keys
from backend.tests.data import PERFECT_ANSWERS, VALID_CANDIDATE


FORBIDDEN_QUESTION_KEYS = {"correct_answer", "expected", "answer", "answer_key"}


def _walk_keys(obj, found=None):
    if found is None:
        found = set()
    if isinstance(obj, dict):
        found.update(obj.keys())
        for value in obj.values():
            _walk_keys(value, found)
    elif isinstance(obj, list):
        for item in obj:
            _walk_keys(item, found)
    return found


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_questions_has_active_unique_keys_and_no_answer_leakage(client):
    response = client.get("/api/questions")
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Data Scientist Technical Review"

    keys = collect_question_keys(payload)
    assert payload["total_questions"] == len(keys)
    assert len(set(keys)) == len(keys)
    assert keys == QUESTION_KEYS
    assert len(keys) == len(get_answer_key())

    all_keys = _walk_keys(payload)
    assert FORBIDDEN_QUESTION_KEYS.isdisjoint(all_keys)

    raw = json.dumps(payload)
    assert "correct_answer" not in raw
    assert "Answer Key" not in raw
    assert "get_answer_key" not in raw

    table = None
    asyncio_options = None
    ml_keys = []
    docker_keys = []
    for section in payload["sections"]:
        for category in section["categories"]:
            for block in category["blocks"]:
                if block.get("type") == "table":
                    table = block
            for question in category["questions"]:
                if question["key"] == "answer_Asyncio":
                    asyncio_options = question.get("options")
                if question["key"].startswith("answer_ML_"):
                    ml_keys.append(question["key"])
                if question["key"].startswith("answer_Docker_"):
                    docker_keys.append(question["key"])

    assert table is not None
    assert table["columns"] == ["Car Type"]
    assert table["rows"] == [
        ["Sedan"],
        ["SUV"],
        ["Convertible"],
        ["Sedan"],
        ["Convertible"],
        ["SUV"],
    ]
    assert asyncio_options == [
        '"Hello world!, Hello world!"',
        '"world! Hello, world! Hello"',
        '"Hello, Hello, world!, world!"',
        '"world!, world, Hello, Hello"',
    ]
    assert ml_keys == ["answer_ML_q2", "answer_ML_q3"]
    assert docker_keys == [
        "answer_Docker_Build",
        "answer_Docker_Start",
        "answer_Docker_Stop",
    ]


def test_submit_400_on_empty(client):
    response = client.post("/api/submit", json={})
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert "fields" in body
    for field in ("name", "email", "phone", "recruiter_email", "answers"):
        assert field in body["fields"]


def test_submit_400_invalid_candidate_and_blank_answers(client):
    response = client.post(
        "/api/submit",
        json={
            "name": "Test123",
            "email": "not-an-email",
            "phone": "abc",
            "recruiter_email": "also-bad",
            "answers": {key: "" for key in QUESTION_KEYS},
        },
    )
    assert response.status_code == 400
    fields = response.json()["fields"]
    assert "name" in fields
    assert "email" in fields
    assert "phone" in fields
    assert "recruiter_email" in fields
    assert "answers" in fields


def test_submit_200_mocked_smtp_persists_all_answers(client, mock_send_email, db_path):
    active_count = len(get_answer_key())
    mock_send_email.return_value = (True, None)
    response = client.post(
        "/api/submit",
        json={**VALID_CANDIDATE, "answers": PERFECT_ANSWERS},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["correct_count"] == active_count
    assert body["total_questions"] == active_count
    assert body["score_percentage"] == 100.0
    assert body["email_sent"] is True
    assert body["email_warning"] is None
    assert len(body["detailed_results"]) == active_count
    assert body["detailed_results"][0]["key"] == "answer_Unpacking"
    assert body["detailed_results"][0]["status"] == "correct"
    mock_send_email.assert_called_once()

    from backend.database import get_session
    from backend.models import Answer, Submission

    session = get_session()
    try:
        submissions = session.query(Submission).all()
        assert len(submissions) == 1
        assert submissions[0].email == VALID_CANDIDATE["email"]
        assert submissions[0].correct_count == active_count
        assert getattr(submissions[0], "assessment", "ds") == "ds"
        answers = session.query(Answer).filter_by(submission_id=submissions[0].id).all()
        assert len(answers) == active_count
        assert {row.question_key for row in answers} == set(QUESTION_KEYS)
    finally:
        session.close()
    assert db_path.exists()


def test_submit_smtp_failure_still_200_and_persists(client, mock_send_email):
    mock_send_email.return_value = (
        False,
        "Email sending failed: connection refused. Results saved to database.",
    )
    response = client.post(
        "/api/submit",
        json={**VALID_CANDIDATE, "answers": PERFECT_ANSWERS},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email_sent"] is False
    assert "Results saved to database" in body["email_warning"]
    assert body["correct_count"] == len(get_answer_key())

    from backend.database import get_session
    from backend.models import Submission

    session = get_session()
    try:
        assert session.query(Submission).count() == 1
        assert session.query(Submission).one().email_sent is False
    finally:
        session.close()
