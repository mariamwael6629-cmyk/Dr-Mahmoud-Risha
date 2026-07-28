from flask import jsonify, request

from services import medication_service

def list_records():
    search = request.args.get("search", "").strip()
    records = medication_service.list_medication_records(search or None)
    return jsonify([r.to_dict() for r in records])

def create_record():
    data = request.get_json(force=True) or {}
    if not data.get("name") or not data.get("company") or not data.get("purpose"):
        return jsonify({"error": "name, company and purpose are required"}), 400
    record = medication_service.create_medication_record(data)
    return jsonify(record.to_dict()), 201

def delete_record(record_id):
    record = medication_service.get_medication_record(record_id)
    if not record:
        return jsonify({"error": "Medication record not found"}), 404
    medication_service.delete_medication_record(record)
    return jsonify({"success": True})

def search_library():
    query = request.args.get("q", "").strip()
    results = medication_service.search_medication_library(query)
    return jsonify([r.to_dict() for r in results])

def add_library_entry():
    data = request.get_json(force=True) or {}
    if not (data.get("drugName") or "").strip():
        return jsonify({"error": "drugName is required"}), 400
    entry, created = medication_service.get_or_create_library_entry(data)
    return jsonify(entry.to_dict()), 201 if created else 200
