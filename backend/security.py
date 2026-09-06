"""Server-side authentication for the clinic API.

The whole `/api/*` surface (patient records, invoices, the full data backup)
is protected behind a login session. The frontend and its static assets stay
public so the sign-in page can load; everything with real data does not.
"""

from flask import request, session, jsonify
from werkzeug.security import check_password_hash

from config import AUTH_USERNAME, AUTH_PASSWORD_HASH

# API paths reachable without an authenticated session.
_PUBLIC_API_PATHS = {
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
}


def check_credentials(username, password):
    return (
        (username or "") == AUTH_USERNAME
        and check_password_hash(AUTH_PASSWORD_HASH, password or "")
    )


def is_authenticated():
    return bool(session.get("authenticated"))


def init_auth(app):
    @app.before_request
    def _guard():
        path = request.path or ""
        # Only guard the API; the frontend/static files stay public.
        if not path.startswith("/api/"):
            return None
        if path in _PUBLIC_API_PATHS:
            return None
        if request.method == "OPTIONS":  # CORS preflight
            return None
        if is_authenticated():
            return None
        return jsonify({"error": "authentication_required"}), 401
