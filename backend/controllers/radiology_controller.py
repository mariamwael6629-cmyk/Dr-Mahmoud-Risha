from flask import jsonify, request

from services import radiology_service

def search_library():
    query = request.args.get("q", "").strip()
    results = radiology_service.search_radiology_library(query)
    return jsonify([r.to_dict() for r in results])
