"""TAC Spa collector — bookings, revenue, utilization."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class SpaCollector(BaseCollector):
    SOURCE_FILE = "spa-tac.json"
    SOURCE_NAME = "TAC Spa"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        spa_info = raw["spa"]
        day = next((d for d in raw["dailyData"] if d["date"] == target_date), None)

        if not day:
            return {"source": self.SOURCE_NAME, "date": target_date, "available": False}

        utilization = day.get("therapistUtilization", {})
        avg_util = (
            round(sum(utilization.values()) / len(utilization) * 100, 1)
            if utilization else 0
        )

        # Look-ahead: next day bookings count
        next_day = self._next_date(target_date)
        next_data = next((d for d in raw["dailyData"] if d["date"] == next_day), None)

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "spa_name": spa_info["name"],
            "treatment_rooms": spa_info["treatmentRooms"],
            "total_bookings": day["totalBookings"],
            "completed": day["completed"],
            "no_shows": day["noShows"],
            "revenue": day["revenue"],
            "avg_utilization_pct": avg_util,
            "therapist_utilization": utilization,
            "bookings_detail": day.get("bookings", []),
            "retail_sales": day.get("retailSales", 0),
            # Look-ahead
            "tomorrow_bookings": next_data["totalBookings"] if next_data else None,
            "tomorrow_utilization": (
                round(sum(next_data["therapistUtilization"].values()) /
                      len(next_data["therapistUtilization"]) * 100, 1)
                if next_data and next_data.get("therapistUtilization") else None
            ),
        }

    @staticmethod
    def _next_date(date_str: str) -> str:
        from datetime import datetime, timedelta
        dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
        return dt.strftime("%Y-%m-%d")
