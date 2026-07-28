from flask import jsonify, request

from services import diagnosis_service

def search_library():
    query = request.args.get("q", "").strip()
    results = diagnosis_service.search_diagnosis_library(query)
    return jsonify([r.to_dict() for r in results])
