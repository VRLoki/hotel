"""
Hotel Intel — Database Seeder.

Seeds the database with properties, users, mock data, and default settings.
Run: python dashboard/seed.py
"""

import json
import sys
from pathlib import Path

# Ensure we can import database
sys.path.insert(0, str(Path(__file__).parent))

import bcrypt
from database import get_db, init_db

PROJECT_ROOT = Path(__file__).parent.parent
MOCK_DIR = PROJECT_ROOT / "mock-data"
PROFILES_DIR = PROJECT_ROOT / "app" / "profiles"


def load_json(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def compute_delta(current, previous):
    if previous is None or previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


def compute_delta_abs(current, previous):
    if previous is None:
        return None
    return round(current - previous, 2)


def build_recap_for_date(data, target_date):
    """Build a full recap dict for a given date from mock data."""
    opera_raw = data["opera"]
    spa_raw = data["spa"]
    fb_raw = data["fb"]
    incidents_raw = data["incidents"]
    concierge_raw = data["concierge"]
    villas_raw = data["villas"]

    # Opera
    opera_day = {}
    opera_prev = {}
    daily_stats = opera_raw.get("dailyStats", [])
    for i, day in enumerate(daily_stats):
        if day["date"] == target_date:
            opera_day = day
            if i > 0:
                opera_prev = daily_stats[i - 1]
            break

    if not opera_day:
        return None

    # Spa
    spa_day = {}
    spa_prev = {}
    for i, day in enumerate(spa_raw.get("dailyData", [])):
        if day["date"] == target_date:
            spa_day = day
            if i > 0:
                spa_prev = spa_raw["dailyData"][i - 1]
            break

    # F&B
    fb_day = {}
    fb_prev = {}
    for i, day in enumerate(fb_raw.get("dailyData", [])):
        if day["date"] == target_date:
            fb_day = day
            if i > 0:
                fb_prev = fb_raw["dailyData"][i - 1]
            break

    # Incidents
    day_incidents = [inc for inc in incidents_raw.get("incidents", []) if inc["date"] == target_date]

    # Concierge
    day_concierge = [req for req in concierge_raw.get("conciergeRequests", []) if req["date"] == target_date]

    # Villas
    villas_day = {}
    villas_info = villas_raw.get("villas", {})
    for day in villas_raw.get("dailyData", []):
        if day["date"] == target_date:
            villas_day = day
            break

    fb_outlets_meta = fb_raw.get("outlets", {})

    # Compute total revenue
    total_rev = opera_day.get("totalRoomRevenue", 0) + opera_day.get("totalFBRevenue", 0) + opera_day.get("totalSpaRevenue", 0) + opera_day.get("totalOtherRevenue", 0)
    prev_total_rev = (opera_prev.get("totalRoomRevenue", 0) + opera_prev.get("totalFBRevenue", 0) + opera_prev.get("totalSpaRevenue", 0) + opera_prev.get("totalOtherRevenue", 0)) if opera_prev else None

    # F&B totals
    fb_covers = 0
    fb_revenue = 0
    fb_outlets_data = []
    for outlet_key in ("ON_THE_ROCKS", "SAND_BAR"):
        outlet = fb_day.get(outlet_key, {})
        if outlet:
            fb_covers += outlet.get("totalCovers", 0)
            fb_revenue += outlet.get("totalRevenue", 0)
            fb_outlets_data.append({
                "key": outlet_key,
                "name": fb_outlets_meta.get(outlet_key, {}).get("name", outlet_key),
                "type": fb_outlets_meta.get(outlet_key, {}).get("type", ""),
                "totalCovers": outlet.get("totalCovers", 0),
                "totalRevenue": outlet.get("totalRevenue", 0),
                "periods": {k: v for k, v in outlet.items() if k not in ("totalRevenue", "totalCovers")}
            })

    prev_fb_covers = 0
    for outlet_key in ("ON_THE_ROCKS", "SAND_BAR"):
        prev_fb_covers += fb_prev.get(outlet_key, {}).get("totalCovers", 0)

    prev_spa_bookings = spa_prev.get("totalBookings", 0) if spa_prev else None

    # Incidents summary
    inc_by_cat = {}
    inc_by_priority = {"high": 0, "medium": 0, "low": 0}
    for inc in day_incidents:
        cat = inc.get("category", "other")
        inc_by_cat[cat] = inc_by_cat.get(cat, 0) + 1
        pri = inc.get("priority", "low")
        inc_by_priority[pri] = inc_by_priority.get(pri, 0) + 1

    # Executive summary
    occ = round(opera_day.get("occupancy", 0) * 100, 1)
    arrivals = opera_day.get("arrivals", [])
    vip_arrivals = [a for a in arrivals if a.get("vip")]
    high_incidents = [i for i in day_incidents if i.get("priority") == "high"]

    lines = [
        f"**Daily Intelligence Brief — {target_date}**\n",
        f"Occupancy stands at **{occ}%** with **{opera_day.get('roomsSold', 0)}/{opera_day.get('roomsAvailable', 34)}** rooms sold. "
        f"Total property revenue reached **€{total_rev:,.0f}** across all departments.\n",
    ]
    if vip_arrivals:
        vip_names = ", ".join(f"{a['guestName']} ({a['vip']})" for a in vip_arrivals)
        lines.append(f"**VIP Arrivals:** {vip_names}. Ensure welcome protocols are executed.\n")
    if arrivals:
        lines.append(f"**{len(arrivals)} arrival(s)** expected today with **{len(opera_day.get('departures', []))} departure(s)**.\n")
    spa_rev = spa_day.get("revenue", 0)
    spa_bookings = spa_day.get("totalBookings", 0)
    if spa_bookings:
        lines.append(f"Spa has **{spa_bookings} bookings** generating **€{spa_rev:,.0f}** in revenue.\n")
    if high_incidents:
        lines.append(f"⚠️ **{len(high_incidents)} high-priority incident(s)** requiring attention:\n")
        for inc in high_incidents:
            s = "✅ Resolved" if inc.get("status") == "resolved" else "🔴 Open"
            lines.append(f"  • Room {inc.get('room', 'N/A')}: {inc['description']} [{s}]\n")
    pending_concierge = [c for c in day_concierge if c.get("status") == "pending"]
    if pending_concierge:
        lines.append(f"\n**{len(pending_concierge)} pending concierge request(s)** need follow-up.\n")
    occupied_villas = villas_day.get("occupiedVillas", 0)
    villa_rev = villas_day.get("totalRevenue", 0)
    if occupied_villas:
        lines.append(f"\nVillas: **{occupied_villas}/{len(villas_info)}** occupied, generating **€{villa_rev:,.0f}**.\n")

    executive_summary = "".join(lines)

    return {
        "date": target_date,
        "hotel": opera_raw.get("hotel", {}),
        "kpis": {
            "occupancy": {
                "value": occ,
                "delta": compute_delta_abs(opera_day.get("occupancy", 0) * 100, opera_prev.get("occupancy", 0) * 100 if opera_prev else None),
                "rooms_sold": opera_day.get("roomsSold", 0),
                "total_rooms": opera_day.get("roomsAvailable", 0),
            },
            "adr": {
                "value": opera_day.get("adr", 0),
                "delta_pct": compute_delta(opera_day.get("adr", 0), opera_prev.get("adr") if opera_prev else None),
            },
            "revpar": {
                "value": opera_day.get("revpar", 0),
                "delta_pct": compute_delta(opera_day.get("revpar", 0), opera_prev.get("revpar") if opera_prev else None),
            },
            "total_revenue": {
                "value": total_rev,
                "delta_pct": compute_delta(total_rev, prev_total_rev),
            },
            "fb_covers": {
                "value": fb_covers,
                "delta": compute_delta_abs(fb_covers, prev_fb_covers) if prev_fb_covers else None,
            },
            "spa_bookings": {
                "value": spa_day.get("totalBookings", 0),
                "delta": compute_delta_abs(spa_day.get("totalBookings", 0), prev_spa_bookings) if prev_spa_bookings else None,
            },
        },
        "arrivals": opera_day.get("arrivals", []),
        "departures": opera_day.get("departures", []),
        "in_house_by_type": opera_day.get("inHouseByType", {}),
        "revenue_breakdown": opera_day.get("revenueBreakdown", {}),
        "fb": {
            "outlets": fb_outlets_data,
            "total_covers": fb_covers,
            "total_revenue": fb_revenue,
        },
        "spa": {
            "total_bookings": spa_day.get("totalBookings", 0),
            "completed": spa_day.get("completed", 0),
            "no_shows": spa_day.get("noShows", 0),
            "revenue": spa_day.get("revenue", 0),
            "utilization": spa_day.get("therapistUtilization", {}),
            "bookings": spa_day.get("bookings", []),
        },
        "incidents": {
            "items": day_incidents,
            "by_category": inc_by_cat,
            "by_priority": inc_by_priority,
            "total": len(day_incidents),
        },
        "concierge": {
            "items": day_concierge,
            "total": len(day_concierge),
        },
        "villas": {
            "occupied": villas_day.get("occupiedVillas", 0),
            "total": len(villas_info),
            "revenue": villas_day.get("totalRevenue", 0),
            "bookings": villas_day.get("bookings", []),
        },
        "executive_summary": executive_summary,
    }


def seed():
    init_db()
    conn = get_db()

    # Clear existing data
    for table in ["app_configs", "modules", "settings", "recaps", "profiles", "users", "properties"]:
        conn.execute(f"DELETE FROM {table}")

    # ── Properties ───────────────────────────
    conn.execute(
        "INSERT INTO properties (id, name, code, location, logo_url, timezone) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Eden Rock — St Barths", "EDENROCK", "St. Jean Beach, St Barthélemy", "", "America/St_Barthelemy")
    )
    conn.execute(
        "INSERT INTO properties (id, name, code, location, logo_url, timezone) VALUES (?, ?, ?, ?, ?, ?)",
        (2, "Le Bristol Paris", "BRISTOL", "112 Rue du Faubourg Saint-Honoré, Paris", "", "Europe/Paris")
    )

    # ── Users ────────────────────────────────
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, property_id) VALUES (?, ?, ?, ?, ?)",
        ("admin@edenrock.com", "Admin", hash_password("admin123"), "admin", None)
    )
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, property_id) VALUES (?, ?, ?, ?, ?)",
        ("manager@edenrock.com", "Eden Rock Manager", hash_password("manager123"), "manager", 1)
    )
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, property_id) VALUES (?, ?, ?, ?, ?)",
        ("staff@edenrock.com", "Front Desk", hash_password("staff123"), "staff", 1)
    )
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, property_id) VALUES (?, ?, ?, ?, ?)",
        ("manager@bristol.com", "Bristol Manager", hash_password("manager123"), "manager", 2)
    )

    # ── Modules (for both properties) ────────
    modules_eden = {
        "microsoft_365": {"enabled": True, "status": "connected", "endpoint": "https://graph.microsoft.com/v1.0", "description": "Email & OneDrive"},
        "opera_pms": {"enabled": True, "status": "connected", "endpoint": "https://opera.edenrock.com/api", "description": "Property Management System"},
        "tac_spa": {"enabled": True, "status": "connected", "endpoint": "https://tac.edenrock.com/api", "description": "Spa Management"},
        "7rooms": {"enabled": True, "status": "connected", "endpoint": "https://api.sevenrooms.com/v1", "description": "F&B Reservations"},
        "unifocus": {"enabled": True, "status": "connected", "endpoint": "https://unifocus.edenrock.com/api", "description": "Incident Management"},
        "concierge_organizer": {"enabled": True, "status": "connected", "endpoint": "https://concierge.edenrock.com/api", "description": "Concierge Requests"},
        "ervr_villas": {"enabled": True, "status": "connected", "endpoint": "https://ervr.edenrock.com/api", "description": "Villa Management"},
        "sage": {"enabled": False, "status": "disconnected", "endpoint": "", "description": "Accounting"},
        "adyen": {"enabled": False, "status": "disconnected", "endpoint": "", "description": "Payment Processing"},
    }
    modules_bristol = {
        "microsoft_365": {"enabled": True, "status": "connected", "endpoint": "https://graph.microsoft.com/v1.0", "description": "Email & OneDrive"},
        "opera_pms": {"enabled": True, "status": "connected", "endpoint": "https://opera.bristol.com/api", "description": "Property Management System"},
        "tac_spa": {"enabled": False, "status": "disconnected", "endpoint": "", "description": "Spa Management"},
        "7rooms": {"enabled": True, "status": "connected", "endpoint": "https://api.sevenrooms.com/v1", "description": "F&B Reservations"},
        "unifocus": {"enabled": False, "status": "disconnected", "endpoint": "", "description": "Incident Management"},
    }

    for key, mod in modules_eden.items():
        conn.execute(
            "INSERT INTO modules (property_id, module_key, enabled, status, endpoint, description) VALUES (?,?,?,?,?,?)",
            (1, key, int(mod["enabled"]), mod["status"], mod["endpoint"], mod["description"])
        )
    for key, mod in modules_bristol.items():
        conn.execute(
            "INSERT INTO modules (property_id, module_key, enabled, status, endpoint, description) VALUES (?,?,?,?,?,?)",
            (2, key, int(mod["enabled"]), mod["status"], mod["endpoint"], mod["description"])
        )

    # ── Settings ─────────────────────────────
    settings_eden = {
        "llm": {"provider": "openai", "model": "gpt-4o", "providers": ["openai", "anthropic", "mistral", "local"]},
        "delivery": {"email": {"enabled": False, "to": ""}, "telegram": {"enabled": False, "chat_id": ""}},
        "schedule": {"recap_time": "07:00", "timezone": "America/St_Barthelemy"},
    }
    settings_bristol = {
        "llm": {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "providers": ["openai", "anthropic", "mistral", "local"]},
        "delivery": {"email": {"enabled": False, "to": ""}, "telegram": {"enabled": False, "chat_id": ""}},
        "schedule": {"recap_time": "06:30", "timezone": "Europe/Paris"},
    }
    conn.execute("INSERT INTO settings (property_id, data) VALUES (?, ?)", (1, json.dumps(settings_eden)))
    conn.execute("INSERT INTO settings (property_id, data) VALUES (?, ?)", (2, json.dumps(settings_bristol)))

    # ── Guest Profiles (Eden Rock) ───────────
    if PROFILES_DIR.exists():
        for f in sorted(PROFILES_DIR.glob("GID-*.json")):
            profile = load_json(f)
            conn.execute(
                "INSERT INTO profiles (property_id, guest_id, data) VALUES (?, ?, ?)",
                (1, profile["guest_id"], json.dumps(profile))
            )

    # ── Recaps (Eden Rock — from mock data) ──
    mock_data = {
        "opera": load_json(MOCK_DIR / "opera-pms.json"),
        "spa": load_json(MOCK_DIR / "spa-tac.json"),
        "fb": load_json(MOCK_DIR / "fb-7rooms.json"),
        "incidents": load_json(MOCK_DIR / "incidents-unifocus.json"),
        "concierge": load_json(MOCK_DIR / "concierge.json"),
        "villas": load_json(MOCK_DIR / "ervr-villas.json"),
    }

    dates = [d["date"] for d in mock_data["opera"].get("dailyStats", [])]
    for date in dates:
        recap = build_recap_for_date(mock_data, date)
        if recap:
            conn.execute(
                "INSERT INTO recaps (property_id, date, data) VALUES (?, ?, ?)",
                (1, date, json.dumps(recap))
            )

    # ── Bristol demo recap ───────────────────
    bristol_recap = {
        "date": "2026-02-13",
        "hotel": {"name": "Le Bristol Paris", "code": "BRISTOL"},
        "kpis": {
            "occupancy": {"value": 82.5, "delta": 3.2, "rooms_sold": 157, "total_rooms": 190},
            "adr": {"value": 1250, "delta_pct": 2.1},
            "revpar": {"value": 1031, "delta_pct": 5.8},
            "total_revenue": {"value": 285000, "delta_pct": 4.3},
            "fb_covers": {"value": 245, "delta": 12},
            "spa_bookings": {"value": 18, "delta": -2},
        },
        "arrivals": [],
        "departures": [],
        "in_house_by_type": {},
        "revenue_breakdown": {},
        "fb": {"outlets": [], "total_covers": 245, "total_revenue": 48500},
        "spa": {"total_bookings": 18, "completed": 15, "no_shows": 1, "revenue": 8200, "utilization": {}, "bookings": []},
        "incidents": {"items": [], "by_category": {}, "by_priority": {"high": 0, "medium": 0, "low": 0}, "total": 0},
        "concierge": {"items": [], "total": 0},
        "villas": {"occupied": 0, "total": 0, "revenue": 0, "bookings": []},
        "executive_summary": "**Daily Intelligence Brief — 2026-02-13**\n\nOccupancy stands at **82.5%** with **157/190** rooms sold. Total property revenue reached **€285,000** across all departments.\n\n**Le Bristol Paris** operating smoothly with no major incidents reported.\n",
    }
    conn.execute("INSERT INTO recaps (property_id, date, data) VALUES (?, ?, ?)", (2, "2026-02-13", json.dumps(bristol_recap)))

    # ── App Configs (Eden Rock) ──────────────
    eden_apps = [
        ("opera-pms", True, "connected", {
            "ohip_endpoint": "https://edenrock.opera-cloud.com/ohip/v1",
            "client_id": "app-edenrock-prod-001",
            "client_secret": "sk_opera_xxxxxxxxxxxxxxxxxx",
            "hotel_id": "EDENROCK",
            "environment": "production",
            "sync_interval": 15,
            "sync_reservations": True,
            "sync_profiles": True,
            "sync_cashiering": True,
            "sync_housekeeping": True,
        }),
        ("tac-spa", True, "connected", {
            "api_endpoint": "https://api.tac-app.com/v2",
            "api_key": "tac_key_edenrock_xxxxxxxxxx",
            "location_id": "LOC-EDENROCK-SPA",
            "sync_treatments": True,
            "sync_therapists": True,
        }),
        ("sevenrooms", True, "connected", {
            "api_key": "sr_key_xxxxxxxxxxxxxxxxxx",
            "api_secret": "sr_secret_xxxxxxxxxxxxxxxxxx",
            "venue_group_id": "vg_edenrock_001",
            "venues": '["v_on_the_rocks", "v_sand_bar"]',
            "sync_reservations": True,
            "sync_guest_profiles": True,
        }),
        ("unifocus", True, "connected", {
            "api_endpoint": "https://api.unifocus.com/v1",
            "api_key": "uf_key_edenrock_xxxxxxxxxx",
            "property_id": "PROP-EDENROCK",
            "sync_maintenance": True,
            "sync_complaints": True,
            "sync_housekeeping": True,
        }),
        ("concierge-organizer", True, "connected", {
            "api_endpoint": "https://api.conciergeorganizer.com/v1",
            "api_key": "co_key_edenrock_xxxxxxxxxx",
            "property_id": "PROP-EDENROCK",
        }),
        ("ervr", True, "connected", {
            "calendar_ids": '["eden-villa-nina@group.calendar.google.com","eden-villa-rockstar@group.calendar.google.com","eden-villa-maya@group.calendar.google.com"]',
            "sync_interval": 30,
        }),
        ("microsoft-365", True, "connected", {
            "tenant_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "client_id": "f0e1d2c3-b4a5-6789-0abc-def123456789",
            "client_secret": "ms_secret_xxxxxxxxxxxxxxxxxx",
            "monitored_mailboxes": '["reception@edenrock.com","reservations@edenrock.com","concierge@edenrock.com"]',
            "onedrive_paths": "/Shared Documents/Daily Reports",
            "sync_email": True,
            "sync_calendar": True,
            "sync_files": True,
        }),
        ("sage", True, "connected", {
            "api_endpoint": "https://api.sage.com/v3.1",
            "client_id": "sage_edenrock_client",
            "client_secret": "sage_secret_xxxxxxxxxx",
            "company_id": "comp_edenrock_001",
            "environment": "production",
        }),
        ("adyen", True, "connected", {
            "api_key": "adyen_key_xxxxxxxxxxxxxxxxxx",
            "merchant_account": "EdenRockStBarths",
            "environment": "live",
            "terminal_ids": "P400Plus-EDENROCK-001,P400Plus-EDENROCK-002,V400m-EDENROCK-003",
        }),
    ]
    for app_id, enabled, status, config in eden_apps:
        conn.execute(
            "INSERT INTO app_configs (property_id, app_id, config, enabled, status) VALUES (?,?,?,?,?)",
            (1, app_id, json.dumps(config), int(enabled), status)
        )

    conn.commit()
    conn.close()
    print("✅ Database seeded successfully!")
    print("   Properties: Eden Rock — St Barths, Le Bristol Paris")
    print("   Users: admin@edenrock.com/admin123, manager@edenrock.com/manager123, staff@edenrock.com/staff123, manager@bristol.com/manager123")


if __name__ == "__main__":
    seed()
