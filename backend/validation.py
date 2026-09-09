"""Candidate field validation — copied from root app.py."""
import re


def is_valid_name(name):
    # Check if name contains only letters, spaces, and common special characters
    return bool(re.match(r'^[A-Za-z\s\'-]+$', name)) if name else False

def is_valid_email(email):
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email)) if email else False

def is_valid_phone(phone):
    # Allow common phone number formats (including international)
    phone = re.sub(r'[\s\-\(\)]', '', phone)  # Remove spaces, hyphens, and parentheses
    return bool(re.match(r'^\+?1?\d{10,14}$', phone)) if phone else False


def normalize_phone(phone):
    """Canonical phone for uniqueness: digits only, optional leading country 1 stripped.

    Strips spaces, hyphens, and parentheses (same as validation), then removes a
    leading ``+`` / country ``1`` when the remaining length is at least 10 digits.
    """
    if not phone:
        return ""
    cleaned = re.sub(r"[\s\-\(\)]", "", str(phone).strip())
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    digits = re.sub(r"\D", "", cleaned)
    if digits.startswith("1") and len(digits) >= 11:
        digits = digits[1:]
    return digits
