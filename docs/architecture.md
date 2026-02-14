# Hotel Intel — System Architecture

## Overview

Hotel Intel is composed of two modules that share the same data collection layer but produce different outputs:

- **Module 1: Daily Recap** — Collect → Process → Generate → Deliver
- **Module 2: Guest Intelligence** — Collect → Match → Profile → Alert

Both modules run on local infrastructure at each property to meet security requirements for guest data handling.

```
┌──────────────────────────────────────────────────────────────────┐
│                       HOTEL PROPERTY                              │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  OPERA   │  │   TAC    │  │  7rooms  │  │ Unifocus │  ...     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │              │              │              │               │
│       ▼              ▼              ▼              ▼               │
│  ┌───────────────────────────────────────────────────┐           │
│  │              1. COLLECT                            │           │
│  │        API connectors / file watchers              │           │
│  └──────────┬────────────────────────┬───────────────┘           │
│             │                        │                            │
│     ┌───────▼───────┐       ┌───────▼────────┐                   │
│     │ MODULE 1:     │       │ MODULE 2:      │                   │
│     │ DAILY RECAP   │       │ GUEST INTEL    │                   │
│     │               │       │                │                   │
│     │ 2. Process    │       │ 2. Match       │                   │
│     │    KPIs       │       │    Identity    │                   │
│     │               │       │    Graph       │                   │
│     │ 3. Generate   │       │ 3. Profile     │                   │
│     │    LLM Recap  │       │    Build/Store │                   │
│     │               │       │                │                   │
│     │ 4. Deliver    │       │ 4. Alert       │                   │
│     │    Email/TG   │       │    Arrival     │                   │
│     │               │       │    Briefs      │                   │
│     └───────────────┘       └───────┬────────┘                   │
│                                     │                             │
│                              ┌──────▼──────┐                     │
│                              │  PROFILE DB │                     │
│                              │  (Local)    │                     │
│                              └─────────────┘                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Stage 1: Collect (Shared)

The collection layer connects to each hotel system and pulls relevant data on a scheduled basis (typically nightly or early morning).

| Connector Type | Systems | Method |
|----------------|---------|--------|
| REST API | Oracle OPERA (OHIP), 7rooms, Adyen | Authenticated API calls |
| Calendar API | ERVR (Google Calendar) | Google Calendar API |
| Microsoft Graph | OneDrive, Outlook, Teams, SharePoint | Microsoft Graph API |
| Database / Export | TAC, Micros, Sage, Octane, Spendex | DB read or file export |
| Web / Proprietary | Unifocus Knowcross, Concierge Organizer | Platform-specific API or scraping |
| File System | Local files/folders | File watcher / scheduled scan |

Each connector is a modular component that:
- Authenticates with the source system
- Pulls data for the target date range (typically yesterday + today lookahead)
- Handles retries, rate limits, and error logging
- Outputs a normalized data payload

## Module 1: Daily Recap Pipeline

### Stage 2: Process

Raw data from connectors is normalized into a unified data model:

- **Validation** — Schema checks, data type enforcement, duplicate detection
- **Normalization** — Consistent date formats, currency handling, guest name standardization
- **Computation** — Derived KPIs: occupancy %, ADR, RevPAR, revenue totals, cover counts
- **Storage** — Local database (PostgreSQL or SQLite) for historical comparison and trend detection
- **Enrichment** — Cross-reference data (e.g., VIP arrivals matched with concierge requests, spa bookings)

### Stage 3: Generate

The processed data is fed to an LLM to produce the daily recap:

- **Structured prompt** — Template with sections, KPIs, and priorities
- **Context window** — Yesterday's data + today's lookahead + relevant historical comparisons
- **Tone** — Professional, concise, action-oriented — written for a GM reading on mobile
- **Anomaly highlighting** — AI flags deviations from normal patterns
- **Multi-format output** — Plain text, HTML (for email), structured JSON (for dashboard)

### Stage 4: Deliver

- **Email** — Formatted HTML recap to configured recipients
- **Telegram** — Bot message to hotel management channel/group
- **Dashboard** — Web interface for interactive exploration
- **TTS** — Audio version of the recap (optional)

## Module 2: Guest Intelligence Pipeline

### Stage 2: Match — Guest Identity Graph

The matching engine builds a **guest identity graph** by linking records across all hotel systems:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  OPERA  │     │   TAC   │     │ 7rooms  │
│ "Priya  │     │ "P.     │     │ "Kapoor │
│  Kapoor"│     │  Kapoor" │    │  party"  │
│ Room 106│     │ Room 106│     │          │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     └───────┬───────┘               │
             │    Fuzzy name match   │
             │    + Room match       │
             ▼                       │
     ┌───────────────┐              │
     │  UNIFIED      │◄─────────────┘
     │  GUEST        │   Name match
     │  PROFILE      │
     │  "Priya       │
     │   Kapoor"     │
     └───────────────┘
```

