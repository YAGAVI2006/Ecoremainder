"""
EcoReminder Security & Input Validation Helpers
"""

import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_upload_filename(filename: str, prefix: str = "") -> str:
    cleaned = secure_filename(filename)
    if prefix:
        return f"{prefix}_{cleaned}"
    return cleaned


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
