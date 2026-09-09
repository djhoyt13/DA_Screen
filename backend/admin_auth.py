"""Simple admin API-key auth via X-Admin-Key header or admin_key query param."""
import os
from typing import Optional

from fastapi.responses import JSONResponse


def get_admin_api_key():
    return (os.getenv("ADMIN_API_KEY") or "").strip()


def admin_unauthorized(message="Admin authentication required"):
    return JSONResponse(status_code=401, content={"error": message})


def admin_misconfigured():
    return JSONResponse(
        status_code=503,
        content={
            "error": "ADMIN_API_KEY is not configured on the server. Set it in .env to enable the admin dashboard."
        },
    )


def require_admin(
    x_admin_key: Optional[str] = None,
    admin_key: Optional[str] = None,
):
    """Return None if authorized, otherwise a JSONResponse error."""
    expected = get_admin_api_key()
    if not expected:
        return admin_misconfigured()
    provided = (x_admin_key or admin_key or "").strip()
    if not provided or provided != expected:
        return admin_unauthorized()
    return None
