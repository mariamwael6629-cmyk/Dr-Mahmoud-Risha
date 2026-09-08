"""Browser E2E tests (Playwright + Chromium).

Skipped automatically if no Chromium is available. Credentials come from env
(DOCTOR_USERNAME / DOCTOR_PASSWORD). These mirror the manual QA flows: login
validation, dashboard, create-patient workflow, autocomplete, i18n, theme and
responsive layout.
"""
import pytest

from conftest import (BASE_URL, DOCTOR_USERNAME, DOCTOR_PASSWORD,
                      NURSE_USERNAME, NURSE_PASSWORD, find_chromium, unique_suffix)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
CHROME = find_chromium()
pytestmark = pytest.mark.skipif(CHROME is None, reason="No Chromium available for E2E")


@pytest.fixture()
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        yield b
        b.close()


def _login(page, user, pw):
    page.goto(BASE_URL + "/")
    page.wait_for_timeout(700)
    page.fill("#si-user", user)
    page.fill("#si-pass", pw)
    page.get_by_role("button", name="Sign In").first.click()
    page.wait_for_timeout(1500)


def _toast(page):
    t = page.locator('.toast,[class*="toast"]')
    try:
        return t.first.inner_text().strip() if t.count() else ""
    except Exception:
        return ""


def _role(pg):
    return pg.evaluate("state.currentUser && state.currentUser.role")


def test_doctor_login_succeeds(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    assert _role(pg) == "doctor"
    ctx.close()


def test_invalid_logins_rejected(browser):
    for user, pw in [("", ""), ("wrong", "wrong"), (DOCTOR_USERNAME, "wrongpass")]:
        ctx = browser.new_context()
        pg = ctx.new_page()
        _login(pg, user, pw)
        assert pg.evaluate("state.currentUser") is None
        ctx.close()


def test_nurse_login_and_nav_restrictions(browser):
    """Nurse logs in and does NOT get the clinical (doctor-only) nav items."""
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, NURSE_USERNAME, NURSE_PASSWORD)
    assert _role(pg) == "nurse"
    nav = " ".join(pg.locator(".nav-btn").nth(i).inner_text() for i in range(pg.locator(".nav-btn").count()))
    assert "Prescription" not in nav
    assert "Medications" not in nav
    # direct navigation to a doctor-only page is blocked
    pg.evaluate("navigate('prescription')"); pg.wait_for_timeout(600)
    assert pg.evaluate("state.currentPage") == "home"
    ctx.close()


def test_nurse_add_patient_hides_medical_fields(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, NURSE_USERNAME, NURSE_PASSWORD)
    pg.evaluate("navigate('addPatient')"); pg.wait_for_timeout(700)
    assert pg.locator('#patientForm input[name="name"]').count() == 1
    assert pg.locator('#patientForm input[name="diagnosis"]').count() == 0
    assert pg.locator('#patientForm input[name="symptoms"]').count() == 0
    ctx.close()


def test_logout(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pg.evaluate("doLogout()"); pg.wait_for_timeout(800)
    assert pg.evaluate("state.currentUser") is None
    assert pg.evaluate("state.currentPage") == "signIn"
    ctx.close()


def test_session_isolation_between_contexts(browser):
    a = browser.new_context(); pga = a.new_page()
    b = browser.new_context(); pgb = b.new_page()
    _login(pga, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pgb.goto(BASE_URL + "/"); pgb.wait_for_timeout(1000)
    assert pgb.evaluate("state.currentUser") is None
    assert pgb.locator("#si-user").is_visible()
    a.close(); b.close()


def test_create_patient_workflow(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    name = f"E2E Patient {unique_suffix()}"
    mobile = "0188" + unique_suffix()[-7:]
    pg.evaluate("navigate('addPatient')"); pg.wait_for_timeout(800)
    pg.fill('#patientForm input[name="name"]', name)
    pg.fill('#patientForm input[name="age"]', "48")
    pg.select_option('#patientForm select[name="gender"]', index=1)
    pg.fill('#patientForm input[name="mobileNumber"]', mobile)
    pg.get_by_role("button", name="Save Patient").first.click()
    pg.wait_for_timeout(1500)
    assert "success" in _toast(pg).lower() or _toast(pg) != ""
    # verify via same-origin API
    ok = pg.evaluate(
        "async (n)=>{const r=await fetch('/api/patients?search='+encodeURIComponent(n)).then(r=>r.json());return r.total>=1;}",
        name,
    )
    assert ok
    ctx.close()


def test_autocomplete_diagnosis_and_medication(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pg.evaluate("navigate('prescription')"); pg.wait_for_timeout(1000)
    pg.fill("#rx-diag", "rheu"); pg.wait_for_timeout(800)
    assert pg.locator("#ac-dropdown").is_visible()
    pg.get_by_role("button", name="+ Add Drug").first.click(); pg.wait_for_timeout(400)
    pg.locator("#rx-drugs-list input").first.fill("met"); pg.wait_for_timeout(800)
    assert pg.locator("#ac-dropdown .ac-item").count() > 0
    ctx.close()


def test_i18n_arabic_rtl(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pg.evaluate("toggleLang()"); pg.wait_for_timeout(800)
    assert pg.evaluate("document.documentElement.dir") == "rtl"
    assert pg.evaluate("document.documentElement.lang") == "ar"
    ctx.close()


def test_theme_persists(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pg.evaluate("applyTheme('rose')"); pg.wait_for_timeout(300)
    assert pg.evaluate("localStorage.getItem('clinicTheme')") == "rose"
    ctx.close()


def test_dark_mode_toggle_and_persist(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    pg.click("#modeBtn"); pg.wait_for_timeout(300)
    assert pg.evaluate("document.documentElement.getAttribute('data-mode')") == "dark"
    assert pg.evaluate("localStorage.getItem('clinicMode')") == "dark"
    pg.click("#modeBtn"); pg.wait_for_timeout(300)
    assert pg.evaluate("document.documentElement.getAttribute('data-mode')") == "light"
    ctx.close()


def test_no_horizontal_overflow_responsive(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    _login(pg, DOCTOR_USERNAME, DOCTOR_PASSWORD)
    for w, h in [(320, 568), (375, 667), (768, 1024), (1920, 1080)]:
        pg.set_viewport_size({"width": w, "height": h})
        pg.evaluate("navigate('patients')"); pg.wait_for_timeout(500)
        sw = pg.evaluate("document.documentElement.scrollWidth")
        cw = pg.evaluate("document.documentElement.clientWidth")
        assert sw <= cw + 2, f"Horizontal overflow at {w}x{h}: {sw}>{cw}"
    ctx.close()
