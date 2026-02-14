# Hotel Intel — Product Overview

## Vision

Hotel Intel transforms the morning briefing at luxury and palace hotels. Instead of managers manually pulling numbers from a dozen disconnected systems, an AI-powered pipeline collects operational data overnight and delivers a polished, actionable intelligence recap before the first coffee is poured.

## The Problem

Luxury hotels run on 10–15+ software systems that don't talk to each other. Every morning, department heads spend 30–60 minutes hunting through Oracle OPERA, spa platforms, F&B tools, incident logs, and finance systems to piece together yesterday's picture. The result is often incomplete, late, or both.

General managers receive fragmented updates — if they receive them at all. Critical patterns (VIP arrivals coinciding with understaffing, revenue dips, recurring incidents) go unnoticed until it's too late.

## The Solution

Hotel Intel is a SaaS product that:

1. **Connects** to the hotel's existing tech stack via APIs and secure integrations
2. **Aggregates** operational, financial, and guest data from all sources
3. **Generates** an AI-powered daily intelligence recap — clear, concise, prioritized
4. **Delivers** it via email, Telegram, and a web dashboard every morning

No new software for staff to learn. No manual data entry. Just signal, not noise.

## Value Proposition

| For | Value |
|-----|-------|
| **General Managers** | Complete operational picture in 2 minutes instead of 30 |
| **Department Heads** | Cross-departmental visibility without meetings |
| **Ownership / Asset Managers** | Daily financial pulse without bothering on-site teams |
| **Operations Teams** | Proactive issue detection — incidents, staffing gaps, revenue anomalies |

## Target Audience

- **Primary:** Luxury hotels and palace hotels (5-star, palace-rated)
- **Sweet spot:** Properties running Oracle OPERA as their PMS
- **Geography:** International — starting with French luxury market
- **Size:** 30–200 rooms with complex operations (multiple F&B outlets, spa, villas, concierge)

## First Pilot

**Eden Rock — St Barths**

A iconic luxury property in St-Barthélemy with a complex tech stack including Oracle OPERA, TAC spa, 7rooms, Micros, Unifocus Knowcross, Concierge Organizer, villa rentals (ERVR), and the full Microsoft 365 suite. The perfect proving ground for Hotel Intel.

## Business Model

SaaS subscription — per property, per month. Pricing scales with property size and number of integrations activated.

## Current Status

🟡 **Ideation phase** — scoping PMS integrations, defining MVP recap content, researching Oracle OHIP API.


---


# Hotel Intel — System Architecture

## Overview

Hotel Intel follows a four-stage pipeline: **Collect → Process → Generate → Deliver**. The system runs on local infrastructure at each property to meet security requirements for guest data handling.

