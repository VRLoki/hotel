# Hotel Intel — Module 2: Guest Intelligence

## Overview

Guest Intelligence is Hotel Intel's second core module. It solves the **fragmented guest data problem** in luxury hotels: a single guest's information is scattered across 7+ systems, and no staff member has the complete picture when that guest arrives.

Guest Intelligence connects the dots — matching guest identities across all hotel systems, building unified profiles, and generating actionable arrival briefs so every team member knows exactly who they're welcoming.

---

## Guest Identity Matching

### The Problem

A guest named "Priya Kapoor" checks in via OPERA PMS. She also has:
- A spa booking under "P. Kapoor" in TAC
- A dinner reservation under "Kapoor, party of 2" in 7rooms
- A concierge request for a vegetarian tasting menu
- An incident report about room service menu labeling

No single system knows all of this. Staff discover preferences reactively — or not at all.

### The Solution: Identity Graph

The matching engine builds a **guest identity graph** by linking records across all hotel systems using multiple matching strategies.

### Matching Algorithm

**Priority order (most reliable first):**

| Strategy | Method | Confidence | Example |
|----------|--------|------------|---------|
| **Exact name** | Case-insensitive string match | High | "Priya Kapoor" = "priya kapoor" |
| **Room + date** | Same room number on overlapping dates | High | Room 106, Feb 13 in OPERA = Room 106, Feb 13 in TAC |
| **Email match** | Exact email address | Very High | Same email across OPERA and 7rooms |
| **Phone match** | Normalized phone number | Very High | Same phone across systems |
| **Fuzzy name** | Levenshtein distance ≤ 2 | Medium | "Müller" ≈ "Mueller" |
| **Last name + room** | Surname match + room correlation | Medium | "Kapoor" in concierge + Room 106 |

**Matching rules:**
- A single high-confidence match is sufficient to link records
- Medium-confidence matches require a second corroborating signal
- All matches are logged for audit and manual review
- False positive threshold: prefer missing a link over creating a wrong one

### Cross-System Search

For each arriving guest (from OPERA PMS), the matcher searches:

| System | What We Search | Match Fields |
|--------|---------------|--------------|
| **Opera PMS** | Historical stays, guest profile | Name, email, phone, loyalty ID |
| **TAC (Spa)** | Bookings, treatment history | Guest name, room number |
| **7rooms (F&B)** | Reservations, dining history | Guest name, party name |
| **Micros (POS)** | Payment transactions | Room charge (room number) |
| **Unifocus (Incidents)** | Complaints, maintenance requests | Guest name, room number |
| **Concierge Organizer** | Requests, arrangements | Guest name, room number |
| **M365 (Email)** | Email mentions, correspondence | Guest name in email body/subject |

---

## Profile Building

### Profile Structure

Each guest gets a unified JSON profile:

```json
{
  "guest_id": "GID-20260213-001",
  "names": ["Priya Kapoor"],
  "emails": [],
  "phones": [],
  "nationality": "IN",
  "vip_level": null,
  "visits": [
    {
      "checkin": "2026-02-13",
      "checkout": "2026-02-19",
      "room": 106,
      "room_type": "OSV",
      "rate": 2800,
      "nights": 6,
      "confirmation": "ER260213-001"
    }
  ],
  "preferences": {
    "dietary": ["vegetarian"],
    "wines": [],
    "room_type": "OSV",
    "pillow_type": null,
    "spa_treatments": ["Premium Anti-Aging Facial"],
    "preferred_therapists": ["Anaïs"],
    "special_requests": ["Vegetarian options clearly marked"]
  },
  "spend_history": {
    "total": 3120.00,
    "rooms": 2800.00,
    "fb": 0,
    "spa": 320.00,
    "concierge": 0,
    "other": 0
  },
  "incidents": [
    {
      "date": "2026-02-13",
      "category": "guest_complaint",
      "description": "Vegetarian options not clearly marked on room service menu",
      "resolution": "Printed custom vegetarian menu card",
      "resolved": true
    }
  ],
  "concierge_history": [
    {
      "date": "2026-02-13",
      "type": "restaurant_booking",
      "details": "On The Rocks, 8pm, 2 pax, Valentine's Eve dinner, vegetarian tasting menu"
    }
  ],
  "special_occasions": [],
  "notes": ["First-time guest", "Vegetarian - inform F&B"],
  "first_visit": "2026-02-13",
  "total_visits": 1,
  "last_updated": "2026-02-13"
}
```

### Data Sources Per Profile Field

| Profile Field | Primary Source | Secondary Sources |
|--------------|---------------|-------------------|
| **Name, nationality** | OPERA PMS | Concierge, M365 emails |
| **Email, phone** | OPERA PMS | 7rooms, M365 |
| **Visit history** | OPERA PMS | — |
| **VIP level** | OPERA PMS | — |
| **Dietary preferences** | 7rooms, Concierge | OPERA notes, Incident reports |
| **Wine/drink preferences** | 7rooms (order history) | Concierge, F&B notes |
| **Room type preference** | OPERA (repeat bookings) | — |
| **Spa treatments** | TAC | — |
| **Preferred therapists** | TAC (repeat bookings) | — |
| **Spend history** | OPERA (rooms), Micros (F&B), TAC (spa) | Concierge (arrangements) |
| **Incidents** | Unifocus Knowcross | M365 emails |
| **Concierge requests** | Concierge Organizer | M365 emails |
| **Special occasions** | OPERA notes, Concierge | M365 emails |

---

## Arrival Alerts

