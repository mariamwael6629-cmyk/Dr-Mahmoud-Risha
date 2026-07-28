from database import db
from models.lab_radiology import RadiologyLibrary

def search_radiology_library(query, limit=20):
    if not query:
        return RadiologyLibrary.query.order_by(RadiologyLibrary.exam_name).limit(limit).all()
    like = f"%{query}%"
    return (
        RadiologyLibrary.query.filter(
            db.or_(RadiologyLibrary.exam_name.ilike(like), RadiologyLibrary.code.ilike(like))
        )
        .order_by(RadiologyLibrary.exam_name)
        .limit(limit)
        .all()
    )
