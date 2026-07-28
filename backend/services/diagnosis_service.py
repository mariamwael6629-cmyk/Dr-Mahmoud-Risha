from database import db
from models.diagnosis import DiagnosisLibrary

def search_diagnosis_library(query, limit=20):
    if not query:
        return DiagnosisLibrary.query.order_by(DiagnosisLibrary.diagnosis).limit(limit).all()
    like = f"%{query}%"
    return (
        DiagnosisLibrary.query.filter(
            db.or_(DiagnosisLibrary.diagnosis.ilike(like), DiagnosisLibrary.code.ilike(like))
        )
        .order_by(DiagnosisLibrary.diagnosis)
        .limit(limit)
        .all()
    )
