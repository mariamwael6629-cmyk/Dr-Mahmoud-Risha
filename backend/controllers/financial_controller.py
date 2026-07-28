from flask import jsonify, request

from services import financial_service

def list_invoices():
    patient_id_raw = request.args.get("patientId") or None
    status = request.args.get("status") or None
    patient_id = int(patient_id_raw) if patient_id_raw else None
    rows = financial_service.list_invoices(patient_id=patient_id, status=status)
    return jsonify([r.to_dict() for r in rows])

def create_invoice():
    data = request.get_json(force=True) or {}
    if not data.get("patientId") or data.get("amount") is None:
        return jsonify({"error": "patientId and amount are required"}), 400
    invoice = financial_service.create_invoice(data)
    return jsonify(invoice.to_dict()), 201

def update_invoice(invoice_id):
    invoice = financial_service.get_invoice(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    data = request.get_json(force=True) or {}
    invoice = financial_service.update_invoice(invoice, data)
    return jsonify(invoice.to_dict())

def record_payment(invoice_id):
    invoice = financial_service.get_invoice(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    data = request.get_json(force=True) or {}
    if data.get("amount") is None:
        return jsonify({"error": "amount is required"}), 400
    invoice = financial_service.record_payment(invoice, data["amount"])
    return jsonify(invoice.to_dict())

def delete_invoice(invoice_id):
    invoice = financial_service.get_invoice(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    financial_service.delete_invoice(invoice)
    return jsonify({"success": True})

def revenue_summary():
    return jsonify(financial_service.revenue_summary())
