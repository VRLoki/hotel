# Hotel Intel — Daily Recap Template

> This file contains the **Markdown template** (for Telegram/dashboard) and **HTML design spec** (for email).
> Placeholders use `{{variable}}` syntax. Arrays use `{{#each}}...{{/each}}` blocks.

---

## MARKDOWN VERSION

---

# ☀️ {{property_name}} — {{recap_date_formatted}}

*Delivered {{delivery_time}} · Covering yesterday's actuals + today's lookahead*

---

## 🔑 Executive Summary

{{executive_summary}}

---

## 📊 Key Metrics

```
              Yesterday    vs LW     vs LY     MTD        Budget Var
─────────────────────────────────────────────────────────────────────
Occupancy     {{occ_pct}}%      {{occ_vs_lw}}    {{occ_vs_ly}}    {{occ_mtd}}%      {{occ_budget_var}}
ADR           {{currency}}{{adr}}    {{adr_vs_lw}}    {{adr_vs_ly}}    {{currency}}{{adr_mtd}}   {{adr_budget_var}}
RevPAR        {{currency}}{{revpar}}  {{revpar_vs_lw}} {{revpar_vs_ly}} {{currency}}{{revpar_mtd}} {{revpar_budget_var}}
Room Rev      {{currency}}{{room_rev}} {{room_rev_vs_lw}} {{room_rev_vs_ly}} {{currency}}{{room_rev_mtd}} {{room_rev_budget_var}}
Total Rev     {{currency}}{{total_rev}} {{total_rev_vs_lw}} {{total_rev_vs_ly}} {{currency}}{{total_rev_mtd}} {{total_rev_budget_var}}
```

