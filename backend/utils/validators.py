"""
Validation and sanitization utilities for InsureVisionAI.
"""

import re
from typing import Tuple, Set

# Regex patterns
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^[+]?[\d\s\-()]{7,20}$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_ASSISTANCE_TYPES: Set[str] = {
    "Rescue Team",
    "Towing",
    "Medical Assistance"
}

ALLOWED_ASSISTANCE_STATUSES: Set[str] = {
    "Requested",
    "Accepted",
    "In Progress",
    "Completed",
    "Cancelled"
}

VALID_STATUS_TRANSITIONS = {
    "Requested": {"Accepted", "Cancelled"},
    "Accepted": {"In Progress", "Cancelled"},
    "In Progress": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set()
}


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 255:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    """Validate phone format."""
    if not phone:
        return False
    return bool(PHONE_REGEX.match(phone.strip()))


def is_valid_date(date_str: str) -> bool:
    """Validate YYYY-MM-DD date string."""
    if not date_str:
        return False
    return bool(DATE_REGEX.match(date_str.strip()))


def validate_fault_percentages(user_pct: int, other_pct: int) -> Tuple[bool, str]:
    """Validate that responsibility percentages are 0-100 and sum to 100."""
    if not (0 <= user_pct <= 100):
        return False, f"User fault percentage ({user_pct}) must be between 0 and 100."
    if not (0 <= other_pct <= 100):
        return False, f"Other vehicle fault percentage ({other_pct}) must be between 0 and 100."
    if (user_pct + other_pct) != 100:
        return False, f"Total fault percentage must equal 100% (currently {user_pct + other_pct}%)."
    return True, ""


def is_valid_status_transition(current_status: str, new_status: str) -> bool:
    """Validate lifecycle transitions for assistance requests."""
    if new_status not in ALLOWED_ASSISTANCE_STATUSES:
        return False
    allowed = VALID_STATUS_TRANSITIONS.get(current_status, set())
    return new_status in allowed


def sanitize_csv_field(value: str) -> str:
    """
    Sanitize text to prevent CSV formula injection attacks
    when exported files are opened in Excel/Google Sheets.
    """
    if not isinstance(value, str):
        return str(value)
    
    clean_val = value.strip()
    # If starting with dangerous formula characters, escape with a single quote
    if clean_val and clean_val[0] in ("=", "+", "-", "@", "\t", "\r"):
        clean_val = "'" + clean_val
    return clean_val
