import os
import sys
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS

from config import Config, DATABASE_DIR, UPLOADS_DIR, STATIC_ROOT
from database import db
import models  # noqa: F401
from database.migrate import run_migrations
from database.seed import seed_if_empty
import permissions
from routes import register_blueprints


def _load_secret_key():
    """Stable session secret. Prefer CLINIC_SECRET_KEY; otherwise persist a
    generated one next to the database so sessions survive restarts on the
    clinic PC without any manual setup."""
    env = os.environ.get("CLINIC_SECRET_KEY")
    if env:
        return env
    os.makedirs(DATABASE_DIR, exist_ok=True)
    key_path = os.path.join(DATABASE_DIR, "secret_key")
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    key = os.urandom(32).hex()
    with open(key_path, "w", encoding="utf-8") as fh:
        fh.write(key)
    return key


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    app.json.ensure_ascii = False

    app.secret_key = _load_secret_key()
    app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # CORS must allow credentials so the session cookie is honoured by browsers.
    CORS(app, supports_credentials=True)
    db.init_app(app)

    @app.before_request
    def _enforce_auth():
        path = request.path
        # Only guard the JSON API; static files and the SPA shell are public.
        if not path.startswith("/api/"):
            return None
        if request.method == "OPTIONS" or permissions.is_public(path):
            return None
        role = session.get("role")
        if not role:
            return jsonify({"error": "not_authenticated",
                            "message": "Authentication required."}), 401
        if permissions.forbidden_for_role(role, request.method, path):
            return jsonify({"error": "forbidden",
                            "message": "Your role is not permitted to perform this action."}), 403
        return None
    if not getattr(sys, "frozen", False):
        from flasgger import Swagger
        Swagger(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
        run_migrations()
        seed_if_empty()

    @app.get("/")
    def serve_index():
        return send_from_directory(STATIC_ROOT, "index.html")

    @app.get("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(STATIC_ROOT, "assets"), filename)

    @app.get("/Images/<path:filename>")
    def serve_images(filename):
        return send_from_directory(os.path.join(STATIC_ROOT, "Images"), filename)

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(_err):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug)
