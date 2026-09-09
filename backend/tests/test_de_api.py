"""Data Engineer assessment API coverage."""

import json

from backend.de_quiz import DE_QUESTION_KEYS, get_de_answer_key
from backend.tests.data import VALID_CANDIDATE, perfect_de_answers


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


def test_assessments_lists_ds_and_de(client):
    response = client.get("/api/assessments")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["assessments"]}
    assert ids == {"ds", "de"}


def test_de_questions_payload(client):
    response = client.get("/api/questions?assessment=de")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assessment"] == "de"
    assert payload["title"] == "Data Engineer Technical Review"
    assert payload["total_questions"] == 16

    keys = []
    for section in payload["sections"]:
        for category in section["categories"]:
            for question in category["questions"]:
                keys.append(question["key"])
    assert keys == DE_QUESTION_KEYS
    assert len(keys) == len(get_de_answer_key())

    all_keys = _walk_keys(payload)
    assert FORBIDDEN_QUESTION_KEYS.isdisjoint(all_keys)
    raw = json.dumps(payload)
    assert "Answer Key" not in raw
    assert "get_de_answer_key" not in raw


def test_unknown_assessment_404(client):
    response = client.get("/api/questions?assessment=marketing")
    assert response.status_code == 404


def test_de_submit_perfect(client, mock_send_email):
    mock_send_email.return_value = (True, None)
    response = client.post(
        "/api/submit",
        json={
            **VALID_CANDIDATE,
            "assessment": "de",
            "answers": perfect_de_answers(),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["assessment"] == "de"
    assert body["correct_count"] == 16
    assert body["total_questions"] == 16
    assert body["score_percentage"] == 100.0
    assert body["email_sent"] is True
    mock_send_email.assert_called_once()
    kwargs = mock_send_email.call_args.kwargs
    assert kwargs.get("assessment_title") == "Data Engineer Initial Assessment"

    from backend.database import get_session
    from backend.models import Submission

    session = get_session()
    try:
        row = session.query(Submission).one()
        assert row.assessment == "de"
        assert row.correct_count == 16
    finally:
        session.close()
