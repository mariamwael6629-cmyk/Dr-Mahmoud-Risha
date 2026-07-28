import json

from database import db
from models.prescription import Prescription

def create_prescription(data):
    record = Prescription(
        patient_id=data["patientId"],
        date=data.get("date"),
        diagnosis=data.get("diagnosis"),
        notes=data.get("notes"),
        drugs_json=json.dumps(data.get("drugs", [])),
    )
    db.session.add(record)
    db.session.commit()
    return record

def list_prescriptions_for_patient(patient_id):
    return (
        Prescription.query.filter_by(patient_id=patient_id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
