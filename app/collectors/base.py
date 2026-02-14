"""
Base collector — defines the interface all data collectors must implement.

Each collector is responsible for one data source (PMS, spa, F&B, etc.).
For now they read from local JSON mock files; swap in real API calls later
by overriding `fetch_raw()`.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from config import settings


class BaseCollector(ABC):
    """Abstract base for all Hotel Intel data collectors."""

    # Subclasses set this to their mock-data filename (e.g. "opera-pms.json")
    SOURCE_FILE: str = ""
    SOURCE_NAME: str = ""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or settings.MOCK_DATA_DIR

    # ── Public API ───────────────────────────

    def collect(self, target_date: str) -> dict[str, Any]:
        """
        Main entry point.  Returns a standardised dict for the given date.

        Args:
            target_date: ISO date string, e.g. "2026-02-12"
        """
        raw = self.fetch_raw()
        return self.parse(raw, target_date)

    # ── Overridable hooks ────────────────────

    def fetch_raw(self) -> Any:
        """Load raw data.  Default: read from JSON mock file."""
        path = self.data_dir / self.SOURCE_FILE
        if not path.exists():
            raise FileNotFoundError(f"Mock data not found: {path}")
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    @abstractmethod
    def parse(self, raw: Any, target_date: str) -> dict[str, Any]:
        """Transform raw data into the collector's standardised output dict."""
        ...