```
┌─────────────────────────────────────────────────────────┐
│                    HOTEL PROPERTY                        │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │  OPERA   │   │   TAC    │   │  7rooms  │   ...       │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘            │
│       │              │              │                    │
│       ▼              ▼              ▼                    │
│  ┌──────────────────────────────────────────┐           │
│  │           1. COLLECT                      │           │
│  │     API connectors / file watchers        │           │
│  └─────────────────┬────────────────────────┘           │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────┐           │
│  │           2. PROCESS                      │           │
│  │   Normalize, validate, store, compute     │           │
│  └─────────────────┬────────────────────────┘           │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────┐           │
│  │           3. GENERATE                     │           │
│  │      LLM-powered recap generation         │           │
│  └─────────────────┬────────────────────────┘           │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────┐           │
│  │           4. DELIVER                      │           │
│  │    Email / Telegram / Dashboard / TTS     │           │
│  └──────────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Stage 1: Collect

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

## Stage 2: Process

Raw data from connectors is normalized into a unified data model:

- **Validation** — Schema checks, data type enforcement, duplicate detection
- **Normalization** — Consistent date formats, currency handling, guest name standardization
- **Computation** — Derived KPIs: occupancy %, ADR, RevPAR, revenue totals, cover counts
- **Storage** — Local database (PostgreSQL or SQLite) for historical comparison and trend detection
- **Enrichment** — Cross-reference data (e.g., VIP arrivals matched with concierge requests, spa bookings)

## Stage 3: Generate

The processed data is fed to an LLM to produce the daily recap:

- **Structured prompt** — Template with sections, KPIs, and priorities
- **Context window** — Yesterday's data + today's lookahead + relevant historical comparisons
- **Tone** — Professional, concise, action-oriented — written for a GM reading on mobile
- **Anomaly highlighting** — AI flags deviations from normal patterns (unusual occupancy, spike in incidents, revenue outliers)
- **Multi-format output** — Plain text, HTML (for email), structured JSON (for dashboard)

### LLM Considerations

- Model runs via API call (OpenAI, Anthropic, or similar)
- Only aggregated/anonymized operational data leaves the local network for LLM processing
- Guest PII is stripped or pseudonymized before LLM input
- Future option: local LLM for full on-premise processing

## Stage 4: Deliver

See [delivery.md](./delivery.md) for full details on output channels.

- **Email** — Formatted HTML recap to configured recipients
- **Telegram** — Bot message to hotel management channel/group
- **Dashboard** — Web interface for interactive exploration
- **TTS** — Audio version of the recap (optional)

## Local Hosting Model

Hotel Intel runs **on-premise** at each property:

- **Compute** — Small server or VM at the hotel (or hotel group's data center)
- **Database** — Local PostgreSQL/SQLite for all operational data
- **Network** — Connectors access hotel systems on the local network where possible
- **Outbound only** — External calls limited to: LLM API, email delivery (SMTP), Telegram API
- **No guest PII leaves the property** — LLM receives only aggregated metrics and anonymized summaries

## Technology Stack (Preliminary)

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11+ or Node.js |
| Scheduler | Cron / Celery / custom scheduler |
| Database | PostgreSQL (primary) or SQLite (lightweight) |
| API Framework | FastAPI or Express |
| LLM | OpenAI GPT-4 / Anthropic Claude (via API) |
| Dashboard | Next.js or lightweight SPA |
| Deployment | Docker containers on local server |

## Existing Solutions to Explore

**Mosaic Projects** — An existing data aggregation tool that may overlap with Hotel Intel's collection/processing layers. Potential integration or leverage point to be evaluated during development.


---


# Hotel Intel — Integrations

Each integration connects to a hotel system to pull operational data into the Hotel Intel pipeline. This document details every source system, what data we extract, and the known integration method.

---

## Oracle OPERA (PMS)

**Category:** Property Management System
**Priority:** 🔴 Critical — primary data source

### What It Does
Oracle OPERA is the industry-standard PMS for luxury and palace hotels. It manages reservations, guest profiles, room inventory, billing, and reporting.

### Data We Pull
- **Occupancy** — Rooms occupied, available, out of order
- **ADR** (Average Daily Rate) — Revenue per occupied room
- **RevPAR** (Revenue Per Available Room)
- **Arrivals** — Today's check-ins with guest details, room assignments, special requests
- **Departures** — Today's check-outs
- **In-house guests** — Current guest count and profile data
- **VIP guests** — VIP-flagged arrivals and in-house guests (VIP level, preferences, notes)
- **Revenue** — Room revenue, ancillary revenue breakdowns
- **Rate codes & segments** — Booking source analysis

### Integration Method
- **API:** Oracle Hospitality Integration Platform (OHIP) — REST APIs
- **Authentication:** OAuth 2.0 (client credentials flow)
- **Endpoints:** OHIP provides dedicated endpoints for reservations, availability, guest profiles, rate plans, and financial postings
- **Environment:** Oracle Cloud or on-premise OPERA — OHIP availability depends on OPERA version and Oracle licensing
- **Notes:** OPERA Cloud has better API support than legacy OPERA 5 (on-prem). Eden Rock's deployment type needs confirmation. RNA (Report and Analytics) module may provide additional reporting endpoints.

---

## TAC (Spa)

**Category:** Spa Management

### What It Does
TAC is a spa management platform handling bookings, treatments, therapist scheduling, and spa retail.

### Data We Pull
- **Spa bookings** — Today's appointments, therapist assignments
- **Spa revenue** — Treatment revenue, retail sales
- **Utilization** — Treatment room and therapist utilization rates
- **Lookahead** — Upcoming bookings for capacity planning

### Integration Method
- **API:** To be determined — TAC may offer a REST API or require database-level access
- **Fallback:** Scheduled data export (CSV/Excel) or direct database read
- **Notes:** Integration method depends on TAC version and deployment. Needs vendor discussion.

---

## 7rooms (F&B Reservations)

**Category:** Food & Beverage — Reservations

### What It Does
7rooms (SevenRooms) is a restaurant reservation and guest management platform used by hotel F&B outlets.

### Data We Pull
- **Covers** — Total covers per outlet, per service (breakfast, lunch, dinner)
- **Reservations** — Booking count, walk-ins, no-shows, cancellations
- **VIP diners** — Flagged guests, special occasions
- **Revenue per cover** (if available)
- **Outlet performance** — Comparison across multiple restaurants/bars

### Integration Method
- **API:** SevenRooms API (REST) — well-documented public API
- **Authentication:** API key + secret
- **Endpoints:** Reservations, venues, guests, availability
- **Documentation:** [SevenRooms API Docs](https://api.sevenrooms.com)
- **Notes:** Good API with webhooks support. Likely one of the easier integrations.

---

## Micros (F&B Payments)

**Category:** Food & Beverage — Point of Sale

### What It Does
Oracle MICROS (Simphony) is the POS system for hotel restaurants, bars, and room service. Handles orders, payments, and F&B operational data.

### Data We Pull
- **F&B revenue** — Per outlet, per service period
- **Transaction data** — Payment totals, average check size
- **Menu mix** — Top-selling items (if relevant for recap)
- **Meal period performance** — Breakfast vs lunch vs dinner revenue

### Integration Method
- **API:** Oracle MICROS Simphony Transaction Services API or Reporting API
- **Authentication:** Oracle identity management (may be bundled with OHIP)
- **Fallback:** Database export or MICROS reporting module
- **Notes:** As an Oracle product, Micros may integrate more smoothly alongside OPERA via OHIP. Check if OHIP provides consolidated access.

---

## Unifocus Knowcross (Incident Management)

**Category:** Operations — Incident & Task Management

### What It Does
Unifocus Knowcross is a hotel operations platform for managing guest incidents, maintenance tasks, housekeeping, and service recovery.

### Data We Pull
- **Open incidents** — Unresolved guest complaints, maintenance issues
- **Closed incidents** — Yesterday's resolved issues with resolution time
- **Task completion** — Housekeeping, engineering, and operational task status
- **Service recovery** — Compensation or follow-up actions taken
- **Trends** — Recurring incident categories (noise complaints, AC issues, etc.)

### Integration Method
- **API:** Unifocus/Knowcross platform API (to be confirmed)
- **Fallback:** Scheduled report export or email-based reporting
- **Notes:** Integration method depends on Unifocus's current API offering. May require partnership discussion.

---

## Concierge Organizer

**Category:** Concierge Management

### What It Does
Concierge Organizer manages guest requests, restaurant bookings, activity reservations, transportation, and other concierge services.

### Data We Pull
- **Guest requests** — Volume and type of concierge requests
- **Request categories** — Restaurant bookings, transfers, tours, tickets, special arrangements
- **Fulfillment status** — Open vs completed requests
- **VIP requests** — Special arrangements for VIP guests
- **Popular services** — Most requested activities/services

### Integration Method
- **API:** To be determined — likely proprietary API or database access
- **Fallback:** Data export or direct database query
- **Notes:** Concierge Organizer is a niche product — integration method needs vendor engagement.

---

## ERVR — Eden Rock Villa Rental (Google Calendar)

**Category:** Villa Rental Management

### What It Does
ERVR manages villa rental bookings for Eden Rock's "Petit Maison" and other villa properties. Bookings are tracked via Google Calendar.

### Data We Pull
- **Villa bookings** — Current and upcoming villa occupancy
- **Check-ins / check-outs** — Villa arrivals and departures
- **Occupancy rates** — Villa utilization
- **Revenue** (if stored in calendar events or linked system)

### Integration Method
- **API:** Google Calendar API (REST)
- **Authentication:** OAuth 2.0 (Google service account or user consent)
- **Endpoints:** Events list, calendar metadata
- **Notes:** Calendar events need a consistent naming/tagging convention to reliably extract booking data. This is Eden Rock-specific — other properties may use different villa management tools.

---

## Microsoft 365

**Category:** Collaboration & Productivity

Covers four sub-integrations via the Microsoft Graph API:

### OneDrive
- **Data:** Shared documents, reports, spreadsheets that contain operational data
- **Use case:** Hotels often store daily reports, financial summaries, or operational checklists in shared OneDrive folders
- **Method:** Microsoft Graph API — Files endpoints

### Outlook
- **Data:** Key emails (supplier communications, guest pre-arrival requests, internal reports)
- **Use case:** Monitor specific mailboxes or folders for operational intelligence
- **Method:** Microsoft Graph API — Mail endpoints

### Teams
- **Data:** Channel messages, important announcements, shift handover notes
- **Use case:** Capture operational communications from Teams channels (e.g., #front-desk, #housekeeping)
- **Method:** Microsoft Graph API — Teams/Channels endpoints

### SharePoint
- **Data:** Shared documents, lists, operational databases stored in SharePoint
- **Use case:** Hotels use SharePoint for SOPs, checklists, and shared operational data
- **Method:** Microsoft Graph API — Sites/Lists endpoints

### Integration Method (All M365)
- **API:** Microsoft Graph API (REST)
- **Authentication:** OAuth 2.0 with Azure AD app registration
- **Permissions:** Application permissions (daemon/background) or delegated with admin consent
- **Notes:** Single Azure AD app registration covers all four services. Scope permissions carefully — principle of least privilege.

---

## Sage (Finance)

**Category:** Finance & Accounting

### What It Does
Sage handles financial accounting, general ledger, accounts payable/receivable, and financial reporting for the property.

### Data We Pull
- **Daily revenue summary** — Total revenue by department
- **Payroll data** — Staff costs, overtime (via Sage HR/Payroll module)
- **P&L indicators** — Key financial metrics for the daily recap
- **Budget vs actual** — Variance reporting

### Integration Method
- **API:** Sage API (REST) — depends on Sage product version (Sage 100, Sage X3, Sage Intacct)
- **Authentication:** OAuth 2.0 or API key (version-dependent)
- **Notes:** Sage has multiple product lines with different API capabilities. Need to confirm which Sage product Eden Rock uses.

---

## Adyen (Payments)

**Category:** Payment Processing

### What It Does
Adyen is the credit card processing gateway handling guest payments across all hotel touchpoints.

### Data We Pull
- **Transaction volume** — Number and value of transactions
- **Payment methods** — Card types, digital wallets
- **Settlement data** — Daily settlement amounts
- **Chargebacks / disputes** — Flagged transactions requiring attention

### Integration Method
- **API:** Adyen API (REST) — well-documented, enterprise-grade
- **Authentication:** API key + HMAC signature
- **Endpoints:** Payments, settlements, reports
- **Documentation:** [Adyen API Docs](https://docs.adyen.com)
- **Notes:** Adyen has excellent API documentation and sandbox environment. Relatively straightforward integration.

---

## Octane (HR — Time Logging)

**Category:** Human Resources

### What It Does
Octane handles employee time tracking and attendance logging.

### Data We Pull
- **Attendance** — Staff present, absent, late
- **Hours worked** — Department-level staffing hours
- **Overtime** — Overtime hours flagged
- **Staffing levels** — Actual vs scheduled staffing

### Integration Method
- **API:** To be determined — depends on Octane product/version
- **Fallback:** Scheduled data export
- **Notes:** HR data is sensitive — ensure only aggregated staffing metrics are included in recaps, not individual employee data.

---

## Spendex (Expenses)

**Category:** Expense Management

### What It Does
Spendex manages employee expense submissions, approvals, and reimbursements.

### Data We Pull
- **Expense volume** — Total submitted expenses
- **Categories** — Expense breakdown by type
- **Pending approvals** — Outstanding expense approvals
- **Budget tracking** — Department spend vs budget

### Integration Method
- **API:** To be determined
- **Fallback:** Scheduled data export or email digest
- **Notes:** Lower priority for daily recap — may be more relevant for weekly/monthly summaries.

---

## File System (FS)

**Category:** Local Files

### What It Does
Direct access to specific files and folders on the hotel's local network or shared drives that contain operational data not available via other integrations.

### Data We Pull
- Custom reports exported by hotel staff
- Spreadsheets with manual data entry
- PDF reports from legacy systems

### Integration Method
- **Method:** File system watcher / scheduled directory scan
- **Formats:** CSV, Excel (.xlsx), PDF (with text extraction)
- **Notes:** Catch-all for data that doesn't come through a proper API. Define specific watched paths per property.

---

## Integration Priority (MVP)

| Priority | System | Reason |
|----------|--------|--------|
| 🔴 P0 | Oracle OPERA (OHIP) | Core PMS — occupancy, revenue, guests |
| 🟠 P1 | TAC, 7rooms, Unifocus Knowcross | Key operational systems |
| 🟡 P2 | ERVR, Concierge Organizer, Microsoft 365 | Important but secondary |
| 🟢 P3 | Sage, Adyen, Micros, Octane, Spendex | Financial/HR — phase 2 |


---


# Hotel Intel — Daily Recap

## Overview

The daily recap is the core output of Hotel Intel. It's an AI-generated intelligence briefing delivered every morning, designed to give hotel leadership a complete operational picture in under 2 minutes.

**Delivery time:** 06:00–07:00 local time (configurable)
**Covers:** Yesterday's actuals + today's lookahead
**Tone:** Professional, concise, action-oriented. Written for a GM reading on mobile.

---

## Recap Structure

### 1. 🔑 Executive Summary

A 3–5 sentence AI-generated overview of the most important things to know today. Highlights anomalies, key arrivals, and anything requiring attention.

> *Example: "Occupancy hit 94% yesterday with ADR at €1,240 — both above monthly average. Three VIP arrivals today including [Guest Name], returning guest (4th stay). Two open incidents from last night require follow-up. Spa is fully booked through Saturday."*

---

### 2. 📊 Key Performance Indicators

| Metric | Description | Source |
|--------|-------------|--------|
| **Occupancy %** | Rooms occupied / rooms available | OPERA |
| **ADR** | Average Daily Rate — room revenue / rooms sold | OPERA |
| **RevPAR** | Revenue Per Available Room — room revenue / total rooms | OPERA |
| **Total Revenue** | All-department revenue (rooms + F&B + spa + other) | OPERA + Sage |
| **Room Revenue** | Rooms department only | OPERA |

Displayed with:
- Yesterday's actual
- Same day last week
- Same day last year (if available)
- Month-to-date cumulative
- Budget variance (if budget data available)

---

### 3. 🛎️ Arrivals & Departures

**Today's Arrivals:**
- Total arriving guests / rooms
- VIP arrivals (flagged with VIP level, stay history, preferences)
- Special requests or notes
- Group arrivals (if any)
- Room assignments status

**Today's Departures:**
- Total departing guests / rooms
- Late check-outs
- Notable departures

**In-House:**
- Current house count
- Notable in-house guests

*Source: Oracle OPERA*

---

### 4. ⭐ VIP Watch

Dedicated section for VIP guests — the detail luxury hotels care most about:

- VIP arrivals today with profile summary
- Return guest indicator (Nth stay)
- Known preferences and special arrangements
- Birthday/anniversary alerts
- Connected concierge requests
- VIP departures (for farewell arrangements)

*Source: OPERA + Concierge Organizer*

---

### 5. 🍽️ Food & Beverage

Per outlet (e.g., "Sand Bar," "Jean-Georges," "Room Service"):

| Metric | Description |
|--------|-------------|
| **Covers** | Total covers per service period (breakfast, lunch, dinner) |
| **Reservations** | Booked vs walk-in ratio |
| **No-shows** | Reservation no-show count |
| **Revenue** | F&B revenue by outlet |
| **Average check** | Revenue per cover |

**Today's lookahead:**
- Expected covers per outlet
- Notable reservations (VIPs, large parties, special events)

*Source: 7rooms + Micros*

---

### 6. 💆 Spa & Wellness

| Metric | Description |
|--------|-------------|
| **Bookings** | Total spa appointments yesterday |
| **Revenue** | Treatment revenue + retail |
| **Utilization** | Treatment room / therapist utilization % |
| **Retail** | Spa product sales |

**Today's lookahead:**
- Today's booking count and capacity remaining
- Peak hours

*Source: TAC*

---

### 7. 🏠 Villa Bookings (Eden Rock Specific)

- Current villa occupancy
- Villa check-ins / check-outs today
- Upcoming villa bookings (next 7 days)
- Villa revenue (if available)

*Source: ERVR (Google Calendar)*

---

### 8. 🚨 Incidents & Issues

- **Open incidents** — Unresolved from yesterday or earlier
- **New incidents** — Logged yesterday
- **Resolved** — Closed yesterday with resolution time
- **Categories** — Breakdown by type (maintenance, noise, service, etc.)
- **Recurring patterns** — AI flags if the same issue type keeps appearing

*Source: Unifocus Knowcross*

---

### 9. 🎩 Concierge Activity

- **Request volume** — Total requests yesterday
- **Top categories** — Restaurant bookings, transfers, activities, etc.
- **Open requests** — Pending fulfillment
- **Notable arrangements** — Special or high-effort requests

*Source: Concierge Organizer*

---

### 10. 👥 Staffing Overview (Phase 2)

- Staff on duty today by department
- Actual vs scheduled
- Overtime alerts
- Key absences

*Source: Octane + Sage*

---

### 11. 💰 Financial Snapshot (Phase 2)

- Daily revenue summary by department
- Payment processing summary (Adyen)
- Budget vs actual variance
- Expense flags

*Source: Sage + Adyen + Spendex*

---

## AI-Powered Insights

Beyond presenting data, the AI layer adds:

- **Anomaly detection** — "Occupancy dropped 15% vs same day last year"
- **Correlation alerts** — "High VIP count today + spa fully booked = potential availability issue"
- **Trend summaries** — "Third consecutive day of declining F&B covers at lunch"
- **Action suggestions** — "Consider opening additional lunch seating given arrival count"
- **Weather context** — Local weather integrated for outdoor dining / activity planning

---

## Recap Formats

| Channel | Format | Details |
|---------|--------|---------|
| **Email** | HTML | Fully formatted with tables, color coding, sections |
| **Telegram** | Markdown | Condensed version optimized for mobile reading |
| **Dashboard** | Interactive | Clickable sections, drill-down, historical comparison |
| **TTS** | Audio | Spoken summary — executive summary + KPIs + highlights |

---

## Customization

Each property can configure:

- Which sections to include/exclude
- KPI thresholds for anomaly flagging
- VIP level threshold for the VIP Watch section
- Recipients per channel
- Delivery time
- Language (multi-language support planned)


---


# Hotel Intel — Delivery Channels

## Overview

Hotel Intel delivers the daily recap through multiple channels simultaneously. Each channel is optimized for its context — detailed HTML for email, concise markdown for Telegram, interactive data for the dashboard, and a spoken summary for TTS.

---

## 📧 Email

**Primary channel for most users.**

### Format
- **HTML email** with responsive design (mobile-first)
- Branded header with hotel logo and date
- Collapsible sections (where email clients support it)
- Color-coded KPIs: 🟢 above target, 🟡 on target, 🔴 below target
- Tables for numerical data, prose for AI insights
- Footer with link to dashboard for drill-down

### Delivery
- **Method:** SMTP or transactional email service (SendGrid, Postmark, SES)
- **Schedule:** Configurable — default 06:30 local time
- **Recipients:** Configurable per property — GM, department heads, ownership
- **Reply handling:** Future — reply to email to ask follow-up questions

### Example Structure
```
Subject: 🏨 Hotel Intel — Eden Rock — Feb 13, 2026

