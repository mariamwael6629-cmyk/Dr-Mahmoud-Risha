import os
import sys
import secrets
from datetime import timedelta

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)

def _stable_data_dir():
    """A FIXED per-user data location so patient data does not depend on
    where the .exe happens to live. Moving, replacing or re-downloading the
    program keeps the same database — the old "next to the exe" behaviour
    made data appear to vanish when the exe was run from a new folder."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(
            os.path.expanduser("~"), "AppData", "Local")
    else:
        base = os.path.expanduser("~")
    return os.path.join(base, "DrRishaClinic")


def _migrate_legacy_data(new_dir):
    """One-time move of any older database that was stored next to the exe
    (or in the source tree) into the new stable location, so upgrading users
    keep their existing patients."""
    try:
        if os.path.exists(os.path.join(new_dir, "database", "clinic.db")):
            return
        candidates = []
        if getattr(sys, "frozen", False):
            candidates.append(os.path.join(os.path.dirname(sys.executable), "ClinicData"))
        candidates.append(os.path.join(BASE_DIR, "database"))  # never matches new_dir
        for legacy in candidates:
            legacy_db = os.path.join(legacy, "database", "clinic.db")
            if os.path.exists(legacy_db):
                import shutil
                os.makedirs(new_dir, exist_ok=True)
                shutil.copytree(legacy, new_dir, dirs_exist_ok=True)
                return
    except Exception:
        pass


if getattr(sys, "frozen", False):
    STATIC_ROOT = sys._MEIPASS
    DATA_DIR = _stable_data_dir()
    _migrate_legacy_data(DATA_DIR)
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
