from flask import jsonify, request

from services import report_service

def visits_per_day():
    days = int(request.args.get("days", 14))
    return jsonify(report_service.visits_per_day(days=days))

def patient_summary():
    return jsonify(report_service.patient_summary())

def visit_type_breakdown():
    return jsonify(report_service.visit_type_breakdown())

def queue_snapshot():
    return jsonify(report_service.queue_snapshot())

def revenue_by_status():
    return jsonify(report_service.revenue_by_status())

def monthly_report():
    year = request.args.get("year") or None
    month = request.args.get("month") or None
    return jsonify(report_service.monthly_report(year=year, month=month))
