from datetime import datetime

from database import db

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True, index=True)
    description = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False, default=0)
    paid_amount = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="invoices")

    @property
    def status(self):
        if self.paid_amount <= 0:
            return "unpaid"
        if self.paid_amount >= self.amount:
            return "paid"
        return "partial"

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "appointmentId": self.appointment_id,
            "description": self.description,
            "amount": self.amount,
            "paidAmount": self.paid_amount,
            "balance": round(self.amount - self.paid_amount, 2),
            "status": self.status,
            "date": self.date,
            "patientName": self.patient.name if self.patient else None,
            "patientNumber": self.patient.patient_number if self.patient else None,
        }
