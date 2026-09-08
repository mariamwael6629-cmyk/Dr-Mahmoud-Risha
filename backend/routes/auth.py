from flask import Blueprint

from controllers import auth_controller

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """Authenticate a user and start a session.
    ---
    tags: [Auth]
    responses:
      200: {description: Logged in, returns the user}
      401: {description: Invalid credentials}
    """
    return auth_controller.login()


@auth_bp.post("/logout")
def logout():
    """End the current session.
    ---
    tags: [Auth]
    responses:
      200: {description: Logged out}
    """
    return auth_controller.logout()


@auth_bp.get("/me")
def me():
    """Return the currently authenticated user.
    ---
    tags: [Auth]
    responses:
      200: {description: The current user}
      401: {description: Not authenticated}
    """
    return auth_controller.me()
