"""
validate_trips.py — Structural validator for all 13 trip files.

Checks:
  1. All 13 expected files exist
  2. Status line (line 2) is present and uses a recognized prefix
  3. Required sections are present (PLANNED/BOOKED trips only — STUBs are exempt)

Run any time before a session or after editing trip files:
  python validate_trips.py
"""

import os
import sys

TRIPS_DIR = os.path.join(os.path.dirname(__file__), "trips")

EXPECTED_FILES = [
    "trip-1-bryant.md",
    "trip-2-south-florida.md",
    "trip-3-temple.md",
    "trip-4-louisiana-tech.md",
    "trip-5-tulane.md",
    "trip-6-florida-atlantic.md",
    "trip-7-tulsa.md",
    "trip-8-memphis.md",
    "trip-9-air-force.md",
    "trip-10-east-carolina.md",
    "trip-11-rice.md",
    "trip-12-army-navy.md",
    "trip-13-bowl-game.md",
]

VALID_STATUS_PREFIXES = (
    "**Status: BOOKED",
    "**Status: PARTIALLY BOOKED",
    "**Status: PLANNED",
    "**Status: STUB",
)

# Each entry: (label, [keywords that satisfy the check — any match passes])
# Checked on PLANNED and BOOKED trips only. STUBs are exempt.
REQUIRED_SECTIONS = [
    ("Game details",         ["GAME DETAILS"]),
    ("Transport/drive plan", ["OUTBOUND FLIGHT", "DRIVE PLAN", "TRANSPORT", "RETURN FLIGHT"]),
    ("Hotel section",        ["HOTEL OPTIONS", "HOTEL —"]),
    ("Cost summary",         ["COST SUMMARY", "COST ESTIMATE"]),
    ("Notes section",        ["NOTES &", "NOTES AND"]),
    ("Rules compliance",     ["RULES COMPLIANCE"]),
]


def parse_status(line2: str) -> str:
    """Return the status keyword (BOOKED, PLANNED, PARTIALLY BOOKED, etc.) or 'UNKNOWN'."""
    for prefix in VALID_STATUS_PREFIXES:
        if line2.startswith(prefix):
            # Extract the status keyword after "**Status: "
            rest = line2[len("**Status: "):]
            # "PARTIALLY BOOKED" is two words — detect it before splitting
            if rest.startswith("PARTIALLY BOOKED"):
                return "PARTIALLY BOOKED"
            return rest.split()[0].rstrip("*—-,")
    return "UNKNOWN"


def check_sections(content: str) -> list[str]:
    """Return list of missing section labels."""
    missing = []
    upper = content.upper()
    for label, keywords in REQUIRED_SECTIONS:
        if not any(kw.upper() in upper for kw in keywords):
            missing.append(label)
    return missing




def validate_file(filename: str) -> list[str]:
    """Return list of error strings for a trip file. Empty = clean."""
    path = os.path.join(TRIPS_DIR, filename)
    errors = []

    if not os.path.exists(path):
        return [f"FILE MISSING: {filename}"]

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # Check line 2 exists
    if len(lines) < 2:
        return ["File has fewer than 2 lines — status line missing entirely"]

    line2 = lines[1].strip()

    if not line2:
        errors.append("Line 2 is blank — status line missing")
        return errors  # Can't determine status; stop here

    status = parse_status(line2)

    if status == "UNKNOWN":
        errors.append(
            f"Line 2 has unrecognized status: '{line2[:80]}'\n"
            f"  Expected one of: BOOKED, PARTIALLY BOOKED, PLANNED, STUB"
        )
        return errors  # Can't determine if sections are required; stop here

    # STUBs are exempt from section checks — they're intentionally incomplete
    if status == "STUB":
        return errors

    content = "".join(lines)
    missing = check_sections(content)
    for section in missing:
        errors.append(f"Missing section: {section}")

    return errors


def main():
    print("=" * 60)
    print("TRIP FILE VALIDATION")
    print("=" * 60)

    all_clean = True
    status_summary = {}

    for filename in EXPECTED_FILES:
        path = os.path.join(TRIPS_DIR, filename)
        errors = validate_file(filename)

        # Read status for summary (best-effort)
        status = "MISSING"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) >= 2:
                status = parse_status(lines[1].strip())

        status_summary[filename] = status

        if errors:
            all_clean = False
            print(f"\n  FAIL  {filename}  [{status}]")
            for err in errors:
                print(f"        - {err}")
        else:
            print(f"  OK    {filename}  [{status}]")

    print()
    if all_clean:
        print("All 13 trip files passed validation.")
    else:
        print("Validation failed — see errors above.")
        sys.exit(1)

    # Status summary
    from collections import Counter
    counts = Counter(status_summary.values())
    print()
    print("Status breakdown:")
    for status, count in sorted(counts.items()):
        files = [f for f, s in status_summary.items() if s == status]
        print(f"  {status:<20} {count}  ({', '.join(f.replace('trip-','').replace('.md','') for f in files)})")
    print("=" * 60)


if __name__ == "__main__":
    main()
