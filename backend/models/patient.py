import json
from datetime import datetime

from database import db

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    patient_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    previous_operations = db.Column(db.Text)
    previous_treatment = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    family_history = db.Column(db.Text)

    mobile_number = db.Column(db.String(30), index=True)
    emergency_contact = db.Column(db.String(30))
    notes = db.Column(db.Text)
    medical_history_extra = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship(
        "Appointment", backref="patient", cascade="all, delete-orphan",
        order_by="Appointment.id",
    )
    files = db.relationship("UploadedFile", backref="patient", cascade="all, delete-orphan")

    def to_dict(self, include_appointments=True):
        data = {
            "id": self.id,
            "patientNumber": self.patient_number,
            "Name": self.name,
            "age": self.age,
            "gender": self.gender,
            "previousOperations": self.previous_operations,
            "previousTreatment": self.previous_treatment,
            "diagnosis": self.diagnosis,
            "symptoms": self.symptoms,
            "familyHistory": self.family_history,
            "mobileNumber": self.mobile_number,
            "emergencyContact": self.emergency_contact,
            "notes": self.notes,
            "medicalHistoryExtra": json.loads(self.medical_history_extra) if self.medical_history_extra else {},
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
        if include_appointments:
            data["appointments"] = [a.to_dict() for a in self.appointments]
        return data
