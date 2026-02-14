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
