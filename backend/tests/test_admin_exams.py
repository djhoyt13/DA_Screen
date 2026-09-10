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


def test_admin_create_open_ack_complete_flow(client, admin_key, mock_send_invite_email):
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
    assert body["source"] == "invite"
    assert body["row_id"] == f"invite-{body['id']}"
    assert body["token"]
    assert "/data-scientist?invite=" in body["invite_url"]
    assert body["email_sent"] is True
    assert body["email_warning"] is None
    mock_send_invite_email.assert_called_once()
    call_kwargs = mock_send_invite_email.call_args.kwargs
    assert call_kwargs["email"] == "pat@example.com"
    assert body["invite_url"] in call_kwargs["invite_url"]
    assert "Data Scientist" in call_kwargs["assessment_title"]
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
    assert any(
        row["id"] == invite_id
        and row["source"] == "invite"
        and row["status"] == "opened_but_not_completed"
        for row in exams
    )

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
    assert detail_body["source"] == "invite"
    assert detail_body["row_id"] == f"invite-{invite_id}"
    assert detail_body["results"]["correct_count"] == len(PERFECT_ANSWERS)
    assert len(detail_body["results"]["detailed_results"]) == len(PERFECT_ANSWERS)

    by_row_id = client.get(f"/api/admin/exams/invite-{invite_id}", headers=headers)
    assert by_row_id.status_code == 200
    assert by_row_id.json()["id"] == invite_id


def test_admin_create_requires_phone_and_recruiter(client, admin_key):
    headers = {"X-Admin-Key": admin_key}
    missing_phone = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert missing_phone.status_code == 400
    assert "phone" in missing_phone.json()["fields"]

    missing_recruiter = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "phone": "5551234567",
            "assessment": "ds",
        },
    )
    assert missing_recruiter.status_code == 400
    assert "recruiter_email" in missing_recruiter.json()["fields"]


def test_admin_create_duplicate_incomplete_phone(client, admin_key, mock_send_invite_email):
    headers = {"X-Admin-Key": admin_key}
    payload = {
        "name": "First Candidate",
        "email": "first@example.com",
        "phone": "(555) 123-4567",
        "recruiter_email": "recruiter@example.com",
        "assessment": "ds",
    }
    first = client.post("/api/admin/exams", headers=headers, json=payload)
    assert first.status_code == 200

    second = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            **payload,
            "name": "Second Candidate",
            "email": "second@example.com",
            "phone": "+1-555-123-4567",
        },
    )
    assert second.status_code == 400
    assert "phone" in second.json()["fields"]


