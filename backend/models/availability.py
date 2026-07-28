from database import db

class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availability"

    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)                        
    start_time = db.Column(db.String(5), nullable=False)           
    end_time = db.Column(db.String(5), nullable=False)             
    slot_minutes = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "dayOfWeek": self.day_of_week,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "slotMinutes": self.slot_minutes,
            "isActive": self.is_active,
        }
