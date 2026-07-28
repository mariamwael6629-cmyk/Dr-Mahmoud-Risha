"""
Clinic Management System - Backend entry point.

Serves the JSON API under /api/* and (for same-origin LAN access) the
existing static frontend (index.html, Images/, assets/) unchanged.
Run with:  python app.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger

from config import Config, DATABASE_DIR, UPLOADS_DIR
from database import db
import models  # noqa: F401 - register models for create_all()
from database.migrate import run_migrations
from database.seed import seed_if_empty
from routes import register_blueprints


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    app.json.ensure_ascii = False  # JSON_AS_ASCII config key was removed in Flask 2.3+

    CORS(app)
    db.init_app(app)
    Swagger(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
        run_migrations()  # NEW FEATURE: add any newly-introduced columns to existing tables
        seed_if_empty()

    # --- NEW FEATURE: serve the existing static frontend for same-origin LAN access ---
    @app.get("/")
    def serve_index():
        return send_from_directory(REPO_ROOT, "index.html")

    @app.get("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(REPO_ROOT, "assets"), filename)

    @app.get("/Images/<path:filename>")
    def serve_images(filename):
        return send_from_directory(os.path.join(REPO_ROOT, "Images"), filename)

    # --- FIX: JSON error responses instead of Flask's default HTML error pages,
    # so the frontend's fetch-based API client always gets parseable JSON ---
    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(_err):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    # FIX: debug mode enables Werkzeug's interactive debugger (remote code
    # execution if reachable on an unhandled exception); this app is served
    # on the clinic LAN by design, so default debug to off.
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug)