[Executive Summary - 3-5 sentences]

📊 KPIs
┌──────────┬───────────┬──────────┬──────────┐
│ Metric   │ Yesterday │ Last Wk  │ Budget   │
├──────────┼───────────┼──────────┼──────────┤
│ Occ %    │ 94%       │ 87%      │ 90%      │
│ ADR      │ €1,240    │ €1,180   │ €1,200   │
│ RevPAR   │ €1,166    │ €1,027   │ €1,080   │
└──────────┴───────────┴──────────┴──────────┘

[Arrivals & VIPs]
[F&B Summary]
[Spa Summary]
[Incidents]
...

→ View full dashboard: https://intel.hotel/dashboard
```

---

## 💬 Telegram Bot

**Fast, mobile-first delivery for on-the-go managers.**

### Format
- **Markdown messages** optimized for Telegram's rendering
- Shorter than email — executive summary + KPIs + highlights only
- Emoji-driven section headers for scannability
- Inline keyboard buttons for "Show more" on each section

### Bot Features
- **Daily push** — Automated morning recap to configured group or individual chats
- **On-demand queries** — "What's today's occupancy?" / "VIP arrivals?" / "Spa status?"
- **Alerts** — Push notifications for urgent items (critical incidents, VIP last-minute changes)
- **Follow-up** — Ask questions about the recap and get AI-powered answers

### Delivery
- **Method:** Telegram Bot API
- **Schedule:** Same as email, or slight offset (e.g., 06:35)
- **Recipients:** Telegram group (e.g., "Eden Rock Management") and/or individual DMs
- **Interaction:** Users can reply to the bot for clarifications

### Bot Commands
```
/recap       — Get today's full recap
/kpi         — KPIs only
/arrivals    — Today's arrivals & VIPs
/fnb         — F&B summary
/spa         — Spa status
/incidents   — Open incidents
/help        — Available commands
```

---

## 📊 Dashboard

**Interactive web interface for deep dives.**

### Features
- **Today view** — Current day's recap in interactive format
- **Historical** — Browse past days, compare periods
- **Drill-down** — Click any metric to see underlying data
- **Charts** — Trend lines for KPIs over time (7d, 30d, 90d, YTD)
- **Filters** — By department, date range, metric type
- **Export** — Download data as CSV/Excel/PDF

### Access
- **URL:** Property-specific (e.g., `https://intel.edenrock.local/dashboard`)
- **Auth:** SSO via Microsoft 365 or username/password
- **Mobile responsive** — Usable on tablets and phones
- **Hosted locally** — Runs on the same on-premise server as the pipeline

