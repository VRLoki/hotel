"""ERVR Villas collector."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class VillasCollector(BaseCollector):
    SOURCE_FILE = "ervr-villas.json"
    SOURCE_NAME = "ERVR Villas"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        villas_meta = raw["villas"]
        total_villas = len(villas_meta)

        day = next((d for d in raw["dailyData"] if d["date"] == target_date), None)
        if not day:
            return {"source": self.SOURCE_NAME, "date": target_date, "available": False}

        bookings = day.get("bookings", [])
        checkins = [b for b in bookings if b.get("status") == "arrived"]
        checkouts = [b for b in bookings if b.get("checkOut") == target_date]

        # Next 7 days upcoming bookings
        from datetime import datetime, timedelta
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        upcoming = 0
        for d in raw["dailyData"]:
            d_dt = datetime.strptime(d["date"], "%Y-%m-%d")
            if target_dt < d_dt <= target_dt + timedelta(days=7):
                upcoming += len([b for b in d.get("bookings", []) if b.get("status") == "arrived"])

        villa_details = []
        for b in bookings:
            villa_code = b.get("villa", "")
            meta = villas_meta.get(villa_code, {})
            villa_details.append({
                "villa_code": villa_code,
                "villa_name": meta.get("name", villa_code),
                "status": b.get("status", "unknown"),
                "guest_name": b.get("guest", ""),
                "nightly_rate": b.get("nightlyRate", 0),
                "notes": b.get("notes", ""),
            })

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "total_villas": total_villas,
            "occupied": day.get("occupiedVillas", 0),
            "total_revenue": day.get("totalRevenue", 0),
            "checkins_today": len(checkins),
            "checkouts_today": len(checkouts),
            "upcoming_7_days": upcoming,
            "villa_details": villa_details,
        }
