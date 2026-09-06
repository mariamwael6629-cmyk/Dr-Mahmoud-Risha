import os
import sys
import secrets
from datetime import timedelta

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)

if getattr(sys, "frozen", False):
    STATIC_ROOT = sys._MEIPASS
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "ClinicData")
else:
    STATIC_ROOT = REPO_ROOT
    DATA_DIR = BASE_DIR

DATABASE_DIR = os.path.join(DATA_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "clinic.db")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

ALLOWED_FILE_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024


def _load_or_create_secret_key():
    """A stable secret so login sessions survive server restarts.

    Order of precedence: CLINIC_SECRET_KEY env var, then a persisted file
    next to the data, otherwise a freshly generated one that is saved.
    """
    env_key = os.environ.get("CLINIC_SECRET_KEY")
    if env_key:
        return env_key
    key_path = os.path.join(DATA_DIR, "secret_key.txt")
    try:
        if os.path.exists(key_path):
            with open(key_path, "r", encoding="utf-8") as fh:
                saved = fh.read().strip()
                if saved:
                    return saved
        os.makedirs(DATA_DIR, exist_ok=True)
        new_key = secrets.token_hex(32)
        with open(key_path, "w", encoding="utf-8") as fh:
            fh.write(new_key)
        return new_key
    except Exception:
        # Last resort: an in-memory key (sessions reset on restart).
        return secrets.token_hex(32)


# --- Authentication -------------------------------------------------------
# Credentials can be overridden with env vars; otherwise the clinic's
# original username/password are used, but validated server-side against a
# hash instead of being embedded in the browser.
AUTH_USERNAME = os.environ.get("CLINIC_USERNAME", "Risha")
_AUTH_PASSWORD = os.environ.get("CLINIC_PASSWORD", "Risha12345")
AUTH_PASSWORD_HASH = generate_password_hash(_AUTH_PASSWORD)


class Config:
    SECRET_KEY = _load_or_create_secret_key()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOADS_DIR
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    JSON_AS_ASCII = False
    SWAGGER = {
        "title": "Clinic Management API",
        "uiversion": 3,
        "specs_route": "/apidocs/",
    }
