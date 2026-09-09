"""Admin exam invite tracking API tests."""
import pytest

from backend.tests.data import PERFECT_ANSWERS, VALID_CANDIDATE


@pytest.fixture
def admin_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key")
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:5173")
    return "test-admin-key"


def test_admin_requires_key(client, monkeypatch):
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    response = client.get("/api/admin/exams")
    assert response.status_code == 503


def test_admin_create_open_ack_complete_flow(client, admin_key, mock_send_email):
    headers = {"X-Admin-Key": admin_key}

    created = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "phone": "5551234567",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["status"] == "sent"
    assert body["token"]
    assert "/data-scientist?invite=" in body["invite_url"]
    token = body["token"]
    invite_id = body["id"]

    opened = client.post(f"/api/invite/{token}/open", json={"opened_at": "2026-09-09T18:00:00Z"})
    assert opened.status_code == 200
    assert opened.json()["status"] == "opened"

    ack = client.post(
        f"/api/invite/{token}/acknowledge",
        json={"acknowledged_at": "2026-09-09T18:01:00Z"},
    )
    assert ack.status_code == 200
    assert ack.json()["status"] == "opened_but_not_completed"

    listed = client.get("/api/admin/exams", headers=headers)
    assert listed.status_code == 200
    exams = listed.json()["exams"]
    assert any(row["id"] == invite_id and row["status"] == "opened_but_not_completed" for row in exams)

    submit = client.post(
        "/api/submit",
        json={
            **VALID_CANDIDATE,
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 200

    detail = client.get(f"/api/admin/exams/{invite_id}", headers=headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["status"] == "completed"
    assert detail_body["results"]["correct_count"] == len(PERFECT_ANSWERS)
    assert len(detail_body["results"]["detailed_results"]) == len(PERFECT_ANSWERS)


def test_admin_unauthorized(client, admin_key):
    response = client.get("/api/admin/exams", headers={"X-Admin-Key": "wrong"})
    assert response.status_code == 401