def test_admin_create_allows_reinvite_after_complete(client, admin_key, mock_send_invite_email):
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
    token = created.json()["token"]
    submit = client.post(
        "/api/submit",
        json={
            **VALID_CANDIDATE,
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "phone": "5551234567",
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 200

    again = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Pat Candidate",
            "email": "pat2@example.com",
            "phone": "5551234567",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert again.status_code == 200
    assert again.json()["email_sent"] is True


def test_admin_create_smtp_failure_still_200(client, admin_key, mock_send_invite_email):
    headers = {"X-Admin-Key": admin_key}
    mock_send_invite_email.return_value = (
        False,
        "Email sending failed: smtp down. Invite saved; email not sent.",
    )
    created = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Pat Candidate",
            "email": "pat@example.com",
            "phone": "5559998888",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["email_sent"] is False
    assert body["email_warning"]
    assert body["token"]
    assert body["invite_url"]


def test_admin_list_includes_orphan_submission(client, admin_key, mock_send_email):
    headers = {"X-Admin-Key": admin_key}

    submit = client.post(
        "/api/submit",
        json={
            **VALID_CANDIDATE,
            "name": "Walk In",
            "email": "walkin@example.com",
            "assessment": "ds",
            "answers": PERFECT_ANSWERS,
            "timing": {
                "opened_at": "2026-09-09T17:00:00Z",
                "acknowledged_at": "2026-09-09T17:01:00Z",
                "submitted_at": "2026-09-09T17:30:00Z",
            },
        },
    )
    assert submit.status_code == 200
    score = submit.json()["score_percentage"]
    correct = submit.json()["correct_count"]
    total = submit.json()["total_questions"]

    listed = client.get("/api/admin/exams", headers=headers)
    assert listed.status_code == 200
    exams = listed.json()["exams"]
    orphans = [row for row in exams if row.get("source") == "submission"]
    assert len(orphans) >= 1
    row = next(r for r in orphans if r["email"] == "walkin@example.com")
    assert row["row_id"] == f"submission-{row['id']}"
    assert row["status"] == "completed"
    assert row["status_label"] == "Completed"
    assert row["score_percentage"] == score
    assert row["correct_count"] == correct
    assert row["total_questions"] == total
    assert row.get("invite_url") in (None, "")
    assert "token" not in row or row.get("token") in (None, "")

    detail = client.get(f"/api/admin/exams/submission-{row['id']}", headers=headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["source"] == "submission"
    assert detail_body["row_id"] == f"submission-{row['id']}"
    assert detail_body["results"]["correct_count"] == correct
    assert len(detail_body["results"]["detailed_results"]) == total


def test_admin_linked_submission_not_duplicated(client, admin_key, mock_send_email):
    headers = {"X-Admin-Key": admin_key}

    created = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Linked Candidate",
            "email": "linked@example.com",
            "phone": "5551234567",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    token = created.json()["token"]
    invite_id = created.json()["id"]

    submit = client.post(
        "/api/submit",
        json={
            **VALID_CANDIDATE,
            "name": "Linked Candidate",
            "email": "linked@example.com",
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 200

    listed = client.get("/api/admin/exams", headers=headers)
    exams = listed.json()["exams"]
    invite_rows = [
        r for r in exams if r["source"] == "invite" and r["id"] == invite_id
    ]
    assert len(invite_rows) == 1
    submission_id = invite_rows[0]["submission_id"]
    assert submission_id is not None
    dupes = [
        r
        for r in exams
        if r["source"] == "submission" and r["id"] == submission_id
    ]
    assert dupes == []


def test_submit_with_invite_upserts_edited_contact_fields(
    client, admin_key, mock_send_email, mock_send_invite_email
):
    """Edited name/email/phone on submit update both submission and invite rows."""
    from backend.database import get_session
    from backend.models import Submission
    from backend.models_invites import ExamInvite
    from backend.validation import normalize_phone

    headers = {"X-Admin-Key": admin_key}
    original_recruiter = "recruiter@example.com"
    created = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Original Name",
            "email": "original@example.com",
            "phone": "5551112222",
            "recruiter_email": original_recruiter,
            "assessment": "ds",
        },
    )
    assert created.status_code == 200
    token = created.json()["token"]
    invite_id = created.json()["id"]

    edited = {
        "name": "Edited Name",
        "email": "edited@example.com",
        "phone": "(555) 333-4444",
        "recruiter_email": "other-recruiter@example.com",
    }
    submit = client.post(
        "/api/submit",
        json={
            **edited,
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 200

    detail = client.get(f"/api/admin/exams/invite-{invite_id}", headers=headers)
    assert detail.status_code == 200
    invite_body = detail.json()
    assert invite_body["name"] == "Edited Name"
    assert invite_body["email"] == "edited@example.com"
    assert invite_body["phone"] == "(555) 333-4444"
    assert invite_body["recruiter_email"] == original_recruiter
    assert invite_body["status"] == "completed"
    submission_id = invite_body["submission_id"]
    assert submission_id is not None

    session = get_session()
    try:
        submission = session.get(Submission, submission_id)
        assert submission.name == "Edited Name"
        assert submission.email == "edited@example.com"
        assert submission.phone == "(555) 333-4444"
        assert submission.recruiter_email == "other-recruiter@example.com"

        invite_row = session.get(ExamInvite, invite_id)
        assert invite_row.name == "Edited Name"
        assert invite_row.email == "edited@example.com"
        assert invite_row.phone == "(555) 333-4444"
        assert invite_row.phone_normalized == normalize_phone("(555) 333-4444")
        assert invite_row.recruiter_email == original_recruiter
    finally:
        session.close()


def test_submit_with_invite_rejects_phone_on_other_incomplete(
    client, admin_key, mock_send_email, mock_send_invite_email
):
    """Edited phone colliding with another incomplete invite → 400 fields.phone."""
    headers = {"X-Admin-Key": admin_key}

    first = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "First Candidate",
            "email": "first@example.com",
            "phone": "5551000001",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert first.status_code == 200
    token = first.json()["token"]

    second = client.post(
        "/api/admin/exams",
        headers=headers,
        json={
            "name": "Second Candidate",
            "email": "second@example.com",
            "phone": "5551000002",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
        },
    )
    assert second.status_code == 200

    submit = client.post(
        "/api/submit",
        json={
            "name": "First Candidate",
            "email": "first@example.com",
            "phone": "5551000002",
            "recruiter_email": "recruiter@example.com",
            "assessment": "ds",
            "invite_token": token,
            "answers": PERFECT_ANSWERS,
        },
    )
    assert submit.status_code == 400
    assert "phone" in submit.json()["fields"]

    # Original invite must still be incomplete
    detail = client.get(f"/api/admin/exams/invite-{first.json()['id']}", headers=headers)
    assert detail.json()["status"] != "completed"
    assert detail.json()["submission_id"] is None


def test_admin_unauthorized(client, admin_key):
    response = client.get("/api/admin/exams", headers={"X-Admin-Key": "wrong"})
    assert response.status_code == 401
