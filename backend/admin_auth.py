"""Admin auth via email + last-name password (company domains only)."""
from typing import Optional, Tuple

from fastapi.responses import JSONResponse

ALLOWED_ADMIN_DOMAINS = frozenset({"mantech.com", "elderresearch.com"})


def normalize_admin_email(email: Optional[str]) -> str:
    return (email or "").strip().lower()


def expected_password_from_email(email: Optional[str]) -> Optional[str]:
    """Return last-name password from local-part after the last '.', or None."""
    normalized = normalize_admin_email(email)
    if "@" not in normalized:
        return None
    local, _, _domain = normalized.partition("@")
    if "." not in local:
        return None
    return local.rsplit(".", 1)[-1]


def is_allowed_admin_email(email: Optional[str]) -> bool:
    normalized = normalize_admin_email(email)
    if "@" not in normalized:
        return False
    domain = normalized.rsplit("@", 1)[-1]
    return domain in ALLOWED_ADMIN_DOMAINS


def admin_unauthorized(message: str = "Admin authentication required") -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": message})


def credentials_valid(email: Optional[str], password: Optional[str]) -> bool:
    """True when email domain is allowed and password matches last name (case-insensitive)."""
    if not email or not password:
        return False
    if not is_allowed_admin_email(email):
        return False
    expected = expected_password_from_email(email)
    if expected is None:
        return False
    return (password or "").strip().lower() == expected.lower()


def require_admin(
    x_admin_email: Optional[str] = None,
    x_admin_password: Optional[str] = None,
):
    """Return None if authorized, otherwise a 401 JSONResponse."""
    email = (x_admin_email or "").strip()
    password = (x_admin_password or "").strip()
    if not email or not password:
        return admin_unauthorized("Admin email and password are required")
    if not credentials_valid(email, password):
        return admin_unauthorized("Invalid admin credentials")
    return None


def verify_admin_login(
    email: Optional[str], password: Optional[str]
) -> Tuple[bool, Optional[str], Optional[JSONResponse]]:
    """
    Validate login body credentials.

    Returns (ok, normalized_email, error_response).
    On success error_response is None; on failure normalized_email is None.
    """
    email = (email or "").strip()
    password = (password or "").strip()
    if not email or not password:
        return False, None, admin_unauthorized("Admin email and password are required")
    if not credentials_valid(email, password):
        return False, None, admin_unauthorized("Invalid admin credentials")
    return True, normalize_admin_email(email), None
