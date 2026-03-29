"""
american.py — American Airlines booking handler

Navigates aa.com, fills the search form, submits, and attempts to match
the target flight by flight number. Stops before payment.

Selectors verified against live aa.com DOM (2026-03-29).
"""

import random
import time


# ── helpers ──────────────────────────────────────────────────────────────────

def _delay(lo: float = 0.4, hi: float = 1.2) -> None:
    time.sleep(random.uniform(lo, hi))


def _type_into(locator, text: str) -> None:
    """Click, clear, then type character-by-character to trigger autocomplete."""
    locator.click()
    _delay(0.1, 0.3)
    locator.fill("")
    locator.type(text, delay=random.randint(50, 120))


# ── main handler ──────────────────────────────────────────────────────────────

def run(page, payload: dict) -> None:
    dep = payload["departure_airport"].upper()
    arr = payload["arrival_airport"].upper()
    dep_date = payload["departure_date"]          # YYYY-MM-DD
    ret_date = payload.get("return_date", "")
    flight_numbers = [fn.upper() for fn in payload["flight_numbers"]]
    pax_count = len(payload["passengers"])

    # Convert YYYY-MM-DD → MM/DD/YYYY for aa.com date fields
    def fmt_date(d):
        y, m, day = d.split("-")
        return f"{m}/{day}/{y}"

    print("[american] Navigating to aa.com")
    page.goto("https://www.aa.com/booking/find-flights", timeout=30000)
    _delay(2.0, 3.5)

    # ── dismiss cookie banner if present ─────────────────────────────────────
    try:
        allow_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Allow All')")
        if allow_btn.count() > 0 and allow_btn.first.is_visible(timeout=3000):
            print("[american] Dismissing cookie banner")
            allow_btn.first.click()
            _delay(0.5, 1.0)
    except Exception:
        pass  # no banner, continue

    # ── trip type (Material Design mat-select) ────────────────────────────────
    trip_label = "Round trip" if ret_date else "One way"
    print(f"[american] Setting trip type: {trip_label}")
    try:
        trip_select = page.locator(".mat-mdc-select-required")
        trip_select.first.click()
        _delay(0.5, 1.0)
        page.locator(f"mat-option:has-text('{trip_label}')").first.click()
        _delay(0.5, 1.0)
    except Exception:
        print("[american] WARNING: could not set trip type — proceeding")

    # ── origin ────────────────────────────────────────────────────────────────
    print(f"[american] Filling origin: {dep}")
    origin = page.locator("#matOriginAirport")
    _type_into(origin, dep)
    _delay(0.8, 1.5)
    suggestion = page.locator(f"mat-option:has-text('{dep}')").first
    try:
        suggestion.wait_for(timeout=5000)
        suggestion.click()
        _delay(0.4, 0.8)
    except Exception:
        print(f"[american] WARNING: no autocomplete match for {dep} — typing and pressing Enter")
        origin.press("Enter")
        _delay(0.4, 0.8)

    # ── destination ───────────────────────────────────────────────────────────
    print(f"[american] Filling destination: {arr}")
    dest = page.locator("#matDestinationAirport")
    _type_into(dest, arr)
    _delay(0.8, 1.5)
    suggestion = page.locator(f"mat-option:has-text('{arr}')").first
    try:
        suggestion.wait_for(timeout=5000)
        suggestion.click()
        _delay(0.4, 0.8)
    except Exception:
        print(f"[american] WARNING: no autocomplete match for {arr} — pressing Enter")
        dest.press("Enter")
        _delay(0.4, 0.8)

    # ── departure date ────────────────────────────────────────────────────────
    print(f"[american] Filling departure date: {dep_date}")
    dep_field_id = "#matDepartureDatePicker" if ret_date else "#matOneWayDatePicker"
    dep_field = page.locator(dep_field_id)
    dep_field.click()
    dep_field.fill(fmt_date(dep_date))
    dep_field.press("Tab")
    _delay(0.4, 0.8)

    # ── return date ───────────────────────────────────────────────────────────
    if ret_date:
        print(f"[american] Filling return date: {ret_date}")
        ret_field = page.locator("#matReturnDatePicker")
        ret_field.click()
        ret_field.fill(fmt_date(ret_date))
        ret_field.press("Tab")
        _delay(0.4, 0.8)

    # ── passenger count ───────────────────────────────────────────────────────
    if pax_count > 1:
        print(f"[american] Setting passenger count: {pax_count}")
        try:
            # AA uses a native <select> with integer options 1–9
            pax_selects = page.locator("select").all()
            matched = False
            for sel in pax_selects:
                opts = sel.locator("option").all_text_contents()
                # Options are plain integers ("1", "2", ..., "9")
                if "1" in opts and "9" in opts:
                    sel.select_option(str(pax_count))
                    _delay(0.3, 0.6)
                    matched = True
                    break
            if not matched:
                print(
                    f"[american] WARNING: passenger count selector not found — "
                    f"search will default to 1 passenger. "
                    f"Set count manually before selecting your flight."
                )
        except Exception as exc:
            print(f"[american] WARNING: could not set passenger count ({exc}) — proceeding with 1")

    # ── submit ────────────────────────────────────────────────────────────────
    print("[american] Submitting search")
    page.locator("button.btn-search").click()
    _delay(1.0, 2.0)

    print("[american] Waiting for results to load")
    page.wait_for_load_state("load", timeout=30000)
    _delay(5.0, 7.0)  # aa.com results render async after load

    # ── match flight by number ────────────────────────────────────────────────
    target = flight_numbers[0]
    print(f"[american] Looking for flight: {target}")
    _delay(1.0, 2.0)

    # Strip the "AA" prefix — results often show just the number
    target_num = target.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

    # Try multiple locator strategies, pick the first that finds something
    flight_row = None
    for loc in [
        page.locator(f"[data-testid*='{target}']"),
        page.locator(f"[aria-label*='{target}']"),
        page.get_by_text(target, exact=False),
        page.get_by_text(target_num, exact=False),
    ]:
        if loc.count() > 0:
            flight_row = loc
            break

    if flight_row is not None:
        print(f"[american] Found flight {target} — scrolling into view")
        flight_row.first.scroll_into_view_if_needed()
        _delay(0.5, 1.0)
        # Try to click a nearby Select button
        try:
            select_btn = page.locator(
                f"[aria-label*='{target}'] >> xpath=ancestor-or-self::*//button[contains(text(),'Select')]"
            )
            if select_btn.count() > 0:
                print(f"[american] Clicking Select for {target}")
                select_btn.first.click()
                _delay(1.0, 2.0)
        except Exception:
            print(f"[american] Flight {target} highlighted — select it manually in the browser")
    else:
        print(
            f"[american] Flight {target} not found in results. "
            "Verify the flight number and date, then select manually."
        )

    print("[american] Handler complete — stopping before payment.")