### Dashboard Sections
1. Executive summary card
2. KPI scorecards with sparklines
3. Arrivals/departures timeline
4. F&B covers by outlet (bar chart)
5. Spa utilization gauge
6. Incident status board
7. Concierge request feed
8. Villa occupancy calendar

---

## 🔊 TTS / Speech (Optional)

**Listen to the recap instead of reading it.**

### Use Case
- GM listens during morning commute or while walking the property
- Hands-free briefing during breakfast
- Accessibility option

### Format
- AI-generated audio from the executive summary + key highlights
- Duration target: 2–3 minutes
- Natural voice (not robotic) — ElevenLabs or similar TTS service

### Delivery
- **Telegram voice message** — Attached to the daily bot message
- **Email attachment** — MP3 or link to audio file
- **Dashboard** — Play button on the recap page

---

## 🤖 AI Interaction (Future)

Beyond passive delivery, Hotel Intel will support interactive queries:

- **Audio input** — Ask questions verbally, get spoken answers
- **Email replies** — Reply to the recap email with a question
- **Telegram chat** — Conversational follow-ups with the bot
- **Actions** — "Send a welcome email to VIP arriving today" / "Add a calendar event for the wine dinner"

### Planned Capabilities
- Send emails on behalf of hotel staff
- Create calendar events
- Send SMS to guests (with approval workflow)
- Trigger tasks in operational systems

