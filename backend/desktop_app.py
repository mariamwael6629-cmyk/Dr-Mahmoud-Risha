"""Desktop launcher for the Dr Mahmoud Risha Clinic system.

One .exe, three simple behaviours decided by small text files placed next to
the .exe (no code changes needed by the user):

  * Default (no marker files) -> single machine. The server listens only on
    127.0.0.1, so there is NO Windows Firewall prompt. Opens a clean app
    window; closing it shuts everything down.

  * A file named ``SHARE-ON-NETWORK.txt`` next to the .exe -> this is the
    MAIN (doctor's) PC. The server also listens on the local network so other
    PCs in the clinic can share the same patient data. On first run Windows
    asks once to allow it through the firewall (we also try to add the rule
    automatically). The PC's network address is written to
    ``THIS-PC-ADDRESS.txt`` so you know what to type on the nurse's PC.

  * A file named ``CONNECT-TO.txt`` containing the main PC's address
    (e.g. ``192.168.1.20``) -> this is a CLIENT (nurse's) PC. It does NOT run
    a server; it just opens a clean window showing the main PC's data.
"""

import os
import sys
import time
import socket
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PORT = 5000
DISCOVERY_PORT = 5001
DISCOVERY_REQUEST = b"DR-RISHA-CLINIC-DISCOVERY?"
DISCOVERY_REPLY = b"DR-RISHA-CLINIC:"
WINDOW_TITLE = "Dr Mahmoud Risha Clinic"


def _app_dir():
    """Folder that holds the .exe (or this script when running from source)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return BASE_DIR


def _read_marker(name):
    """Return the trimmed contents of a marker file next to the exe, or None."""
    path = os.path.join(_app_dir(), name)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            return fh.read().strip()
    except Exception:
        return ""


def _port_is_open(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _wait_until_up(host, timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        if _port_is_open(host, PORT):
            return True
        time.sleep(0.3)
    return False


def _lan_ip():
    """Best-effort local network IP of this PC."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))  # no data is actually sent
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def _add_firewall_rule():
    """Best-effort: allow inbound TCP 5000 (web) and UDP 5001 (auto-discovery)
    so LAN clients can find and connect to this PC."""
    if os.name != "nt":
        return
    import subprocess
    rules = [
        ["name=Dr Risha Clinic", "protocol=TCP", "localport=%d" % PORT],
        ["name=Dr Risha Clinic Discovery", "protocol=UDP",
         "localport=%d" % DISCOVERY_PORT],
    ]
    for extra in rules:
        cmd = ["netsh", "advfirewall", "firewall", "add", "rule",
               "dir=in", "action=allow"] + extra
        try:
            subprocess.run(
                cmd,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=10,
            )
        except Exception:
            pass  # Not admin: Windows shows its own one-time allow prompt.


def _discovery_responder():
    """On the main PC: answer LAN 'where is the clinic server?' broadcasts."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", DISCOVERY_PORT))
    except Exception:
        return
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if data.strip() == DISCOVERY_REQUEST:
                s.sendto(DISCOVERY_REPLY + _lan_ip().encode("utf-8"), addr)
        except Exception:
            time.sleep(0.5)


def _discover_server(timeout=6):
    """On the nurse's PC: find the main PC automatically on the LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(1.0)
    except Exception:
        return None
    end = time.time() + timeout
    try:
        while time.time() < end:
            try:
                s.sendto(DISCOVERY_REQUEST, ("255.255.255.255", DISCOVERY_PORT))
                data, _addr = s.recvfrom(1024)
                if data.startswith(DISCOVERY_REPLY):
                    return data[len(DISCOVERY_REPLY):].decode("utf-8").strip()
            except socket.timeout:
                continue
            except Exception:
                break
    finally:
        s.close()
    return None


