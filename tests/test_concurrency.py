"""Concurrency tests — regression coverage for BUG-002 (patient-number race).

Before the fix, two simultaneous patient creations / walk-in bookings could pick
the same auto-generated P-XXXX number and crash with HTTP 500
(UNIQUE constraint failed: patients.patient_number). The service layer now
retries on IntegrityError. These tests fail if that regresses.
"""
import threading

import requests

from conftest import API, unique_suffix


def _parallel(fn, n):
    results = []
    lock = threading.Lock()

    def run(i):
        r = fn(i)
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

    def create(i):
        return requests.post(f"{API}/patients", json={
            "Name": f"Race Pt {base}-{i}", "age": 30, "gender": "male",
            "mobileNumber": f"01{base}{i:02d}",
        }).status_code

    statuses = _parallel(create, 8)
    assert all(s == 201 for s in statuses), f"Expected all 201, got {statuses} (BUG-002 regression)"


def test_concurrent_walkin_booking_no_500(api):
    def book(i):
        return requests.post(f"{API}/appointments/book",
                             json={"name": f"RaceBook {i}", "nearest": True}).status_code

    statuses = _parallel(book, 8)
    assert all(s == 201 for s in statuses), f"Expected all 201, got {statuses} (BUG-002 regression)"


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

    def edit(i):
        return requests.put(f"{API}/patients/{pid}", json={"diagnosis": f"DX-{i}"}).status_code

    statuses = _parallel(edit, 10)
    assert all(s == 200 for s in statuses)
    final = api.get(f"{API}/patients/{pid}").json()["diagnosis"]
    assert final.startswith("DX-")  # one of the writers won, record intact
