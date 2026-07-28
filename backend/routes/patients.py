from flask import Blueprint

from controllers import patient_controller

patients_bp = Blueprint("patients", __name__, url_prefix="/api/patients")


@patients_bp.get("")
def list_patients():
    """List / search patients (paginated)
    ---
    tags: [Patients]
    parameters:
      - name: search
        in: query
        type: string
      - name: page
        in: query
        type: integer
      - name: perPage
        in: query
        type: integer
    responses:
      200:
        description: Paginated list of patients
    """
    return patient_controller.list_patients()


@patients_bp.get("/next-number")
def next_number():
    """Get the next available patient file number
    ---
    tags: [Patients]
    responses:
      200:
        description: Next available patient number
    """
    return patient_controller.next_number()


@patients_bp.get("/duplicate-check")
def check_duplicate():
    """Check if a mobile number is already registered to a patient
    ---
    tags: [Patients]
    parameters:
      - name: mobileNumber
        in: query
        type: string
        required: true
    responses:
      200:
        description: Whether a duplicate patient exists
    """
    return patient_controller.check_duplicate()


@patients_bp.get("/<int:patient_id>")
def get_patient(patient_id):
    """Get a single patient with appointments
    ---
    tags: [Patients]
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Patient details
      404:
        description: Patient not found
    """
    return patient_controller.get_patient(patient_id)


@patients_bp.post("")
def create_patient():
    """Create a new patient (with optional nested appointments)
    ---
    tags: [Patients]
    responses:
      201:
        description: Patient created
      400:
        description: Validation error
      409:
        description: Duplicate mobile number
    """
    return patient_controller.create_patient()


@patients_bp.put("/<int:patient_id>")
def update_patient(patient_id):
    """Update an existing patient
    ---
    tags: [Patients]
    responses:
      200:
        description: Patient updated
      404:
        description: Patient not found
      409:
        description: Duplicate mobile number
    """
    return patient_controller.update_patient(patient_id)


@patients_bp.delete("/<int:patient_id>")
def delete_patient(patient_id):
    """Delete a patient
    ---
    tags: [Patients]
    responses:
      200:
        description: Patient deleted
      404:
        description: Patient not found
    """
    return patient_controller.delete_patient(patient_id)
