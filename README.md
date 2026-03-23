# Army Football Travel Execution System — 2026 Season

A Claude Code-based travel planning system for all 13 Army Black Knights football
games. It generates complete, accurate trip plans using real flight data and verified
hotel options, then saves them to structured files for booking reference.

---

## How This System Works

**The application logic lives in `CLAUDE.md`.** This is not a traditional program —
it is a workflow specification executed by Claude Code. When you open this project in
Claude Code and ask it to plan a trip, Claude reads `CLAUDE.md` and follows a
mandatory 7-step workflow to produce a structured travel plan.

```
CLAUDE.md         ← The executable: workflow steps, rules, prohibitions
travel-system.md  ← Configuration: game schedule, master settings, per-trip overrides
output-template.md← Output schema: exact format every trip plan must follow
flights.py        ← API shim: fetches real flight search results via SerpAPI
trips/            ← Database: 13 Markdown files, one per game
logs/             ← Audit trail: session logs written after every action
```

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure your API key**
```bash
cp .env.example .env
# Edit .env and set SERPAPI_KEY=your_actual_key
```
Get a free key at serpapi.com (100 searches/month on the free tier).

**3. Verify**
```bash
python flights.py
```

---

## How to Plan a Trip

Open this project in Claude Code and ask:

```
Plan trip 8
Plan the Memphis game
Plan the October Memphis trip
```

Claude will run the full workflow and save the completed plan to `trips/trip-8-memphis.md`.

---

## Trip Status

Each trip file has a status line (line 2) that Step 0 reads on every session start:

| Status | Meaning |
|--------|---------|
| `BOOKED — ...` | Confirmed reservation exists |
| `PARTIALLY BOOKED — ...` | Some components confirmed, others pending |
| `PLANNED — ...` | Full plan exists, nothing booked yet |
| `STUB` | Placeholder only, needs full planning |

**Do not edit line 2 manually** unless you know what you are doing — Step 0 parses
it to generate the session briefing and URGENT/CRITICAL flags.

---

## Game Schedule

| # | Opponent | Date | Transport |
|---|----------|------|-----------|
| 1 | Bryant (HOME) | Sep 5 | Fly DFW→NYC |
| 2 | South Florida (HOME) | Sep 12 | Fly DFW→NYC |
| 3 | @ Temple | Sep 26 | Fly DFW→PHL |
| 4 | @ Louisiana Tech | Oct 3 | Drive I-20 E |
| 5 | Tulane (HOME) | Oct 10 | Fly DFW→NYC |
| 6 | Florida Atlantic (HOME) | Oct 17 | Fly DFW→NYC |
| 7 | @ Tulsa | Oct 23 (Fri) | Drive US-75 N |
| 8 | @ Memphis | Oct 31 | Fly DFW→MEM |
| 9 | Air Force (HOME) | Nov 7 | Fly DFW→NYC |
| 10 | East Carolina (HOME) | Nov 21 | Fly DFW→NYC |
| 11 | @ Rice | Nov 28 | Drive I-45 S |
| 12 | vs Navy (MetLife) | Dec 12 | Fly DFW→NYC |
| 13 | Bowl Game (TBD) | TBD | TBD |

Full details, airport assignments, and trip-specific rules are in `travel-system.md`.

---

## Key Rules

- **No invented flights** — every flight must come from `flights.py` results
- **No placeholder hotels** — hotels must be found via web search
- **Nonstop first** — connecting flights only if no nonstop exists on any routing
- **Lowest price wins** — among nonstop options, cheapest regardless of airline
- **Choice Hotels preferred** — Comfort Suites, Crowne Plaza, Comfort Inn
- **SerpAPI limit** — free tier is 100 searches/month; budget ~6–8 searches per trip

---

## Secrets

`.env` is gitignored and must never be committed. If you suspect the key was exposed,
rotate it immediately at serpapi.com and update `.env`.
