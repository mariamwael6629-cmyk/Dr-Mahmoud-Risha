import csv
import io
import json
from datetime import datetime, date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from database import db
from models.appointment import Appointment
from models.patient import Patient
from services import patient_service

BUSINESS_START_HOUR = 16
BUSINESS_END_HOUR = 21
MAX_DAYS_AHEAD = 120

VALID_BOOKING_WEEKDAYS = {6, 1, 3}

VISIT_TYPE_DURATIONS = {
    "consultation": 15,
    "followUp": 10,
    "procedure": 30,
    "other": 15,
}
DEFAULT_VISIT_DURATION = 15

class AppointmentConflictError(Exception):
    """Raised when a booking would overlap an existing (non-cancelled)
    appointment at the same date/time — double-booking prevention."""
    def __init__(self, existing=None):
        self.existing = existing
        super().__init__("That time slot is already booked.")


class StaleVersionError(Exception):
    """Optimistic-locking conflict on appointment update."""
    def __init__(self, current_version):
        self.current_version = current_version
        super().__init__("This appointment was changed by someone else")


def visit_duration_minutes(visit_type):
    return VISIT_TYPE_DURATIONS.get(visit_type, DEFAULT_VISIT_DURATION)


def has_conflict(date_str, time_str, visit_type, exclude_id=None):
    """True if [start, start+duration) overlaps an existing non-cancelled
    appointment on the same day."""
    if not date_str or not time_str:
        return False
    try:
        day = date.fromisoformat(date_str)
        start = datetime.combine(day, datetime.strptime(time_str, "%H:%M").time())
    except (ValueError, TypeError):
        return False
    end = start + timedelta(minutes=visit_duration_minutes(visit_type))
    for a in list_appointments(date=date_str):
        if a.id == exclude_id or a.status == "cancelled" or not a.time:
            continue
        try:
            a_start = datetime.combine(day, datetime.strptime(a.time, "%H:%M").time())
        except ValueError:
            continue
        a_end = a_start + timedelta(minutes=visit_duration_minutes(a.visit_type))
        if start < a_end and end > a_start:
            return True
    return False

def is_valid_booking_day(day):
    return day.weekday() in VALID_BOOKING_WEEKDAYS

def add_appointment(patient, data):
    if has_conflict(data.get("date"), data.get("time"), data.get("visitType")):
        raise AppointmentConflictError()
    appt = Appointment(
        patient_id=patient.id,
        date=data.get("date"),
        time=data.get("time"),
        diagnosis=data.get("diagnosis"),
        drugs=data.get("drugs"),
        required_tests=data.get("requiredTests"),
        tests_result=data.get("testsResult"),
        medical_xray_required=data.get("medicalXRayRequired"),
        medical_xray_result=data.get("medicalXRayResult"),
        status=data.get("status") or "waiting",
        visit_type=data.get("visitType"),
        visit_notes=data.get("visitNotes"),
    )
    db.session.add(appt)
    db.session.commit()
    return appt

def get_appointment(appointment_id):
    return Appointment.query.get(appointment_id)

def update_appointment(appointment, data):
    expected = data.get("version")
    if expected is not None and int(expected) != (appointment.version or 1):
        raise StaleVersionError(appointment.version or 1)
    # Re-check for double-booking when the date/time is being changed.
    if ("date" in data or "time" in data) and data.get("status") != "cancelled":
        new_date = data.get("date", appointment.date)
        new_time = data.get("time", appointment.time)
        new_vt = data.get("visitType", appointment.visit_type)
        if has_conflict(new_date, new_time, new_vt, exclude_id=appointment.id):
            raise AppointmentConflictError()
    field_map = [
        ("date", "date"), ("time", "time"), ("diagnosis", "diagnosis"), ("drugs", "drugs"),
        ("requiredTests", "required_tests"), ("testsResult", "tests_result"),
        ("medicalXRayRequired", "medical_xray_required"), ("medicalXRayResult", "medical_xray_result"),
        ("status", "status"), ("visitType", "visit_type"), ("visitNotes", "visit_notes"),
    ]
    for json_key, attr in field_map:
        if json_key in data:
            setattr(appointment, attr, data[json_key])
    appointment.version = (appointment.version or 1) + 1
    db.session.commit()
    return appointment

def delete_appointment(appointment):
    db.session.delete(appointment)
    db.session.commit()

def list_appointments(date=None, patient_id=None, status=None):
    query = Appointment.query.options(selectinload(Appointment.patient), selectinload(Appointment.files))
    if date:
        query = query.filter(Appointment.date == date)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if status:
        query = query.filter(Appointment.status == status)
    return query.order_by(Appointment.date.desc(), Appointment.time.asc(), Appointment.id.asc()).all()

def _booked_intervals(day):
    day_str = day.isoformat()
    intervals = []
    for a in list_appointments(date=day_str):
        if not a.time or a.status == "cancelled":
            continue
        try:
            start = datetime.combine(day, datetime.strptime(a.time, "%H:%M").time())
        except ValueError:
            continue
        intervals.append((start, start + timedelta(minutes=visit_duration_minutes(a.visit_type))))
    intervals.sort(key=lambda iv: iv[0])
    return intervals

def _round_up_to_5_minutes(dt):
    remainder = dt.minute % 5
    if remainder == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt.replace(second=0, microsecond=0)
    add = 5 - remainder
    return (dt + timedelta(minutes=add)).replace(second=0, microsecond=0)

