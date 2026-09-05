# 🏥 Dr Mahmoud Risha Rheumatology Clinic — Patient Management System

A full-stack Patient Management System for the clinic, with patient records,
appointments, file uploads (X-Ray/test results), a diagnosis/medication
autocomplete, and a pixel-faithful bilingual (English/Arabic) prescription
generator matching the clinic's real letterhead.

---

## ✨ Key Features

- **📊 Comprehensive Dashboard:** Instantly view clinic statistics including total patients, appointments, medications, and inventory metrics at a glance.
- **👤 Patient Onboarding & Records:** Manage full patient profiles including secure IDs, mobile/emergency contact numbers, medical history (previous operations/treatments), symptoms, family background, and free-text notes.
- **📅 Dynamic Appointment Tracking:** Log and update appointments with integrated fields for diagnosis, required tests, lab/X-ray results, and custom physician notes.
- **📎 File Uploads:** Attach PDF/PNG/JPG test results and X-ray images to a patient or a specific appointment.
- **🔎 Smart Autocomplete:** Diagnosis and medication name fields suggest matches as you type, backed by a searchable library in the database.
- **💊 Medication Database:** A dedicated panel to add, view, and organize available drugs, active ingredients, and specific usage notes.
- **📋 Smart Prescription Generator:** Automatically generates a high-fidelity, printable bilingual prescription matching the clinic's real paper letterhead (Dr Mahmoud Risha — Rheumatology Clinic).
- **📦 Clinic Inventory Management:** Real-time stock tracking for clinic supplies with automated status indicators (In Stock, Low Stock, Out of Stock).

---

## 🛠️ Tech Stack

- **Frontend:** Single-file vanilla JS/HTML/CSS app (`index.html`) — no build step, no framework. Tailwind is loaded via CDN for utility classes; most UI is hand-rolled CSS.
- **Backend:** Python, Flask + Flask-SQLAlchemy, SQLite (file-based DB, no separate DB server to install). Layered as `models/` → `services/` → `controllers/` → `routes/` (Blueprints), assembled in `backend/app.py`.
- **API docs:** Auto-generated interactive Swagger UI (via `flasgger`) at `/apidocs` once the backend is running — every endpoint is documented there, including request/response schemas.
- **LAN/offline mode:** Flask serves both the API (`/api/*`) and the static frontend (`/`, `/assets/*`, `/Images/*`) from the same process, so any device on the clinic's LAN can use the system by pointing a browser at the host machine's IP — no internet connection required.

---

## 🖱️ One-click desktop app (recommended for the clinic PC)

For the doctor's computer you do **not** need to install Python or run any
commands. A single Windows program does everything:

1. Open the **Releases** page of this repository and download
   **`Dr-Risha-Clinic.exe`** (built automatically by the *Build Windows EXE*
   GitHub Action).
2. Put it on the Desktop (or right-click → *Send to → Desktop* to make a
   shortcut with the clinic logo).
3. Double-click it. The clinic system opens in its own clean window.
4. Close the window when finished — the server shuts down with it.

There is no console window, no Python install, no package installation, and
no Windows Firewall permission prompt (the app talks only to itself on
`127.0.0.1`). Patient data is stored in a `ClinicData` folder created next to
the `.exe`, so keep the program in a fixed location (e.g. its own folder on
the Desktop).

> First launch only: because the file is not code-signed, Windows may show a
> blue *"Windows protected your PC"* screen. Click **More info → Run anyway**
> once; it will not appear again on that PC.

### 🖧 Sharing data with a second PC (nurse's desk)

The doctor's PC holds the data; the nurse's PC views the same records over the
clinic's local network (Wi-Fi/LAN). Two tiny text files (shipped with the
release) control which PC is which:

**On the doctor's (main) PC**

1. Put `SHARE-ON-NETWORK.txt` in the **same folder** as `Dr-Risha-Clinic.exe`.
2. Run the app. The first time, Windows asks once to allow it through the
   firewall — click **Allow access**.
3. A file `THIS-PC-ADDRESS.txt` appears next to the .exe with this PC's
   address, e.g. `192.168.1.20`. Note it down.

**On the nurse's PC**

1. Copy `Dr-Risha-Clinic.exe` and `CONNECT-TO.txt` into a folder.
2. Open `CONNECT-TO.txt` and replace the placeholder line with the doctor PC's
   address (e.g. `192.168.1.20`). Save.
