import json

from flask import jsonify, request

from services import settings_service

def get_branding():
    settings = settings_service.get_branding()
    if not settings:
        return jsonify({"error": "Clinic settings not initialized"}), 404
    return jsonify(settings.to_dict())

def update_branding():
    data = request.get_json(force=True) or {}
    settings = settings_service.update_branding(data)
    if not settings:
        return jsonify({"error": "Clinic settings not initialized"}), 404
    return jsonify(settings.to_dict())

def get_backup():
    return jsonify(settings_service.export_backup())

def import_data():
    data = None
    if "file" in request.files:
        try:
            data = json.load(request.files["file"])
        except (ValueError, UnicodeError) as exc:
            return jsonify({"error": f"Invalid backup file: {exc}"}), 400
    else:
        data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON backup object is required"}), 400
    counts = settings_service.import_backup(data)
    return jsonify({"imported": counts})
