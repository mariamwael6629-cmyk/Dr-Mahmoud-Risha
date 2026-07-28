from database import db

class DiagnosisLibrary(db.Model):
    __tablename__ = "diagnosis_library"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), index=True)
    diagnosis = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    specialty = db.Column(db.String(100))

    def to_dict(self):
        return {
            "code": self.code,
            "diagnosis": self.diagnosis,
            "description": self.description,
            "specialty": self.specialty,
        }
