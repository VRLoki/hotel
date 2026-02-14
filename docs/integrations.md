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
