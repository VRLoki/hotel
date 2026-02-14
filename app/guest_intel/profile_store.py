"""
Guest Intelligence — Profile Store.

Simple JSON-based profile database. Each guest profile is stored as a
separate JSON file in the profiles/ directory, keyed by guest_id.

Provides load, save, list, search, and delete operations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProfileStore:
    """JSON file-based guest profile storage."""

    def __init__(self, profiles_dir: Path | None = None):
        if profiles_dir is None:
            profiles_dir = Path(__file__).parent.parent / "profiles"
        self.profiles_dir = profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, guest_id: str) -> Path:
        """Get the file path for a guest profile."""
        safe_id = guest_id.replace("/", "_").replace("\\", "_")
        return self.profiles_dir / f"{safe_id}.json"

    def save(self, profile: dict) -> None:
        """Save a guest profile to disk."""
        guest_id = profile.get("guest_id")
        if not guest_id:
            raise ValueError("Profile must have a guest_id")

        path = self._path_for(guest_id)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(profile, fh, indent=2, ensure_ascii=False, default=str)

    def load(self, guest_id: str) -> dict | None:
        """Load a guest profile by ID. Returns None if not found."""
        path = self._path_for(guest_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_all(self) -> list[dict]:
        """List all stored profiles (summary only: id, names, last_updated)."""
        profiles = []
        for path in sorted(self.profiles_dir.glob("GID-*.json")):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                profiles.append({
                    "guest_id": data.get("guest_id"),
                    "names": data.get("names", []),
                    "total_visits": data.get("total_visits", 0),
                    "last_updated": data.get("last_updated"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return profiles

    def search_by_name(self, name: str) -> list[dict]:
        """Search profiles by guest name (case-insensitive partial match)."""
        name_lower = name.lower()
        results = []
        for path in self.profiles_dir.glob("GID-*.json"):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                names = data.get("names", [])
                if any(name_lower in n.lower() for n in names):
                    results.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
        return results

    def delete(self, guest_id: str) -> bool:
        """Delete a guest profile. Returns True if deleted, False if not found."""
        path = self._path_for(guest_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear_all(self) -> int:
        """Delete all profiles. Returns count of deleted files."""
        count = 0
        for path in self.profiles_dir.glob("GID-*.json"):
            path.unlink()
            count += 1
        return count
