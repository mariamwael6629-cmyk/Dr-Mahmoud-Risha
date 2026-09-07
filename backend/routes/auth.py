from flask import Blueprint, request, session, jsonify

from security import resolve_role, is_authenticated, current_role

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = resolve_role(username, password)
    if role:
        session.permanent = True
        session["authenticated"] = True
        session["username"] = username
        session["role"] = role
        return jsonify({"authenticated": True, "username": username, "role": role})
    return jsonify({"authenticated": False, "error": "invalid_credentials"}), 401


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@auth_bp.get("/me")
def me():
    if is_authenticated():
        return jsonify({"authenticated": True, "username": session.get("username"), "role": current_role()})
    return jsonify({"authenticated": False})
