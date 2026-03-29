"""
booking_executor.py — Step 8: Execute Booking

Accepts a payload JSON path, launches a Playwright browser, routes to the
appropriate airline handler, and pauses before payment for manual completion.

Usage:
    python automation/booking_executor.py payloads/trip-N.json
"""

import json
import sys
import time
from pathlib import Path

# Ensure repo root is on sys.path so `automation.airlines.*` resolves
# regardless of where the script is invoked from.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


SUPPORTED_AIRLINES = {
    "american airlines": "american",
    "delta": "delta",
    "united": "united",
    "spirit": "spirit",
}


def load_payload(payload_path: str) -> dict:
    path = Path(payload_path)
    if not path.exists():
        raise FileNotFoundError(f"Payload not found: {payload_path}")
    with open(path, "r") as f:
        payload = json.load(f)
    _validate_payload(payload)
    return payload


def _validate_payload(payload: dict) -> None:
    required = ["airline", "departure_airport", "arrival_airport",
                 "departure_date", "passengers", "flight_numbers"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"Payload missing required fields: {missing}")
    if not payload.get("passengers"):
        raise ValueError("Payload must include at least one passenger")
    if not payload.get("flight_numbers"):
        raise ValueError("Payload must include at least one flight number")


def route_to_handler(payload: dict, page):
    airline_key = payload["airline"].lower()
    matched = next((v for k, v in SUPPORTED_AIRLINES.items() if k in airline_key), None)
    if matched is None:
        raise ValueError(
            f"Unsupported airline: {payload['airline']}. "
            f"Supported: {list(SUPPORTED_AIRLINES.keys())}"
        )

    if matched == "american":
        from automation.airlines.american import run
    elif matched == "delta":
        from automation.airlines.delta import run
    elif matched == "united":
        from automation.airlines.united import run
    elif matched == "spirit":
        from automation.airlines.spirit import run

    print(f"[executor] Routing to handler: {matched}")
    run(page, payload)


def main():
    if len(sys.argv) < 2:
        print("Usage: python automation/booking_executor.py payloads/trip-N.json")
        sys.exit(1)

    payload_path = sys.argv[1]
    print(f"[executor] Loading payload: {payload_path}")
    payload = load_payload(payload_path)

    airline = payload["airline"]
    dep = payload["departure_airport"]
    arr = payload["arrival_airport"]
    date = payload["departure_date"]
    flights = ", ".join(payload["flight_numbers"])
    pax = len(payload["passengers"])

    print(f"[executor] Airline      : {airline}")
    print(f"[executor] Route        : {dep} -> {arr}")
    print(f"[executor] Depart date  : {date}")
    print(f"[executor] Flight(s)    : {flights}")
    print(f"[executor] Passengers   : {pax}")
    print()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # Use installed Chrome (channel="chrome") so aa.com bot detection
        # sees a real browser fingerprint rather than Playwright's Chromium.
        # Falls back to bundled Chromium if Chrome is not installed.
        launch_args = dict(
            headless=False,
            slow_mo=150,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        try:
            browser = p.chromium.launch(channel="chrome", **launch_args)
            print("[executor] Launched: Google Chrome (system install)")
        except Exception:
            browser = p.chromium.launch(**launch_args)
            print("[executor] Launched: Playwright Chromium (Chrome not found)")
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        try:
            route_to_handler(payload, page)
        except Exception as e:
            print(f"\n[executor] ERROR during booking flow: {e}")
            print("[executor] Browser left open for manual inspection.")
            print("[executor] Press Enter to close.")
            try:
                input()
            except EOFError:
                pass
            raise

        print("\n[executor] *** PAUSED BEFORE PAYMENT ***")
        print("[executor] Complete payment manually in the browser.")
        print("[executor] Press Enter here when done (or to abort).")
        try:
            input()
        except EOFError:
            print("[executor] Non-interactive stdin — closing browser.")
            print("[executor] Run manually in your terminal for real bookings.")

        browser.close()
        print("[executor] Browser closed. Booking session complete.")


if __name__ == "__main__":
    main()
