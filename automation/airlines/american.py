"""
american.py — American Airlines booking handler

Navigates aa.com, fills the search form, submits, and attempts to match
the target flight by flight number. Stops before payment.

This is the ONLY fully implemented airline handler.
"""

import random
import time


# ── helpers ──────────────────────────────────────────────────────────────────

def _delay(lo: float = 0.4, hi: float = 1.2) -> None:
    """Small randomized pause to simulate human pacing."""
    time.sleep(random.uniform(lo, hi))


def _type_slow(locator, text: str) -> None:
    """Type text character-by-character with slight randomized delay."""
    locator.click()
    _delay(0.1, 0.3)
    for char in text:
        locator.type(char, delay=random.randint(40, 120))


# ── main handler ──────────────────────────────────────────────────────────────

def run(page, payload: dict) -> None:
    """
    Full American Airlines booking flow up to (but NOT including) payment.

    payload keys used:
        departure_airport   str     IATA code, e.g. "DFW"
        arrival_airport     str     IATA code, e.g. "BOS"
        departure_date      str     YYYY-MM-DD
        return_date         str     YYYY-MM-DD (optional — omit for one-way)
        flight_numbers      list    e.g. ["AA1234"]
        passengers          list    list of passenger dicts with "name" key
    """
    dep = payload["departure_airport"].upper()
    arr = payload["arrival_airport"].upper()
    dep_date = payload["departure_date"]          # YYYY-MM-DD
    ret_date = payload.get("return_date", "")
    flight_numbers = [fn.upper() for fn in payload["flight_numbers"]]
    pax_count = len(payload["passengers"])

    print(f"[american] Navigating to aa.com")
    page.goto("https://www.aa.com/booking/find-flights", timeout=30000)
    _delay(1.0, 2.0)

    # ── trip type ─────────────────────────────────────────────────────────────
    if ret_date:
        print(f"[american] Setting trip type: Round Trip")
        try:
            rt_radio = page.locator("input[value='roundTrip'], label:has-text('Round trip')")
            rt_radio.first.click()
            _delay()
        except Exception:
            print("[american] WARNING: could not set round-trip radio — proceeding")
    else:
        print(f"[american] Setting trip type: One Way")
        try:
            ow_radio = page.locator("input[value='oneWay'], label:has-text('One way')")
            ow_radio.first.click()
            _delay()
        except Exception:
            print("[american] WARNING: could not set one-way radio — proceeding")

    # ── origin ────────────────────────────────────────────────────────────────
    print(f"[american] Filling origin: {dep}")
    origin_input = page.locator("#aa-leavingFrom, [data-testid='origin-input'], input[placeholder*='From']")
    origin_input.first.triple_click()
    _delay(0.2, 0.5)
    _type_slow(origin_input.first, dep)
    _delay(0.8, 1.5)
    # select first autocomplete suggestion
    origin_suggestion = page.locator(
        f"[role='option']:has-text('{dep}'), "
        f"li:has-text('{dep}'), "
        f"[data-testid='suggestion']:has-text('{dep}')"
    )
    if origin_suggestion.count() > 0:
        origin_suggestion.first.click()
        _delay()
    else:
        print(f"[american] WARNING: no autocomplete suggestion found for {dep}")

    # ── destination ───────────────────────────────────────────────────────────
    print(f"[american] Filling destination: {arr}")
    dest_input = page.locator("#aa-goingTo, [data-testid='destination-input'], input[placeholder*='To']")
    dest_input.first.triple_click()
    _delay(0.2, 0.5)
    _type_slow(dest_input.first, arr)
    _delay(0.8, 1.5)
    dest_suggestion = page.locator(
        f"[role='option']:has-text('{arr}'), "
        f"li:has-text('{arr}'), "
        f"[data-testid='suggestion']:has-text('{arr}')"
    )
    if dest_suggestion.count() > 0:
        dest_suggestion.first.click()
        _delay()
    else:
        print(f"[american] WARNING: no autocomplete suggestion found for {arr}")

    # ── departure date ────────────────────────────────────────────────────────
    print(f"[american] Filling departure date: {dep_date}")
    # AA date picker expects MM/DD/YYYY
    year, month, day = dep_date.split("-")
    dep_date_display = f"{month}/{day}/{year}"
    dep_date_input = page.locator(
        "#departureDate, [data-testid='departure-date'], input[placeholder*='Depart']"
    )
    dep_date_input.first.triple_click()
    _delay(0.2, 0.4)
    _type_slow(dep_date_input.first, dep_date_display)
    _delay(0.5, 1.0)

    # ── return date (if round trip) ───────────────────────────────────────────
    if ret_date:
        print(f"[american] Filling return date: {ret_date}")
        r_year, r_month, r_day = ret_date.split("-")
        ret_date_display = f"{r_month}/{r_day}/{r_year}"
        ret_date_input = page.locator(
            "#returnDate, [data-testid='return-date'], input[placeholder*='Return']"
        )
        ret_date_input.first.triple_click()
        _delay(0.2, 0.4)
        _type_slow(ret_date_input.first, ret_date_display)
        _delay(0.5, 1.0)

    # ── passenger count ───────────────────────────────────────────────────────
    if pax_count > 1:
        print(f"[american] Setting passenger count: {pax_count}")
        try:
            pax_btn = page.locator(
                "[data-testid='passenger-selector'], "
                "button:has-text('Passenger'), "
                "#passengerCount"
            )
            pax_btn.first.click()
            _delay(0.5, 1.0)
            # click the adult "+" button (pax_count - 1) additional times
            add_adult = page.locator(
                "button[aria-label*='Add adult'], "
                "button[data-testid='increase-adult'], "
                "[aria-label='Increase adults']"
            )
            for _ in range(pax_count - 1):
                add_adult.first.click()
                _delay(0.3, 0.6)
        except Exception:
            print(f"[american] WARNING: could not set passenger count to {pax_count} — proceeding with default")

    # ── submit search ─────────────────────────────────────────────────────────
    print("[american] Submitting search")
    search_btn = page.locator(
        "button[type='submit']:has-text('Search'), "
        "button:has-text('Find flights'), "
        "[data-testid='search-button']"
    )
    search_btn.first.click()
    _delay(1.0, 2.0)

    print("[american] Waiting for results page to load")
    page.wait_for_load_state("networkidle", timeout=30000)
    _delay(1.5, 3.0)

    # ── match flight by number ────────────────────────────────────────────────
    target_flight = flight_numbers[0]  # match on first flight number in payload
    print(f"[american] Looking for flight: {target_flight}")

    flight_locator = page.locator(
        f"[data-testid*='{target_flight}'], "
        f"text={target_flight}, "
        f"[aria-label*='{target_flight}']"
    )
    _delay(1.0, 2.0)

    if flight_locator.count() > 0:
        print(f"[american] Found flight {target_flight} — scrolling into view")
        flight_locator.first.scroll_into_view_if_needed()
        _delay(0.5, 1.0)
        # click "Select" button near the matched flight row
        select_btn = flight_locator.first.locator(
            "xpath=ancestor::*[contains(@class,'flight') or contains(@data-testid,'flight')]"
            "//button[contains(text(),'Select') or @data-testid='select-flight']"
        )
        if select_btn.count() > 0:
            print(f"[american] Clicking Select for flight {target_flight}")
            select_btn.first.click()
            _delay(1.0, 2.0)
        else:
            print(
                f"[american] Flight {target_flight} found but 'Select' button not located — "
                "manual selection required."
            )
    else:
        print(
            f"[american] WARNING: flight {target_flight} not found in results. "
            "Confirm the flight number is correct and the date matches."
        )
        print("[american] Leaving browser open on results page for manual selection.")

    print("[american] Handler complete. Stopping before payment.")
    print("[american] *** DO NOT PROCEED PAST THIS POINT AUTOMATICALLY ***")
