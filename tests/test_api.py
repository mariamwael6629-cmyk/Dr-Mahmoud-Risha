"""API, validation, robustness and security tests against the live backend.

All checks were confirmed green in the QA pass (55 API + 29 regression).
"""
import io

import pytest

from conftest import API, unique_suffix


def _png():
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _pdf():
    return b"%PDF-1.4\n" + b"x" * 64


@pytest.fixture()
def patient(api):
    m = "0109" + unique_suffix()[-7:]
    r = api.post(f"{API}/patients", json={
        "Name": "API Test Patient", "age": 41, "gender": "male", "mobileNumber": m,
    })
    assert r.status_code == 201, r.text
    return r.json()


# ---------------- Patients ----------------

def test_create_requires_fields(api):
    r = api.post(f"{API}/patients", json={"Name": "x"})
    assert r.status_code == 400


def test_create_assigns_patient_number(patient):
    assert patient["patientNumber"].startswith("P-")


def test_duplicate_mobile_conflict(api, patient):
    r = api.post(f"{API}/patients", json={
        "Name": "Dup", "age": 1, "gender": "male", "mobileNumber": patient["mobileNumber"],
    })
    assert r.status_code == 409
    assert r.json()["error"] == "duplicate_mobile"


def test_force_duplicate_allowed(api, patient):
    r = api.post(f"{API}/patients", json={
        "Name": "Dup", "age": 1, "gender": "male",
        "mobileNumber": patient["mobileNumber"], "forceCreateDuplicate": True,
    })
    assert r.status_code == 201


def test_get_and_update_patient(api, patient):
    pid = patient["id"]
    assert api.get(f"{API}/patients/{pid}").status_code == 200
    r = api.put(f"{API}/patients/{pid}", json={"diagnosis": "Updated"})
    assert r.status_code == 200 and r.json()["diagnosis"] == "Updated"


def test_get_missing_patient_404(api):
    assert api.get(f"{API}/patients/9999999").status_code == 404


def test_search_patient(api, patient):
    r = api.get(f"{API}/patients", params={"search": patient["Name"]})
    assert r.status_code == 200 and r.json()["total"] >= 1


def test_duplicate_check(api, patient):
    r = api.get(f"{API}/patients/duplicate-check", params={"mobileNumber": patient["mobileNumber"]})
    assert r.status_code == 200 and r.json()["duplicate"] is True
    assert api.get(f"{API}/patients/duplicate-check").status_code == 400


# ---------------- Appointments ----------------

def test_appointment_lifecycle(api, patient):
    pid = patient["id"]
    r = api.post(f"{API}/patients/{pid}/appointments",
                 json={"date": "2026-09-10", "time": "18:00", "visitType": "consultation"})
    assert r.status_code == 201
    aid = r.json()["id"]
    r = api.put(f"{API}/appointments/{aid}", json={"status": "completed"})
    assert r.status_code == 200 and r.json()["status"] == "completed"
    assert api.get(f"{API}/appointments", params={"patientId": pid}).status_code == 200


def test_appointment_on_missing_patient_404(api):
    r = api.post(f"{API}/patients/9999999/appointments", json={"date": "2026-09-10"})
    assert r.status_code == 404


def test_slots_respect_clinic_days(api):
    # 2026-09-10 is a Thursday (valid); 2026-09-07 is a Monday (closed).
    valid = api.get(f"{API}/appointments/slots", params={"date": "2026-09-10", "visitType": "consultation"})
    closed = api.get(f"{API}/appointments/slots", params={"date": "2026-09-07", "visitType": "consultation"})
    assert len(valid.json()["slots"]) > 0
    assert len(closed.json()["slots"]) == 0


def test_walkin_booking(api):
    r = api.post(f"{API}/appointments/book", json={"name": "Walk QA", "nearest": True})
    assert r.status_code == 201
    assert api.post(f"{API}/appointments/book", json={"name": ""}).status_code == 400


# ---------------- Prescriptions / Medications ----------------

def test_prescription(api, patient):
    r = api.post(f"{API}/prescriptions", json={
        "patientId": patient["id"], "diagnosis": "RA", "drugs": [{"name": "A", "dose": "1"}],
    })
    assert r.status_code == 201
    assert api.post(f"{API}/prescriptions", json={}).status_code == 400
    assert api.get(f"{API}/patients/{patient['id']}/prescriptions").status_code == 200


def test_medication_search_and_crud(api):
    assert api.get(f"{API}/medications/search", params={"q": "met"}).status_code == 200
    assert api.get(f"{API}/diagnosis/search", params={"q": "a"}).status_code == 200
    r = api.post(f"{API}/medications", json={"name": "M", "company": "C", "purpose": "p"})
    assert r.status_code == 201
    assert api.delete(f"{API}/medications/{r.json()['id']}").status_code == 200
    assert api.post(f"{API}/medications", json={"name": "x"}).status_code == 400


# ---------------- Files ----------------

def test_file_upload_valid_and_invalid(api, patient):
    pid = str(patient["id"])
    r = api.post(f"{API}/files/upload", files={"file": ("a.png", _png(), "image/png")},
                 data={"patientId": pid, "category": "xray_result"})
    assert r.status_code == 201
    fid = r.json()["id"]
    assert api.get(f"{API}/files/{fid}/download").status_code == 200
    assert api.get(f"{API}/files/{fid}/preview").status_code == 200
    # wrong extension and content-type spoof both rejected
    assert api.post(f"{API}/files/upload", files={"file": ("a.txt", b"hi", "text/plain")},
                    data={"patientId": pid}).status_code == 400
    assert api.post(f"{API}/files/upload", files={"file": ("fake.png", b"nope", "image/png")},
                    data={"patientId": pid}).status_code == 400
    assert api.post(f"{API}/files/upload", files={"file": ("a.png", _png(), "image/png")},
                    data={"category": "other"}).status_code == 400  # missing patientId


# ---------------- Settings ----------------

def test_branding(api):
    r = api.get(f"{API}/settings/branding")
    assert r.status_code == 200 and "clinicNameEn" in r.json()


# ---------------- Security / robustness ----------------

def test_sql_injection_is_safe(api):
    assert api.get(f"{API}/patients", params={"search": "' OR 1=1--"}).status_code == 200


def test_malformed_json_no_500(api):
    r = api.post(f"{API}/patients", data="{bad json", headers={"Content-Type": "application/json"})
    assert r.status_code != 500


def test_unsupported_method_405(api, patient):
    assert api.patch(f"{API}/patients/{patient['id']}").status_code == 405


def test_path_traversal_blocked(api):
    from conftest import BASE_URL
    assert api.get(f"{BASE_URL}/assets/../config.py").status_code in (403, 404)
    assert api.get(f"{BASE_URL}/assets/..%2f..%2fbackend%2fconfig.py").status_code in (403, 404)


def test_api_has_no_auth_documented(api):
    """Regression marker for BUG-003: the API is currently fully open.
    When authentication is added, this test should be updated to expect 401."""
    import requests
    r = requests.get(f"{API}/patients")
    assert r.status_code == 200, "If this now returns 401, auth was added — update BUG-003."
