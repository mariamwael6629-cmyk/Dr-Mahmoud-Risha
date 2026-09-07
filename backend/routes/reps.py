from flask import Blueprint

from controllers import rep_controller

reps_bp = Blueprint("reps", __name__, url_prefix="/api/reps")


@reps_bp.get("")
def list_reps():
    return rep_controller.list_reps()


@reps_bp.post("")
def create_rep():
    return rep_controller.create_rep()


@reps_bp.delete("/<int:rep_id>")
def delete_rep(rep_id):
    return rep_controller.delete_rep(rep_id)
