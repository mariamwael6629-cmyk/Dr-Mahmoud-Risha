import os
import uuid

from werkzeug.utils import secure_filename

from config import ALLOWED_FILE_EXTENSIONS, UPLOADS_DIR
from database import db
from models.file import UploadedFile

class InvalidFileError(Exception):
    pass

def _extension(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

def allowed_file(filename):
    return _extension(filename) in ALLOWED_FILE_EXTENSIONS

                                                                                
                                                                              
_MAGIC_SIGNATURES = {
    "pdf": (b"%PDF",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
}

def _matches_signature(file_storage, ext):
    header = file_storage.stream.read(8)
    file_storage.stream.seek(0)
    return any(header.startswith(sig) for sig in _MAGIC_SIGNATURES.get(ext, ()))

def save_uploaded_file(file_storage, patient_id, appointment_id=None, category="other"):
    original_name = file_storage.filename or ""
    if not original_name or not allowed_file(original_name):
        raise InvalidFileError("Only PDF, PNG, JPG and JPEG files are allowed.")

    ext = _extension(original_name)
    if not _matches_signature(file_storage, ext):
        raise InvalidFileError("File content does not match its extension.")
    safe_name = secure_filename(original_name) or f"file.{ext}"
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"

    patient_dir = os.path.join(UPLOADS_DIR, str(patient_id))
    os.makedirs(patient_dir, exist_ok=True)
    disk_path = os.path.join(patient_dir, stored_name)
    file_storage.save(disk_path)

    relative_path = os.path.join(str(patient_id), stored_name)
    record = UploadedFile(
        patient_id=patient_id,
        appointment_id=appointment_id,
        category=category,
        file_name=stored_name,
        original_name=original_name,
        file_path=relative_path,
        file_type=ext,
    )
    db.session.add(record)
    db.session.commit()
    return record

def get_file(file_id):
    return UploadedFile.query.get(file_id)

def list_files_for_patient(patient_id):
    return (
        UploadedFile.query.filter_by(patient_id=patient_id)
        .order_by(UploadedFile.upload_date.desc())
        .all()
    )

def list_files_for_appointment(appointment_id):
    return (
        UploadedFile.query.filter_by(appointment_id=appointment_id)
        .order_by(UploadedFile.upload_date.desc())
        .all()
    )

def delete_file(record):
    disk_path = os.path.join(UPLOADS_DIR, record.file_path)
    if os.path.exists(disk_path):
        os.remove(disk_path)
    db.session.delete(record)
    db.session.commit()

def absolute_path(record):
    return os.path.join(UPLOADS_DIR, record.file_path)
