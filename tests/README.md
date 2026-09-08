# QA Test Suite — Dr Mahmoud Risha Clinic

Reusable automated tests produced during the QA pass. They exercise the **real
running application** (HTTP API, browser E2E, and concurrency), not mocks.

## Prerequisites

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install pytest requests playwright     # test-only deps
python3 app.py                             # start the app on :5000 (separate terminal)
```

For the browser E2E test, Playwright needs a Chromium build. Either run
`playwright install chromium`, or set `CHROMIUM_PATH` to an existing Chromium
executable — the suite auto-detects a system Chromium if present and otherwise
**skips** the browser tests (API + concurrency tests still run).

## Credentials — via environment variables (never hard-coded here)

```bash
export DOCTOR_USERNAME=Risha
export DOCTOR_PASSWORD=Risha12345
# export BASE_URL=http://127.0.0.1:5000      # optional, this is the default
# export CHROMIUM_PATH=/path/to/chromium     # optional, for E2E
```

The suite reads these at runtime and does not store secrets in the repo.
(Note: the current app hard-codes the credential in `index.html`; these tests
are written role-agnostically so they keep working if a real auth system and a
Nurse account are added later — set `NURSE_USERNAME`/`NURSE_PASSWORD` too.)

## Run

```bash
cd tests
pytest -v                    # everything
pytest -v test_api.py        # API + security + robustness
pytest -v test_concurrency.py  # BUG-002 regression + race checks
pytest -v test_e2e.py        # browser login + clinical workflow (needs Chromium)
```

## Files

| File | Covers |
|---|---|
| `conftest.py` | base URL, credentials from env, Chromium discovery, shared fixtures |
| `test_api.py` | patients / appointments / prescriptions / medications / files / settings CRUD, validation, malformed input, wrong method, SQLi, path traversal, upload spoofing, unauthenticated access |
| `test_concurrency.py` | parallel patient/walk-in creation (BUG-002 regression), unique patient numbers, concurrent-edit last-write-wins |
| `test_e2e.py` | login validation matrix, dashboard, create-patient workflow, autocomplete, i18n (EN/AR RTL), theme persistence, responsive overflow |
