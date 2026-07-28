from database import db
from models.availability import DoctorAvailability

def list_availability():
    return DoctorAvailability.query.order_by(DoctorAvailability.day_of_week).all()

def get_availability(availability_id):
    return DoctorAvailability.query.get(availability_id)

def create_availability(data):
    row = DoctorAvailability(
        day_of_week=int(data["dayOfWeek"]),
        start_time=data["startTime"],
        end_time=data["endTime"],
        slot_minutes=int(data.get("slotMinutes") or 30),
        is_active=bool(data.get("isActive", True)),
    )
    db.session.add(row)
    db.session.commit()
    return row

def update_availability(row, data):
    field_map = [
        ("dayOfWeek", "day_of_week"), ("startTime", "start_time"), ("endTime", "end_time"),
        ("slotMinutes", "slot_minutes"), ("isActive", "is_active"),
    ]
    for json_key, attr in field_map:
        if json_key in data:
            setattr(row, attr, data[json_key])
    db.session.commit()
    return row

def delete_availability(row):
    db.session.delete(row)
    db.session.commit()
