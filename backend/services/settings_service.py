import json
from datetime import datetime

from database import db
from models.settings import ClinicSettings
from models.patient import Patient
from models.appointment import Appointment
from models.medication import MedicationRecord, MedicationLibrary
from models.diagnosis import DiagnosisLibrary
from models.prescription import Prescription
from models.availability import DoctorAvailability
from models.financial import Invoice
from services import patient_service

def get_branding():
    return ClinicSettings.query.first()

def update_branding(data):
    settings = get_branding()
    if not settings:
        return None
    field_map = [
        ("doctorNameEn", "doctor_name_en"), ("doctorNameAr", "doctor_name_ar"),
        ("clinicNameEn", "clinic_name_en"), ("clinicNameAr", "clinic_name_ar"),
        ("specialtyEn", "specialty_en"), ("specialtyAr", "specialty_ar"),
        ("credentialsEn", "credentials_en"), ("credentialsAr", "credentials_ar"),
        ("address1", "address_1"), ("address2", "address_2"),
        ("phone1", "phone_1"), ("phone2", "phone_2"),
        ("footerNoteAr", "footer_note_ar"),
    ]
    for json_key, attr in field_map:
        if json_key in data:
            setattr(settings, attr, data[json_key])
    db.session.commit()
    return settings

def export_backup():
    settings = get_branding()
    return {
        "exportedAt": datetime.utcnow().isoformat(),
        "branding": settings.to_dict() if settings else None,
        "patients": [p.to_dict() for p in Patient.query.all()],
        "appointments": [a.to_dict(include_patient=True) for a in Appointment.query.all()],
        "medicationRecords": [m.to_dict() for m in MedicationRecord.query.all()],
        "medicationLibrary": [m.to_dict() for m in MedicationLibrary.query.all()],
        "diagnosisLibrary": [d.to_dict() for d in DiagnosisLibrary.query.all()],
        "prescriptions": [p.to_dict() for p in Prescription.query.all()],
        "doctorAvailability": [a.to_dict() for a in DoctorAvailability.query.all()],
        "invoices": [i.to_dict() for i in Invoice.query.all()],
    }

def _build_appointment(a):
    return Appointment(
        date=a.get("date"),
        time=a.get("time"),
        diagnosis=a.get("diagnosis"),
        drugs=a.get("drugs"),
        required_tests=a.get("requiredTests"),
        tests_result=a.get("testsResult"),
        medical_xray_required=a.get("medicalXRayRequired"),
        medical_xray_result=a.get("medicalXRayResult"),
        status=a.get("status") or "completed",
        visit_type=a.get("visitType"),
        visit_notes=a.get("visitNotes"),
    )

def import_backup(data):
    counts = {"patients": 0, "appointments": 0, "prescriptions": 0, "invoices": 0, "medications": 0}
    id_map = {}

    for p in data.get("patients", []):
        number = p.get("patientNumber")
        existing = Patient.query.filter_by(patient_number=number).first() if number else None
        if existing:
            id_map[p.get("id")] = existing
            continue
        patient = Patient(
            patient_number=number or patient_service.next_patient_number(),
            name=p.get("Name") or "Unknown",
            age=p.get("age"),
            gender=p.get("gender"),
            previous_operations=p.get("previousOperations"),
            previous_treatment=p.get("previousTreatment"),
            diagnosis=p.get("diagnosis"),
            symptoms=p.get("symptoms"),
            family_history=p.get("familyHistory"),
            mobile_number=p.get("mobileNumber"),
            emergency_contact=p.get("emergencyContact"),
            notes=p.get("notes"),
            medical_history_extra=json.dumps(p.get("medicalHistoryExtra")) if p.get("medicalHistoryExtra") else None,
        )
        for a in p.get("appointments", []):
            patient.appointments.append(_build_appointment(a))
            counts["appointments"] += 1
        db.session.add(patient)
        db.session.flush()
        id_map[p.get("id")] = patient
        counts["patients"] += 1

    for rx in data.get("prescriptions", []):
        patient = id_map.get(rx.get("patientId"))
        if not patient:
            continue
        db.session.add(Prescription(
            patient_id=patient.id,
            date=rx.get("date"),
            diagnosis=rx.get("diagnosis"),
            notes=rx.get("notes"),
            drugs_json=json.dumps(rx.get("drugs") or []),
        ))
        counts["prescriptions"] += 1

    for inv in data.get("invoices", []):
        patient = id_map.get(inv.get("patientId"))
        if not patient:
            continue
        db.session.add(Invoice(
            patient_id=patient.id,
            description=inv.get("description"),
            amount=inv.get("amount") or 0,
            paid_amount=inv.get("paidAmount") or 0,
            date=inv.get("date"),
        ))
        counts["invoices"] += 1

    for m in data.get("medicationRecords", []):
        if not m.get("name"):
            continue
        db.session.add(MedicationRecord(
            name=m.get("name"),
            company=m.get("company"),
            purpose=m.get("purpose"),
            date_added=m.get("date"),
            generic_name=m.get("genericName"),
            category=m.get("category"),
            dosage=m.get("dosage"),
        ))
        counts["medications"] += 1

    existing_library = {r.drug_name for r in MedicationLibrary.query.all()}
    for m in data.get("medicationLibrary", []):
        name = m.get("drugName")
        if not name or name in existing_library:
            continue
        db.session.add(MedicationLibrary(
            drug_name=name,
            generic_name=m.get("genericName"),
            dosage=m.get("dosage"),
            category=m.get("category"),
            notes=m.get("notes"),
        ))
        existing_library.add(name)

    existing_diag = {d.diagnosis for d in DiagnosisLibrary.query.all()}
    for d in data.get("diagnosisLibrary", []):
        name = d.get("diagnosis")
        if not name or name in existing_diag:
            continue
        db.session.add(DiagnosisLibrary(
            code=d.get("code"),
            diagnosis=name,
            description=d.get("description"),
            specialty=d.get("specialty"),
        ))
        existing_diag.add(name)

    db.session.commit()
    return counts
