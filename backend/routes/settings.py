from flask import Blueprint

from controllers import settings_controller

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@settings_bp.get("/branding")
def get_branding():
    """Get the clinic / doctor branding settings used by the navbar, login, prescription and reports
    ---
    tags: [Settings]
    responses:
      200:
        description: Clinic branding settings
      404:
        description: Clinic settings not initialized
    """
    return settings_controller.get_branding()


@settings_bp.put("/branding")
def update_branding():
    """Update the clinic / doctor branding settings
    ---
    tags: [Settings]
    responses:
      200:
        description: Updated clinic branding settings
    """
    return settings_controller.update_branding()


@settings_bp.get("/backup")
def get_backup():
    """Export a full JSON backup of all clinic data (patients, appointments, medications, prescriptions, invoices, availability, branding)
    ---
    tags: [Settings]
    responses:
      200:
        description: Full data export
    """
    return settings_controller.get_backup()


@settings_bp.post("/import")
def import_data():
    """Import clinic data from a JSON backup exported by this or another system
    ---
    tags: [Settings]
    responses:
      200:
        description: Import summary counts
      400:
        description: Invalid backup payload
    """
    return settings_controller.import_data()
