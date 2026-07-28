from flask import jsonify, request

from services import prescription_service

def create_prescription():
    data = request.get_json(force=True) or {}
    if not data.get("patientId"):
        return jsonify({"error": "patientId is required"}), 400
    record = prescription_service.create_prescription(data)
    return jsonify(record.to_dict()), 201

def list_patient_prescriptions(patient_id):
    records = prescription_service.list_prescriptions_for_patient(patient_id)
    return jsonify([r.to_dict() for r in records])
