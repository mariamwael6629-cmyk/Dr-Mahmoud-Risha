from datetime import date

from database import db
from models.medication import MedicationLibrary, MedicationRecord

                                                                            

def list_medication_records(search=None):
    query = MedicationRecord.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                MedicationRecord.name.ilike(like),
                MedicationRecord.company.ilike(like),
                MedicationRecord.generic_name.ilike(like),
                MedicationRecord.category.ilike(like),
                MedicationRecord.dosage.ilike(like),
            )
        )
    return query.order_by(MedicationRecord.id.desc()).all()

def create_medication_record(data):
    record = MedicationRecord(
        name=data["name"],
        company=data.get("company"),
        purpose=data.get("purpose"),
        date_added=data.get("date") or date.today().isoformat(),
        generic_name=data.get("genericName"),
        category=data.get("category"),
        dosage=data.get("dosage"),
    )
    db.session.add(record)
    db.session.commit()
    return record

def get_medication_record(record_id):
    return MedicationRecord.query.get(record_id)

def delete_medication_record(record):
    db.session.delete(record)
    db.session.commit()

                                                      

def get_or_create_library_entry(data):
    drug_name = (data.get("drugName") or "").strip()
    existing = MedicationLibrary.query.filter(
        db.func.lower(MedicationLibrary.drug_name) == drug_name.lower()
    ).first()
    if existing:
        return existing, False
    entry = MedicationLibrary(
        drug_name=drug_name,
        generic_name=data.get("genericName") or None,
        dosage=data.get("dosage") or None,
        category=data.get("category") or None,
        notes=data.get("notes") or None,
    )
    db.session.add(entry)
    db.session.commit()
    return entry, True

def search_medication_library(query, limit=20):
    if not query:
        return MedicationLibrary.query.order_by(MedicationLibrary.drug_name).limit(limit).all()
    like = f"%{query}%"
    return (
        MedicationLibrary.query.filter(
            db.or_(
                MedicationLibrary.drug_name.ilike(like),
                MedicationLibrary.generic_name.ilike(like),
                MedicationLibrary.category.ilike(like),
            )
        )
        .order_by(MedicationLibrary.drug_name)
        .limit(limit)
        .all()
    )
