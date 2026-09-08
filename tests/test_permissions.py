"""Auth, role-based authorization, double-booking and optimistic-locking tests.

Covers the features added after the first QA pass:
  - real authentication (session login/logout)
  - Doctor vs Nurse permissions enforced SERVER-SIDE
  - Nurse has no access to any medical information
  - double-booking prevention
  - optimistic locking (concurrent-edit protection)
"""
import pytest

from conftest import (API, DOCTOR_USERNAME, DOCTOR_PASSWORD,
                      NURSE_USERNAME, NURSE_PASSWORD, unique_suffix)

MEDICAL_PATIENT_FIELDS = ["diagnosis", "symptoms", "previousOperations",
                          "previousTreatment", "familyHistory", "medicalHistoryExtra"]


# ---------------- Authentication ----------------

def test_login_logout_flow(anon_api):
    assert anon_api.get(f"{API}/auth/me").status_code == 401
    r = anon_api.post(f"{API}/auth/login", json={"username": DOCTOR_USERNAME, "password": DOCTOR_PASSWORD})
    assert r.status_code == 200 and r.json()["role"] == "doctor"
    assert anon_api.get(f"{API}/auth/me").status_code == 200
    assert anon_api.post(f"{API}/auth/logout").status_code == 200
    assert anon_api.get(f"{API}/auth/me").status_code == 401


def test_bad_credentials_rejected(anon_api):
    assert anon_api.post(f"{API}/auth/login", json={"username": DOCTOR_USERNAME, "password": "nope"}).status_code == 401
    assert anon_api.post(f"{API}/auth/login", json={"username": "ghost", "password": "x"}).status_code == 401


def test_nurse_account_exists(nurse_api):
    assert nurse_api.get(f"{API}/auth/me").json()["role"] == "nurse"


# ---------------- Doctor: full access ----------------

@pytest.fixture()
def doctor_patient(api):
    m = "0155" + unique_suffix()[-7:]
    r = api.post(f"{API}/patients", json={
        "Name": "Perm Test Pt", "age": 60, "gender": "male", "mobileNumber": m,
        "diagnosis": "RA-clinical", "symptoms": "swelling",
    })
    assert r.status_code == 201
    return r.json()


def test_doctor_sees_medical_fields(api, doctor_patient):
    got = api.get(f"{API}/patients/{doctor_patient['id']}").json()
    assert got["diagnosis"] == "RA-clinical"
    assert got["symptoms"] == "swelling"


def test_doctor_can_prescribe(api, doctor_patient):
    r = api.post(f"{API}/prescriptions", json={"patientId": doctor_patient["id"],
                                               "drugs": [{"name": "X", "dose": "1"}]})
    assert r.status_code == 201


# ---------------- Nurse: no medical information ----------------

def test_nurse_sees_demographics_not_medical(nurse_api, doctor_patient):
    got = nurse_api.get(f"{API}/patients/{doctor_patient['id']}")
    assert got.status_code == 200
    body = got.json()
    assert body["Name"] == "Perm Test Pt"          # demographics visible
    for f in MEDICAL_PATIENT_FIELDS:
        assert f not in body, f"Nurse should not receive medical field '{f}'"


def test_nurse_medical_writes_ignored(api, nurse_api, doctor_patient):
    pid = doctor_patient["id"]
    # nurse attempts to change a clinical field + a demographic field
    r = nurse_api.put(f"{API}/patients/{pid}", json={"diagnosis": "nurse-hack", "notes": "desk note"})
    assert r.status_code == 200
    # doctor verifies the clinical field is unchanged but the demographic one applied
    after = api.get(f"{API}/patients/{pid}").json()
    assert after["diagnosis"] == "RA-clinical"      # medical write blocked
    assert after["notes"] == "desk note"            # non-medical write applied


@pytest.mark.parametrize("method,path", [
    ("post", "/prescriptions"),
    ("get", "/medications/search?q=a"),
    ("get", "/diagnosis/search?q=a"),
    ("get", "/lab-tests/search?q=a"),
    ("get", "/radiology/search?q=a"),
    ("put", "/settings/branding"),
    ("get", "/settings/backup"),
])
def test_nurse_forbidden_endpoints(nurse_api, method, path):
    r = getattr(nurse_api, method)(f"{API}{path}", **({"json": {}} if method in ("post", "put") else {}))
    assert r.status_code == 403, f"{method} {path} should be 403 for nurse, got {r.status_code}"


