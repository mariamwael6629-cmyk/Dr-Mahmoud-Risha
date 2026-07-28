from flask import Blueprint

from controllers import lab_test_controller

lab_tests_bp = Blueprint("lab_tests", __name__, url_prefix="/api/lab-tests")


@lab_tests_bp.get("/search")
def search_library():
    """Search the lab test suggestion library
    ---
    tags: [LabTests]
    parameters:
      - name: q
        in: query
        type: string
        description: Search text (test name or code); empty returns top entries
    responses:
      200:
        description: List of matching lab tests {code, testName, description, category}
    """
    return lab_test_controller.search_library()
