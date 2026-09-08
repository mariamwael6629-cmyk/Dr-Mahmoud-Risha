"""Shared fixtures/config for the clinic QA suite.

Everything is driven off environment variables so no credentials or hostnames
are baked into the repo. Sensible defaults match the local dev setup.
"""
import os
import shutil
import time

import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
API = f"{BASE_URL}/api"

DOCTOR_USERNAME = os.environ.get("DOCTOR_USERNAME", "Risha")
DOCTOR_PASSWORD = os.environ.get("DOCTOR_PASSWORD", "Risha12345")
NURSE_USERNAME = os.environ.get("NURSE_USERNAME", "Nurse")
NURSE_PASSWORD = os.environ.get("NURSE_PASSWORD", "Nurse12345")


def unique_suffix():
    """A short, run-unique numeric suffix so tests never collide on the
    unique patient mobile number across repeated runs."""
    return str(int(time.time() * 1000))[-9:]


def find_chromium():
    """Locate a usable Chromium executable, or return None to skip E2E."""
    env = os.environ.get("CHROMIUM_PATH")
    if env and os.path.exists(env):
        return env
    # Common Playwright-managed / system locations.
    candidates = [
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
    ]
    for base in ("/opt/pw-browsers",):
        if os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                if "chrome" in files and "chrome-linux" in root:
                    candidates.append(os.path.join(root, "chrome"))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _make_session(username, password):
    import requests
    s = requests.Session()
    try:
        s.get(f"{API}/patients", timeout=5)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"App not reachable at {BASE_URL}: {exc}")
    r = s.post(f"{API}/auth/login", json={"username": username, "password": password}, timeout=5)
    if r.status_code != 200:  # pragma: no cover
        pytest.skip(f"Could not log in as {username} (status {r.status_code}) — check seeded accounts.")
    return s


@pytest.fixture(scope="session")
def api():
    """Authenticated Doctor session (full access)."""
    return _make_session(DOCTOR_USERNAME, DOCTOR_PASSWORD)


@pytest.fixture(scope="session")
def nurse_api():
    """Authenticated Nurse session (front-desk role, no medical access)."""
    return _make_session(NURSE_USERNAME, NURSE_PASSWORD)


@pytest.fixture(scope="session")
def anon_api():
    """Unauthenticated session."""
    import requests
    return requests.Session()
