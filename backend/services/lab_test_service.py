from database import db
from models.lab_radiology import LabTestLibrary

def search_lab_test_library(query, limit=20):
    if not query:
        return LabTestLibrary.query.order_by(LabTestLibrary.test_name).limit(limit).all()
    like = f"%{query}%"
    return (
        LabTestLibrary.query.filter(
            db.or_(LabTestLibrary.test_name.ilike(like), LabTestLibrary.code.ilike(like))
        )
        .order_by(LabTestLibrary.test_name)
        .limit(limit)
        .all()
    )