def available_slots(date_str, visit_type=None):
    try:
        day = date.fromisoformat(date_str)
    except (TypeError, ValueError):
        return []
    if not is_valid_booking_day(day):
        return []
    duration = visit_duration_minutes(visit_type)
    business_start = datetime(day.year, day.month, day.day, BUSINESS_START_HOUR, 0)
    business_end = datetime(day.year, day.month, day.day, BUSINESS_END_HOUR, 0)
    now = datetime.now()
    candidate = business_start
    if day == now.date():
        candidate = max(candidate, _round_up_to_5_minutes(now))
    intervals = _booked_intervals(day)
    slots = []
    while candidate + timedelta(minutes=duration) <= business_end:
        conflict = next(
            (iv for iv in intervals if candidate < iv[1] and candidate + timedelta(minutes=duration) > iv[0]),
            None,
        )
        if conflict:
            candidate = conflict[1]
            continue
        slots.append(candidate.strftime("%H:%M"))
        candidate += timedelta(minutes=duration)
    return slots

def next_available_slot(visit_type=None):
    today = datetime.now().date()
    for day_offset in range(MAX_DAYS_AHEAD):
        day = today + timedelta(days=day_offset)
        if not is_valid_booking_day(day):
            continue
        slots = available_slots(day.isoformat(), visit_type)
        if slots:
            return day.isoformat(), slots[0]
    return None, None

def valid_booking_days(count=8):
    today = datetime.now().date()
    days = []
    offset = 0
    while len(days) < count and offset < MAX_DAYS_AHEAD:
        day = today + timedelta(days=offset)
        if is_valid_booking_day(day):
            days.append(day.isoformat())
        offset += 1
    return days

def resolve_slot(date_str, time_str, visit_type):
    if date_str and time_str:
        return date_str, time_str
    if date_str and not time_str:
        slots = available_slots(date_str, visit_type)
        if slots:
            return date_str, slots[0]
    return next_available_slot(visit_type)

def _find_or_create_patient(name, mobile_number):
    if mobile_number:
        existing = patient_service.find_duplicate_by_mobile(mobile_number)
        if existing:
            return existing
    last_error = None
    for _ in range(patient_service._PATIENT_NUMBER_RETRIES):
        patient = Patient(
            patient_number=patient_service.next_patient_number(),
            name=name,
            mobile_number=mobile_number or None,
        )
        db.session.add(patient)
        try:
            db.session.flush()
            return patient
        except IntegrityError as exc:
            # Two concurrent walk-ins raced for the same P-XXXX number.
            # Roll back and retry with a freshly computed one.
            db.session.rollback()
            last_error = exc
    raise last_error

def book_walkin(data):
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("A patient name is required.")
    mobile_number = (data.get("mobileNumber") or "").strip()
    visit_type = data.get("visitType") or "consultation"
    nearest = bool(data.get("nearest"))
    date_str = None if nearest else (data.get("date") or None)
    time_str = None if nearest else (data.get("time") or None)

    explicit_time = bool(time_str)  # the caller picked a specific slot
    # Create/find the patient once and persist, so slot retries below never
    # duplicate the patient record.
    patient = _find_or_create_patient(name, mobile_number)
    db.session.commit()

    # For auto-picked ("nearest") slots, if a concurrent booking just took the
    # slot we resolved, transparently move to the next free one. For an
    # explicitly requested time, a clash is reported so the caller can choose.
    for _ in range(8):
        booking_date, booking_time = resolve_slot(date_str, time_str, visit_type)
        if not booking_date or not booking_time:
            raise ValueError("No available slot could be found.")
        if has_conflict(booking_date, booking_time, visit_type):
            if explicit_time:
                raise AppointmentConflictError()
            db.session.expire_all()
            continue
        appt = Appointment(
            patient_id=patient.id,
            date=booking_date,
            time=booking_time,
            visit_type=visit_type,
            status="waiting",
        )
        db.session.add(appt)
        db.session.commit()
        return patient, appt
    raise AppointmentConflictError()

def _rows_from_file(file_storage):
    raw = file_storage.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig", errors="replace")
    text = raw.strip()
    if not text:
        return []
    if text[0] in "[{":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("appointments") or data.get("items") or []
        return [r for r in data if isinstance(r, dict)]
    reader = csv.DictReader(io.StringIO(text))
    return [dict(r) for r in reader]

def _row_value(row, *keys):
    for k in keys:
        for candidate in (k, k.lower(), k.upper(), k.capitalize()):
            if candidate in row and str(row[candidate]).strip():
                return str(row[candidate]).strip()
    return ""

def import_appointments_file(file_storage):
    rows = _rows_from_file(file_storage)
    imported = 0
    for row in rows:
        name = _row_value(row, "name", "patientName")
        if not name:
            continue
        mobile = _row_value(row, "mobile", "mobileNumber", "phone")
        visit_type = _row_value(row, "visitType", "type") or "consultation"
        if visit_type not in VISIT_TYPE_DURATIONS:
            visit_type = "consultation"
        date_str = _row_value(row, "date") or None
        time_str = _row_value(row, "time") or None
        booking_date, booking_time = resolve_slot(date_str, time_str, visit_type)
        if not booking_date or not booking_time:
            continue
        patient = _find_or_create_patient(name, mobile)
        db.session.add(Appointment(
            patient_id=patient.id,
            date=booking_date,
            time=booking_time,
            visit_type=visit_type,
            status="waiting",
        ))
        imported += 1
    db.session.commit()
    return imported
