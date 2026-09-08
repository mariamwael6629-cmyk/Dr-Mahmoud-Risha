"""Central authentication / authorization rules.

Roles:
  - "doctor": full access to everything.
  - "nurse" : front-desk role. NO access to any medical/clinical information —
    prescriptions, the medication/diagnosis/lab/radiology drug database, uploaded
    medical files, and the clinical fields on patients and appointments are all
    off-limits (enforced server-side, not merely hidden in the UI). The nurse can
    still manage patient demographics, appointments/queue, billing and scheduling.

Enforcement lives here so the frontend can never be trusted to hide things:
`before_request` (see app.py) calls `forbidden_for_role()` for every /api call,
and the patient/appointment controllers use the field helpers to strip clinical
data out of responses and ignore it on writes for nurses.
"""
import re

DOCTOR = "doctor"
NURSE = "nurse"

# Clinical fields nurses must never read or write.
MEDICAL_PATIENT_FIELDS = {
    "previousOperations", "previousTreatment", "diagnosis",
    "symptoms", "familyHistory", "medicalHistoryExtra",
}
MEDICAL_APPOINTMENT_FIELDS = {
    "diagnosis", "drugs", "requiredTests", "testsResult",
    "medicalXRayRequired", "medicalXRayResult", "files",
}

# Endpoints that require an authenticated session but are open to any role.
# Everything else under /api requires login; medical routes additionally require
# the doctor role (see forbidden_for_role).
_PUBLIC_PREFIXES = ("/api/auth/login",)

# Substrings that mark a request path as medical/clinical → nurse forbidden.
_MEDICAL_PATH_MARKERS = (
    "/api/prescriptions", "/prescriptions",
    "/api/medications", "/api/diagnosis",
    "/api/lab-tests", "/api/radiology",
    "/files",
)

_PATIENT_ID_PATH = re.compile(r"^/api/patients/\d+$")


def is_public(path):
    return any(path.startswith(p) for p in _PUBLIC_PREFIXES)


def forbidden_for_role(role, method, path):
    """Return True if a user with `role` may NOT perform `method` on `path`."""
    if role == DOCTOR:
        return False
    # ---- nurse restrictions ----
    if any(marker in path for marker in _MEDICAL_PATH_MARKERS):
        return True
    # nurses cannot delete patient records
    if method == "DELETE" and _PATIENT_ID_PATH.match(path):
        return True
    # settings: nurse may only READ branding (needed for the app shell); all
    # other settings operations (branding write, import, full DB backup) are
    # doctor-only.
    if path.startswith("/api/settings"):
        if path == "/api/settings/branding" and method == "GET":
            return False
        return True
    return False


def strip_patient_medical(data):
    """Remove clinical fields from a patient dict (in place) and return it.
    Nested appointments are sanitised too."""
    for f in MEDICAL_PATIENT_FIELDS:
        data.pop(f, None)
    if isinstance(data.get("appointments"), list):
        for appt in data["appointments"]:
            strip_appointment_medical(appt)
    return data


def strip_appointment_medical(data):
    for f in MEDICAL_APPOINTMENT_FIELDS:
        data.pop(f, None)
    return data


def sanitize_patient_input(data):
    """Drop clinical keys a nurse is not allowed to set."""
    for f in MEDICAL_PATIENT_FIELDS:
        data.pop(f, None)
    if isinstance(data.get("appointments"), list):
        for appt in data["appointments"]:
            sanitize_appointment_input(appt)
    return data


def sanitize_appointment_input(data):
    for f in MEDICAL_APPOINTMENT_FIELDS:
        data.pop(f, None)
    return data
