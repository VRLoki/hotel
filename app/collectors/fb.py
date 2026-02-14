"""7rooms F&B collector — covers, revenue, outlet performance."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class FBCollector(BaseCollector):
    SOURCE_FILE = "fb-7rooms.json"
    SOURCE_NAME = "7rooms F&B"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        outlets_meta = raw["outlets"]
        day = next((d for d in raw["dailyData"] if d["date"] == target_date), None)

        if not day:
            return {"source": self.SOURCE_NAME, "date": target_date, "available": False}

        outlet_results = []
        total_covers = 0
        total_revenue = 0.0

        for code, meta in outlets_meta.items():
            outlet_day = day.get(code)
            if not outlet_day:
                continue
            covers = outlet_day.get("totalCovers", 0)
            revenue = outlet_day.get("totalRevenue", 0.0)
            avg_check = round(revenue / covers, 2) if covers else 0
            total_covers += covers
            total_revenue += revenue

            outlet_results.append({
                "code": code,
                "name": meta["name"],
                "type": meta["type"],
                "covers": covers,
                "revenue": revenue,
                "avg_check": avg_check,
                "meals": {
                    k: v for k, v in outlet_day.items()
                    if isinstance(v, dict)
                },
                "notes": outlet_day.get("notes", ""),
            })

        # Look-ahead
        next_day_str = self._next_date(target_date)
        next_day = next((d for d in raw["dailyData"] if d["date"] == next_day_str), None)
        tomorrow_reservations = {}
        if next_day:
            for code in outlets_meta:
                od = next_day.get(code, {})
                if isinstance(od, dict):
                    total_res = sum(
                        v.get("reservations", 0) for v in od.values() if isinstance(v, dict)
                    )
                    tomorrow_reservations[code] = total_res

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "outlets": outlet_results,
            "total_covers": total_covers,
            "total_revenue": total_revenue,
            "avg_check": round(total_revenue / total_covers, 2) if total_covers else 0,
            "tomorrow_reservations": tomorrow_reservations,
        }

    @staticmethod
    def _next_date(date_str: str) -> str:
        from datetime import datetime, timedelta
        dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
        return dt.strftime("%Y-%m-%d")
