"""
booking_executor.py — Step 8: Execute Booking

Accepts either a payload JSON file or a trip markdown file directly.
Launches a Playwright browser, routes to the appropriate airline handler,
and pauses before payment for manual completion.

Usage:
    # From a JSON payload (explicit)
    python automation/booking_executor.py payloads/trip-2.json

    # Directly from a trip file (payload built in memory)
    python automation/booking_executor.py trips/trip-2-south-florida.md

    # Flags
    --debug           Print the generated payload before launching browser
    --save-payload    Write the generated payload to payloads/trip-N.json
    --passengers N    Number of passengers (default: 1; trip files don't store this)
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


# ── input loading ─────────────────────────────────────────────────────────────

def load_input(path: str, passengers: int = 1) -> dict:
    """
    Detect input type and return a validated payload dict.

    .json  → load directly (existing behavior, unchanged)
    .md    → parse confirmed flight section, build payload in memory
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if p.suffix.lower() == ".json":
        print(f"[executor] Input type  : JSON payload")
        with open(p, "r") as f:
            payload = json.load(f)
    elif p.suffix.lower() == ".md":
        print(f"[executor] Input type  : Trip markdown file")
        from automation.parse_trip import parse_trip_file, TripParseError
        try:
            payload = parse_trip_file(path, passengers=passengers)
        except TripParseError as e:
            msg = str(e).encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8")
            print(f"\n[executor] Cannot build payload from trip file:\n  {msg}")
            sys.exit(1)
    else:
        raise ValueError(f"Unsupported input file type: {p.suffix} — use .json or .md")

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


def _save_payload(payload: dict, source_path: str) -> Path:
    """Derive a payload filename from the source path and write it."""
    src = Path(source_path)
    # trip-2-south-florida.md  →  payloads/trip-2.json
    # payloads/trip-2.json     →  payloads/trip-2.json (no-op rewrite)
    stem = src.stem  # e.g. "trip-2-south-florida" or "trip-2"
    trip_id = stem.split("-")[0] + "-" + stem.split("-")[1] if "-" in stem else stem
    out_path = _REPO_ROOT / "payloads" / f"{trip_id}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    return out_path


# ── airline routing ───────────────────────────────────────────────────────────

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


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args(argv):
    """Minimal arg parser — no external dependencies."""
    args = {
        "input": None,
        "debug": False,
        "save_payload": False,
        "passengers": 1,
    }
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--debug":
            args["debug"] = True
        elif arg == "--save-payload":
            args["save_payload"] = True
        elif arg == "--passengers":
            i += 1
            try:
                args["passengers"] = int(argv[i])
            except (IndexError, ValueError):
                print("ERROR: --passengers requires an integer argument")
                sys.exit(1)
        elif not arg.startswith("--"):
            args["input"] = arg
        i += 1
    return args


def main():
    args = _parse_args(sys.argv)

    if not args["input"]:
        print(
            "Usage: python automation/booking_executor.py <input> [--debug] "
            "[--save-payload] [--passengers N]\n"
            "\n"
            "  <input>  Path to a payload JSON file OR a trip markdown file\n"
            "\n"
            "Examples:\n"
            "  python automation/booking_executor.py payloads/trip-2.json\n"
            "  python automation/booking_executor.py trips/trip-2-south-florida.md\n"
            "  python automation/booking_executor.py trips/trip-2-south-florida.md --passengers 3 --debug\n"
        )
        sys.exit(1)

    payload = load_input(args["input"], passengers=args["passengers"])

    # ── summary ───────────────────────────────────────────────────────────────
    airline  = payload["airline"]
    dep      = payload["departure_airport"]
    arr      = payload["arrival_airport"]
    date     = payload["departure_date"]
    ret      = payload.get("return_date", "one-way")
    flights  = ", ".join(payload["flight_numbers"])
    pax      = len(payload["passengers"])

    print(f"[executor] Airline      : {airline}")
    print(f"[executor] Route        : {dep} -> {arr}")
    print(f"[executor] Depart date  : {date}")
    print(f"[executor] Return date  : {ret}")
    print(f"[executor] Flight(s)    : {flights}")
    print(f"[executor] Passengers   : {pax}")

    if args["debug"]:
        print("\n[executor] --- GENERATED PAYLOAD ---")
        print(json.dumps(payload, indent=2))
        print("[executor] --- END PAYLOAD ---\n")

    if args["save_payload"]:
        saved = _save_payload(payload, args["input"])
        print(f"[executor] Payload saved : {saved}")

    print()

    # ── browser ───────────────────────────────────────────────────────────────
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
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

        context = browser.new_context(viewport={"width": 1280, "height": 900})
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
