# Hotel Intel 🏨

AI-powered daily intelligence recap for luxury hotels (palaces).

**First client / pilot:** Eden Rock — St Barths

## Goal

Gather data from the tools hotels already use, aggregate it, and deliver a clean daily recap every morning.

## Data Sources (MVP)

| System | Tool | Data |
|--------|------|------|
| PMS | Oracle OPERA (OHIP) | Occupancy, arrivals, departures, revenue, VIPs |
| SPA | TAC | Spa bookings, revenue |
| F&B | 7rooms | Restaurant reservations, covers |
| F&B Payments | Micros | Payment data |
| Collaboration | Microsoft 365 | OneDrive, Outlook, Teams, SharePoint |
| File System | FS | Specific files/folders |
| Incident Mgmt | Unifocus Knowcross | Incidents, tasks |
| Concierge | Concierge Organizer | Guest requests |
| Villa Rental | ERVR (Google Calendar) | Villa bookings |
| Finance | Sage | Financial data |
| HR | Sage, Octane, Spendex | Payroll, time logs, expenses |
| Payments | Adyen | Credit card processing |

## Output

- Daily morning text recap (AI-generated)
- Email + Telegram + Dashboard
- Optional: Speech (TTS)
- AI interaction: audio input, send emails/calendar/SMS

## Data Collection Methods

| Method | Systems |
|--------|---------|
| ✅ API | Opera (OHIP), 7rooms, Adyen, M365 (Graph), ERVR (Google Cal) |
| 📧 Email parsing | Sage, Unifocus, Octane, Spendex |
| 🤖 RPA (OpenClaw scraper) | TAC Spa, Concierge Organizer, Micros |
| 📁 CSV/Excel | Sage exports, Micros reports |

## Key Requirements

- **Security:** Local hosting
- **RPA:** Standalone OpenClaw instance for screen scraping systems without APIs
- **Explore:** Mosaic Projects (existing data aggregation tool — possible integration?)

## Decisions

- **Model:** SaaS product for multiple palace hotels
- **Delivery:** Email + Telegram bot + Dashboard (all three)
- **Priority data source:** PMS / Bookings (first integration)
- **Target:** Luxury hotels / palaces
- **Hosting:** Cloud SaaS (default) or on-premise server (option)
- **LLM:** OpenAI/Anthropic (cloud) or local Ollama (on-premise)
- **Business model:** Monthly subscription, modular pricing — pay per module
- **Web app:** Config dashboard where hotels connect services (OAuth, credentials)
- **Growth:** Module marketplace — start with core, add integrations over time

## Product Architecture

### Two deployment modes:
1. **☁️ Cloud SaaS** — hosted, uses OpenAI/Anthropic, quick onboarding
2. **🏠 On-premise** — local server, Ollama for LLM, full data sovereignty

### Web App (Configuration Dashboard):
- Hotel signs up → gets a dashboard
- Connects integrations: OAuth for M365, credentials for Opera, 7rooms, etc.
- Enables/disables modules
- Configures recap schedule, delivery channels, recipients
- Views guest profiles, daily recaps, analytics

### Module Marketplace:
- **Core:** Daily Recap, Guest Intelligence
- **Integrations:** Opera, 7rooms, M365, Sage, TAC, Adyen, Google, etc.
- Each integration = paid module, monthly pricing
- Easy to add new integrations over time → growing revenue per hotel

## Status

🟡 MVP phase — core pipeline built, guest intelligence in progress.

## PMS Target

- **Primary:** Oracle Opera (OHIP — Oracle Hospitality Integration Platform)
- Oracle Opera is the industry standard for luxury/palace hotels

## Next Steps

- Research Oracle OHIP API (REST APIs, authentication, available endpoints)
- Map key data points: occupancy, ADR, RevPAR, arrivals, departures, VIPs
- Define MVP daily recap content/template
- Prototype a data pipeline (API → aggregation → recap)
- Design email + Telegram + dashboard output
