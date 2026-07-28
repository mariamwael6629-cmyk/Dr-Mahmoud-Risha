from flask import Blueprint

from controllers import radiology_controller

radiology_bp = Blueprint("radiology", __name__, url_prefix="/api/radiology")


@radiology_bp.get("/search")
def search_library():
    """Search the radiology/imaging suggestion library
    ---
    tags: [Radiology]
    parameters:
      - name: q
        in: query
        type: string
        description: Search text (exam name or code); empty returns top entries
    responses:
      200:
        description: List of matching radiology exams {code, examName, description, category}
    """
    return radiology_controller.search_library()
