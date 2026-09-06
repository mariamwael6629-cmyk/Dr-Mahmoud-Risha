from flask import Blueprint, request, session, jsonify

from security import check_credentials, is_authenticated
from config import AUTH_USERNAME

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if check_credentials(username, password):
        session.permanent = True
        session["authenticated"] = True
        session["username"] = username
        return jsonify({"authenticated": True, "username": username})
    return jsonify({"authenticated": False, "error": "invalid_credentials"}), 401


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@auth_bp.get("/me")
def me():
    if is_authenticated():
        return jsonify({"authenticated": True, "username": session.get("username")})
    return jsonify({"authenticated": False})
