# 🏥 Dr Mahmoud Risha Clinic — Complete QA Test Report

**Date:** 2026-09-08
**Tested by:** Senior QA / E2E Automation / Security / Full-Stack Debug pass
**Application:** Dr-Mahmoud-Risha Patient Management System
**Method:** Real running application driven through a real browser (Chromium via
Playwright), real HTTP API calls, direct database/state verification,
multi-context concurrency, and security probing against the local instance only.

---

## ✅ Overall Verdict: **PASS WITH WARNINGS**

The application **starts cleanly, runs stably, and every feature that actually
exists works well** — patient records, appointments/booking, the bilingual
prescription generator, medications, financial invoicing, autocomplete, search,
i18n and theming all function with no console errors and correct, persistent
data. The backend API is unusually solid: correct status codes, real file
magic-byte validation, path-traversal protection, parameterized queries, and
graceful handling of malformed input.

The **warnings are important and mostly about a gap between the test brief and
the delivered product**, plus one genuine concurrency bug (now fixed):

1. **There is no "Nurse" account and no role system at all.** The brief assumes
   two roles (Doctor + Nurse) with different permissions. The code has exactly
   one hard-coded credential and no concept of roles. The Nurse login is
   rejected because the account does not exist.
2. **The backend has no authentication or authorization whatsoever.** Every
   `/api/*` endpoint is fully open to anyone who can reach the port.
3. **A concurrency bug caused HTTP 500s** when two people added patients / booked
   walk-ins at the same instant. **This has been fixed and re-verified** in this
   pass.

Because of #1 and #2, the large "Doctor vs Nurse simultaneous" and
"permission-enforcement" portions of the brief **cannot be executed as written**
— there is nothing in the product to test them against. That is reported here as
the headline finding rather than faked as passing tests.

---

## 🖥️ Environment

| Item | Value |
|---|---|
| OS | Linux 6.18 (x86_64 container) |
| Python | 3.11.15 (venv per README) |
| Backend | Flask 3.0.3 + Flask-SQLAlchemy 3.1.1 + SQLite, `python3 app.py` |
| Database | SQLite `backend/database/clinic.db` (auto-created + seeded on boot) |
| Browser | Chromium 1194 (headless), driven by Playwright 1.62 |
| App URL | http://127.0.0.1:5000/ |
| Swagger | http://127.0.0.1:5000/apidocs/ (loads, HTTP 200) |

**Startup:** Backend booted with **no exceptions**. `/` serves the frontend
(HTTP 200), `/apidocs/` loads, all `/api/*` respond, assets (`/assets/rx-*`)
load. Dependencies installed cleanly *only inside a fresh venv* — a system-wide
`pip install` fails to build `flasgger` on the old distro setuptools, so the
README's venv instructions must be followed (documented, not a bug).

---

## 📊 Statistics

| Metric | Count |
|---|---|
| Automated API/robustness/security checks | 55 + 29 regression = **84**, all passing |
| Concurrency checks (post-fix) | 16/16 passing |
| Browser E2E flows | login matrix (10), nav (7 pages), full patient→Rx workflow, i18n, theme, responsive (5 viewports), 2-context isolation |
| Bugs found | 8 (1 fixed) |
| Blocked areas (feature does not exist) | Nurse role, role permissions, inventory |

---

## 🔬 What Was Actually Tested (and how)

- **Login page & auth matrix** — real form, real button, Enter key, empty/wrong
  creds, whitespace handling, and the Nurse account, each in a fresh browser
  context.
- **All 7 navigation pages** — Home, Add Patient, Booking, Patients,
  Prescription, Medications, Financial, Settings — rendered and screenshotted,
  console + network monitored.
- **Full clinical workflow in the browser** — created patient
  *"QA Concurrent Patient 2026"* (P-0006, 01000000001) via the real form,
  verified in the list, on the API, and in the DB; built a prescription with
  diagnosis + medication via autocomplete and rendered the print preview.
- **API** — every resource group, valid + invalid + boundary + malformed +
  wrong-method + unauthenticated.
- **Security** — SQLi, stored XSS, path traversal, file-upload spoofing,
  unauthenticated access, IDOR (all local instance only).
- **Concurrency** — two independent browser contexts + parallel HTTP threads;
  lost-update, double-booking, and patient-number race.
- **i18n / theme / responsive** — English↔Arabic (RTL), 12 color themes,
  5 viewports 320→1920.

---

## 👨‍⚕️ Doctor (Risha) Results

