import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

USAGE_FILE = os.path.join(os.path.dirname(__file__), ".serpapi_usage.json")
QUOTA_LIMIT = 100
QUOTA_WARN_AT = 80


def _load_usage():
    current_month = datetime.now().strftime("%Y-%m")
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE) as f:
            data = json.load(f)
        if data.get("month") == current_month:
            return data
    return {"month": current_month, "count": 0}


def _save_usage(usage):
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)


def get_flights(origin, destination, date):
    """
    Search for flights using SerpAPI Google Flights engine.

    Returns a list of nonstop flight dicts, each with:
      airline, flight_number, departs, arrives, from, to, duration_min, price

    If no nonstops found, falls back to all flights (adds 'stops' key).
    Last item in list is always {'_usage': '...'} with quota info.
    """
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "ERROR: API key missing — set SERPAPI_KEY in .env"

    usage = _load_usage()
    if usage["count"] >= QUOTA_LIMIT:
        return (
            f"ERROR: SerpAPI monthly quota exhausted ({usage['count']}/{QUOTA_LIMIT} "
            f"searches used in {usage['month']}). Wait for next month or upgrade your "
            "SerpAPI plan. Do not fabricate flight data."
        )

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "type": "2",       # one-way
        "currency": "USD",
        "hl": "en",
        "api_key": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.exceptions.Timeout:
        return "ERROR: Network timeout — SerpAPI did not respond in 15 seconds. Try again."
    except requests.exceptions.ConnectionError as e:
        return f"ERROR: Network connection failed — {e}"
    except Exception as e:
        return f"ERROR: Request failed — {e}"

    if response.status_code == 401:
        return "ERROR: Invalid or missing SerpAPI key. Check your .env file."
    if response.status_code == 429:
        return "ERROR: SerpAPI quota exhausted. Upgrade plan or wait for reset."
    if response.status_code >= 500:
        return f"ERROR: SerpAPI server error (HTTP {response.status_code}). Try again later."
    if response.status_code != 200:
        return f"ERROR: Unexpected HTTP {response.status_code} from SerpAPI."

    try:
        data = response.json()
    except Exception:
        return "ERROR: SerpAPI returned non-JSON response. The API may be down."

    if "error" in data:
        error_msg = data["error"]
        if any(w in error_msg.lower() for w in ("credit", "quota", "limit")):
            return f"ERROR: SerpAPI quota exhausted — {error_msg}"
        return f"ERROR: SerpAPI returned an error — {error_msg}"

    # Increment usage counter on successful API call
    usage["count"] += 1
    _save_usage(usage)

    def parse_flight_group(flight_group, require_nonstop=True):
        segs = flight_group.get("flights", [])
        if not segs:
            return None
        if require_nonstop and len(segs) != 1:
            return None
        seg = segs[0]
        result = {
            "airline": seg.get("airline", ""),
            "flight_number": seg.get("flight_number", ""),
            "departs": seg.get("departure_airport", {}).get("time", ""),
            "arrives": seg.get("arrival_airport", {}).get("time", ""),
            "from": seg.get("departure_airport", {}).get("id", origin),
            "to": seg.get("arrival_airport", {}).get("id", destination),
            "duration_min": flight_group.get("total_duration", seg.get("duration", 0)),
            "price": flight_group.get("price"),
        }
        if len(segs) > 1:
            result["stops"] = len(segs) - 1
            result["airline"] = " / ".join(s.get("airline", "") for s in segs)
            result["flight_number"] = " / ".join(s.get("flight_number", "") for s in segs)
            result["arrives"] = segs[-1].get("arrival_airport", {}).get("time", "")
            result["to"] = segs[-1].get("arrival_airport", {}).get("id", destination)
        return result

    all_groups = data.get("best_flights", []) + data.get("other_flights", [])

    # Try nonstops first
    flights = [f for g in all_groups if (f := parse_flight_group(g, require_nonstop=True))]

    # Fall back to all flights if no nonstops found
    if not flights:
        flights = [f for g in all_groups if (f := parse_flight_group(g, require_nonstop=False))]

    if not flights:
        return (
            "NO RESULTS: No flights found for this route/date. "
            "Flight data unavailable — do not fabricate."
        )

    # Sort by price (cheapest first), then by departure time
    flights.sort(key=lambda f: (f.get("price") or 9999, f.get("departs") or ""))

    # Attach usage info
    calls_used = usage["count"]
    remaining = QUOTA_LIMIT - calls_used
    usage_note = f"SERPAPI USAGE: {calls_used}/{QUOTA_LIMIT} searches used this month ({remaining} remaining)."
    if calls_used >= QUOTA_WARN_AT:
        usage_note += f" WARNING: Only {remaining} searches left — plan remaining trips carefully."

    flights.append({"_usage": usage_note})
    return flights