---

## Channel Comparison

| Feature | Email | Telegram | Dashboard | TTS |
|---------|-------|----------|-----------|-----|
| Full recap | ✅ | Condensed | ✅ Interactive | Summary only |
| Mobile optimized | ✅ | ✅ | ✅ | ✅ |
| Real-time alerts | ❌ | ✅ | ✅ | ❌ |
| Interactive queries | Future | ✅ | ✅ | Future |
| Historical data | ❌ | ❌ | ✅ | ❌ |
| Offline access | ✅ | ✅ | ❌ | ✅ (downloaded) |
| Setup complexity | Low | Low | Medium | Low |

---

## Configuration

Per property, configure:

```yaml
delivery:
  email:
    enabled: true
    time: "06:30"
    recipients:
      - gm@edenrock.com
      - ops@edenrock.com
    format: full  # full | summary
  
  telegram:
    enabled: true
    time: "06:35"
    chat_id: "-100123456789"
    format: summary
    interactive: true
  
  dashboard:
    enabled: true
    url: "https://intel.edenrock.local"
    auth: microsoft365
  
  tts:
    enabled: false
    voice: "elevenlabs:rachel"
    duration_target: 180  # seconds
```


---


# Hotel Intel — MVP & Roadmap

## MVP Philosophy

Ship the smallest version that delivers real value to Eden Rock's GM every morning. One integration, one output channel, one property. Then iterate.

