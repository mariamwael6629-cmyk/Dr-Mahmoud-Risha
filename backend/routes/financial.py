"""--- NEW FEATURE: financial tracking (invoices/payments) ---"""
from flask import Blueprint

from controllers import financial_controller

financial_bp = Blueprint("financial", __name__, url_prefix="/api/financial")


@financial_bp.get("/invoices")
def list_invoices():
    """List invoices, optionally filtered by patient/status
    ---
    tags: [Financial]
    parameters:
      - name: patientId
        in: query
        type: integer
      - name: status
        in: query
        type: string
        description: unpaid | partial | paid
    responses:
      200:
        description: List of invoices
    """
    return financial_controller.list_invoices()


@financial_bp.post("/invoices")
def create_invoice():
    """Create an invoice for a patient
    ---
    tags: [Financial]
    responses:
      201:
        description: Invoice created
      400:
        description: Validation error
    """
    return financial_controller.create_invoice()


@financial_bp.put("/invoices/<int:invoice_id>")
def update_invoice(invoice_id):
    """Update an invoice
    ---
    tags: [Financial]
    responses:
      200:
        description: Invoice updated
      404:
        description: Not found
    """
    return financial_controller.update_invoice(invoice_id)


@financial_bp.post("/invoices/<int:invoice_id>/payments")
def record_payment(invoice_id):
    """Record a payment against an invoice
    ---
    tags: [Financial]
    responses:
      200:
        description: Invoice updated with new paid amount
      404:
        description: Not found
    """
    return financial_controller.record_payment(invoice_id)


@financial_bp.delete("/invoices/<int:invoice_id>")
def delete_invoice(invoice_id):
    """Delete an invoice
    ---
    tags: [Financial]
    responses:
      200:
        description: Deleted
      404:
        description: Not found
    """
    return financial_controller.delete_invoice(invoice_id)


@financial_bp.get("/summary")
def revenue_summary():
    """Revenue summary (total billed/collected/outstanding)
    ---
    tags: [Financial]
    responses:
      200:
        description: Revenue summary
    """
    return financial_controller.revenue_summary()
