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
