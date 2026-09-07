from flask import jsonify, request

from services import appointment_service, patient_service
from security import sanitize_appointment, sanitize_patient, current_role

def add_appointment(patient_id):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    data = request.get_json(force=True) or {}
    appt = appointment_service.add_appointment(patient, data)
    return jsonify(sanitize_appointment(appt.to_dict(), current_role())), 201

def update_appointment(appointment_id):
    appt = appointment_service.get_appointment(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    data = request.get_json(force=True) or {}
    appt = appointment_service.update_appointment(appt, data)
    return jsonify(sanitize_appointment(appt.to_dict(), current_role()))

def delete_appointment(appointment_id):
    appt = appointment_service.get_appointment(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    appointment_service.delete_appointment(appt)
    return jsonify({"success": True})

def list_appointments():
    date = request.args.get("date") or None
    patient_id_raw = request.args.get("patientId") or None
    status = request.args.get("status") or None
    patient_id = int(patient_id_raw) if patient_id_raw else None
    appts = appointment_service.list_appointments(date=date, patient_id=patient_id, status=status)
    role = current_role()
    return jsonify([sanitize_appointment(a.to_dict(include_patient=True), role) for a in appts])

def next_slot():
    visit_type = request.args.get("visitType") or None
    date, time = appointment_service.next_available_slot(visit_type)
    return jsonify({"date": date, "time": time})

def slots():
    date = request.args.get("date") or None
    visit_type = request.args.get("visitType") or None
    return jsonify({
        "date": date,
        "slots": appointment_service.available_slots(date, visit_type),
        "validDays": appointment_service.valid_booking_days(),
    })

def book():
    data = request.get_json(force=True) or {}
    try:
        patient, appt = appointment_service.book_walkin(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    role = current_role()
    result = sanitize_appointment(appt.to_dict(include_patient=True), role)
    result["patient"] = sanitize_patient(patient.to_dict(include_appointments=False), role)
    return jsonify(result), 201

def import_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    try:
        imported = appointment_service.import_appointments_file(request.files["file"])
    except (ValueError, UnicodeError) as exc:
        return jsonify({"error": f"Could not read the file: {exc}"}), 400
    return jsonify({"imported": imported})
