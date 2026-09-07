from datetime import datetime

from database import db

class ClinicSettings(db.Model):
    __tablename__ = "clinic_settings"

    id = db.Column(db.Integer, primary_key=True)
    doctor_name_en = db.Column(db.String(150))
    doctor_name_ar = db.Column(db.String(150))
    clinic_name_en = db.Column(db.String(150))
    clinic_name_ar = db.Column(db.String(150))
    specialty_en = db.Column(db.String(200))
    specialty_ar = db.Column(db.String(200))
    credentials_en = db.Column(db.Text)
    credentials_ar = db.Column(db.Text)
    address_1 = db.Column(db.Text)
    address_2 = db.Column(db.Text)
    phone_1 = db.Column(db.String(30))
    phone_2 = db.Column(db.String(30))
    footer_note_ar = db.Column(db.Text)
    logo_path = db.Column(db.String(255))
    signature_path = db.Column(db.String(255))
    qr_path = db.Column(db.String(255))
    checkup_price = db.Column(db.Float, default=0)       # كشف
    followup_price = db.Column(db.Float, default=0)      # إعادة
    consultation_price = db.Column(db.Float, default=0)  # استشارة
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "doctorNameEn": self.doctor_name_en,
            "doctorNameAr": self.doctor_name_ar,
            "clinicNameEn": self.clinic_name_en,
            "clinicNameAr": self.clinic_name_ar,
            "specialtyEn": self.specialty_en,
            "specialtyAr": self.specialty_ar,
            "credentialsEn": self.credentials_en,
            "credentialsAr": self.credentials_ar,
            "address1": self.address_1,
            "address2": self.address_2,
            "phone1": self.phone_1,
            "phone2": self.phone_2,
            "footerNoteAr": self.footer_note_ar,
            "logoUrl": self.logo_path,
            "signatureUrl": self.signature_path,
            "qrUrl": self.qr_path,
            "checkupPrice": self.checkup_price or 0,
            "followupPrice": self.followup_price or 0,
            "consultationPrice": self.consultation_price or 0,
        }
