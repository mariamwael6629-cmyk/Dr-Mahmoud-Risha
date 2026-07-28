from flask import Blueprint

from controllers import medication_controller

medications_bp = Blueprint("medications", __name__, url_prefix="/api/medications")


@medications_bp.get("/search")
def search_library():
    """Search the medication autocomplete library
    ---
    tags: [Medications]
    parameters:
      - name: q
        in: query
        type: string
        description: Search text (drug name or generic name); empty returns top entries
    responses:
      200:
        description: List of matching medications {drugName, genericName, dosage, category, notes}
    """
    return medication_controller.search_library()


@medications_bp.post("/library")
def add_library_entry():
    """Auto-capture a new medication typed on the Rx page into the autocomplete library
    ---
    tags: [Medications]
    responses:
      201:
        description: New library entry created
      200:
        description: Entry already existed (case-insensitive drug name match)
      400:
        description: Validation error
    """
    return medication_controller.add_library_entry()


@medications_bp.get("")
def list_records():
    """List the clinic's existing medication records (original Medications page)
    ---
    tags: [Medications]
    responses:
      200:
        description: List of medication records
    """
    return medication_controller.list_records()


@medications_bp.post("")
def create_record():
    """Add a medication record to the clinic's Medications page
    ---
    tags: [Medications]
    responses:
      201:
        description: Medication record created
      400:
        description: Validation error
    """
    return medication_controller.create_record()


@medications_bp.delete("/<int:record_id>")
def delete_record(record_id):
    """Delete a medication record
    ---
    tags: [Medications]
    responses:
      200:
        description: Deleted
      404:
        description: Not found
    """
    return medication_controller.delete_record(record_id)
