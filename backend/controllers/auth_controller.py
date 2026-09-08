from flask import jsonify, request, session

from database import db
from models.user import User


def _current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def login():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials",
                        "message": "Invalid username or password."}), 401
    session.clear()
    session["user_id"] = user.id
    session["role"] = user.role
    session.permanent = True
    return jsonify(user.to_dict())


def logout():
    session.clear()
    return jsonify({"success": True})


def me():
    user = _current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401
    return jsonify(user.to_dict())
