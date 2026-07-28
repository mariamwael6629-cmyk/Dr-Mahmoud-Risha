from datetime import datetime

from database import db

class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True, index=True)
                                                                  
    category = db.Column(db.String(30), nullable=False, default="other")
    file_name = db.Column(db.String(255), nullable=False)                             
    original_name = db.Column(db.String(255), nullable=False)                            
    file_path = db.Column(db.String(500), nullable=False)                                      
    file_type = db.Column(db.String(10), nullable=False)                                 
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "appointmentId": self.appointment_id,
            "category": self.category,
            "fileName": self.file_name,
            "originalName": self.original_name,
            "fileType": self.file_type,
            "uploadDate": self.upload_date.isoformat() if self.upload_date else None,
            "previewUrl": f"/api/files/{self.id}/preview",
            "downloadUrl": f"/api/files/{self.id}/download",
        }