{{#if kpi_anomalies}}
⚠️ **Anomalies:** {{kpi_anomalies}}
{{/if}}

---

## 🛎️ Arrivals & Departures

**Today's Arrivals:** {{arrivals_rooms}} rooms / {{arrivals_guests}} guests
**Today's Departures:** {{departures_rooms}} rooms / {{departures_guests}} guests
**In-House After Moves:** {{in_house_rooms}} rooms ({{in_house_occ_pct}}%)

{{#if group_arrivals}}
📋 **Groups:** {{group_arrivals}}
{{/if}}

### ⭐ VIP Arrivals

{{#each vip_arrivals}}
- **{{guest_name}}** — {{vip_level}} · {{stay_history}} · Room {{room_number}}
  {{#if preferences}}💡 {{preferences}}{{/if}}
  {{#if special_arrangements}}🎁 {{special_arrangements}}{{/if}}
{{/each}}

{{#if vip_departures}}
### 👋 VIP Departures
{{#each vip_departures}}
- **{{guest_name}}** — {{departure_notes}}
{{/each}}
{{/if}}

{{#if birthdays_anniversaries}}
### 🎂 Celebrations Today
{{#each birthdays_anniversaries}}
- **{{guest_name}}** — {{occasion}} {{details}}
{{/each}}
{{/if}}

---

## 🍽️ Food & Beverage

### Yesterday's Performance

| Outlet | Covers | Revenue | Avg Check | vs LW |
|--------|-------:|--------:|----------:|------:|
{{#each fb_outlets}}
| {{outlet_name}} | {{covers}} | {{currency}}{{revenue}} | {{currency}}{{avg_check}} | {{vs_lw}} |
{{/each}}
| **Total** | **{{fb_total_covers}}** | **{{currency}}{{fb_total_revenue}}** | **{{currency}}{{fb_avg_check}}** | **{{fb_vs_lw}}** |

{{#if fb_notable}}
📌 {{fb_notable}}
{{/if}}

### Today's Lookahead

{{#each fb_outlets_today}}
- **{{outlet_name}}:** {{reservations_count}} reservations {{#if notable}}· {{notable}}{{/if}}
{{/each}}

---

## 💆 Spa & Wellness

| Metric | Yesterday | Today's Outlook |
|--------|----------:|----------------:|
| Bookings | {{spa_bookings_yesterday}} | {{spa_bookings_today}} |
| Revenue | {{currency}}{{spa_revenue}} | — |
| Utilization | {{spa_utilization}}% | {{spa_utilization_today}}% |
| Retail Sales | {{currency}}{{spa_retail}} | — |

{{#if spa_peak_hours}}
⏰ **Peak hours today:** {{spa_peak_hours}}
{{/if}}
{{#if spa_capacity_note}}
💡 {{spa_capacity_note}}
{{/if}}

---

## 🏠 Villas

| Status | Count |
|--------|------:|
| Occupied | {{villas_occupied}} / {{villas_total}} |
| Check-ins Today | {{villa_checkins}} |
| Check-outs Today | {{villa_checkouts}} |
| Next 7 Days | {{villa_upcoming}} bookings |

{{#if villa_revenue}}
💰 Villa revenue yesterday: {{currency}}{{villa_revenue}}
{{/if}}

{{#each villa_details}}
- **{{villa_name}}:** {{status}} {{#if guest_name}}({{guest_name}}){{/if}} {{#if notes}}· {{notes}}{{/if}}
{{/each}}

---

## 🚨 Incidents & Follow-ups

**Open:** {{incidents_open}} · **New yesterday:** {{incidents_new}} · **Resolved:** {{incidents_resolved}} (avg {{incidents_avg_resolution}})

{{#each incidents}}
- {{icon}} **{{title}}** — {{status}} · {{department}} · {{timestamp}}
  {{description}}
  {{#if action_required}}➡️ {{action_required}}{{/if}}
{{/each}}

{{#if incident_patterns}}
🔁 **Pattern alert:** {{incident_patterns}}
{{/if}}

---

## 🎩 Concierge Highlights

**Requests yesterday:** {{concierge_total}} ({{concierge_top_categories}})
**Pending:** {{concierge_pending}}

{{#if concierge_notable}}
### Notable Arrangements
{{#each concierge_notable}}
- {{description}} {{#if guest_name}}({{guest_name}}){{/if}}
{{/each}}
{{/if}}

---

## 🌤️ Weather & Events

**Today:** {{weather_today}}
**Tomorrow:** {{weather_tomorrow}}

{{#if local_events}}
### 📅 Local Events
{{#each local_events}}
- {{event_name}} — {{event_details}}
{{/each}}
{{/if}}

{{#if weather_impact}}
💡 {{weather_impact}}
{{/if}}

---

## ✅ Action Items

{{#each action_items}}
{{priority_icon}} **{{title}}** — {{owner}}
  {{detail}}
{{/each}}

---

*Generated by Hotel Intel · {{generation_timestamp}} · Data sources: {{data_sources}}*

---
---

## EMAIL HTML VERSION — Design Specification

### Overall Design

- **Width:** 640px centered, responsive down to 320px mobile
- **Font:** System font stack (`-apple-system, 'Segoe UI', Roboto, Helvetica, sans-serif`)
- **Background:** `#f7f7f5` (warm off-white)
- **Card background:** `#ffffff` with `1px solid #e8e5e0` border, `8px` border-radius
- **Text color:** `#2c2c2c` body, `#6b6560` secondary
- **Accent color:** `#1a1a2e` (deep navy) for headers, `#c9a96e` (muted gold) for highlights/VIP badges
- **Spacing:** 24px between sections, 16px card padding

### Header

- Property logo (left-aligned, max 140px wide)
- Date in elegant serif font (`Georgia`) — e.g., "Friday, 13 February 2026"
- Thin gold rule (`#c9a96e`, 1px) beneath

### Executive Summary

- No card — direct on background
- Text in slightly larger font (17px), `#2c2c2c`
- Italic style, with subtle left border (3px `#c9a96e`) as a pull-quote

### Key Metrics Dashboard

- White card with 5 metric tiles in a row (stacks to 2+3 on mobile)
- Each tile: metric label (small caps, `#6b6560`), value (28px bold `#1a1a2e`), delta arrow + percentage
- Delta colors: `#2d8a4e` (green) for positive, `#c44536` (red) for negative, `#6b6560` for neutral
- Subtle background tint on anomalies (`#fff3cd`)

### Arrivals & Departures

- White card, summary numbers as a compact 3-column header row (Arrivals | Departures | In-House)
- VIP section: each VIP as a mini-card with gold left border
  - Name bold, VIP badge as small pill (`#c9a96e` bg, white text)
  - Stay count, preferences as small text beneath
  - Birthday/anniversary: small 🎂 icon inline

### F&B Performance

- White card with clean HTML table
- Alternating row tint (`#fafaf8`)
- Revenue cells right-aligned, monospaced numerals
- vs-LW column with colored arrows
- Today's lookahead as bullet list below table

### Spa Snapshot

- White card, 4 mini-metric boxes (2×2 grid) similar to KPI tiles
- Capacity bar: thin horizontal progress bar showing utilization

### Villas

- White card, simple table or grid
- Each villa row with status dot (🟢 occupied / ⚪ available / 🔵 arriving)

### Incidents

- White card with colored severity indicators
  - Open: `#c44536` red dot
  - In progress: `#e8a838` amber dot
  - Resolved: `#2d8a4e` green dot
- Pattern alert: amber callout box at bottom

### Concierge Highlights

- White card, light and clean — bullet list with category icons
- Notable arrangements highlighted with gold left border

### Weather & Events

- Subtle card with weather icon (☀️/🌧️ etc.), temperature, condition
- Tomorrow preview in lighter text
- Events as clean list below
- Impact note in amber callout if relevant (e.g., "Rain expected — consider closing beach service")

### Action Items

- White card, each item as a row with priority indicator:
  - 🔴 Urgent — red left border
  - 🟡 Important — amber left border
  - 🔵 Standard — blue left border
- Owner name in small pill/badge
- Tappable on mobile (links to dashboard detail if available)

### Footer

- Light text: "Generated by Hotel Intel · [timestamp]"
- Data sources listed
- Unsubscribe / preferences link
- Property address

### Mobile Optimizations

- All metric grids stack vertically
- Tables become card-based list view at <480px
- Touch targets minimum 44px
- Executive summary becomes full-width pull quote
- Sections collapsible with `<details>` fallback for clients that support it
