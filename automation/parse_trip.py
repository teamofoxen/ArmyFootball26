"""
parse_trip.py — Parse a trip markdown file into a booking payload dict.

The payload schema is the internal contract; this module produces it from
a trip file so the user doesn't need to maintain a separate JSON file.

Expected confirmed flight format in trip files:

  FLIGHTS ✅ CONFIRMED — American Airlines
  ────────────────────────────────────────
    Out  Fri Sep 11   AA1234   DFW  7:00 AM CT  →  EWR  11:30 AM ET
    Ret  Sun Sep 13   AA5678   EWR  2:00 PM ET  →  DFW   5:30 PM CT
"""

import re
from pathlib import Path

# Month abbreviation → zero-padded number
_MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

# "FLIGHTS ✅ CONFIRMED — Airline Name"
_RE_AIRLINE = re.compile(
    r"FLIGHTS\s.*?CONFIRMED\s*[—\-]+\s*(.+)", re.IGNORECASE
)

# "Out  Fri Sep 11   AA1234   DFW  7:00 AM CT  →  EWR  11:30 AM ET"
# "Ret  Sun Sep 13   AA5678   EWR  2:00 PM ET  →  DFW   5:30 PM CT"
_RE_FLIGHT_LINE = re.compile(
    r"(?P<dir>Out|Ret)\s+"
    r"(?P<dow>\w+)\s+(?P<mon>\w+)\s+(?P<day>\d+)\s+"
    r"(?P<flight>[A-Z]{1,3}\d+)\s+"
    r"(?P<dep>[A-Z]{3})\s+"
    r"[\d:]+\s*[AP]M\s+\w+\s*"   # departure time (consumed, not captured)
    r"[^\w]*"                      # arrow / whitespace
    r"(?P<arr>[A-Z]{3})",
    re.IGNORECASE,
)

# "Date        : Saturday, September 12, 2026"
_RE_GAME_DATE = re.compile(
    r"Date\s*:\s*\w+,\s+\w+\s+\d+,\s+(\d{4})"
)


class TripParseError(ValueError):
    """Raised when required flight data cannot be extracted from a trip file."""


def parse_trip_file(path: str, passengers: int = 1) -> dict:
    """
    Parse a trip markdown file and return a payload dict matching the
    booking executor schema.

    Args:
        path:       Path to the trip .md file.
        passengers: Number of passengers (trip files don't store this;
                    caller supplies it — defaults to 1).

    Returns:
        dict with keys: airline, departure_airport, arrival_airport,
                        departure_date, return_date (optional),
                        flight_numbers, passengers

    Raises:
        TripParseError: if confirmed flight data is missing or incomplete.
        FileNotFoundError: if the file doesn't exist.
    """
    content = Path(path).read_text(encoding="utf-8", errors="replace")

    # ── year ──────────────────────────────────────────────────────────────────
    year_match = _RE_GAME_DATE.search(content)
    year = year_match.group(1) if year_match else None

    # ── airline ───────────────────────────────────────────────────────────────
    airline_match = _RE_AIRLINE.search(content)
    if not airline_match:
        raise TripParseError(
            "No confirmed flight found in trip file.\n"
            "The file must contain a line like:\n"
            "  FLIGHTS [checkmark] CONFIRMED - American Airlines"
        )
    airline = airline_match.group(1).strip()

    # ── outbound / return flight lines ────────────────────────────────────────
    out_match = None
    ret_match = None
    for m in _RE_FLIGHT_LINE.finditer(content):
        if m.group("dir").lower() == "out" and out_match is None:
            out_match = m
        elif m.group("dir").lower() == "ret" and ret_match is None:
            ret_match = m

    if not out_match:
        raise TripParseError(
            "Could not parse outbound flight line.\n"
            "Expected format:\n"
            "  Out  Fri Sep 11   AA1234   DFW  7:00 AM CT  →  EWR  11:30 AM ET"
        )

    def _to_iso(mon_str: str, day_str: str, yr: str) -> str:
        mon_key = mon_str.lower()[:3]
        mon_num = _MONTHS.get(mon_key)
        if not mon_num:
            raise TripParseError(f"Unrecognized month abbreviation: {mon_str!r}")
        if not yr:
            raise TripParseError(
                "Could not determine year from trip file. "
                "Add a 'Date : ..., YYYY' line under GAME DETAILS."
            )
        return f"{yr}-{mon_num}-{int(day_str):02d}"

    dep_airport  = out_match.group("dep").upper()
    arr_airport  = out_match.group("arr").upper()
    dep_date     = _to_iso(out_match.group("mon"), out_match.group("day"), year)
    out_flight   = out_match.group("flight").upper()

    flight_numbers = [out_flight]
    ret_date = ""

    if ret_match:
        ret_date = _to_iso(ret_match.group("mon"), ret_match.group("day"), year)
        ret_flight = ret_match.group("flight").upper()
        flight_numbers.append(ret_flight)

    payload = {
        "airline":           airline,
        "departure_airport": dep_airport,
        "arrival_airport":   arr_airport,
        "departure_date":    dep_date,
        "flight_numbers":    flight_numbers,
        "passengers":        [{"name": f"Traveler {i+1}"} for i in range(passengers)],
    }
    if ret_date:
        payload["return_date"] = ret_date

    return payload
