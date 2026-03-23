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
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "ERROR: API key missing"

    usage = _load_usage()
    if usage["count"] >= QUOTA_LIMIT:
        return (
            f"ERROR: SerpAPI monthly quota exhausted ({usage['count']}/{QUOTA_LIMIT} searches used in {usage['month']}). "
            "Wait for next month or upgrade your SerpAPI plan. Do not fabricate flight data."
        )

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f"flights from {origin} to {destination} on {date}",
        "api_key": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.Timeout:
        return "ERROR: Network timeout — SerpAPI did not respond in 10 seconds. Try again."
    except requests.exceptions.ConnectionError as e:
        return f"ERROR: Network connection failed — {e}"
    except Exception as e:
        return f"ERROR: Request failed — {e}"

    if response.status_code == 401:
        return "ERROR: Invalid or missing SerpAPI key. Check your .env file."
    if response.status_code == 429:
        return "ERROR: SerpAPI quota exhausted (100 searches/month on free tier). Upgrade plan or wait for reset."
    if response.status_code >= 500:
        return f"ERROR: SerpAPI server error (HTTP {response.status_code}). Try again later."
    if response.status_code != 200:
        return f"ERROR: Unexpected HTTP {response.status_code} from SerpAPI."

    try:
        data = response.json()
    except Exception:
        return "ERROR: SerpAPI returned non-JSON response. The API may be down."

    # SerpAPI also returns quota/auth errors in the JSON body
    if "error" in data:
        error_msg = data["error"]
        if "credit" in error_msg.lower() or "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return f"ERROR: SerpAPI quota exhausted — {error_msg}"
        return f"ERROR: SerpAPI returned an error — {error_msg}"

    # Successful call — increment usage counter
    usage["count"] += 1
    _save_usage(usage)

    # Extract useful results
    results = []
    for r in data.get("organic_results", [])[:5]:
        results.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet"),
        })

    if not results:
        return "NO RESULTS: SerpAPI returned no organic results for this search. Flight data unavailable — do not fabricate."

    # Attach usage info so Claude can log it; warn if approaching limit
    calls_used = usage["count"]
    remaining = QUOTA_LIMIT - calls_used
    usage_note = f"SERPAPI USAGE: {calls_used}/{QUOTA_LIMIT} searches used this month ({remaining} remaining)."
    if calls_used >= QUOTA_WARN_AT:
        usage_note += f" WARNING: Only {remaining} searches left — plan remaining trips carefully."

    results.append({"_usage": usage_note})

    return results