| Area | Result | Notes |
|---|---|---|
| Authentication | ✅ PASS | `Risha` / `Risha12345` logs in; Enter key works; username trimmed; password not trimmed; wrong/empty rejected with clear toast |
| Dashboard (Home) | ✅ PASS | Out-Patient list + live queue + booked/waiting/completed stat cards render, no errors |
| Add Patient / Patients | ✅ PASS | Create, list, search, edit, patient detail all work; duplicate-mobile detection (409 → confirm dialog); persists across refresh & DB |
| Booking / Appointments | ✅ PASS | Slot engine respects clinic days (Sun/Tue/Thu) & hours (16:00–21:00); walk-in booking works; per-appointment fields save |
| Diagnosis autocomplete | ✅ PASS | Suggestions appear from `/api/diagnosis/search`; selection persists |
| Medications | ✅ PASS | Autocomplete + records CRUD + library; correct 400/404s |
| Prescription | ✅ PASS | Pixel-faithful bilingual letterhead; patient/diagnosis/drugs/notes/date/signature/QR/contact bar all correct; print preview clean (see `11_prescription_EN.png`, `12_prescription_AR.png`) |
| File upload | ✅ PASS | PNG/JPG/PDF accepted; content-type spoofing & bad extensions rejected (magic-byte check); download/preview work; attached to patient/appointment |
| Financial | ✅ PASS | Invoices, payments, summary render and compute |
| Settings / Branding | ✅ PASS | Branding get/put, backup export, monthly report |
| Language (EN/AR) | ✅ PASS | Full RTL flip (`dir=rtl`, `lang=ar`), nav/labels translated |
| Theme | ✅ PASS (see BUG-006) | 12 palettes, persisted in localStorage — **but all are light; no dark mode** |
| Logout | ❌ **MISSING** (BUG-004) | No logout button/function exists anywhere |
| Security | ⚠️ See bug list | Frontend escapes output (XSS safe on render); backend has **no auth** |

---

## 👩‍⚕️ Nurse Results

| Area | Result |
|---|---|
| Authentication | ❌ **BLOCKED — account does not exist** |
| Everything else | ⛔ Not testable |

The Nurse credentials (`Nurse` / `Nurse12345`) are **rejected** by the real
login screen. The sign-in handler (`index.html`, `doSignIn()`) contains a single
hard-coded check:

```js
if (u === 'Risha' && p === 'Risha12345') { … } else { toast(badCreds) }
```

There is **no Nurse user, no user table, no roles, and no backend login
endpoint**. This is the #1 finding (BUG-001).

---

## 🔐 Doctor vs Nurse Permission Matrix

Because the product has **one role and no server-side authorization**, the matrix
below documents *reality*, not a working RBAC system. "EXPECTED" reflects the
brief; "ACTUAL" reflects the code.

| Feature | Doctor (expected) | Nurse (expected) | Doctor (actual) | Nurse (actual) | Backend enforces? | Result |
|---|---|---|---|---|---|---|
| Log in | ✅ | ✅ | ✅ | ❌ no account | n/a (client-side only) | ❌ FAIL (no Nurse) |
| View patients | ✅ | ✅ | ✅ | ⛔ can't log in | ❌ open to all | ⚠️ no enforcement |
| Create/edit patient | ✅ | ⚠️ maybe | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Delete patient (API) | ✅ | ❌ | ✅ (API only, no UI) | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Appointments | ✅ | ✅ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Prescriptions | ✅ | ❌ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Medications | ✅ | ⚠️ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Files | ✅ | ⚠️ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Financial | ✅ | ❌ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Settings/Branding | ✅ | ❌ | ✅ | ⛔ | ❌ open to all | ⚠️ no enforcement |
| Inventory | ✅ | ⚠️ | ❌ **feature absent** | ❌ | ❌ n/a | ❌ FAIL (no feature) |

**Key takeaway:** even if a Nurse account existed in the frontend, it would grant
identical power, because **the API performs no authorization** — any client
(browser, `curl`, script) can perform any operation without authenticating.

---

## 🔀 Concurrent User Test (Phases 12/13/31)

Run with **two independent browser contexts** (isolated cookies / sessionStorage)
plus parallel HTTP threads against the same records.

| Scenario | Observed behavior | Verdict |
|---|---|---|
| Session isolation | Context A logged in; Context B (fresh) started **unauthenticated** and showed the sign-in screen. Client sessions are isolated per browser context. | ✅ (client-side only) |
| Shared backend record | Both contexts read the **same** patient record; an edit saved in B was visible in A on refetch. | ✅ |
| Concurrent field edits (10 parallel PUTs) | All returned 200, **last-write-wins**, no corruption — but a **silent lost update** (no optimistic locking / version check). | ⚠️ BUG-005 (MEDIUM) |
| Concurrent walk-in booking / patient add (before fix) | One request **crashed with HTTP 500** — `UNIQUE constraint failed: patients.patient_number`. | ❌ BUG-002 (**fixed**) |
| Same test **after fix** | 8 parallel walk-ins + 8 parallel patient creates → **all 201**, patient numbers all unique, zero 500s, zero tracebacks. | ✅ FIXED |
| Double-booking same slot | Explicit-time booking and the nested `/patients/<id>/appointments` endpoint have **no slot-conflict check** — two appointments can occupy the same slot (the slot *suggestion* list avoids overlaps, but nothing enforces it). | ⚠️ BUG-007 (LOW/MEDIUM, ambiguous rule) |

