from flask import Blueprint

from controllers import prescription_controller

prescriptions_bp = Blueprint("prescriptions", __name__, url_prefix="/api")


@prescriptions_bp.post("/prescriptions")
def create_prescription():
    """Save a generated prescription record to the patient's history
    ---
    tags: [Prescriptions]
    responses:
      201:
        description: Prescription record saved
      400:
        description: Validation error
    """
    return prescription_controller.create_prescription()


@prescriptions_bp.get("/patients/<int:patient_id>/prescriptions")
def list_patient_prescriptions(patient_id):
    """List saved prescription history for a patient
    ---
    tags: [Prescriptions]
    responses:
      200:
        description: List of prescription records
    """
    return prescription_controller.list_patient_prescriptions(patient_id)
