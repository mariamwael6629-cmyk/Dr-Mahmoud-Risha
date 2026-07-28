from flask import Blueprint

from controllers import report_controller

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.get("/visits-per-day")
def visits_per_day():
    """Daily visit counts for the last N days
    ---
    tags: [Reports]
    parameters:
      - name: days
        in: query
        type: integer
    responses:
      200:
        description: List of {date, visits}
    """
    return report_controller.visits_per_day()


@reports_bp.get("/patient-summary")
def patient_summary():
    """Patient/appointment totals
    ---
    tags: [Reports]
    responses:
      200:
        description: Totals summary
    """
    return report_controller.patient_summary()


@reports_bp.get("/visit-types")
def visit_type_breakdown():
    """Appointment counts grouped by visit type
    ---
    tags: [Reports]
    responses:
      200:
        description: List of {visitType, count}
    """
    return report_controller.visit_type_breakdown()


@reports_bp.get("/queue-snapshot")
def queue_snapshot():
    """Today's queue status counts
    ---
    tags: [Reports]
    responses:
      200:
        description: Counts by status
    """
    return report_controller.queue_snapshot()


@reports_bp.get("/revenue-by-status")
def revenue_by_status():
    """Billed amount grouped by invoice status
    ---
    tags: [Reports]
    responses:
      200:
        description: Amounts by status
    """
    return report_controller.revenue_by_status()


@reports_bp.get("/monthly")
def monthly_report():
    """Monthly clinic report (visits, follow-ups, money collected, outstanding)
    ---
    tags: [Reports]
    parameters:
      - name: year
        in: query
        type: integer
      - name: month
        in: query
        type: integer
    responses:
      200:
        description: Monthly summary
    """
    return report_controller.monthly_report()