3. Double-click the .exe — it opens the **same** clinic data in a clean window.
   (It does not run its own server; it just connects to the doctor's PC.)

Both PCs must be on the same network, and the doctor's PC must be on with the
app open for the nurse's PC to connect.

---

## 🚀 Installation & Local Setup (developers)

### Requirements

- Python 3.9+
- A modern browser (Chrome/Edge/Firefox/Safari)

### 1. Clone the repository

```bash
git clone https://github.com/mariamwael6629-cmyk/Full-Stack-Patient-Management-System.git
cd Full-Stack-Patient-Management-System
```

### 2. Set up and run the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

The first run creates `backend/database/clinic.db` automatically and seeds it
with the diagnosis/medication autocomplete libraries and the clinic's
branding settings (see [Test/seed data](#-testseed-data) below).

### 3. Open the app

- App (frontend + API, same origin): **http://127.0.0.1:5000/**
- Interactive API docs (Swagger UI): **http://127.0.0.1:5000/apidocs**

Sign in with username `admin` / password `123` (placeholder credentials —
see `index.html`'s sign-in handler if you need to change them).

### 4. Use it from another device on the same LAN

Find the host machine's local IP (e.g. `192.168.1.20`), make sure port 5000
is reachable on the LAN, then browse to `http://192.168.1.20:5000/` from any
other device — secretary desk, doctor's room, etc. No internet access is
required since both the API and the static frontend are served locally.

### 5. Run automatically in the background (Windows)

`backend/run_silent.vbs` launches the server with the venv's `pythonw.exe`
(no console window). Add it to Windows Task Scheduler with an "At log on"
trigger so the server starts automatically every time the host PC boots,
instead of opening a terminal and running `python3 app.py` manually.
`backend/stop_server.bat` stops whatever process is listening on port 5000,
for the rare case you need to restart it by hand.

### 6. Desktop shortcut with the doctor's name/icon (Windows)

Create a normal Windows shortcut whose target is your browser with the URL
as an argument (e.g. `"C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://127.0.0.1:5000/`),
rename it to the clinic/doctor's name, then set its icon to
`assets/rx-logo.ico` (already included in this repo) via the shortcut's
Properties → Change Icon.

### 7. Hourly backups to a USB flash drive (Windows)

`backend/backup_to_usb.bat` copies `backend\database\clinic.db` and
`backend\uploads\` into a timestamped folder (`ClinicBackups\YYYY-MM-DD_HH-MM-SS\`)
on the first USB flash drive it finds. If no flash drive is plugged in when
it runs, it just logs that to `backend\backup_log.txt` and exits cleanly —
it never throws an error popup, so it's safe to trigger automatically on a
schedule whether or not the drive happens to be connected at that moment.
Backups older than 7 days on the drive are pruned automatically so it
doesn't fill up over time.

**Test it manually first:** plug in the flash drive and double-click
`backend\backup_now.bat` — it runs one backup and prints the result on
screen (and the last few lines of the log).

**Schedule it hourly:**

1. Open **Task Scheduler** → *Create Task…* (not *Basic Task*, so you get
   the repeat-interval option).
2. **General** tab: name it e.g. `Clinic USB Backup`, and check
   *Run whether user is logged on or not*.
3. **Triggers** tab → *New…* → trigger type *Daily*, start at any time today,
   then check *Repeat task every* → **1 hour**, *for a duration of* →
   **Indefinitely**.
4. **Actions** tab → *New…* → Program/script: browse to
   `backend\backup_silent.vbs` (this wrapper runs the `.bat` with no visible
   console window, same pattern as `run_silent.vbs` for the server itself).
5. Save. To confirm it's working, plug a flash drive in, wait for the next
   trigger (or right-click the task → *Run*), then check
   `backend\backup_log.txt` and the drive's `ClinicBackups\` folder.

This only ever *copies* data onto the flash drive — it never deletes or
modifies `clinic.db` or `uploads\` on the clinic PC, so it's safe to leave
running unattended.

---

## 📖 API Reference

All endpoints are namespaced under `/api/*` and fully documented (with
parameters and example responses) in the interactive Swagger UI at
`/apidocs` once the backend is running. Summary of resource groups:

| Resource | Base path | Notes |
|---|---|---|
| Patients | `/api/patients` | CRUD + `/api/patients/duplicate-check` (duplicate-mobile-number detection) |
| Appointments | `/api/patients/<id>/appointments`, `/api/appointments/<id>` | Nested under a patient |
| Files | `/api/files/upload`, `/api/files/<id>/download`, `/api/files/<id>/preview` | PDF/PNG/JPG/JPEG, attached to a patient or appointment |
| Diagnosis autocomplete | `/api/diagnosis/search?q=...` | Backs the diagnosis suggestion dropdown |
| Medications | `/api/medications`, `/api/medications/search?q=...` | CRUD + autocomplete |
| Prescriptions | `/api/prescriptions`, `/api/patients/<id>/prescriptions` | Saved prescriptions per patient |
| Settings | `/api/settings/branding` | Clinic/doctor branding used by the prescription template |

---

## 🧪 Test/seed data

- **Diagnosis & medication libraries + clinic branding** are seeded
  automatically on first boot (`backend/database/seed.py`, runs from
  `app.py` only if those tables are empty) — this is what powers the
  autocomplete dropdowns out of the box.
- **Sample patients** (with an appointment each) are *not* auto-seeded, to
  avoid cluttering a real clinic's data. To load them for manual testing/demo
  purposes, run:

  ```bash
  cd backend
  source venv/bin/activate
  python3 -m database.seed_demo_patients
  ```

  This is idempotent — re-running it skips patients that already exist
  (matched by `patientNumber`).

---

## 🔄 Migration notes

See [`MIGRATION.md`](./MIGRATION.md) for what changed when the original
static `index.html` prototype was extended with a real backend, and what's
preserved vs. new.
