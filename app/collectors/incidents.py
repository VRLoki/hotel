"""Unifocus incidents collector."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class IncidentsCollector(BaseCollector):
    SOURCE_FILE = "incidents-unifocus.json"
    SOURCE_NAME = "Unifocus Incidents"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        all_incidents = raw.get("incidents", [])

        # Incidents for the target date
        day_incidents = [i for i in all_incidents if i["date"] == target_date]

        # Open incidents (not resolved) as of target date
        open_incidents = [
            i for i in all_incidents
            if i["date"] <= target_date and i["status"] != "resolved"
        ]

        resolved_today = [i for i in day_incidents if i["status"] == "resolved"]
        resolution_times = [i["resolutionMinutes"] for i in resolved_today if "resolutionMinutes" in i]
        avg_resolution = round(sum(resolution_times) / len(resolution_times)) if resolution_times else 0

        # Category breakdown
        categories = {}
        for i in day_incidents:
            cat = i.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "incidents_today": day_incidents,
            "new_count": len(day_incidents),
            "open_count": len(open_incidents),
            "resolved_count": len(resolved_today),
            "avg_resolution_minutes": avg_resolution,
            "categories": categories,
        }
