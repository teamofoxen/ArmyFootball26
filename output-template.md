# Travel Plan Output Template

Use this exact structure for every trip plan. All sections are required.
If real data is unavailable for a section, write: `DATA UNAVAILABLE — [reason]`
Never leave a section blank or fill it with invented information.

---

```
═══════════════════════════════════════════════════════════════
  ARMY BLACK KNIGHTS TRAVEL PLAN
  Trip [#] — [Opponent Name]
═══════════════════════════════════════════════════════════════

GAME DETAILS
────────────────────────────────────────────────────────────────
  Opponent    : [Team Name]
  Date        : [Day, Month DD, YYYY]
  Kickoff     : [Time TZ] | [Network]
  Stadium     : [Stadium Name]
  Location    : [City, State]


OUTBOUND FLIGHT OPTIONS  (rename to DRIVE PLAN for drive trips)
────────────────────────────────────────────────────────────────
  Travel Date : [Outbound Date]
  Route       : [Origin Airport Code] → [Destination Airport Code]
                (Drive trips: [City] → [City] via [Highway], [X hrs / X miles])

  Option 1 (RECOMMENDED)
  ┌─────────────────────────────────────────────────────────┐
  │  Airline     : [Airline Name]                           │
  │  Flight #    : [Flight Number or N/A]                   │
  │  Departs     : [HH:MM AM/PM TZ] from [Airport Code]     │
  │  Arrives     : [HH:MM AM/PM TZ] at [Airport Code]       │
  │  Stops       : [Nonstop / 1 stop: via XXX (Xh Xm lay)]  │
  │  Price       : $[XXX] per person                        │
  └─────────────────────────────────────────────────────────┘

  Option 2
  ┌─────────────────────────────────────────────────────────┐
  │  Airline     : [Airline Name]                           │
  │  Flight #    : [Flight Number or N/A]                   │
  │  Departs     : [HH:MM AM/PM TZ] from [Airport Code]     │
  │  Arrives     : [HH:MM AM/PM TZ] at [Airport Code]       │
  │  Stops       : [Nonstop / 1 stop: via XXX (Xh Xm lay)]  │
  │  Price       : $[XXX] per person                        │
  └─────────────────────────────────────────────────────────┘

  Option 3 (BUDGET)
  ┌─────────────────────────────────────────────────────────┐
  │  Airline     : [Airline Name]                           │
  │  Flight #    : [Flight Number or N/A]                   │
  │  Departs     : [HH:MM AM/PM TZ] from [Airport Code]     │
  │  Arrives     : [HH:MM AM/PM TZ] at [Airport Code]       │
  │  Stops       : [Nonstop / 1 stop: via XXX (Xh Xm lay)]  │
  │  Price       : $[XXX] per person                        │
  └─────────────────────────────────────────────────────────┘


RETURN FLIGHT OPTIONS
────────────────────────────────────────────────────────────────
  Travel Date : [Return Date]
  Route       : [Destination Airport Code] → [Origin Airport Code]

  Option 1 (RECOMMENDED)
  ┌─────────────────────────────────────────────────────────┐
  │  Airline     : [Airline Name]                           │
  │  Flight #    : [Flight Number or N/A]                   │
  │  Departs     : [HH:MM AM/PM TZ] from [Airport Code]     │
  │  Arrives     : [HH:MM AM/PM TZ] at [Airport Code]       │
  │  Stops       : [Nonstop / 1 stop: via XXX (Xh Xm lay)]  │
  │  Price       : $[XXX] per person                        │
  └─────────────────────────────────────────────────────────┘

  Option 2
  ┌─────────────────────────────────────────────────────────┐
  │  Airline     : [Airline Name]                           │
  │  Departs     : [HH:MM AM/PM TZ] from [Airport Code]     │
  │  Arrives     : [HH:MM AM/PM TZ] at [Airport Code]       │
  │  Stops       : [Nonstop / 1 stop: via XXX (Xh Xm lay)]  │
  │  Price       : $[XXX] per person                        │
  └─────────────────────────────────────────────────────────┘


HOTEL OPTIONS
────────────────────────────────────────────────────────────────
  Check-in    : [Outbound Date]
  Check-out   : [Return Date]
  Nights      : [#]

  Option 1 (RECOMMENDED)
  ┌─────────────────────────────────────────────────────────┐
  │  Name        : [Hotel Name]                             │
  │  Chain       : [Marriott / Hilton / Hyatt / Other]      │
  │  Address     : [Address]                                │
  │  Rate        : $[XXX]/night | Total: $[XXX]             │
  │  Distance    : [X.X miles] from [Stadium Name]          │
  │  Parking     : [Free / $XX/night / Not available]       │
  │  Notes       : [Any relevant details]                   │
  └─────────────────────────────────────────────────────────┘

  Option 2
  ┌─────────────────────────────────────────────────────────┐
  │  Name        : [Hotel Name]                             │
  │  Chain       : [Chain]                                  │
  │  Rate        : $[XXX]/night | Total: $[XXX]             │
  │  Distance    : [X.X miles] from [Stadium Name]          │
  │  Parking     : [Free / $XX/night / Not available]       │
  │  Notes       : [Any relevant details]                   │
  └─────────────────────────────────────────────────────────┘

  Option 3 (BUDGET)
  ┌─────────────────────────────────────────────────────────┐
  │  Name        : [Hotel Name]                             │
  │  Chain       : [Chain]                                  │
  │  Rate        : $[XXX]/night | Total: $[XXX]             │
  │  Distance    : [X.X miles] from [Stadium Name]          │
  │  Parking     : [Free / $XX/night / Not available]       │
  │  Notes       : [Any relevant details]                   │
  └─────────────────────────────────────────────────────────┘


GROUND TRANSPORTATION
────────────────────────────────────────────────────────────────
  Mode          : [Uber/Lyft | Rental Car | Drive | Train | Walk]
  Details       : [Specific guidance — pickup point, estimated cost, etc.]
  Backup        : [Alternate option if primary fails]
  Game Day Note : [Any stadium-specific transport tips]


COST SUMMARY
────────────────────────────────────────────────────────────────
  (Based on Option 1 recommendations, 2 adults)

  Flights (RT)    : $[XXX] × 2 = $[XXXX]
  Hotel           : $[XXX]/night × [#] nights = $[XXXX]
  Ground Transit  : ~$[XXX] estimated
  ─────────────────────────────────────────
  ESTIMATED TOTAL : ~$[XXXX]

  Budget Status   : [WITHIN BUDGET / OVER BUDGET — see notes]


RULES COMPLIANCE CHECK
────────────────────────────────────────────────────────────────
  ✓/✗  Flights from real get_flights data (not invented) — N/A for drive trips
  ✓/✗  No layovers exceed 2h 30m
  ✓/✗  No red-eye flights
  ✓/✗  Hotel within 10 miles of stadium
  ✓/✗  Hotel rate within MASTER SETTINGS limits
  ✓/✗  Preferred airline used (or documented why not)
  ✓/✗  Arrive destination ≥ 3 hours before kickoff


NOTES & RECOMMENDATIONS
────────────────────────────────────────────────────────────────
  [Any trip-specific advice, booking urgency, alerts, or exceptions
   to MASTER SETTINGS with clear justification]

═══════════════════════════════════════════════════════════════
  Generated: [Date Generated]
  Data source: SerpAPI (web search) + hotel web search
  Flight data reflects availability at time of query only.
═══════════════════════════════════════════════════════════════
```
