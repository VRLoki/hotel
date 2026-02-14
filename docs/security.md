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
