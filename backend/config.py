import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)

if getattr(sys, "frozen", False):
    STATIC_ROOT = sys._MEIPASS
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "ClinicData")
else:
    STATIC_ROOT = REPO_ROOT
    DATA_DIR = BASE_DIR

DATABASE_DIR = os.path.join(DATA_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "clinic.db")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

ALLOWED_FILE_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024


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
