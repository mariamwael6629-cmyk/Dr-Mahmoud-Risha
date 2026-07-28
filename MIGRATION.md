# Migration notes — Phase 1

This documents what changed when the original static, frontend-only
prototype (`index.html` with in-memory/mock state) was extended into a
full-stack system. Per the project's guiding rule, **nothing existing was
rebuilt, renamed, or removed** — the backend was added alongside the
existing frontend, and the frontend was extended in place.

## What's preserved

- `index.html` is still the single entry point for the UI — same file,
  same top-level structure, same IDs/classes/function names for everything
  that existed before.
- All pre-existing screens, navigation, and styling are unchanged unless a
  specific phase task called for a visual update (the prescription
  template redesign and the clinic branding are the two intentional visual
  changes in Phase 1 — see below).
- The app still works as a single HTML file you can open directly; running
  the Flask backend is what unlocks persistence, file uploads, and
  autocomplete, but it serves the *same* `index.html` rather than a rebuilt
  version of it.

## What's new

- **Backend** (`backend/`): Flask + Flask-SQLAlchemy + SQLite, layered as
  `models/` → `services/` → `controllers/` → `routes/`, assembled in
  `backend/app.py`. Not present before; added without touching the
  frontend's existing JS state management.
- **Persistence**: patients/appointments/medications/files now persist to
  `backend/database/clinic.db` via the API instead of living only in
  in-memory JS state. The frontend's existing `state` object and rendering
  functions were extended to call the API (fetch) rather than replaced.
- **Extended patient fields**: `mobileNumber`, `emergencyContact`, `notes`
  were added to the patient model/form alongside the original fields
  (name, age, gender, previous operations/treatment, diagnosis, symptoms,
  family history) — the originals are untouched.
- **File uploads**: PDF/PNG/JPG/JPEG uploads for X-Ray and test results,
  stored under `backend/uploads/` and linked to a patient or appointment
  via `/api/files/*`.
- **Autocomplete**: a `DiagnosisLibrary` and `MedicationLibrary` table back
  the diagnosis/medication suggestion dropdowns (`/api/diagnosis/search`,
  `/api/medications/search`), reusing the same shared dropdown component
  pattern already used elsewhere in the app (`data-ac-ctx` + `#ac-dropdown`).
- **Prescription template redesign**: `buildRxPreview()` was rewritten to
  match the clinic's real printed prescription pad pixel-for-pixel
  (bilingual EN/AR letterhead, gold info bar, watermark, signature/QR
  footer, contact bar). This is the one place an existing function's
  *output* was intentionally replaced rather than extended, because the
  task explicitly called for matching the real document — the function
  name, call sites, and its `pt`/`state` data dependencies are unchanged.
- **Branding**: the placeholder "General Clinic" / "Doctor's Name" text
  (navbar, sign-in screen, page `<title>`) was replaced with the clinic's
  real name (Dr Mahmoud Risha — Rheumatology Clinic) in both `LANG.en` and
  `LANG.ar`, using the same `t()` translation mechanism that was already
  in place.

## Data migration

There is no data to migrate from the old prototype — it held no real
persisted data (everything lived in volatile JS state, lost on refresh).
First boot of the new backend starts from an empty `clinic.db`, auto-seeded
only with the diagnosis/medication libraries and clinic branding settings
(see `backend/database/seed.py`). Sample patient records for testing can be
loaded on demand via `backend/database/seed_demo_patients.py` (see README).

## Backend route layout

All API routes are namespaced under `/api/*` and documented interactively
at `/apidocs` (Swagger UI, via `flasgger`) once the backend is running —
see the README's [API Reference](./README.md#-api-reference) section for
the resource summary.
