"""Server-side authentication and role-based permissions for the clinic API.

Two roles:
  * doctor — full access.
  * nurse  — reception only: today's queue, bookings, basic patient info
    (name / number / age / gender / mobile) and medical reps. The nurse can
    NEVER see medical data (diagnosis, symptoms, drugs, tests, history,
    prescriptions), the financial pages, or the settings/backup — enforced
    here on the server, so restricted data never leaves the doctor's PC.
"""

from flask import request, session, jsonify
from werkzeug.security import check_password_hash

from config import (
    AUTH_USERNAME, AUTH_PASSWORD_HASH,
    NURSE_USERNAME, NURSE_PASSWORD_HASH,
)

# API paths reachable without an authenticated session.
_PUBLIC_API_PATHS = {
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
}

# API path prefixes the nurse role may NOT touch at all.
_DOCTOR_ONLY_PREFIXES = (
    "/api/financial",
    "/api/prescriptions",
    "/api/settings",
    "/api/reports",
)

# Patient fields hidden from the nurse.
NURSE_HIDDEN_PATIENT_KEYS = {
    "diagnosis", "symptoms", "previousOperations", "previousTreatment",
    "familyHistory", "notes", "medicalHistoryExtra",
}
# Appointment/consultation fields hidden from the nurse.
NURSE_HIDDEN_APPT_KEYS = {
    "diagnosis", "drugs", "requiredTests", "testsResult",
    "medicalXRayRequired", "medicalXRayResult", "visitNotes", "files",
}


def resolve_role(username, password):
    username = username or ""
    password = password or ""
    if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD_HASH, password):
        return "doctor"
    if username == NURSE_USERNAME and check_password_hash(NURSE_PASSWORD_HASH, password):
        return "nurse"
    return None


def is_authenticated():
    return bool(session.get("authenticated"))


def current_role():
    return session.get("role") or ("doctor" if is_authenticated() else None)


def _is_doctor_only(path):
    # Prescriptions live under /api/patients/<id>/prescriptions too, so match
    # the segment anywhere in the path.
    if "/prescriptions" in path:
        return True
    return any(path == p or path.startswith(p) for p in _DOCTOR_ONLY_PREFIXES)


def sanitize_patient(d, role=None):
    """Strip medical fields from a patient dict for the nurse role."""
    role = role or current_role()
    if role != "nurse" or not isinstance(d, dict):
        return d
    for k in NURSE_HIDDEN_PATIENT_KEYS:
        d.pop(k, None)
    for appt in (d.get("appointments") or []):
        for k in NURSE_HIDDEN_APPT_KEYS:
            appt.pop(k, None)
    return d


def sanitize_appointment(d, role=None):
    role = role or current_role()
    if role != "nurse" or not isinstance(d, dict):
        return d
    for k in NURSE_HIDDEN_APPT_KEYS:
        d.pop(k, None)
    return d


def init_auth(app):
    @app.before_request
    def _guard():
        path = request.path or ""
        if not path.startswith("/api/"):
            return None
        if path in _PUBLIC_API_PATHS:
            return None
        if request.method == "OPTIONS":  # CORS preflight
            return None
        if not is_authenticated():
            return jsonify({"error": "authentication_required"}), 401
        # Role restriction: the nurse cannot reach doctor-only areas.
        if current_role() != "doctor" and _is_doctor_only(path):
            return jsonify({"error": "forbidden"}), 403
        return None
