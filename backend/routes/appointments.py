from flask import Blueprint

from controllers import appointment_controller

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api")


@appointments_bp.get("/appointments")
def list_appointments():
    """List/filter appointments across all patients
    ---
    tags: [Appointments]
    parameters:
      - name: date
        in: query
        type: string
      - name: patientId
        in: query
        type: integer
      - name: status
        in: query
        type: string
    responses:
      200:
        description: List of appointments
    """
    return appointment_controller.list_appointments()


@appointments_bp.get("/appointments/next-slot")
def next_slot():
    """Suggest the next available booking slot on a valid clinic day
    ---
    tags: [Appointments]
    parameters:
      - name: visitType
        in: query
        type: string
    responses:
      200:
        description: The earliest free {date, time}
    """
    return appointment_controller.next_slot()


@appointments_bp.get("/appointments/slots")
def slots():
    """List free time slots for a given day plus the upcoming valid clinic days
    ---
    tags: [Appointments]
    parameters:
      - name: date
        in: query
        type: string
      - name: visitType
        in: query
        type: string
    responses:
      200:
        description: Available slots and valid days
    """
    return appointment_controller.slots()


@appointments_bp.post("/appointments/book")
def book():
    """Book an appointment for anyone by free-text name and phone
    ---
    tags: [Appointments]
    responses:
      201:
        description: Appointment booked
      400:
        description: Validation error
    """
    return appointment_controller.book()


@appointments_bp.post("/appointments/import")
def import_file():
    """Import appointments from an uploaded CSV/JSON file and auto-schedule them
    ---
    tags: [Appointments]
    consumes: [multipart/form-data]
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Number of appointments imported
      400:
        description: Invalid file
    """
    return appointment_controller.import_file()


@appointments_bp.post("/patients/<int:patient_id>/appointments")
def add_appointment(patient_id):
    """Add an appointment to a patient
    ---
    tags: [Appointments]
    responses:
      201:
        description: Appointment created
      404:
        description: Patient not found
    """
    return appointment_controller.add_appointment(patient_id)


@appointments_bp.put("/appointments/<int:appointment_id>")
def update_appointment(appointment_id):
    """Update an appointment
    ---
    tags: [Appointments]
    responses:
      200:
        description: Appointment updated
      404:
        description: Appointment not found
    """
    return appointment_controller.update_appointment(appointment_id)


@appointments_bp.delete("/appointments/<int:appointment_id>")
def delete_appointment(appointment_id):
    """Delete an appointment
    ---
    tags: [Appointments]
    responses:
      200:
        description: Appointment deleted
      404:
        description: Appointment not found
    """
    return appointment_controller.delete_appointment(appointment_id)