**Final DB state after all concurrency runs:** consistent — no orphan records, no
duplicate patient numbers, foreign keys intact, no corrupted rows.

---

## 🐞 Bugs

### BUG-001 — No Nurse account & no role/permission system — **CRITICAL (vs brief)**
- **Feature:** Authentication / Authorization
- **Page:** Sign-in (`index.html` `doSignIn`)
- **Steps:** Enter `Nurse` / `Nurse12345` → click Sign In.
- **Expected:** Nurse logs into a Nurse dashboard with restricted permissions.
- **Actual:** "Invalid username or password." The only credential in the code is
  `Risha`/`Risha12345`; there is no user model, no roles, no Nurse.
- **DB impact:** None (no user table exists).
- **Recommended fix:** Introduce a real `User` model (username, hashed password,
  role), a `/api/auth/login` endpoint issuing a session/JWT, and role checks. Add
  the Nurse account and define Doctor vs Nurse permissions.

### BUG-002 — Concurrent patient/walk-in creation → HTTP 500 (race) — **HIGH** ✅ FIXED
- **Feature:** Patient creation / walk-in booking
- **Endpoints:** `POST /api/patients`, `POST /api/appointments/book`,
  `POST /api/appointments/import`
- **Steps:** Fire two creates/bookings simultaneously (realistic: secretary desk
  + doctor's room on the same LAN).
- **Expected:** Both succeed with distinct `P-XXXX` numbers.
- **Actual (before):** `next_patient_number()` reads max+1 non-atomically; two
  callers pick the same number → `sqlite3.IntegrityError: UNIQUE constraint
  failed: patients.patient_number` → uncaught → **HTTP 500 "Internal server
  error"** and the second record is lost.
- **Backend error:** confirmed in server log (traceback at
  `appointment_service._find_or_create_patient` / `patient_service.create_patient`).
- **Fix applied (this pass):** wrapped the insert in a bounded retry that rolls
  back and re-computes a fresh number on `IntegrityError` (explicit
  caller-supplied numbers still surface the conflict). Files:
  `backend/services/patient_service.py`, `backend/services/appointment_service.py`.
- **Re-verified:** 8×8 parallel creates/bookings all 201, numbers unique, no 500s.

### BUG-003 — No authentication on the API — **CRITICAL (security)**
- **Feature:** Whole backend
- **Steps:** `curl http://127.0.0.1:5000/api/patients` with no credentials.
- **Expected:** 401/403 for unauthenticated access to patient health data.
- **Actual:** 200 — full read/write to all patient records, files, prescriptions,
  financials without any auth. On the LAN deployment the README describes, anyone
  on the network can exfiltrate or alter the entire clinic database.
- **Recommended fix:** Require authentication on all `/api/*` routes; add
  authorization once roles exist. (Not auto-fixed — this is a design-level change,
  not a safe one-line fix.)

### BUG-004 — No logout function — **MEDIUM**
- **Feature:** Session management
- **Actual:** There is no logout button anywhere and no `signOut`/`logout` code.
  A user can only "log out" by closing the browser tab (sessionStorage clears).
  Phase 26 (logout → back button → protected page) cannot be exercised via the UI.
- **Recommended fix:** Add a logout control that clears auth state and returns to
  the sign-in screen (and, once server sessions exist, invalidates them).

### BUG-005 — Lost update on concurrent edits (no optimistic locking) — **MEDIUM**
- **Feature:** Patient/appointment update
- **Actual:** Simultaneous edits to the same record silently overwrite each other
  (last-write-wins); no version/ETag/conflict detection. Two staff editing the
  same patient can lose one another's changes with no warning.
- **Recommended fix:** Add a `version`/`updated_at` optimistic-lock check and
  return 409 on stale writes.

### BUG-006 — "Dark mode" does not exist; only light themes — **LOW**
- **Feature:** Theme system
- **Actual:** The 12 themes (`THEMES` in `index.html`) only change accent color
  and a light background gradient. There is no dark theme, so Phase 24
  (light↔dark) has nothing to switch to. Text/contrast were checked across all
  light themes and are fine.
- **Recommended fix:** If dark mode is required, add a dark palette + toggle.

### BUG-007 — Double-booking not prevented — **LOW/MEDIUM (rule ambiguous)**
- **Feature:** Appointments
- **Actual:** `POST /api/patients/<id>/appointments` and explicit-time
  `POST /api/appointments/book` do **not** check for slot conflicts, so two
  appointments can share the same date/time. The available-slots *suggestions*
  avoid overlap, but nothing enforces it on write.
- **Not auto-fixed:** the intended rule (walk-ins may legitimately overlap?) is
  undefined; enforcing uniqueness could break intended flexibility. Flagged for
  product decision.

### BUG-008 — Weak field validation on the API — **LOW**
- **Feature:** Patient creation
- **Steps:** `POST /api/patients` with `age: "not-a-number"`.
- **Actual:** Accepted (201) and stored as a string in the INTEGER `age` column
  (SQLite is loosely typed). The UI's `type=number` prevents this in the browser,
  but the API does not. Also `mobileNumber` accepts any string (no format check).
- **Recommended fix:** Coerce/validate `age` to a non-negative integer and
  validate phone format server-side.

### Documentation mismatch — Inventory feature absent — **note**
- README advertises "📦 Clinic Inventory Management" with stock status. There is
  **no inventory model, route, or UI** anywhere in the codebase (0 references).
  Phases 20–21 (inventory) are not testable. Either build it or remove the claim.

### Documentation mismatch — README login credentials — **note**
- README says sign in with `admin` / `123`; the actual code accepts only
  `Risha` / `Risha12345`. `admin/123` is rejected.

### Offline mode caveat — Tailwind via CDN — **LOW**
- The page loads Tailwind from `https://cdn.tailwindcss.com`. In a truly offline
  LAN (as the README promises), that request fails. Most styling is hand-rolled
  CSS so the app remains usable, but utility classes silently do nothing.
  Recommend vendoring Tailwind locally for genuine offline use.

---

## 🛡️ Security Test Summary (local instance only)

| Test | Result |
|---|---|
| Authentication bypass | ⚠️ N/A — there is **no auth to bypass**; API is fully open (BUG-003) |
| Authorization bypass / IDOR | ⚠️ Trivial — no roles; every object reachable by any caller |
| Stored XSS | ✅ Safe on render — `<script>` name is stored raw but the frontend `esc()`-escapes on output; no alert fired |
| SQL injection | ✅ Safe — SQLAlchemy parameterized queries; `' OR 1=1--` returns 200 with no injection |
| File-upload spoofing | ✅ Blocked — magic-byte signature check rejects `.txt` and fake-`.png` |
| Path traversal | ✅ Blocked — `/assets/../config.py` and encoded variants → 404; stored files use UUID names |
| Malformed JSON | ✅ Handled — returns 400, not 500 |
| Sensitive data / stack traces | ✅ Errors return generic JSON (`{"error": "Internal server error"}`), no stack traces leaked to clients |

**Headline security issue:** the total absence of API authentication (BUG-003)
combined with no roles (BUG-001) means all patient PHI is unprotected on the
network. This is the most serious real-world risk and should be prioritized.

---

## 🧪 Error Handling (Phase 29)

Invalid login, missing/nonexistent IDs, bad file types, duplicate patients, empty
forms, malformed requests, and unsupported methods were all exercised. In every
case the app returned a **useful error with the correct HTTP status** (400/404/
405/409), did **not crash**, exposed **no stack trace**, and kept the UI usable.
The single exception was the concurrency 500 (BUG-002), now fixed.

---

## 🔧 Fix Applied in This Pass

**Concurrency-safe patient number allocation** (BUG-002):

- `backend/services/patient_service.py` — `create_patient()` now retries on
  `IntegrityError`, rolling back and recomputing `next_patient_number()`; explicit
  caller-supplied numbers still raise on real conflict.
- `backend/services/appointment_service.py` — `_find_or_create_patient()`
  (used by walk-in booking and CSV/JSON import) got the same bounded retry.

Minimal, behavior-preserving for the normal path, and verified with 16 parallel
create/book requests producing zero 500s and zero duplicate numbers. Full API
regression (29 checks) re-run afterward: **all green**.

---

## 📌 Prioritized Recommendations

1. **Add real authentication + authorization** to the backend (BUG-003) — highest
   real-world risk (unprotected PHI on the LAN).
2. **Implement the Nurse account and a role system** (BUG-001) — required for the
   product's own stated two-user model.
3. **Add logout** (BUG-004).
4. **Add optimistic locking** to prevent silent lost updates (BUG-005).
5. **Decide the double-booking rule** and enforce it if needed (BUG-007).
6. **Reconcile the README** with reality (inventory feature, login credentials).
7. **Vendor Tailwind locally** for genuine offline use.
8. Tighten server-side field validation (BUG-008).

---

## 📷 Evidence (in `qa/`)

`01_login_page.png`, `02_home_dashboard.png`, `10_patient_list.png`,
`11_prescription_EN.png`, `12_prescription_AR.png`, `resp_375.png`,
`resp_768.png`, and per-page captures `page_*.png`. Reusable automated tests live
in `tests/` (see `tests/README.md`).