---

## Phase 1: MVP (v1.0)

**Goal:** Daily AI recap with core hotel data, delivered via email and Telegram.

### Integrations (MVP)

| System | Data | Priority |
|--------|------|----------|
| Oracle OPERA (OHIP) | Occupancy, ADR, RevPAR, arrivals, departures, VIPs, revenue | P0 — first |
| TAC | Spa bookings, revenue | P1 |
| 7rooms | F&B covers, reservations | P1 |
| Unifocus Knowcross | Incidents, tasks | P1 |
| ERVR (Google Calendar) | Villa bookings | P1 |
| Concierge Organizer | Guest requests | P1 |
| Microsoft 365 | OneDrive/Outlook — specific files/reports | P2 |
| File System | Watched folders for manual reports | P2 |

### Recap Sections (MVP)
- ✅ Executive summary (AI-generated)
- ✅ KPIs: occupancy, ADR, RevPAR
- ✅ Arrivals & departures
- ✅ VIP watch
- ✅ F&B covers per outlet
- ✅ Spa bookings & utilization
- ✅ Villa bookings
- ✅ Open incidents
- ✅ Concierge activity summary

### Delivery (MVP)
- ✅ Email (HTML formatted)
- ✅ Telegram bot (condensed recap + basic commands)
- ❌ Dashboard (Phase 2)
- ❌ TTS (Phase 2)

### Infrastructure (MVP)
- Local server at Eden Rock (Docker-based)
- PostgreSQL database
- Scheduled pipeline (cron — runs at 05:00, delivers at 06:30)
- LLM via API (Claude or GPT-4)

### MVP Success Criteria
- [ ] GM receives the recap every morning by 06:30
- [ ] Data is accurate and matches source systems
- [ ] Recap is read and found useful (qualitative feedback)
- [ ] System runs reliably for 30 consecutive days
- [ ] <5 minutes of manual intervention per week

---

## Phase 2: Enhanced (v1.5)

**Goal:** Dashboard, more integrations, interactive queries.

