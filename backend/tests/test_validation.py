from backend.validation import is_valid_email, is_valid_name, is_valid_phone


def test_valid_name():
    assert is_valid_name("Jane Doe") is True
    assert is_valid_name("Jane Doe-O'Brien") is True
    assert is_valid_name("Mary-Anne") is True


def test_invalid_name():
    assert is_valid_name("") is False
    assert is_valid_name(None) is False
    assert is_valid_name("Test123") is False
    assert is_valid_name("Jane_Doe") is False


def test_valid_email():
    assert is_valid_email("jane@example.com") is True
    assert is_valid_email("a@b.co") is True


def test_invalid_email():
    assert is_valid_email("") is False
    assert is_valid_email(None) is False
    assert is_valid_email("not-an-email") is False
    assert is_valid_email("missing-at.com") is False


def test_valid_phone():
    assert is_valid_phone("5551234567") is True
    assert is_valid_phone("+1 (555) 123-4567") is True
    assert is_valid_phone("555-123-4567") is True


def test_invalid_phone():
    assert is_valid_phone("abc") is False
    assert is_valid_phone("") is False
    assert is_valid_phone("123") is False
