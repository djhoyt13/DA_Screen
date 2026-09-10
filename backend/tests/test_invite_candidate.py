"""PATCH /api/invite/{token}/candidate — persist contact edits before submit."""
import pytest

from backend.tests.data import PERFECT_ANSWERS
from backend.validation import normalize_phone


@pytest.fixture
def admin_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key")
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:5173")
    return "test-admin-key"


def _create_invite(client, admin_key, **overrides):
    headers = {"X-Admin-Key": admin_key}
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


def test_patch_candidate_partial_update(client, admin_key):
    invite = _create_invite(client, admin_key)
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


def test_patch_candidate_phone_collision(client, admin_key):
    first = _create_invite(
        client,
        admin_key,
        name="First Candidate",
        email="first@example.com",
        phone="5551000001",
    )
    _create_invite(
        client,
        admin_key,
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


def test_patch_candidate_missing_token(client, admin_key):
    response = client.patch(
        "/api/invite/does-not-exist-token/candidate",
        json={"name": "Nobody"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_patch_candidate_completed_invite(client, admin_key):
    invite = _create_invite(client, admin_key)
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


def test_patch_candidate_empty_body(client, admin_key):
    invite = _create_invite(client, admin_key)
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
