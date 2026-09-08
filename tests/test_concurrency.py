"""Concurrency tests — regression coverage for BUG-002 (patient-number race).

Before the fix, two simultaneous patient creations / walk-in bookings could pick
the same auto-generated P-XXXX number and crash with HTTP 500
(UNIQUE constraint failed: patients.patient_number). The service layer now
retries on IntegrityError. These tests fail if that regresses.
"""
import threading

from conftest import (API, DOCTOR_USERNAME, DOCTOR_PASSWORD, unique_suffix,
                      _make_session)


def _parallel(fn, n):
    results = []
    lock = threading.Lock()

    def run(i):
        # Each thread uses its own authenticated session.
        s = _make_session(DOCTOR_USERNAME, DOCTOR_PASSWORD)
        r = fn(s, i)
        with lock:
            results.append(r)

    threads = [threading.Thread(target=run, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_concurrent_patient_creation_no_500(api):
    base = unique_suffix()

    def create(s, i):
        return s.post(f"{API}/patients", json={
            "Name": f"Race Pt {base}-{i}", "age": 30, "gender": "male",
            "mobileNumber": f"01{base}{i:02d}",
        }).status_code

    statuses = _parallel(create, 8)
    assert all(s == 201 for s in statuses), f"Expected all 201, got {statuses} (BUG-002 regression)"


def test_concurrent_walkin_booking_no_500(api):
    def book(s, i):
        return s.post(f"{API}/appointments/book",
                      json={"name": f"RaceBook {i}", "nearest": True}).status_code

    statuses = _parallel(book, 8)
    # BUG-002 guard: no 500s / crashes under concurrency. The double-booking
    # check may legitimately return 409 in the rare case two requests race for
    # the very same auto-slot faster than the retry can re-resolve.
    assert 500 not in statuses, f"Server error under concurrency: {statuses}"
    assert all(s in (201, 409) for s in statuses), statuses
    assert statuses.count(201) >= 1


def test_patient_numbers_are_unique(api):
    items = api.get(f"{API}/patients", params={"perPage": 200}).json()["items"]
    nums = [p["patientNumber"] for p in items]
    assert len(nums) == len(set(nums)), "Duplicate patient numbers exist (BUG-002 regression)"


def test_concurrent_edit_last_write_wins(api):
    """Documents BUG-005: concurrent edits succeed (200) with last-write-wins and
    no corruption. Purely descriptive — asserts the app stays consistent, not
    that a conflict is detected (it currently is not)."""
    base = unique_suffix()
    pid = api.post(f"{API}/patients", json={
        "Name": f"Edit Race {base}", "age": 20, "gender": "male",
        "mobileNumber": f"017{base}",
    }).json()["id"]

    def edit(s, i):
        return s.put(f"{API}/patients/{pid}", json={"diagnosis": f"DX-{i}"}).status_code

    statuses = _parallel(edit, 10)
    assert all(s == 200 for s in statuses)
    final = api.get(f"{API}/patients/{pid}").json()["diagnosis"]
    assert final.startswith("DX-")  # one of the writers won, record intact
