from flask import jsonify, request

from services import patient_service

REQUIRED_FIELDS = ["Name", "age", "gender", "mobileNumber"]

def _validate(data):
    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    return missing

def list_patients():
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("perPage", 50)), 200)
    items, total = patient_service.list_patients(search=search or None, page=page, per_page=per_page)
    return jsonify({
        "items": [p.to_dict() for p in items],
        "total": total,
        "page": page,
        "perPage": per_page,
    })

def get_patient(patient_id):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient.to_dict())

def create_patient():
    data = request.get_json(force=True) or {}
    missing = _validate(data)
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    force = bool(data.pop("forceCreateDuplicate", False))
    try:
        patient = patient_service.create_patient(data, allow_duplicate=force)
    except patient_service.DuplicatePatientError as exc:
        return jsonify({
            "error": "duplicate_mobile",
            "message": "A patient with this mobile number already exists.",
            "existingPatient": exc.existing_patient.to_dict(include_appointments=False),
        }), 409
    return jsonify(patient.to_dict()), 201

def update_patient(patient_id):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    data = request.get_json(force=True) or {}
    if "mobileNumber" in data:
        dup = patient_service.find_duplicate_by_mobile(data["mobileNumber"], exclude_id=patient_id)
        if dup:
            return jsonify({
                "error": "duplicate_mobile",
                "message": "A patient with this mobile number already exists.",
                "existingPatient": dup.to_dict(include_appointments=False),
            }), 409
    patient = patient_service.update_patient(patient, data)
    return jsonify(patient.to_dict())

def delete_patient(patient_id):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    patient_service.delete_patient(patient)
    return jsonify({"success": True})

def next_number():
    return jsonify({"patientNumber": patient_service.next_patient_number()})

def check_duplicate():
    mobile_number = request.args.get("mobileNumber", "").strip()
    if not mobile_number:
        return jsonify({"error": "mobileNumber query param is required"}), 400
    dup = patient_service.find_duplicate_by_mobile(mobile_number)
    return jsonify({
        "duplicate": dup is not None,
        "patient": dup.to_dict(include_appointments=False) if dup else None,
    })
