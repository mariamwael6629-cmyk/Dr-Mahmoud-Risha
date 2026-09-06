import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config, DATABASE_DIR, UPLOADS_DIR, STATIC_ROOT
from database import db
import models  # noqa: F401
from database.migrate import run_migrations
from database.seed import seed_if_empty
from routes import register_blueprints
from security import init_auth


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    app.json.ensure_ascii = False

    CORS(app, supports_credentials=True)
    init_auth(app)
    db.init_app(app)
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
