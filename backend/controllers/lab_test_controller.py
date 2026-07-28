from flask import jsonify, request

from services import lab_test_service

def search_library():
    query = request.args.get("q", "").strip()
    results = lab_test_service.search_lab_test_library(query)
    return jsonify([r.to_dict() for r in results])
