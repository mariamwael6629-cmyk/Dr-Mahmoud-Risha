from datetime import datetime

from database import db


class MedicalRep(db.Model):
    """A pharmaceutical sales rep who visits the clinic."""
    __tablename__ = "medical_reps"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(40))
    company = db.Column(db.String(150))
    drug = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "company": self.company,
            "drug": self.drug,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
