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
    amount = max(float(data.get("amount") or 0), 0)
    # Amount paid can never be negative or exceed the invoice total, so the
    # balance stays >= 0 and the status is always meaningful.
    paid = min(max(float(data.get("paidAmount") or 0), 0), amount)
    invoice = Invoice(
        patient_id=int(data["patientId"]),
        appointment_id=int(data["appointmentId"]) if data.get("appointmentId") else None,
        description=data.get("description"),
        amount=amount,
        paid_amount=paid,
        date=data.get("date"),
    )
    db.session.add(invoice)
    db.session.commit()
    return invoice

def record_payment(invoice, amount):
    payment = max(float(amount), 0)
    new_paid = (invoice.paid_amount or 0) + payment
    # Never let the total paid exceed the invoice amount.
    invoice.paid_amount = min(new_paid, invoice.amount or 0)
    db.session.commit()
    return invoice

def update_invoice(invoice, data):
    if "amount" in data:
        invoice.amount = max(float(data["amount"] or 0), 0)
    if "description" in data:
        invoice.description = data["description"]
    if "date" in data:
        invoice.date = data["date"]
    if "paidAmount" in data:
        invoice.paid_amount = min(max(float(data["paidAmount"] or 0), 0), invoice.amount or 0)
    else:
        # Keep paid within the (possibly changed) amount.
        invoice.paid_amount = min(invoice.paid_amount or 0, invoice.amount or 0)
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
