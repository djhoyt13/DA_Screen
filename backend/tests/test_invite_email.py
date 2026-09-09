"""Unit tests for candidate invite email HTML and send helper."""
from unittest.mock import MagicMock, patch

from backend.emailer import build_invite_email_html, send_invite_email
from backend.validation import normalize_phone


def test_normalize_phone_strips_formatting_and_country_code():
    assert normalize_phone("(555) 123-4567") == "5551234567"
    assert normalize_phone("+1-555-123-4567") == "5551234567"
    assert normalize_phone("15551234567") == "5551234567"
    assert normalize_phone("5551234567") == "5551234567"


def test_build_invite_email_html_includes_cta_and_context():
    html = build_invite_email_html(
        name="Jane Doe",
        email="jane@example.com",
        phone="5551234567",
        recruiter_email="recruiter@example.com",
        invite_url="http://127.0.0.1:5173/data-scientist?invite=abc123",
        assessment_title="Data Scientist Initial Assessment",
    )
    assert "Jane Doe" in html
    assert "Data Scientist Initial Assessment" in html
    assert "recruiter@example.com" in html
    assert "Start Assessment" in html
    assert "http://127.0.0.1:5173/data-scientist?invite=abc123" in html
    assert "do not share" in html.lower() or "Please do not share" in html


def test_send_invite_email_calls_smtp_with_candidate_address(monkeypatch):
    monkeypatch.setenv("SENDER_EMAIL", "sender@example.com")
    monkeypatch.setenv("SENDER_PASSWORD", "secret")

    mock_smtp = MagicMock()
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    with patch("backend.emailer.smtplib.SMTP", mock_smtp):
        sent, warning = send_invite_email(
            name="Jane Doe",
            email="jane@example.com",
            phone="5551234567",
            recruiter_email="recruiter@example.com",
            invite_url="http://127.0.0.1:5173/data-scientist?invite=tok",
            assessment_title="Data Scientist Initial Assessment",
        )

    assert sent is True
    assert warning is None
    mock_server.login.assert_called_once_with("sender@example.com", "secret")
    args = mock_server.sendmail.call_args[0]
    assert args[0] == "sender@example.com"
    assert args[1] == "jane@example.com"
    import base64
    import re

    match = re.search(
        r"Content-Type: text/html.*?Content-Transfer-Encoding: base64\n\n([A-Za-z0-9+/=\n]+)",
        args[2],
        re.S,
    )
    assert match, "expected base64 text/html part in MIME message"
    html = base64.b64decode(match.group(1)).decode()
    assert "invite=tok" in html
    assert "jane@example.com" in html
    assert "Start Assessment" in html


def test_send_invite_email_missing_creds(monkeypatch):
    monkeypatch.delenv("SENDER_EMAIL", raising=False)
    monkeypatch.delenv("SENDER_PASSWORD", raising=False)
    sent, warning = send_invite_email(
        name="Jane",
        email="jane@example.com",
        phone="555",
        recruiter_email="r@example.com",
        invite_url="http://example.com/invite",
    )
    assert sent is False
    assert warning
