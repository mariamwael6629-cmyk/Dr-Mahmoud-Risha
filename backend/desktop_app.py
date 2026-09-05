"""Desktop launcher for the Dr Mahmoud Risha Clinic system.

Goals (what the user asked for):
  * One click -> the app opens, no black console window, no dialogs.
  * No Windows Firewall permission prompt (we bind to 127.0.0.1 only, so
    Windows never asks to allow the app on the network).
  * Opens as a clean app window (Edge/Chrome "app mode"), not a browser tab.
  * When that window is closed, everything shuts down cleanly.
  * Nothing to install: when built as a single .exe, Python and every
    library are already inside it.
"""

import os
import sys
import time
import socket
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"

WINDOW_TITLE = "Dr Mahmoud Risha Clinic"


def _port_is_open(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _wait_until_up(timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        if _port_is_open(HOST, PORT):
            return True
        time.sleep(0.3)
    return False


def _serve():
    """Run the web server quietly in a background thread."""
    from app import app

    # Silence the noisy Werkzeug/dev-server logging so nothing prints.
    import logging
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    try:
        # waitress is a small, stable production server (no dev-server warning).
        from waitress import serve
        serve(app, host=HOST, port=PORT, threads=8, _quiet=True)
    except Exception:
        # Fallback to Flask's built-in server if waitress isn't available.
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def _find_app_browser():
    """Return the path to Edge or Chrome, which support chromeless app mode."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _profile_dir():
    """A private browser profile so the window is its own process we can wait on."""
    try:
        from config import DATA_DIR
        base = DATA_DIR
    except Exception:
        base = BASE_DIR
    path = os.path.join(base, "browser")
    os.makedirs(path, exist_ok=True)
    return path


def _open_app_window():
    """Open a clean, chromeless app window. Returns the process, or None."""
    import subprocess

    browser = _find_app_browser()
    if not browser:
        return None

    args = [
        browser,
        f"--app={URL}",
        f"--user-data-dir={_profile_dir()}",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1280,860",
    ]
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        return subprocess.Popen(args, creationflags=creationflags)
    except Exception:
        return None


def main():
    already_running = _port_is_open(HOST, PORT)

    if not already_running:
        threading.Thread(target=_serve, daemon=True).start()
        if not _wait_until_up():
            # Server never came up; open whatever browser we can and give up.
            import webbrowser
            webbrowser.open(URL)
            return

    proc = _open_app_window()

    if proc is not None:
        # Wait until the doctor closes the app window, then exit so the
        # background server thread is torn down with the process.
        try:
            proc.wait()
        except KeyboardInterrupt:
            pass
        return

    # No Edge/Chrome found: fall back to the default browser. In this case we
    # keep the server alive because we can't tell when the tab is closed.
    import webbrowser
    webbrowser.open(URL)
    if not already_running:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
