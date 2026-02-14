"""Concierge Organizer collector."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class ConciergeCollector(BaseCollector):
    SOURCE_FILE = "concierge.json"
    SOURCE_NAME = "Concierge Organizer"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        all_requests = raw.get("conciergeRequests", [])
        day_requests = [r for r in all_requests if r["date"] == target_date]

        # Category counts
        categories = {}
        for r in day_requests:
            t = r.get("type", "other")
            categories[t] = categories.get(t, 0) + 1

        pending = [r for r in day_requests if r.get("status") == "pending"]
        notable = [r for r in day_requests if r.get("type") == "special_request"]

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "total_requests": len(day_requests),
            "categories": categories,
            "pending_count": len(pending),
            "notable_arrangements": notable,
            "requests": day_requests,
        }
