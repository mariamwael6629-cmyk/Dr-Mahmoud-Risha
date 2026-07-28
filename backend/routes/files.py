from flask import Blueprint

from controllers import file_controller

files_bp = Blueprint("files", __name__, url_prefix="/api")


@files_bp.post("/files/upload")
def upload_file():
    """Upload a PDF/image file (X-Ray result, required tests, test result, etc.)
    ---
    tags: [Files]
    consumes: [multipart/form-data]
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      - name: patientId
        in: formData
        type: integer
        required: true
      - name: appointmentId
        in: formData
        type: integer
      - name: category
        in: formData
        type: string
        description: xray_result | required_tests | test_result | other
    responses:
      201:
        description: File uploaded
      400:
        description: Invalid file or missing fields
    """
    return file_controller.upload_file()


@files_bp.get("/patients/<int:patient_id>/files")
def list_patient_files(patient_id):
    """List all uploaded files for a patient
    ---
    tags: [Files]
    responses:
      200:
        description: List of files
    """
    return file_controller.list_patient_files(patient_id)


@files_bp.get("/appointments/<int:appointment_id>/files")
def list_appointment_files(appointment_id):
    """List uploaded files for a specific appointment
    ---
    tags: [Files]
    responses:
      200:
        description: List of files
    """
    return file_controller.list_appointment_files(appointment_id)


@files_bp.get("/files/<int:file_id>/download")
def download_file(file_id):
    """Download an uploaded file as an attachment
    ---
    tags: [Files]
    responses:
      200:
        description: File contents
      404:
        description: File not found
    """
    return file_controller.download_file(file_id)


@files_bp.get("/files/<int:file_id>/preview")
def preview_file(file_id):
    """Stream an uploaded file inline for preview
    ---
    tags: [Files]
    responses:
      200:
        description: File contents (inline)
      404:
        description: File not found
    """
    return file_controller.preview_file(file_id)


@files_bp.delete("/files/<int:file_id>")
def delete_file(file_id):
    """Delete an uploaded file
    ---
    tags: [Files]
    responses:
      200:
        description: Deleted
      404:
        description: File not found
    """
    return file_controller.delete_file(file_id)
