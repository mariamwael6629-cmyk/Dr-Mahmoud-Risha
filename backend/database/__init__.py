"""Database package: hosts the SQLAlchemy instance and the clinic.db file at runtime."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
