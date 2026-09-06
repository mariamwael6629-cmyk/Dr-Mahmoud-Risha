from routes.auth import auth_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.diagnosis import diagnosis_bp
from routes.medications import medications_bp
from routes.lab_tests import lab_tests_bp
from routes.radiology import radiology_bp
from routes.files import files_bp
from routes.prescriptions import prescriptions_bp
from routes.settings import settings_bp
from routes.availability import availability_bp
from routes.financial import financial_bp
from routes.reports import reports_bp

ALL_BLUEPRINTS = (
    auth_bp,
    patients_bp,
    appointments_bp,
    diagnosis_bp,
    medications_bp,
    lab_tests_bp,
    radiology_bp,
    files_bp,
    prescriptions_bp,
    settings_bp,
    availability_bp,
    financial_bp,
    reports_bp,
)


def register_blueprints(app):
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
