from datetime import datetime

from database import db

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    date = db.Column(db.String(20))
    diagnosis = db.Column(db.Text)
    drugs = db.Column(db.Text)
    required_tests = db.Column(db.Text)
    tests_result = db.Column(db.Text)
    medical_xray_required = db.Column(db.Text)
    medical_xray_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default="waiting")
    visit_type = db.Column(db.String(30))
    visit_notes = db.Column(db.Text)
    time = db.Column(db.String(10))

    files = db.relationship("UploadedFile", backref="appointment", cascade="all, delete-orphan")

    def to_dict(self, include_patient=False):
        data = {
            "id": self.id,
            "patientId": self.patient_id,
            "date": self.date,
            "time": self.time,
            "diagnosis": self.diagnosis,
            "drugs": self.drugs,
            "requiredTests": self.required_tests,
            "testsResult": self.tests_result,
            "medicalXRayRequired": self.medical_xray_required,
            "medicalXRayResult": self.medical_xray_result,
            "status": self.status or "waiting",
            "visitType": self.visit_type,
            "visitNotes": self.visit_notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "files": [f.to_dict() for f in self.files],
        }
        if include_patient and self.patient:
            data["patientName"] = self.patient.name
            data["patientNumber"] = self.patient.patient_number
            data["patientMobile"] = self.patient.mobile_number
        return data
