import json
import re

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from database import db
from models.appointment import Appointment
from models.patient import Patient

_PATIENT_NUMBER_RE = re.compile(r"^P-(\d+)$")

# Number of times to retry auto-generated patient-number allocation when two
# concurrent requests race and pick the same P-XXXX value (SQLite UNIQUE
# violation). Explicit, caller-supplied numbers are never retried.
_PATIENT_NUMBER_RETRIES = 5

class DuplicatePatientError(Exception):
    def __init__(self, existing_patient):
        self.existing_patient = existing_patient
        super().__init__("A patient with this mobile number already exists")


class StaleVersionError(Exception):
    """Raised when an update carries an out-of-date `version` (someone else
    edited the record first) — optimistic-locking conflict."""
    def __init__(self, current_version):
        self.current_version = current_version
        super().__init__("This record was changed by someone else")

                                                                                          
_EAGER_LOAD = selectinload(Patient.appointments).selectinload(Appointment.files)

def list_patients(search=None, page=1, per_page=50):
    query = Patient.query.options(_EAGER_LOAD)
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.name.ilike(like),
                Patient.patient_number.ilike(like),
                Patient.mobile_number.ilike(like),
            )
        )
    query = query.order_by(Patient.id.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total

def get_patient(patient_id):
    return Patient.query.options(_EAGER_LOAD).get(patient_id)

def next_patient_number():
    max_n = 0
    for (pn,) in db.session.query(Patient.patient_number).all():
        m = _PATIENT_NUMBER_RE.match(pn or "")
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"P-{max_n + 1:04d}"

def find_duplicate_by_mobile(mobile_number, exclude_id=None):
    q = Patient.query.filter(Patient.mobile_number == mobile_number)
    if exclude_id:
        q = q.filter(Patient.id != exclude_id)
    return q.first()

def _build_appointment(appt_data):
    return Appointment(
        date=appt_data.get("date"),
        diagnosis=appt_data.get("diagnosis"),
        drugs=appt_data.get("drugs"),
        required_tests=appt_data.get("requiredTests"),
        tests_result=appt_data.get("testsResult"),
        medical_xray_required=appt_data.get("medicalXRayRequired"),
        medical_xray_result=appt_data.get("medicalXRayResult"),
    )

def create_patient(data, allow_duplicate=False):
    mobile_number = data["mobileNumber"]
    if not allow_duplicate:
        dup = find_duplicate_by_mobile(mobile_number)
        if dup:
            raise DuplicatePatientError(dup)

    explicit_number = data.get("patientNumber")
    last_error = None
    for attempt in range(_PATIENT_NUMBER_RETRIES):
        patient = Patient(
            patient_number=explicit_number or next_patient_number(),
            name=data["Name"],
            age=data["age"],
            gender=data["gender"],
            previous_operations=data.get("previousOperations"),
            previous_treatment=data.get("previousTreatment"),
            diagnosis=data.get("diagnosis"),
            symptoms=data.get("symptoms"),
            family_history=data.get("familyHistory"),
            mobile_number=mobile_number,
            emergency_contact=data.get("emergencyContact"),
            notes=data.get("notes"),
            medical_history_extra=json.dumps(data["medicalHistoryExtra"]) if data.get("medicalHistoryExtra") else None,
        )
        for appt in data.get("appointments", []):
            patient.appointments.append(_build_appointment(appt))

        db.session.add(patient)
        try:
            db.session.commit()
            return patient
        except IntegrityError as exc:
            # A concurrent request grabbed the same auto-generated number.
            # Roll back and try again with a freshly computed one. If the
            # caller pinned an explicit number, the collision is a real
            # conflict, so surface it instead of looping.
            db.session.rollback()
            last_error = exc
            if explicit_number:
                raise
    raise last_error

def update_patient(patient, data):
    expected = data.get("version")
    if expected is not None and int(expected) != (patient.version or 1):
        raise StaleVersionError(patient.version or 1)
    field_map = [
        ("Name", "name"), ("age", "age"), ("gender", "gender"),
        ("previousOperations", "previous_operations"), ("previousTreatment", "previous_treatment"),
        ("diagnosis", "diagnosis"), ("symptoms", "symptoms"), ("familyHistory", "family_history"),
        ("mobileNumber", "mobile_number"), ("emergencyContact", "emergency_contact"), ("notes", "notes"),
    ]
    for json_key, attr in field_map:
        if json_key in data:
            setattr(patient, attr, data[json_key])
    if "medicalHistoryExtra" in data:
        patient.medical_history_extra = json.dumps(data["medicalHistoryExtra"]) if data["medicalHistoryExtra"] else None
    patient.version = (patient.version or 1) + 1
    db.session.commit()
    return patient

def delete_patient(patient):
    db.session.delete(patient)
    db.session.commit()