def _serve(host):
    """Run the web server quietly in a background thread."""
    from app import app

    import logging
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    try:
        from waitress import serve
        serve(app, host=host, port=PORT, threads=8, _quiet=True)
    except Exception:
        app.run(host=host, port=PORT, debug=False, use_reloader=False)


def _find_app_browser():
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
    path = os.path.join(_app_dir(), "browser")
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        path = os.path.join(os.path.expanduser("~"), ".dr_risha_browser")
        os.makedirs(path, exist_ok=True)
    return path


def _open_app_window(url):
    """Open a clean, chromeless app window. Returns the process, or None."""
    import subprocess

    browser = _find_app_browser()
    if not browser:
        return None

    args = [
        browser,
        "--app=%s" % url,
        "--user-data-dir=%s" % _profile_dir(),
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1280,860",
    ]
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    try:
        return subprocess.Popen(args, creationflags=creationflags)
    except Exception:
        return None


def _message_box(text, title=WINDOW_TITLE):
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)  # info icon
            return
        except Exception:
            pass
    sys.stderr.write(text + "\n")


def _run_window_and_wait(url, keep_alive_if_no_browser):
    """Open the app window and block until it is closed."""
    proc = _open_app_window(url)
    if proc is not None:
        try:
            proc.wait()
        except KeyboardInterrupt:
            pass
        return

    import webbrowser
    webbrowser.open(url)
    if keep_alive_if_no_browser:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


def _run_client(server_addr):
    """Nurse's PC: connect to the main PC, no local server."""
    # Use the first non-empty, non-comment line of CONNECT-TO.txt.
    host = ""
    for line in server_addr.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            host = line
            break

    # "AUTO" (or an unfilled placeholder) -> find the main PC automatically.
    if host == "" or host.upper() == "AUTO" or host.upper().startswith("PUT-"):
        found = _discover_server()
        if not found:
            _message_box(
                "Could not find the doctor's PC on the network.\n\n"
                "Make sure the doctor's computer is turned on, the clinic app "
                "is open on it, and both PCs are on the same Wi-Fi / network."
            )
            return
        host = found
    else:
        host = host.replace("http://", "").replace("https://", "")
        host = host.split("/")[0].split(":")[0].strip()

    url = "http://%s:%d" % (host, PORT)

    if not _port_is_open(host, PORT, timeout=3):
        _message_box(
            "Could not reach the main clinic PC at:\n\n    %s\n\n"
            "Make sure the doctor's computer is turned on and the clinic app "
            "is open on it, and that both PCs are on the same network."
            % host
        )
        return
    _run_window_and_wait(url, keep_alive_if_no_browser=True)


def _run_server(share_on_network):
    host = "0.0.0.0" if share_on_network else "127.0.0.1"

    already_running = _port_is_open("127.0.0.1", PORT)
    if not already_running:
        if share_on_network:
            _add_firewall_rule()
            try:
                with open(os.path.join(_app_dir(), "THIS-PC-ADDRESS.txt"), "w",
                          encoding="utf-8") as fh:
                    fh.write(
                        "On the nurse's PC, put this address inside CONNECT-TO.txt:\n\n"
                        "    %s\n\n(The nurse's PC and this PC must be on the "
                        "same network / Wi-Fi.)\n" % _lan_ip()
                    )
            except Exception:
                pass

        if share_on_network:
            threading.Thread(target=_discovery_responder, daemon=True).start()

        threading.Thread(target=_serve, args=(host,), daemon=True).start()
        if not _wait_until_up("127.0.0.1"):
            import webbrowser
            webbrowser.open("http://127.0.0.1:%d" % PORT)
            return

    _run_window_and_wait("http://127.0.0.1:%d" % PORT,
                         keep_alive_if_no_browser=not already_running)


def main():
    connect_to = _read_marker("CONNECT-TO.txt")
    if connect_to:
        _run_client(connect_to)
        return

    share = _read_marker("SHARE-ON-NETWORK.txt") is not None
    _run_server(share_on_network=share)


if __name__ == "__main__":
    main()
