import json
from datetime import datetime

from database import db

class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    date = db.Column(db.String(20))
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)
    drugs_json = db.Column(db.Text)                             
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "date": self.date,
            "diagnosis": self.diagnosis,
            "notes": self.notes,
            "drugs": json.loads(self.drugs_json) if self.drugs_json else [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
