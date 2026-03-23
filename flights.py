import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_flights(origin, destination, date):
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "ERROR: API key missing"

    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google",
        "q": f"flights from {origin} to {destination} on {date}",
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        return f"ERROR: Request failed - {e}"

    # Extract useful results
    results = []

    for r in data.get("organic_results", [])[:5]:
        results.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet")
        })

    if not results:
        return "No results found."

    return results