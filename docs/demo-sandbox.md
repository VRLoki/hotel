# Demo Sandbox

Development sandbox that simulates a full hotel tech stack. All services share the same guest data (Eden Rock - St Barths) and run on a single VPS.

---

## Server

- **Host:** `51.158.66.245` (Ubuntu 24.04, 4 cores, 8GB RAM, 50GB SSD)
- **Access:** `ssh root@51.158.66.245`

## Services

| Service | Port | API Base | API Key | Tech |
|---------|------|----------|---------|------|
| **Opera PMS** | 8080 | `/api/v1/hotels/EDENROCK/` | `hotel-intel-2026` | FastAPI + Oracle XE 21c |
| **TAC Spa** | 8081 | `/api/v2/locations/EDENROCK-SPA/` | `tac-demo-2026` | FastAPI + SQLite |
| **SevenRooms** | 8082 | `/api/v1/venues/` | `7rooms-demo-2026` | FastAPI + SQLite |
| **Unifocus** | 8083 | `/api/v1/properties/EDENROCK/` | `unifocus-demo-2026` | FastAPI + SQLite |
| **Concierge Organizer** | 8084 | `/api/v1/properties/EDENROCK/` | `concierge-demo-2026` | FastAPI + SQLite |

All services authenticate via `x-api-key` header. Swagger docs available at `/docs` on each port.

## Dashboard Config (Settings → App Catalog)

| App | OHIP/API Endpoint | Credentials |
|-----|-------------------|-------------|
| Oracle OPERA PMS | `http://51.158.66.245:8080/api/v1` | Client Secret: `hotel-intel-2026`, Hotel ID: `EDENROCK` |
| TAC Spa | `http://51.158.66.245:8081/api/v2` | API Key: `tac-demo-2026`, Location ID: `EDENROCK-SPA` |
| SevenRooms | `http://51.158.66.245:8082/api/v1` | API Key: `7rooms-demo-2026`, Venue Group: `edenrock-fb` |
| Unifocus | `http://51.158.66.245:8083/api/v1` | API Key: `unifocus-demo-2026`, Property ID: `EDENROCK` |
| Concierge Organizer | `http://51.158.66.245:8084/api/v1` | API Key: `concierge-demo-2026`, Property ID: `EDENROCK` |

## Data

All services share a consistent dataset centered around **Eden Rock - St Barths** in mid-February 2026.

### Guests (cross-referenced across all services)

| Guest | Room | VIP Status | Key Details |
|-------|------|------------|-------------|
| James Richardson | V04 (Diamond Villa) | VVIP | Private chef, Dom Perignon, private jet transfer |
| Sophie Laurent | 501 (Suite) | VIP | Vegetarian, white orchids, aromatherapy |
| Mohammed Al-Rashid | V05 (Ultra Villa) | ROYALTY | 24h butler, halal, security detail, yacht charter |
| Emma Thompson | 101 (Standard) | — | OTA booking |
| Leonardo Ferragamo | 601 (Premium Suite) | CELEBRITY | Absolute privacy, yacht Feb 16, daily spa |
| Yuki Tanaka | 301 (Deluxe) | — | Package rate, matcha, buckwheat pillow |
| Carlos Mendoza | V01 (Villa Rockstar) | VIP | Cigars, golf 7am daily, black SUV |
| Anna Petrov | 502 (Suite) | — | Corporate, hot-stone massage, Dom Perignon |
| David Chen | 603 (Premium Suite) | VVIP | 12th stay, wine collector, contemporary art |
| Isabel Santos | 302 (Deluxe) | — | Vegan, yoga, ayurvedic spa |
| Dr. Alexander Wolff | 401 (Jr Suite) | — | Arriving Feb 15, golf, Porsche rental |
| Fatima Al-Sayed | V02 (Villa Nina) | VIP | Arriving Feb 15, 3 children, nanny, personal shopper |

### Opera PMS (Oracle XE)
- 30 rooms (standards → premium villas)
- 13 reservations (10 checked-in, 2 arriving, 1 checked-out)
- Folio transactions, housekeeping, traces, rate codes, group block (Cartier event Feb 20-23)

### TAC Spa
- 17 treatments (€80-€890), 8 therapists
- 30+ bookings including Valentine's couples retreats

### SevenRooms
- 3 venues: Jean-Georges, Sand Bar, Rock Bar
- 80+ restaurant reservations with VIP tags and dietary notes
- Valentine's Day special dinners

### Unifocus
- Work orders, guest complaints, housekeeping tasks
- Preventive maintenance schedule
- Staff assignments

### Concierge Organizer
- Guest requests (yacht charters, transfers, activities)
- Transportation schedule
- St Barths activity catalog and recommendations

## Architecture

```
┌─────────────────────────────────────────┐
│         51.158.66.245 (VPS)             │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Oracle XE 21c (Docker)        │    │
│  │  Port 1521 · opera/Opera2026   │    │
│  │  Service: XEPDB1               │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────▼──────────────────┐    │
│  │  Opera PMS API  :8080           │    │
│  │  /opt/opera-api/ (FastAPI)      │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  TAC Spa API    :8081           │    │
│  │  /opt/tac-api/ (FastAPI+SQLite) │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  SevenRooms API :8082           │    │
│  │  /opt/sevenrooms-api/ (FastAPI) │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Unifocus API   :8083           │    │
│  │  /opt/unifocus-api/ (FastAPI)   │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Concierge API  :8084           │    │
│  │  /opt/concierge-api/ (FastAPI)  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
          ▲
          │ HTTP
          │
┌─────────▼──────────────────────────┐
│  Hotel Intel Dashboard             │
│  loki.hbtn.io (Mac Mini M4)       │
│  Pulls data from all 5 services   │
└────────────────────────────────────┘
```

## Management

All services run as systemd units with auto-restart:

```bash
# Check status
ssh root@51.158.66.245 "systemctl status opera-api tac-api sevenrooms-api unifocus-api concierge-api"

# Restart a service
ssh root@51.158.66.245 "systemctl restart opera-api"

# View logs
ssh root@51.158.66.245 "journalctl -u opera-api -f"

# Oracle DB
ssh root@51.158.66.245 "docker exec -it oracle-xe sqlplus opera/Opera2026@//localhost:1521/XEPDB1"
```

## Switching to Production

When connecting to real hotel systems, just change the URL and credentials in the dashboard Settings → App Catalog. The API response format matches the real services, so no code changes needed.
