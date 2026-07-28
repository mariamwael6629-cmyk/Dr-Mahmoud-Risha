import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)

DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "clinic.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

ALLOWED_FILE_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB per upload


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOADS_DIR
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    JSON_AS_ASCII = False
    SWAGGER = {
        "title": "Clinic Management API",
        "uiversion": 3,
        "specs_route": "/apidocs/",
    }