### New Features
- 📊 Web dashboard with historical data and charts
- 🔊 TTS audio recap (Telegram voice message + email attachment)
- 💬 Telegram bot interactive queries ("What's today's occupancy?")
- 📈 Trend analysis (7-day, 30-day comparisons)
- ⚠️ Real-time alerts for critical incidents

### New Integrations
- Micros (F&B payment data)
- Sage (financial summary)
- Adyen (payment processing data)
- Microsoft 365 Teams (operational channel monitoring)
- Microsoft 365 SharePoint (shared operational documents)

### Recap Enhancements
- Staffing overview (from Octane)
- Financial snapshot (from Sage + Adyen)
- Weather integration
- Budget vs actual comparison

---

## Phase 3: Multi-Property (v2.0)

**Goal:** Scale to additional properties. Multi-tenant architecture.

### Features
- Multi-property dashboard with portfolio view
- Property comparison metrics
- Centralized management console
- Self-service onboarding for new integrations
- White-label option
- Role-based access (GM vs department head vs owner)

### AI Enhancements
- Cross-property benchmarking
- Predictive analytics (occupancy forecasting, demand prediction)
- Automated action suggestions with approval workflow
- Email/SMS sending on behalf of staff
- Calendar event creation

---

## Phase 4: Platform (v3.0)

**Goal:** Full intelligence platform for luxury hospitality.

### Features
- Marketplace of integrations (plug-and-play connectors)
- Custom recap templates per role
- Guest journey tracking (cross-system guest timeline)
- Revenue management insights
- Competitive intelligence integration
- Mobile app (native)
- Local LLM option for fully on-premise AI processing

---

## Development Timeline (Estimated)

| Phase | Scope | Timeline |
|-------|-------|----------|
| **Phase 1 (MVP)** | OPERA integration + core recap + email/Telegram | 8–12 weeks |
| **Phase 2** | Dashboard + more integrations + interactive bot | +8–12 weeks |
| **Phase 3** | Multi-property + portfolio view | +12–16 weeks |
| **Phase 4** | Platform + marketplace | +6 months |

### MVP Sprint Breakdown

| Sprint | Focus |
|--------|-------|
| Sprint 1 (2w) | OPERA OHIP API research, auth setup, data mapping |
| Sprint 2 (2w) | OPERA connector — pull occupancy, arrivals, revenue |
| Sprint 3 (2w) | Data processing pipeline + LLM recap generation |
| Sprint 4 (2w) | Email + Telegram delivery |
| Sprint 5 (2w) | Additional connectors (TAC, 7rooms, Unifocus) |
| Sprint 6 (2w) | ERVR, Concierge Organizer, M365 connectors + polish |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OPERA OHIP API access delays | Blocks MVP | Start API application early; prepare mock data pipeline |
| TAC/Knowcross lack APIs | Missing data sources | Fall back to file export or database access |
| LLM hallucination in recap | Incorrect data reported | Structured prompts with data validation; human review period |
| Local server reliability | Missed recaps | Monitoring + alerting; fallback to cloud delivery |
| Data quality issues | Inaccurate KPIs | Validation layer with sanity checks and source comparison |

---

## Open Questions

- [ ] Which Oracle OPERA version does Eden Rock run? (Cloud vs on-prem)
- [ ] OHIP API licensing — is it included or additional cost?
- [ ] TAC integration method — API available?
- [ ] Concierge Organizer integration method?
- [ ] Mosaic Projects — evaluate for potential leverage in data aggregation
- [ ] Server specifications for local hosting at Eden Rock
- [ ] Budget data availability for variance reporting


---


# Hotel Intel — Security & Privacy

## Overview

Hotel Intel handles sensitive guest data from luxury hotels — names, preferences, spending patterns, stay history. Security is not optional; it's a core product requirement. The architecture is designed around **local hosting** to keep guest PII within the property's control.

---

## Local Hosting Model

### Principle
All guest data stays on-premise. The Hotel Intel pipeline runs on a server physically located at (or controlled by) the hotel property.

### Architecture

```
┌─────────────── Hotel Network ───────────────┐
│                                              │
│  Hotel Systems ←→ Hotel Intel Server         │
│  (OPERA, TAC,      (pipeline, DB,            │
│   7rooms, etc.)      dashboard)              │
│                                              │
│         │ Outbound only (encrypted)          │
└─────────┼────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │ External APIs │
   │ - LLM API    │
   │ - SMTP       │
   │ - Telegram   │
   └──────────────┘
```

### What Stays Local
- ✅ Raw data from all hotel systems
- ✅ Guest PII (names, profiles, preferences, stay history)
- ✅ Financial data (revenue, transactions, payroll)
- ✅ Incident details
- ✅ Historical database
- ✅ Dashboard and web interface

### What Leaves the Network
- ⚠️ **LLM API calls** — Aggregated metrics and anonymized summaries only (no raw PII)
- ⚠️ **Email delivery** — Recap content sent via SMTP (contains operational summaries, not raw guest data)
- ⚠️ **Telegram messages** — Condensed recap (operational metrics, no guest PII in standard recap)
- ⚠️ **TTS API** — Summary text only

---

## Data Classification

| Level | Description | Examples | Handling |
|-------|-------------|----------|----------|
| **Restricted** | Guest PII | Names, contact info, payment details, preferences | Local only. Never sent to LLM or external services. |
| **Confidential** | Operational data | Revenue figures, occupancy rates, incident details | Local storage. Aggregated/anonymized before external API calls. |
| **Internal** | Generated content | AI recap text, KPI summaries | Can be delivered via email/Telegram to authorized recipients. |
| **Public** | None | — | Hotel Intel handles no public data. |

