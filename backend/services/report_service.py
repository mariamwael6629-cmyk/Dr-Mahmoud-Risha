from datetime import date, timedelta

from database import db
from models.appointment import Appointment
from models.patient import Patient
from models.financial import Invoice

def visits_per_day(days=14):
    end = date.today()
    start = end - timedelta(days=days - 1)
    rows = (
        db.session.query(Appointment.date, db.func.count(Appointment.id))
        .filter(Appointment.date >= start.isoformat(), Appointment.date <= end.isoformat())
        .group_by(Appointment.date)
        .all()
    )
    counts = {d: c for d, c in rows}
    return [
        {"date": (start + timedelta(days=i)).isoformat(), "visits": counts.get((start + timedelta(days=i)).isoformat(), 0)}
        for i in range(days)
    ]

def patient_summary():
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    new_patients_30d = Patient.query.filter(
        Patient.created_at >= db.func.datetime("now", "-30 days")
    ).count()
    return {
        "totalPatients": total_patients,
        "totalAppointments": total_appointments,
        "newPatientsLast30Days": new_patients_30d,
    }

def visit_type_breakdown():
    rows = (
        db.session.query(Appointment.visit_type, db.func.count(Appointment.id))
        .group_by(Appointment.visit_type)
        .all()
    )
    return [{"visitType": vt or "unspecified", "count": c} for vt, c in rows]

def queue_snapshot():
    today = date.today().isoformat()
    rows = (
        db.session.query(Appointment.status, db.func.count(Appointment.id))
        .filter(Appointment.date == today)
        .group_by(Appointment.status)
        .all()
    )
    counts = {s or "waiting": c for s, c in rows}
    return {
        "waiting": counts.get("waiting", 0),
        "arrived": counts.get("arrived", 0),
        "inConsultation": counts.get("in_consultation", 0),
        "completed": counts.get("completed", 0),
        "cancelled": counts.get("cancelled", 0),
    }

def revenue_by_status():
    rows = Invoice.query.all()
    summary = {"unpaid": 0.0, "partial": 0.0, "paid": 0.0}
    for r in rows:
        summary[r.status] += r.amount or 0
    return {k: round(v, 2) for k, v in summary.items()}

def _prev_month(today):
    first_of_this_month = today.replace(day=1)
    last_of_prev = first_of_this_month - timedelta(days=1)
    return last_of_prev.year, last_of_prev.month

def monthly_report(year=None, month=None):
    today = date.today()
    if not year or not month:
        year, month = _prev_month(today)
    year = int(year)
    month = int(month)
    prefix = f"{year:04d}-{month:02d}"

    appointments = [
        a for a in Appointment.query.filter(Appointment.date.like(f"{prefix}%")).all()
        if a.status != "cancelled"
    ]
    new_visits = sum(1 for a in appointments if a.visit_type == "consultation")
    follow_ups = sum(1 for a in appointments if a.visit_type == "followUp")

    invoices = Invoice.query.filter(Invoice.date.like(f"{prefix}%")).all()
    total_billed = sum(i.amount or 0 for i in invoices)
    money_collected = sum(i.paid_amount or 0 for i in invoices)
    outstanding = total_billed - money_collected

    return {
        "year": year,
        "month": month,
        "label": prefix,
        "newVisits": new_visits,
        "followUps": follow_ups,
        "totalVisits": len(appointments),
        "completedVisits": sum(1 for a in appointments if a.status == "completed"),
        "moneyCollected": round(money_collected, 2),
        "totalBilled": round(total_billed, 2),
        "outstanding": round(outstanding, 2),
        "invoiceCount": len(invoices),
    }
