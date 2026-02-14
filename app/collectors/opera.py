"""Opera PMS collector — rooms, occupancy, revenue, arrivals/departures."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class OperaCollector(BaseCollector):
    SOURCE_FILE = "opera-pms.json"
    SOURCE_NAME = "Opera PMS"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        hotel = raw["hotel"]
        total_rooms = hotel["totalRooms"]

        day = self._find_day(raw["dailyStats"], target_date)
        if not day:
            return {"source": self.SOURCE_NAME, "date": target_date, "available": False}

        prev = self._find_previous(raw["dailyStats"], target_date)

        arrivals = day.get("arrivals", [])
        departures = day.get("departures", [])
        vip_arrivals = [a for a in arrivals if a.get("vip")]

        result = {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "hotel_name": hotel["name"],
            "total_rooms": total_rooms,
            "rooms_sold": day["roomsSold"],
            "occupancy_pct": round(day["occupancy"] * 100, 1),
            "adr": day["adr"],
            "revpar": day["revpar"],
            "room_revenue": day["totalRoomRevenue"],
            "fb_revenue": day["totalFBRevenue"],
            "spa_revenue": day["totalSpaRevenue"],
            "other_revenue": day["totalOtherRevenue"],
            "total_revenue": sum([
                day["totalRoomRevenue"], day["totalFBRevenue"],
                day["totalSpaRevenue"], day["totalOtherRevenue"],
            ]),
            "revenue_breakdown": day.get("revenueBreakdown", {}),
            "arrivals": arrivals,
            "arrivals_count": len(arrivals),
            "departures": departures,
            "departures_count": len(departures),
            "vip_arrivals": vip_arrivals,
            "in_house_by_type": day.get("inHouseByType", {}),
        }

        # Day-over-day deltas
        if prev:
            result["prev_occupancy_pct"] = round(prev["occupancy"] * 100, 1)
            result["prev_adr"] = prev["adr"]
            result["prev_revpar"] = prev["revpar"]
            result["prev_total_revenue"] = sum([
                prev["totalRoomRevenue"], prev["totalFBRevenue"],
                prev["totalSpaRevenue"], prev["totalOtherRevenue"],
            ])

        return result

    # ── helpers ───────────────────────────────

    @staticmethod
    def _find_day(stats: list, date: str) -> dict | None:
        return next((d for d in stats if d["date"] == date), None)

    @staticmethod
    def _find_previous(stats: list, date: str) -> dict | None:
        dates = sorted(d["date"] for d in stats)
        try:
            idx = dates.index(date)
            if idx > 0:
                prev_date = dates[idx - 1]
                return next(d for d in stats if d["date"] == prev_date)
        except ValueError:
            pass
        return None
