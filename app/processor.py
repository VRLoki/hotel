"""
Hotel Intel — Data Processor.

Aggregates all collector outputs into a unified structured summary
with computed KPIs, deltas, and look-ahead data.
"""

from __future__ import annotations
from typing import Any

from config import settings


def process(collector_data: dict[str, dict[str, Any]], target_date: str) -> dict[str, Any]:
    """
    Take the raw outputs from all collectors and produce a single
    structured summary dict ready for the LLM generator.

    Args:
        collector_data: {"opera": {...}, "spa": {...}, ...}
        target_date: ISO date string
    """
    opera = collector_data.get("opera", {})
    spa = collector_data.get("spa", {})
    fb = collector_data.get("fb", {})
    incidents = collector_data.get("incidents", {})
    concierge = collector_data.get("concierge", {})
    villas = collector_data.get("villas", {})
    m365 = collector_data.get("m365", {})

    # ── Room KPIs ────────────────────────────
    occupancy_pct = opera.get("occupancy_pct", 0)
    adr = opera.get("adr", 0)
    revpar = opera.get("revpar", 0)
    room_revenue = opera.get("room_revenue", 0)
    total_revenue = opera.get("total_revenue", 0)

    # Deltas vs previous day
    prev_occ = opera.get("prev_occupancy_pct")
    prev_adr = opera.get("prev_adr")
    prev_revpar = opera.get("prev_revpar")
    prev_total_rev = opera.get("prev_total_revenue")

    def delta(current, previous):
        if previous is None or previous == 0:
            return None
        return round(((current - previous) / previous) * 100, 1)

    def delta_abs(current, previous):
        if previous is None:
            return None
        return round(current - previous, 2)

    # ── F&B KPIs ─────────────────────────────
    fb_total_covers = fb.get("total_covers", 0)
    fb_total_revenue = fb.get("total_revenue", 0)
    fb_avg_check = fb.get("avg_check", 0)

    # ── Spa KPIs ─────────────────────────────
    spa_bookings = spa.get("total_bookings", 0)
    spa_revenue = spa.get("revenue", 0)
    spa_utilization = spa.get("avg_utilization_pct", 0)

    # ── Incidents ────────────────────────────
    incidents_new = incidents.get("new_count", 0)
    incidents_open = incidents.get("open_count", 0)
    incidents_resolved = incidents.get("resolved_count", 0)
    avg_resolution = incidents.get("avg_resolution_minutes", 0)

    # ── Villas ───────────────────────────────
    villas_occupied = villas.get("occupied", 0)
    villas_total = villas.get("total_villas", 0)
    villa_revenue = villas.get("total_revenue", 0)

    # ── Build summary ────────────────────────
    summary = {
        "hotel_name": settings.HOTEL_NAME,
        "currency": settings.CURRENCY,
        "date": target_date,

        # Room metrics
        "occupancy_pct": occupancy_pct,
        "occupancy_delta": delta_abs(occupancy_pct, prev_occ),
        "adr": adr,
        "adr_delta_pct": delta(adr, prev_adr),
        "revpar": revpar,
        "revpar_delta_pct": delta(revpar, prev_revpar),
        "room_revenue": room_revenue,
        "total_revenue": total_revenue,
        "total_revenue_delta_pct": delta(total_revenue, prev_total_rev),
        "total_rooms": opera.get("total_rooms", 0),
        "rooms_sold": opera.get("rooms_sold", 0),
        "revenue_breakdown": opera.get("revenue_breakdown", {}),

        # Arrivals & departures
        "arrivals_count": opera.get("arrivals_count", 0),
        "arrivals": opera.get("arrivals", []),
        "departures_count": opera.get("departures_count", 0),
        "departures": opera.get("departures", []),
        "vip_arrivals": opera.get("vip_arrivals", []),
        "in_house_by_type": opera.get("in_house_by_type", {}),

        # F&B
        "fb_outlets": fb.get("outlets", []),
        "fb_total_covers": fb_total_covers,
        "fb_total_revenue": fb_total_revenue,
        "fb_avg_check": fb_avg_check,
        "fb_tomorrow_reservations": fb.get("tomorrow_reservations", {}),

        # Spa
        "spa_bookings": spa_bookings,
        "spa_completed": spa.get("completed", 0),
        "spa_no_shows": spa.get("no_shows", 0),
        "spa_revenue": spa_revenue,
        "spa_utilization_pct": spa_utilization,
        "spa_retail": spa.get("retail_sales", 0),
        "spa_tomorrow_bookings": spa.get("tomorrow_bookings"),
        "spa_tomorrow_utilization": spa.get("tomorrow_utilization"),

        # Incidents
        "incidents_new": incidents_new,
        "incidents_open": incidents_open,
        "incidents_resolved": incidents_resolved,
        "incidents_avg_resolution_min": avg_resolution,
        "incidents_detail": incidents.get("incidents_today", []),
        "incidents_categories": incidents.get("categories", {}),

        # Concierge
        "concierge_total": concierge.get("total_requests", 0),
        "concierge_categories": concierge.get("categories", {}),
        "concierge_pending": concierge.get("pending_count", 0),
        "concierge_notable": concierge.get("notable_arrangements", []),

        # Villas
        "villas_occupied": villas_occupied,
        "villas_total": villas_total,
        "villa_revenue": villa_revenue,
        "villa_checkins": villas.get("checkins_today", 0),
        "villa_checkouts": villas.get("checkouts_today", 0),
        "villa_upcoming_7d": villas.get("upcoming_7_days", 0),
        "villa_details": villas.get("villa_details", []),

        # M365
        "emails_count": m365.get("emails_count", 0),
        "emails_high_priority": m365.get("emails_high_priority", 0),
        "emails_summary": m365.get("emails", []),
        "onedrive_files": m365.get("onedrive_files", []),

        # Meta
        "data_sources": [
            c.get("source", "unknown")
            for c in collector_data.values()
            if c.get("available", False)
        ],
    }

    return summary
