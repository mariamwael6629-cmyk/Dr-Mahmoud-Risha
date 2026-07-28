from sqlalchemy.orm import selectinload

from database import db
from models.financial import Invoice

def list_invoices(patient_id=None, status=None):
    query = Invoice.query.options(selectinload(Invoice.patient))
    if patient_id:
        query = query.filter(Invoice.patient_id == patient_id)
    rows = query.order_by(Invoice.id.desc()).all()
    if status:
        rows = [r for r in rows if r.status == status]
    return rows

def get_invoice(invoice_id):
    return Invoice.query.get(invoice_id)

def create_invoice(data):
    invoice = Invoice(
        patient_id=int(data["patientId"]),
        appointment_id=int(data["appointmentId"]) if data.get("appointmentId") else None,
        description=data.get("description"),
        amount=float(data.get("amount") or 0),
        paid_amount=float(data.get("paidAmount") or 0),
        date=data.get("date"),
    )
    db.session.add(invoice)
    db.session.commit()
    return invoice

def record_payment(invoice, amount):
    invoice.paid_amount = (invoice.paid_amount or 0) + float(amount)
    db.session.commit()
    return invoice

def update_invoice(invoice, data):
    field_map = [
        ("description", "description"), ("amount", "amount"),
        ("paidAmount", "paid_amount"), ("date", "date"),
    ]
    for json_key, attr in field_map:
        if json_key in data:
            setattr(invoice, attr, data[json_key])
    db.session.commit()
    return invoice

def delete_invoice(invoice):
    db.session.delete(invoice)
    db.session.commit()

def revenue_summary():
    rows = Invoice.query.all()
    total_billed = sum(r.amount or 0 for r in rows)
    total_collected = sum(r.paid_amount or 0 for r in rows)
    return {
        "totalBilled": round(total_billed, 2),
        "totalCollected": round(total_collected, 2),
        "totalOutstanding": round(total_billed - total_collected, 2),
        "invoiceCount": len(rows),
    }
