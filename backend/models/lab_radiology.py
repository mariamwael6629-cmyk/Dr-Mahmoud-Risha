from database import db

class LabTestLibrary(db.Model):
    __tablename__ = "lab_test_library"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), index=True)
    test_name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))

    def to_dict(self):
        return {
            "code": self.code,
            "testName": self.test_name,
            "description": self.description,
            "category": self.category,
        }

class RadiologyLibrary(db.Model):
    __tablename__ = "radiology_library"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), index=True)
    exam_name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))

    def to_dict(self):
        return {
            "code": self.code,
            "examName": self.exam_name,
            "description": self.description,
            "category": self.category,
        }
