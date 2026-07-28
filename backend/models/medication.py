from database import db

class MedicationRecord(db.Model):
    __tablename__ = "medication_records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    purpose = db.Column(db.Text)
    date_added = db.Column(db.String(30))
    generic_name = db.Column(db.String(150))
    category = db.Column(db.String(100))
    dosage = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "purpose": self.purpose,
            "date": self.date_added,
            "genericName": self.generic_name,
            "category": self.category,
            "dosage": self.dosage,
        }

class MedicationLibrary(db.Model):
    __tablename__ = "medication_library"

    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(150), nullable=False, index=True)
    generic_name = db.Column(db.String(150))
    dosage = db.Column(db.String(100))
    category = db.Column(db.String(100))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "drugName": self.drug_name,
            "genericName": self.generic_name,
            "dosage": self.dosage,
            "category": self.category,
            "notes": self.notes,
        }
