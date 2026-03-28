# Travel Plan Output Template

Use this exact structure for every trip plan. All sections are required.
If real data is unavailable for a section, write: `DATA UNAVAILABLE — [reason]`
Never leave a section blank or fill it with invented information.

## BOOKING STATUS DEFINITIONS

These are the only valid values for the status line (line 2) of each trip file:

| Status | Meaning |
|--------|---------|
| `BOOKED` | All applicable components confirmed: flight (fly trips) + hotel + rental car (fly trips) |
| `PARTIALLY BOOKED` | One or more applicable components confirmed, but not all |
| `PLANNED` | Full plan exists but nothing has been booked yet |
| `STUB` | Placeholder only — full planning not yet complete |

> **Drive trips** (Louisiana Tech, Tulsa, Rice): BOOKED requires hotel confirmed only — no flight or rental car needed.
> **Fly trips** (all others): BOOKED requires flight + hotel + rental car all confirmed.
> **Rental car exception**: If a fly trip has a confirmed complimentary shuttle or sufficient public transit, the rental car may be waived. Document the waiver explicitly in the status line detail (e.g., `BOOKED — Flight ✅ | Hotel ✅ | Rental car N/A (hotel shuttle)`).

## PARTIALLY BOOKED STRUCTURE

When one or more components are confirmed but others are not:
- Keep OPTIONS sections only for unresolved components
- Replace the OPTIONS section with a CONFIRMED BOOKING section for each resolved component
- Status line: `PARTIALLY BOOKED — [confirmed] | [what remains]`
- For multi-night hotels where nights are confirmed on different dates, use per-night entries (see MULTI-NIGHT HOTEL FORMAT below)

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


FLIGHT OPTIONS — [Origin] ↔ [Destination]  ·  Out: [Day Mon DD]  ·  Ret: [Day Mon DD]
────────────────────────────────────────────────────────────────
  (Drive trips: rename this section to DRIVE PLAN — see drive format below)
  Carrier  : [Airline(s)] · [flight time]
  Rule     : [Any trip-specific routing rule — e.g., search EWR/LGA/JFK, nonstop only]

  OUTBOUND ([Origin] → [Destination])
    1 ★  [AL]  [Dep time TZ]  → [Arr time TZ]  Nonstop  ~$[XXX]/pp
    2    [AL]  [Dep time TZ]  → [Arr time TZ]  Nonstop  ~$[XXX]/pp
    3 ↓  [AL]  1-stop (last resort)                      ~$[XXX]/pp

  RETURN ([Destination] → [Origin])
    1 ★  [AL]  [Dep time TZ]  → [Arr time TZ]  Nonstop  ~$[XXX]/pp
    2 ⚠️  [AL]  [Dep time TZ]  → [Arr time TZ]  Nonstop  ~$[XXX]/pp

  ★ recommended · ↓ last resort, verify layover ≤2.5h · ⚠️ before 2 PM minimum — do not book without override

  (Drive trips — use this format instead of the table above)
  DRIVE PLAN  (rename section header to DRIVE PLAN)
  ────────────────────────────────────────────────────────────────
    Mode        : Personal vehicle — DRIVE (primary)
    Route       : [City] → [City] via [Highway], [X hrs / X miles]

    Outbound — [Day, Date]
    ┌─────────────────────────────────────────────────────────┐
    │  Depart [Origin] : [HH:MM AM/PM TZ]                     │
    │  Arrive [Dest]   : [HH:MM AM/PM TZ]                     │
    │  Route           : [Highway details]                    │
    └─────────────────────────────────────────────────────────┘

    Return — [Day, Date]
    ┌─────────────────────────────────────────────────────────┐
    │  Depart [Dest]   : [HH:MM AM/PM TZ]                     │
    │  Arrive [Origin] : [HH:MM AM/PM TZ]                     │
    └─────────────────────────────────────────────────────────┘


HOTEL OPTIONS  (up to 10 options, sorted closest to stadium first)
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


CONFIRMED BOOKING  (replace OPTIONS section when a component is booked)
────────────────────────────────────────────────────────────────
  FLIGHTS ✅ CONFIRMED — [Airline] · Confirmation: [Code] · $[XXX]/pp × 3 = $[XXXX] total
  ────────────────────────────────────────────────────────────────
    Out  [Day Mon DD]  [FL#]  [Orig]  [Dep TZ] → [Dest] [Arr TZ]  Nonstop [Xh Xm]
    Ret  [Day Mon DD]  [FL#]  [Dest]  [Dep TZ] → [Orig] [Arr TZ]  Nonstop [Xh Xm]
    [⚠️ Any time-sensitive note — e.g., tight connection to rental car counter]

  HOTEL ✅
  ┌─────────────────────────────────────────────────────────┐
  │  Name          : [Hotel Name]                           │
  │  Chain         : [Chain]                                │
  │  Address       : [Address]                              │
  │  Confirmation  : #[Confirmation Number]                 │
  │  Check-in      : [Date]                                 │
  │  Check-out     : [Date]                                 │
  │  Nights        : [#]                                    │
  │  Rate          : $[XXX]/night | Total: $[XXX]           │
  │  Distance      : [X.X miles] from [Stadium Name]        │
  └─────────────────────────────────────────────────────────┘


MULTI-NIGHT HOTEL FORMAT  (use when nights are booked separately)
────────────────────────────────────────────────────────────────
  NIGHT 1 — [Date] — ✅ BOOKED  (or ⚠️ PENDING DECISION / ❌ Not staying)
  ┌─────────────────────────────────────────────────────────┐
  │  Name          : [Hotel Name]                           │
  │  Address       : [Address]                              │
  │  Confirmation  : #[Confirmation Number]                 │
  │  Check-in      : [Date]                                 │
  │  Check-out     : [Date]                                 │
  │  Rate          : $[XXX]/night                           │
  │  Distance      : [X.X miles] from [Stadium Name]        │
  └─────────────────────────────────────────────────────────┘

  NIGHT 2 — [Date] — ⚠️ PENDING DECISION
  ┌─────────────────────────────────────────────────────────┐
  │  Status      : Not booked                               │
  │  Waiting on  : [What decision is pending]               │
  │  Options     : [What the pending choices are]           │
  └─────────────────────────────────────────────────────────┘

  NIGHT [N] OPTIONS (if pending — show options for unresolved nights only)
  [standard Option 1 / Option 2 / Option 3 boxes here]


GROUND TRANSPORTATION
────────────────────────────────────────────────────────────────
  Mode          : [Uber/Lyft | Rental Car | Drive | Train | Walk]
  Details       : [Specific guidance — pickup point, estimated cost, etc.]
  Backup        : [Alternate option if primary fails]
  Game Day Note : [Any stadium-specific transport tips]


COST SUMMARY
────────────────────────────────────────────────────────────────
  (Based on Option 1 recommendations, 3 passengers)

  Flights (RT)    : $[XXX]/person × 3 = $[XXXX]
  Hotel           : $[XXX]/night × [#] nights = $[XXXX]
  Ground Transit  : ~$[XXX] estimated
  ─────────────────────────────────────────
  ESTIMATED TOTAL : ~$[XXXX]

  Budget Status   : [WITHIN BUDGET / OVER BUDGET — see notes]


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
