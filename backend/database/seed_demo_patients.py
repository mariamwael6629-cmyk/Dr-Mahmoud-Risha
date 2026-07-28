"""
NEW FEATURE: optional demo/test data for manual QA - sample patients with
appointments, so the UI (patient list, prescription, file chips) has
something to look at without manual data entry.

Not run automatically by app.py (seed_if_empty() only seeds the libraries
and clinic branding). Run by hand when you want sample patients:

    cd backend
    python -m database.seed_demo_patients
"""
from datetime import date, timedelta

from app import app
from database import db
from models.patient import Patient
from models.appointment import Appointment

DEMO_PATIENTS = [
    dict(patient_number="P-1001", name="Ahmed Sayed", age=45, gender="Male",
         mobile_number="01012345678", emergency_contact="01098765432",
         diagnosis="Rheumatoid Arthritis (seropositive)", symptoms="Joint pain, morning stiffness",
         previous_treatment="Methotrexate 15mg weekly", family_history="Mother had RA",
         notes="Follow up in 4 weeks"),
    dict(patient_number="P-1002", name="Mona Adel", age=29, gender="Female",
         mobile_number="01077778888", emergency_contact="01055554444",
         diagnosis="Type 2 Diabetes Mellitus", symptoms="Fatigue, frequent urination",
         previous_treatment="Metformin 500mg twice daily", family_history="Father has diabetes",
         notes=""),
    dict(patient_number="P-1003", name="Youssef Hany", age=61, gender="Male",
         mobile_number="01099991111", emergency_contact="01066662222",
         diagnosis="Osteoarthritis of knee", symptoms="Knee pain on walking",
         previous_operations="Right knee arthroscopy (2019)", family_history="",
         notes="Candidate for physiotherapy referral"),
]


def seed_demo_patients():
    today = date.today()
    for entry in DEMO_PATIENTS:
        if Patient.query.filter_by(patient_number=entry["patient_number"]).first():
            continue
        patient = Patient(**entry)
        db.session.add(patient)
        db.session.flush()
        db.session.add(Appointment(
            patient_id=patient.id,
            date=(today - timedelta(days=7)).isoformat(),
            diagnosis=entry["diagnosis"],
            drugs="See prescription",
            required_tests="CBC, ESR, CRP",
        ))
    db.session.commit()
    print(f"Seeded {len(DEMO_PATIENTS)} demo patients (skipping any that already exist).")


if __name__ == "__main__":
    with app.app_context():
        seed_demo_patients()
