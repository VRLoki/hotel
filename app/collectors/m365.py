"""Microsoft 365 collector — emails and OneDrive documents."""

from __future__ import annotations
from typing import Any
from .base import BaseCollector


class M365Collector(BaseCollector):
    SOURCE_FILE = "m365-emails.json"
    SOURCE_NAME = "Microsoft 365"

    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        # Emails: filter by date
        day_emails = [
            e for e in raw
            if e.get("date", "")[:10] == target_date
        ]

        high_priority = [e for e in day_emails if e.get("importance") == "high"]
        unread = [e for e in day_emails if not e.get("isRead", True)]

        # OneDrive: load separately
        onedrive_data = self._load_onedrive()
        day_files = [
            f for f in onedrive_data
            if f.get("lastModified", "")[:10] == target_date
        ]

        return {
            "source": self.SOURCE_NAME,
            "date": target_date,
            "available": True,
            "emails_count": len(day_emails),
            "emails_high_priority": len(high_priority),
            "emails_unread": len(unread),
            "emails": [
                {
                    "from": e["from"]["name"],
                    "subject": e["subject"],
                    "importance": e.get("importance", "normal"),
                    "snippet": e.get("body", "")[:200],
                }
                for e in day_emails
            ],
            "onedrive_files_modified": len(day_files),
            "onedrive_files": [
                {"filename": f["filename"], "path": f["path"], "modified_by": f.get("modifiedBy", "")}
                for f in day_files
            ],
        }

    def _load_onedrive(self) -> list:
        import json
        path = self.data_dir / "m365-onedrive.json"
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