### How It Works

1. **Trigger:** Each morning (or on-demand), fetch today's arrivals from OPERA PMS
2. **Match:** For each guest, run the matching engine across all systems
3. **Profile:** Build or update the unified guest profile
4. **Generate:** Use LLM to create a natural-language arrival brief
5. **Deliver:** Send briefs via configured channels (console, email, Telegram)

### Arrival Brief Examples

**First-time guest:**
> 🆕 **Mrs. Priya Kapoor** — Room 106 (Ocean Suite View) · 6 nights · India
>
> First-time guest. She is **vegetarian** — please inform F&B and room service. Has a spa booking today (Premium Anti-Aging Facial with Anaïs at 9am) and dinner at On The Rocks tonight (8pm, vegetarian tasting menu for 2).
>
> ⚠️ Note: She reported that vegetarian options aren't clearly marked on the room service menu — a custom menu card has been prepared.

**Returning VIP guest:**
> ⭐ **Mme. Isabelle Fontaine** — Room 117 (Superior Garden) · 7 nights · France · VIP2
>
> Welcome back for her **7th stay**! Always requests Room 117. Spa regular: loves the Premium Anti-Aging Facial and Detox Body Wrap. Frequent diner at On The Rocks. Previous issue: balcony door was hard to slide (Feb 11 last visit) — please verify it's been serviced.
>
> Lifetime spend: €28,500+ across 7 visits. Prefers Puligny-Montrachet with dinner.

### Staff Alerts

Beyond the narrative brief, the system generates structured alerts:

| Alert Type | Trigger | Recipient |
|-----------|---------|-----------|
| 🥗 **Dietary** | Guest has dietary restrictions | F&B Manager, Room Service |
| ⭐ **VIP Arrival** | VIP level ≥ 1 | GM, Front Desk, Concierge |
| ⚠️ **Past Issue** | Unresolved or recent incident | Duty Manager, relevant dept |
| 🎂 **Special Occasion** | Birthday/anniversary during stay | Concierge, F&B |
| 🔄 **Return Guest** | 3+ previous stays | Front Desk, GM |
| 💰 **High Value** | Lifetime spend > threshold | GM, Revenue Manager |

---

## Processing Modes

### Batch Processing (Default)

- Runs once daily (early morning, before recap)
- Processes all arrivals for the day
- Updates all affected profiles
- Generates all arrival briefs at once
- Delivered alongside or separately from the daily recap

### Real-Time Processing (Phase 2)

- Triggered by PMS check-in event (webhook from OPERA)
- Matches and generates brief on-demand
- Pushes alert to relevant staff immediately
- Useful for walk-ins, early check-ins, last-minute arrivals

---

## Privacy Considerations

### GDPR Compliance

Guest Intelligence handles PII extensively. Strict compliance is required:

| Requirement | Implementation |
|------------|----------------|
| **Legal basis** | Legitimate interest (personalized hospitality service) |
| **Data minimization** | Only collect data relevant to guest service |
| **Storage** | Local only — profiles never leave the property network |
| **Retention** | Configurable — default 3 years from last stay, then anonymize |
| **Right to erasure** | Guest can request full profile deletion |
| **Right to access** | Guest can request export of their profile data |
| **Consent** | Privacy notice at booking; opt-out mechanism for profiling |
| **Data protection officer** | Hotel's existing DPO covers Hotel Intel processing |

### Data Retention Policy

| Data Type | Retention | After Expiry |
|-----------|-----------|-------------|
| Active guest profiles | Until 3 years after last stay | Anonymize or delete |
| Visit history | 5 years | Aggregate into anonymous statistics |
| Incident records | 2 years after resolution | Delete |
| Spend data | 3 years | Anonymize |
| Profile backups | 90 days rolling | Auto-delete |

### Security Measures

- All profiles stored encrypted at rest (AES-256)
- Access logged with staff ID and timestamp
- No guest PII sent to LLM — briefs are generated from structured data with pseudonymization
- Profile access restricted to authorized roles (GM, Front Desk Manager, Concierge Chief)
- Audit trail for all profile views and modifications

---

## Output Formats

### Guest Cards (JSON)

Machine-readable profile for integration with other systems:

```json
{
  "guest_id": "GID-20260213-001",
  "display_name": "Priya Kapoor",
  "brief": "First-time guest from India...",
  "flags": ["vegetarian", "first_visit"],
  "alerts": [{"type": "dietary", "message": "Vegetarian - inform F&B"}]
}
```

### Arrival Briefs (Markdown)

Human-readable narrative for staff consumption, delivered via email or Telegram.

### Staff Alerts (Structured)

Targeted notifications to specific departments based on guest flags and history.

---

## Technical Implementation

### Module Structure

```
app/
├── guest_intel/
│   ├── __init__.py
│   ├── matcher.py          # Identity matching across systems
│   ├── profile_builder.py  # Builds/updates unified profiles
│   ├── profile_store.py    # JSON-based profile database
│   └── alerts.py           # Generates arrival briefs via LLM
├── profiles/               # Profile database (JSON files per guest)
```

### CLI Usage

```bash
# Run guest intelligence for today's arrivals
python main.py --mode guest-intel

# Run both recap and guest intelligence
python main.py --mode both

# Run only the daily recap (default)
python main.py --mode recap
```

### Dependencies

- `python-Levenshtein` or `rapidfuzz` — for fuzzy name matching
- Existing LLM infrastructure (shared with Daily Recap module)
- Existing collector infrastructure (shared)
