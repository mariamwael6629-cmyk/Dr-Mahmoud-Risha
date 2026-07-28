from flask import jsonify, request, send_file

from services import file_service

ALLOWED_CATEGORIES = {"xray_result", "required_tests", "test_result", "other"}

def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file_storage = request.files["file"]
    patient_id_raw = request.form.get("patientId")
    appointment_id_raw = request.form.get("appointmentId") or None
    category = request.form.get("category", "other")

    if not patient_id_raw:
        return jsonify({"error": "patientId is required"}), 400
                                                                                
    try:
        patient_id = int(patient_id_raw)
        appointment_id = int(appointment_id_raw) if appointment_id_raw else None
    except (TypeError, ValueError):
        return jsonify({"error": "patientId and appointmentId must be integers"}), 400
    if category not in ALLOWED_CATEGORIES:
        category = "other"

    try:
        record = file_service.save_uploaded_file(
            file_storage, patient_id=patient_id,
            appointment_id=appointment_id,
            category=category,
        )
    except file_service.InvalidFileError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(record.to_dict()), 201

def list_patient_files(patient_id):
    files = file_service.list_files_for_patient(patient_id)
    return jsonify([f.to_dict() for f in files])

def list_appointment_files(appointment_id):
    files = file_service.list_files_for_appointment(appointment_id)
    return jsonify([f.to_dict() for f in files])

def download_file(file_id):
    record = file_service.get_file(file_id)
    if not record:
        return jsonify({"error": "File not found"}), 404
    return send_file(file_service.absolute_path(record), as_attachment=True,
                      download_name=record.original_name)

def preview_file(file_id):
    record = file_service.get_file(file_id)
    if not record:
        return jsonify({"error": "File not found"}), 404
    return send_file(file_service.absolute_path(record), as_attachment=False)

def delete_file(file_id):
    record = file_service.get_file(file_id)
    if not record:
        return jsonify({"error": "File not found"}), 404
    file_service.delete_file(record)
    return jsonify({"success": True})
