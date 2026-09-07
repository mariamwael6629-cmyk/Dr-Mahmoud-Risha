from flask import jsonify, request

from database import db
from models.rep import MedicalRep


def list_reps():
    rows = MedicalRep.query.order_by(MedicalRep.id.desc()).all()
    return jsonify([r.to_dict() for r in rows])


def create_rep():
    data = request.get_json(force=True) or {}
    company = (data.get("company") or "").strip()
    drug = (data.get("drug") or "").strip()
    phone = (data.get("phone") or "").strip()
    if not company and not drug and not phone and not (data.get("name") or "").strip():
        return jsonify({"error": "At least one field is required"}), 400
    rep = MedicalRep(
        name=(data.get("name") or "").strip() or None,
        phone=phone or None,
        company=company or None,
        drug=drug or None,
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(rep)
    db.session.commit()
    return jsonify(rep.to_dict()), 201


def delete_rep(rep_id):
    rep = MedicalRep.query.get(rep_id)
    if not rep:
        return jsonify({"error": "Rep not found"}), 404
    db.session.delete(rep)
    db.session.commit()
    return jsonify({"success": True})
