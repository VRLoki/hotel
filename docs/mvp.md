# Hotel Intel — MVP & Roadmap

## MVP Philosophy

Ship the smallest version that delivers real value to Eden Rock's GM every morning. One integration, one output channel, one property. Then iterate.

---

## Phase 1a: Daily Recap MVP (v1.0) ✅

**Goal:** Daily AI recap with core hotel data, delivered via email and Telegram.
**Status:** Built with mock data pipeline.

### Integrations (MVP)

| System | Data | Priority | Status |
|--------|------|----------|--------|
| Oracle OPERA (OHIP) | Occupancy, ADR, RevPAR, arrivals, departures, VIPs, revenue | P0 | ✅ Mock |
| TAC | Spa bookings, revenue | P1 | ✅ Mock |
| 7rooms | F&B covers, reservations | P1 | ✅ Mock |
| Unifocus Knowcross | Incidents, tasks | P1 | ✅ Mock |
| ERVR (Google Calendar) | Villa bookings | P1 | ✅ Mock |
| Concierge Organizer | Guest requests | P1 | ✅ Mock |
| Microsoft 365 | OneDrive/Outlook — specific files/reports | P2 | ✅ Mock |

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
- ✅ Console output
- ✅ Email (HTML formatted)
- ✅ Telegram bot

### Infrastructure (MVP)
- Local server at Eden Rock (Docker-based)
- PostgreSQL database
- Scheduled pipeline (cron — runs at 05:00, delivers at 06:30)
- LLM via API (Claude, GPT-4, Mistral, or local Ollama)

---

## Phase 1b: Guest Intelligence MVP (v1.1) 🟡

**Goal:** Cross-system guest matching and profiling with arrival briefs.
**Status:** In development.

### Features
- 🟡 Guest identity matching across all hotel systems
- 🟡 Unified guest profile database (JSON-based)
- 🟡 Arrival briefs — LLM-generated guest cards for today's check-ins
- 🟡 Staff alerts for dietary needs, VIP preferences, past issues

### Matching Engine
- Exact name matching across OPERA, TAC, 7rooms, Unifocus, Concierge
- Fuzzy name matching (Levenshtein distance)
- Room number correlation (same room = same guest on same date)
- Email/phone deduplication (when available)

### Profile Building
- Visit history aggregated from OPERA
- Spa preferences from TAC
- F&B patterns from 7rooms
- Incident history from Unifocus
- Concierge requests and arrangements
- Email mentions from M365

### Output
- Guest profile cards (JSON)
- LLM-generated arrival briefs
- Console / email / Telegram delivery

### Success Criteria
- [ ] Arriving guests are matched across ≥3 systems
- [ ] Returning guests show full history in arrival brief
- [ ] Dietary/allergy flags are surfaced automatically
- [ ] Staff can access guest cards before check-in
- [ ] Profiles persist across stays

---

## Phase 2: Enhanced (v1.5)

**Goal:** Dashboard, more integrations, interactive queries.

### New Features
- 📊 Web dashboard with historical data and charts
- 🔊 TTS audio recap (Telegram voice message + email attachment)
- 💬 Telegram bot interactive queries ("What's today's occupancy?")
- 📈 Trend analysis (7-day, 30-day comparisons)
- ⚠️ Real-time alerts for critical incidents
- 👤 Guest profile search and browsing in dashboard

### New Integrations
- Micros (F&B payment data — enriches guest spend profiles)
- Sage (financial summary)
- Adyen (payment processing data)
- Microsoft 365 Teams (operational channel monitoring)
- Microsoft 365 SharePoint (shared operational documents)

### Guest Intelligence Enhancements
- Real-time matching (trigger on check-in event, not just batch)
- Guest preference learning over time
- Automated pre-arrival emails with personalized content
- Staff mobile app for guest cards

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
- **Cross-property guest recognition** — guest profiles follow them across properties in the same group

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
- **Guest sentiment analysis** from reviews, emails, incident patterns

---

## Development Timeline (Estimated)

| Phase | Scope | Timeline |
|-------|-------|----------|
| **Phase 1a (Daily Recap)** | Core recap pipeline | ✅ Complete |
| **Phase 1b (Guest Intel)** | Matching + profiles + arrival briefs | 4–6 weeks |
| **Phase 2** | Dashboard + more integrations + interactive bot | +8–12 weeks |
| **Phase 3** | Multi-property + portfolio view | +12–16 weeks |
| **Phase 4** | Platform + marketplace | +6 months |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OPERA OHIP API access delays | Blocks MVP | Start API application early; prepare mock data pipeline |
| TAC/Knowcross lack APIs | Missing data sources | Fall back to file export or database access |
| LLM hallucination in recap | Incorrect data reported | Structured prompts with data validation; human review period |
| Local server reliability | Missed recaps | Monitoring + alerting; fallback to cloud delivery |
| Data quality issues | Inaccurate KPIs | Validation layer with sanity checks and source comparison |
| Guest matching false positives | Wrong profiles merged | Conservative matching thresholds; manual review flagging |
| GDPR compliance for guest profiles | Legal risk | Local-only storage, consent framework, retention policies |

---

## Open Questions

- [ ] Which Oracle OPERA version does Eden Rock run? (Cloud vs on-prem)
- [ ] OHIP API licensing — is it included or additional cost?
- [ ] TAC integration method — API available?
- [ ] Concierge Organizer integration method?
- [ ] Mosaic Projects — evaluate for potential leverage in data aggregation
- [ ] Server specifications for local hosting at Eden Rock
- [ ] Budget data availability for variance reporting
- [ ] Guest consent workflow — how to handle GDPR for profile building?
- [ ] Real-time PMS events — can OPERA push check-in events via webhook?
