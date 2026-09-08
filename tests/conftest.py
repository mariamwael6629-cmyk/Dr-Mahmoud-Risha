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


@pytest.fixture(scope="session")
def api():
    import requests
    s = requests.Session()
    # Fail fast with a clear message if the app is not running.
    try:
        s.get(f"{API}/patients", timeout=5)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"App not reachable at {BASE_URL}: {exc}")
    return s
