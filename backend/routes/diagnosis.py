from flask import Blueprint

from controllers import diagnosis_controller

diagnosis_bp = Blueprint("diagnosis", __name__, url_prefix="/api/diagnosis")


@diagnosis_bp.get("/search")
def search_library():
    """Search the diagnosis suggestion (ICD-style) library
    ---
    tags: [Diagnosis]
    parameters:
      - name: q
        in: query
        type: string
        description: Search text (diagnosis name or ICD code); empty returns top entries
    responses:
      200:
        description: List of matching diagnoses {code, diagnosis, description, specialty}
    """
    return diagnosis_controller.search_library()
