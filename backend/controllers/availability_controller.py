from flask import jsonify, request

from services import availability_service

def list_availability():
    rows = availability_service.list_availability()
    return jsonify([r.to_dict() for r in rows])

def create_availability():
    data = request.get_json(force=True) or {}
    if data.get("dayOfWeek") is None or not data.get("startTime") or not data.get("endTime"):
        return jsonify({"error": "dayOfWeek, startTime and endTime are required"}), 400
    row = availability_service.create_availability(data)
    return jsonify(row.to_dict()), 201

def update_availability(availability_id):
    row = availability_service.get_availability(availability_id)
    if not row:
        return jsonify({"error": "Availability slot not found"}), 404
    data = request.get_json(force=True) or {}
    row = availability_service.update_availability(row, data)
    return jsonify(row.to_dict())

def delete_availability(availability_id):
    row = availability_service.get_availability(availability_id)
    if not row:
        return jsonify({"error": "Availability slot not found"}), 404
    availability_service.delete_availability(row)
    return jsonify({"success": True})
