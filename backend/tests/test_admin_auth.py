"""Admin email/password auth unit and API tests."""
from backend.admin_auth import (
    expected_password_from_email,
    is_allowed_admin_email,
    require_admin,
)


def test_expected_password_from_email():
    assert expected_password_from_email("david.hoyt@mantech.com") == "hoyt"
    assert expected_password_from_email("Jane.Doe@ElderResearch.com") == "doe"
    assert expected_password_from_email("a.b.c@mantech.com") == "c"
    assert expected_password_from_email("nodot@mantech.com") is None
    assert expected_password_from_email("not-an-email") is None


def test_is_allowed_admin_email():
    assert is_allowed_admin_email("david.hoyt@mantech.com") is True
    assert is_allowed_admin_email("Jane.Doe@ElderResearch.com") is True
    assert is_allowed_admin_email("user@example.com") is False
    assert is_allowed_admin_email("user@mantech.com.evil.com") is False


def test_require_admin_case_insensitive_password():
    assert require_admin(
        x_admin_email="David.Hoyt@Mantech.Com",
        x_admin_password="HOYT",
    ) is None


def test_admin_login_valid_mantech(client):
    response = client.post(
        "/api/admin/login",
        json={"email": "david.hoyt@mantech.com", "password": "hoyt"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True, "email": "david.hoyt@mantech.com"}


def test_admin_login_valid_elderresearch(client):
    response = client.post(
        "/api/admin/login",
        json={"email": "Jane.Doe@ElderResearch.com", "password": "DOE"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True, "email": "jane.doe@elderresearch.com"}


def test_admin_login_wrong_password(client):
    response = client.post(
        "/api/admin/login",
        json={"email": "david.hoyt@mantech.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "error" in response.json()


def test_admin_login_bad_domain(client):
    response = client.post(
        "/api/admin/login",
        json={"email": "david.hoyt@example.com", "password": "hoyt"},
    )
    assert response.status_code == 401


def test_admin_login_missing_dot_in_local_part(client):
    response = client.post(
        "/api/admin/login",
        json={"email": "hoyt@mantech.com", "password": "hoyt"},
    )
    assert response.status_code == 401


def test_admin_exams_headers_valid_mantech(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:5173")
    response = client.get(
        "/api/admin/exams",
        headers={
            "X-Admin-Email": "david.hoyt@mantech.com",
            "X-Admin-Password": "hoyt",
        },
    )
    assert response.status_code == 200
    assert "exams" in response.json()


def test_admin_exams_headers_valid_elderresearch(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:5173")
    response = client.get(
        "/api/admin/exams",
        headers={
            "X-Admin-Email": "jane.doe@elderresearch.com",
            "X-Admin-Password": "doe",
        },
    )
    assert response.status_code == 200


def test_admin_exams_wrong_password(client):
    response = client.get(
        "/api/admin/exams",
        headers={
            "X-Admin-Email": "david.hoyt@mantech.com",
            "X-Admin-Password": "nope",
        },
    )
    assert response.status_code == 401


def test_admin_exams_bad_domain(client):
    response = client.get(
        "/api/admin/exams",
        headers={
            "X-Admin-Email": "david.hoyt@gmail.com",
            "X-Admin-Password": "hoyt",
        },
    )
    assert response.status_code == 401


def test_admin_exams_missing_dot_local_part(client):
    response = client.get(
        "/api/admin/exams",
        headers={
            "X-Admin-Email": "hoyt@mantech.com",
            "X-Admin-Password": "hoyt",
        },
    )
    assert response.status_code == 401
