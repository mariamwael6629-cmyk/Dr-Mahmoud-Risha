"""--- NEW FEATURE: doctor weekly availability ---"""
from flask import Blueprint

from controllers import availability_controller

availability_bp = Blueprint("availability", __name__, url_prefix="/api/availability")


@availability_bp.get("")
def list_availability():
    """List the doctor's weekly availability slots
    ---
    tags: [Availability]
    responses:
      200:
        description: List of availability slots
    """
    return availability_controller.list_availability()


@availability_bp.post("")
def create_availability():
    """Add a weekly availability slot
    ---
    tags: [Availability]
    responses:
      201:
        description: Slot created
      400:
        description: Validation error
    """
    return availability_controller.create_availability()


@availability_bp.put("/<int:availability_id>")
def update_availability(availability_id):
    """Update an availability slot
    ---
    tags: [Availability]
    responses:
      200:
        description: Slot updated
      404:
        description: Not found
    """
    return availability_controller.update_availability(availability_id)


@availability_bp.delete("/<int:availability_id>")
def delete_availability(availability_id):
    """Delete an availability slot
    ---
    tags: [Availability]
    responses:
      200:
        description: Deleted
      404:
        description: Not found
    """
    return availability_controller.delete_availability(availability_id)
