"""PATCH /api/invite/{token}/candidate — persist contact edits before submit."""
import pytest

from backend.tests.data import PERFECT_ANSWERS
from backend.validation import normalize_phone


ADMIN_EMAIL = "david.hoyt@mantech.com"
ADMIN_PASSWORD = "hoyt"


@pytest.fixture
def admin_headers(monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:5173")
    return {
        "X-Admin-Email": ADMIN_EMAIL,
        "X-Admin-Password": ADMIN_PASSWORD,
    }


def _create_invite(client, admin_headers, **overrides):
    headers = admin_headers
    payload = {
        "name": "Pat Candidate",
        "email": "pat@example.com",
        "phone": "5551234567",
        "recruiter_email": "recruiter@example.com",
        "assessment": "ds",
        **overrides,
    }
    created = client.post("/api/admin/exams", headers=headers, json=payload)
    assert created.status_code == 200
    return created.json()


def test_patch_candidate_partial_update(client, admin_headers):
    invite = _create_invite(client, admin_headers)
    token = invite["token"]
    original_recruiter = invite["recruiter_email"]
    original_phone = invite["phone"]

    patched = client.patch(
        f"/api/invite/{token}/candidate",
        json={"name": "Updated Name", "email": "updated@example.com"},
    )
    assert patched.status_code == 200
    body = patched.json()
    assert body["token"] == token
    assert body["name"] == "Updated Name"
    assert body["email"] == "updated@example.com"
    assert body["phone"] == original_phone
    assert body["recruiter_email"] == original_recruiter
    assert body["assessment"] == "ds"
    assert body["completed"] is False
    assert "status" in body

    # recruiter_email in body is ignored; other fields still update
    again = client.patch(
        f"/api/invite/{token}/candidate",
        json={
            "phone": "(555) 999-8888",
            "recruiter_email": "hacker@example.com",
        },
    )
    assert again.status_code == 200
    again_body = again.json()
    assert again_body["phone"] == "(555) 999-8888"
    assert again_body["recruiter_email"] == original_recruiter
    assert again_body["name"] == "Updated Name"

    from backend.database import get_session
    from backend.models_invites import ExamInvite

    session = get_session()
    try:
        row = session.get(ExamInvite, invite["id"])
        assert row.name == "Updated Name"
        assert row.email == "updated@example.com"
        assert row.phone == "(555) 999-8888"
        assert row.phone_normalized == normalize_phone("(555) 999-8888")
        assert row.recruiter_email == original_recruiter
    finally:
        session.close()


def test_patch_candidate_phone_collision(client, admin_headers):
    first = _create_invite(
        client,
        admin_headers,
        name="First Candidate",
        email="first@example.com",
        phone="5551000001",
    )
    _create_invite(
        client,
        admin_headers,
        name="Second Candidate",
        email="second@example.com",
        phone="5551000002",
    )

    response = client.patch(
        f"/api/invite/{first['token']}/candidate",
        json={"phone": "5551000002"},
    )
    assert response.status_code == 400
    assert "phone" in response.json()["fields"]

    # Own phone (same token excluded) is allowed
    same = client.patch(
        f"/api/invite/{first['token']}/candidate",
        json={"phone": "5551000001"},
    )
    assert same.status_code == 200
    assert same.json()["phone"] == "5551000001"


def test_patch_candidate_missing_token(client, admin_headers):
    response = client.patch(
        "/api/invite/does-not-exist-token/candidate",
        json={"name": "Nobody"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_patch_candidate_completed_invite(client, admin_headers):
    invite = _create_invite(client, admin_headers)
    token = invite["token"]

    submit = client.post(
        "/api/submit",
        json={
            "name": invite["name"],
            "email": invite["email"],
            "phone": invite["phone"],
            "recruiter_email": invite["recruiter_email"],
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 200

    response = client.patch(
        f"/api/invite/{token}/candidate",
        json={"name": "Too Late"},
    )
    assert response.status_code == 404
    assert "completed" in response.json()["error"].lower()


def test_patch_candidate_empty_body(client, admin_headers):
    invite = _create_invite(client, admin_headers)
    response = client.patch(f"/api/invite/{invite['token']}/candidate", json={})
    assert response.status_code == 400
    assert "name" in response.json()["error"].lower() or "required" in response.json()[
        "error"
    ].lower()

    only_recruiter = client.patch(
        f"/api/invite/{invite['token']}/candidate",
        json={"recruiter_email": "other@example.com"},
    )
    assert only_recruiter.status_code == 400