---

## PII Handling

### Before LLM Processing

Guest PII is stripped or pseudonymized before any data leaves the local network:

```
Raw (local only):
  "Mr. Jean-Pierre Dupont, VIP Level 5, Suite 401, returning guest (4th stay)"

Sent to LLM:
  "1 VIP-5 arrival, returning guest (4th stay), assigned to premium suite category"
```

### PII in Recaps

The email/Telegram recap **may** include guest names for VIP sections (this is operationally necessary). However:
- Recipients are authorized hotel management only
- Distribution list is controlled and auditable
- Guest contact details (email, phone, payment) are **never** included in recaps

---

## Access Control

### System Access
- Hotel Intel server access restricted to authorized IT personnel
- SSH key-based authentication (no password login)
- All admin actions logged

### Dashboard Access
- Authentication via Microsoft 365 SSO (leveraging hotel's existing Azure AD)
- Role-based access:
  - **Admin** — Full access, configuration, user management
  - **Manager** — Full recap view, historical data
  - **Department Head** — Department-specific view
- Session timeout after inactivity
- All access logged with timestamp and IP

### Telegram Bot
- Bot restricted to authorized chat IDs
- No public-facing bot functionality
- Commands authenticated per user ID

### API Credentials
- All integration credentials (OPERA, 7rooms, M365, etc.) stored encrypted at rest
- Credentials never logged or included in error reports
- Rotation policy: quarterly minimum

---

## Network Security

- **Encryption in transit** — All external API calls over TLS 1.2+
- **Encryption at rest** — Database encryption (AES-256)
- **Firewall** — Inbound connections blocked; outbound whitelist only:
  - LLM API endpoints
  - SMTP relay
  - Telegram API (api.telegram.org)
  - Google Calendar API (for ERVR)
  - Microsoft Graph API
  - Integration-specific API endpoints
- **VPN** — Optional VPN tunnel for remote management
- **No public IP** — Dashboard accessible only on hotel network (or via VPN)

---

## Compliance Considerations

### GDPR (EU General Data Protection Regulation)
- **Applies:** Yes — Eden Rock processes EU guest data
- **Legal basis:** Legitimate interest (operational management of guest services)
- **Data minimization:** Only collect data necessary for the daily recap
- **Right to erasure:** Ability to purge specific guest data on request
- **Data processing agreement:** Required between Hotel Intel (as processor) and the hotel (as controller)
- **Records of processing:** Maintain documentation of all data processing activities

### CNIL (French Data Protection Authority)
- **Applies:** Yes — Eden Rock is a French property (St-Barthélemy is a French collectivity)
- **Registration:** May require CNIL notification depending on data scope
- **Employee data:** HR/staffing data has additional CNIL requirements

### PCI DSS (Payment Card Industry)
- **Applies:** Indirectly — Hotel Intel does **not** store or process raw card numbers
- **Adyen integration:** Only transaction summaries and settlement data (no PANs)
- **Mitigation:** Never store, process, or transmit cardholder data

### Hotel Industry Standards
- Guest data handling aligned with luxury hotel confidentiality expectations
- Celebrity/high-profile guest data requires heightened discretion
- VIP guest information restricted to need-to-know recipients

---

## Incident Response

### If a Security Incident Occurs
1. **Detect** — Monitoring alerts on unusual access patterns, failed auth attempts, data anomalies
2. **Contain** — Isolate affected system, revoke compromised credentials
3. **Notify** — Alert hotel IT and management within 1 hour
4. **Investigate** — Determine scope, affected data, root cause
5. **Remediate** — Fix vulnerability, rotate credentials, restore from backup
6. **Report** — GDPR requires notification to authorities within 72 hours if personal data is breached

### Monitoring
- Failed authentication attempts
- Unusual data access patterns
- Pipeline failures (may indicate system compromise)
- Outbound traffic anomalies

---

## Backup & Recovery

- **Database backup:** Daily automated backup, encrypted, stored locally
- **Configuration backup:** Version-controlled (Git)
- **Recovery time objective (RTO):** < 4 hours
- **Recovery point objective (RPO):** < 24 hours (last daily backup)
- **Backup retention:** 90 days

---

## Future: Fully On-Premise AI

To eliminate the need for external LLM API calls entirely:

- Deploy a local LLM (e.g., Llama, Mistral) on the hotel server
- All processing — including AI generation — stays within the hotel network
- Trade-off: requires more powerful local hardware (GPU)
- Planned evaluation in Phase 3+

---

## Security Checklist (Pre-Deployment)

- [ ] Local server hardened (OS patching, unnecessary services disabled)
- [ ] Firewall configured with outbound whitelist
- [ ] All API credentials encrypted at rest
- [ ] Database encryption enabled
- [ ] SSH key-only access configured
- [ ] Dashboard SSO configured with hotel's Azure AD
- [ ] Telegram bot restricted to authorized chat IDs
- [ ] PII stripping verified before LLM API calls
- [ ] GDPR Data Processing Agreement signed with hotel
- [ ] Backup schedule configured and tested
- [ ] Monitoring and alerting operational
- [ ] Access logging enabled and verified