def test_nurse_cannot_delete_patient(nurse_api, doctor_patient):
    assert nurse_api.delete(f"{API}/patients/{doctor_patient['id']}").status_code == 403


def test_nurse_cannot_read_prescriptions(nurse_api, doctor_patient):
    assert nurse_api.get(f"{API}/patients/{doctor_patient['id']}/prescriptions").status_code == 403


def test_nurse_allowed_endpoints(nurse_api):
    assert nurse_api.get(f"{API}/settings/branding").status_code == 200   # read branding OK
    assert nurse_api.get(f"{API}/financial/invoices").status_code == 200  # billing OK
    assert nurse_api.get(f"{API}/patients").status_code == 200            # demographics OK


def test_nurse_appointment_list_has_no_medical(nurse_api):
    appts = nurse_api.get(f"{API}/appointments?date=2026-09-10").json()
    for a in appts:
        for f in ("diagnosis", "drugs", "requiredTests", "testsResult", "medicalXRayResult", "files"):
            assert f not in a


# ---------------- Double-booking prevention ----------------

def _free_day_and_slots(api, need=3):
    """Find a valid clinic day that currently has >= `need` free slots, so the
    test is independent of appointments left by earlier runs."""
    valid = api.get(f"{API}/appointments/slots").json().get("validDays", [])
    for day in valid:
        slots = api.get(f"{API}/appointments/slots",
                        params={"date": day, "visitType": "consultation"}).json()["slots"]
        if len(slots) >= need:
            return day, slots
    pytest.skip("No day with enough free slots to test booking.")


def _plus_minutes(hhmm, mins):
    h, m = map(int, hhmm.split(":"))
    total = h * 60 + m + mins
    return f"{total // 60:02d}:{total % 60:02d}"


def test_double_booking_prevented(api):
    m = "0166" + unique_suffix()[-7:]
    pid = api.post(f"{API}/patients", json={"Name": "DblBook", "age": 30, "gender": "male", "mobileNumber": m}).json()["id"]
    day, slots = _free_day_and_slots(api)
    t = slots[0]
    r1 = api.post(f"{API}/patients/{pid}/appointments", json={"date": day, "time": t, "visitType": "consultation"})
    assert r1.status_code == 201
    r2 = api.post(f"{API}/patients/{pid}/appointments", json={"date": day, "time": t, "visitType": "consultation"})
    assert r2.status_code == 409 and r2.json()["error"] == "slot_conflict"
    # overlapping slot (5 min into a 15-min consultation) also blocked
    r3 = api.post(f"{API}/patients/{pid}/appointments", json={"date": day, "time": _plus_minutes(t, 5), "visitType": "consultation"})
    assert r3.status_code == 409
    # a different free (non-overlapping) slot is allowed
    r4 = api.post(f"{API}/patients/{pid}/appointments", json={"date": day, "time": slots[-1], "visitType": "consultation"})
    assert r4.status_code == 201


# ---------------- Optimistic locking ----------------

def test_optimistic_locking_patient(api):
    m = "0177" + unique_suffix()[-7:]
    p = api.post(f"{API}/patients", json={"Name": "Lock", "age": 30, "gender": "male", "mobileNumber": m}).json()
    v = p["version"]
    ok = api.put(f"{API}/patients/{p['id']}", json={"notes": "a", "version": v})
    assert ok.status_code == 200 and ok.json()["version"] == v + 1
    stale = api.put(f"{API}/patients/{p['id']}", json={"notes": "b", "version": v})
    assert stale.status_code == 409 and stale.json()["error"] == "version_conflict"
    # omitting version stays backward-compatible
    assert api.put(f"{API}/patients/{p['id']}", json={"notes": "c"}).status_code == 200


def test_optimistic_locking_appointment(api):
    m = "0188" + unique_suffix()[-7:]
    pid = api.post(f"{API}/patients", json={"Name": "LockA", "age": 30, "gender": "male", "mobileNumber": m}).json()["id"]
    day, slots = _free_day_and_slots(api, need=1)
    a = api.post(f"{API}/patients/{pid}/appointments", json={"date": day, "time": slots[0], "visitType": "consultation"}).json()
    v = a["version"]
    assert api.put(f"{API}/appointments/{a['id']}", json={"status": "arrived", "version": v}).status_code == 200
    assert api.put(f"{API}/appointments/{a['id']}", json={"status": "completed", "version": v}).status_code == 409