**Matching strategies (in priority order):**

1. **Exact name match** — Same full name across systems
2. **Room number match** — Same room number on same date = same guest
3. **Fuzzy name match** — Levenshtein distance ≤ 2 for typos, abbreviations
4. **Email/phone dedup** — Unique identifiers when available
5. **Temporal correlation** — Booking times that align with stay dates

### Stage 3: Profile — Build & Store

Each matched guest gets a unified profile aggregating data from all sources:

- **Visit history** — All stays with dates, rooms, rates, duration
- **Preferences** — Dietary requirements, room type preferences, pillow type
- **Spa habits** — Favorite treatments, preferred therapists, frequency
- **F&B patterns** — Dining frequency, cuisine preferences, wine/drink orders, average spend
- **Spend history** — Lifetime value across rooms, F&B, spa, concierge
- **Incidents** — Past complaints, resolutions, compensation given
- **Concierge history** — Excursions booked, special requests, vendors used
- **Special occasions** — Birthdays, anniversaries, celebrations
- **Notes** — Free-text observations from any system

Profiles are stored locally as JSON files (one per guest), with a simple index for lookups.

### Stage 4: Alert — Arrival Briefs

When today's arrivals are known (from OPERA), the system:

1. Matches each arriving guest against the profile database
2. Enriches with any new data from current bookings
3. Generates an LLM-powered **arrival brief** per guest

**Example brief (returning guest):**
> "Mrs. Fontaine is returning for her 7th stay (VIP2). She always requests room 117 and has a preference for the Premium Anti-Aging Facial at the spa. Previous visits show she's a regular at On The Rocks (avg check €210). Last visit she had a maintenance issue with her balcony door — ensure it's been serviced. Lifetime spend: €42,000+."

**Example brief (new guest):**
> "Mrs. Kapoor is a first-time guest from India, staying 6 nights in Ocean View Suite. She is vegetarian — please inform F&B. She has a spa booking (Premium Facial) and a dinner reservation at On The Rocks (vegetarian tasting menu). No previous history in our systems."

## LLM Considerations

- Model runs via API call (OpenAI, Anthropic, or similar)
- Only aggregated/anonymized operational data leaves the local network for LLM processing
- Guest PII is stripped or pseudonymized before LLM input
- Future option: local LLM for full on-premise processing

## Local Hosting Model

Hotel Intel runs **on-premise** at each property:

- **Compute** — Small server or VM at the hotel (or hotel group's data center)
- **Database** — Local PostgreSQL/SQLite for operational data + JSON profile store for guest data
- **Network** — Connectors access hotel systems on the local network where possible
- **Outbound only** — External calls limited to: LLM API, email delivery (SMTP), Telegram API
- **No guest PII leaves the property** — LLM receives only aggregated metrics and anonymized summaries

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11+ |
| Scheduler | Cron / Celery / custom scheduler |
| Database | PostgreSQL (primary) or SQLite (lightweight) |
| Profile Store | JSON files (local filesystem) |
| API Framework | FastAPI or Express |
| LLM | OpenAI GPT-4 / Anthropic Claude (via API) |
| Matching | Custom Python (Levenshtein, exact, room-based) |
| Dashboard | Next.js or lightweight SPA |
| Deployment | Docker containers on local server |

## Existing Solutions to Explore

**Mosaic Projects** — An existing data aggregation tool that may overlap with Hotel Intel's collection/processing layers. Potential integration or leverage point to be evaluated during development.
