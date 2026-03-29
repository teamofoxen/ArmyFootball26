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
    print(f"[executor] Route        : {dep} → {arr}")
    print(f"[executor] Depart date  : {date}")
    print(f"[executor] Flight(s)    : {flights}")
    print(f"[executor] Passengers   : {pax}")
    print()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            route_to_handler(payload, page)
        except Exception as e:
            print(f"\n[executor] ERROR during booking flow: {e}")
            print("[executor] Browser left open for manual inspection.")
            print("[executor] Press Enter to close.")
            input()
            raise

        print("\n[executor] *** PAUSED BEFORE PAYMENT ***")
        print("[executor] Complete payment manually in the browser.")
        print("[executor] Press Enter here when done (or to abort).")
        input()

        browser.close()
        print("[executor] Browser closed. Booking session complete.")


if __name__ == "__main__":
    main()
