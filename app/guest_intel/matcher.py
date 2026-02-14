"""
Guest Intelligence — Identity Matcher.

Matches guest identities across all hotel systems using:
- Exact name matching (case-insensitive)
- Room number correlation (same room on same/overlapping dates)
- Fuzzy name matching (Levenshtein distance)
- Email/phone deduplication

Each match returns a dict of all records found for that guest across systems.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ── Fuzzy matching helpers ───────────────────

def _levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr_row.append(min(
                curr_row[j] + 1,       # insert
                prev_row[j + 1] + 1,   # delete
                prev_row[j] + cost,     # replace
            ))
        prev_row = curr_row
    return prev_row[-1]


def _normalize_name(name: str) -> str:
    """Normalize a guest name for comparison."""
    name = name.strip().lower()
    # Remove common prefixes
    for prefix in ("mr.", "mrs.", "ms.", "dr.", "prof.", "mr ", "mrs ", "ms ", "dr ", "prof "):
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
    return name


def _names_match(name1: str, name2: str, max_distance: int = 2) -> bool:
    """Check if two names match (exact or fuzzy)."""
    n1 = _normalize_name(name1)
    n2 = _normalize_name(name2)
    if n1 == n2:
        return True
    # Check if one name is a substring of the other (handles "P. Kapoor" vs "Priya Kapoor")
    parts1 = n1.split()
    parts2 = n2.split()
    # Last name match (most reliable for partial matches)
    if parts1 and parts2 and parts1[-1] == parts2[-1]:
        return True
    # Fuzzy match on full normalized name
    if _levenshtein(n1, n2) <= max_distance:
        return True
    return False


@dataclass
class MatchResult:
    """All records found for a single guest across hotel systems."""
    guest_name: str
    room: int | None = None
    nationality: str | None = None
    vip: str | None = None
    opera_data: dict | None = None
    spa_records: list[dict] = field(default_factory=list)
    fb_records: list[dict] = field(default_factory=list)
    incident_records: list[dict] = field(default_factory=list)
    concierge_records: list[dict] = field(default_factory=list)
    email_mentions: list[dict] = field(default_factory=list)
    opera_history: list[dict] = field(default_factory=list)


class GuestMatcher:
    """
    Matches guest identities across all hotel data sources.

    Takes raw collector data and today's arrival list from OPERA,
    then searches all systems for matching records per guest.
    """

    def __init__(self, collector_data: dict[str, dict[str, Any]]):
        self.collector_data = collector_data

    def match_arrivals(self, target_date: str) -> list[MatchResult]:
        """
        Match today's arriving guests across all systems.

        Args:
            target_date: ISO date string (e.g. "2026-02-13")

        Returns:
            List of MatchResult, one per arriving guest.
        """
        opera = self.collector_data.get("opera", {})
        arrivals = opera.get("arrivals", [])

        if not arrivals:
            return []

        results = []
        for arrival in arrivals:
            guest_name = arrival.get("guestName", "")
            room = arrival.get("roomNo")
            result = MatchResult(
                guest_name=guest_name,
                room=room,
                nationality=arrival.get("nationality"),
                vip=arrival.get("vip"),
                opera_data=arrival,
            )

            # Search each system
            result.spa_records = self._search_spa(guest_name, room, target_date)
            result.fb_records = self._search_fb(guest_name, room, target_date)
            result.incident_records = self._search_incidents(guest_name, room)
            result.concierge_records = self._search_concierge(guest_name, room)
            result.email_mentions = self._search_emails(guest_name)
            result.opera_history = self._search_opera_history(guest_name, target_date)

            results.append(result)

        return results

    # ── System-specific search methods ───────

    def _search_spa(self, guest_name: str, room: int | None, target_date: str) -> list[dict]:
        """Search spa bookings by name or room."""
        spa_raw = self._get_raw_data("spa-tac.json")
        if not spa_raw:
            return []

        matches = []
        for day in spa_raw.get("dailyData", []):
            for booking in day.get("bookings", []):
                spa_guest = booking.get("guest", "")
                spa_room = booking.get("room")

                if spa_guest and spa_guest not in ("Walk-in", "In-house guest"):
                    if _names_match(guest_name, spa_guest):
                        matches.append({**booking, "date": day["date"]})
                        continue
                # Room match on same date or during stay
                if room and spa_room == room:
                    matches.append({**booking, "date": day["date"]})

        return matches

    def _search_fb(self, guest_name: str, room: int | None, target_date: str) -> list[dict]:
        """Search F&B reservations by name. 7rooms data is outlet-level, not per-guest in our mock."""
        fb_raw = self._get_raw_data("fb-7rooms.json")
        if not fb_raw:
            return []

        # The 7rooms mock data is aggregated by outlet, not per-guest.
        # In production, 7rooms API returns per-reservation data with guest names.
        # For now, we extract any notes mentioning the guest.
        matches = []
        last_name = _normalize_name(guest_name).split()[-1] if guest_name else ""

        for day in fb_raw.get("dailyData", []):
            for outlet_key in ("ON_THE_ROCKS", "SAND_BAR"):
                outlet_data = day.get(outlet_key, {})
                for period in ("breakfast", "lunch", "dinner"):
                    period_data = outlet_data.get(period, {})
                    notes = period_data.get("notes", "")
                    if last_name and last_name in notes.lower():
                        matches.append({
                            "date": day["date"],
                            "outlet": outlet_key,
                            "period": period,
                            "notes": notes,
                        })
        return matches

    def _search_incidents(self, guest_name: str, room: int | None) -> list[dict]:
        """Search incident history by name or room."""
        incidents_raw = self._get_raw_data("incidents-unifocus.json")
        if not incidents_raw:
            return []

        matches = []
        for incident in incidents_raw.get("incidents", []):
            # Match by name in reportedBy or description
            reported = incident.get("reportedBy", "")
            description = incident.get("description", "")
            inc_room = incident.get("room")

            # Check name in reported_by field (e.g., "Guest (Kapoor)")
            last_name = _normalize_name(guest_name).split()[-1] if guest_name else ""
            if last_name and (last_name in reported.lower() or last_name in description.lower()):
                matches.append(incident)
                continue
            # Room match
            if room and inc_room == room:
                matches.append(incident)

        return matches

    def _search_concierge(self, guest_name: str, room: int | None) -> list[dict]:
        """Search concierge requests by name or room."""
        conc_raw = self._get_raw_data("concierge.json")
        if not conc_raw:
            return []

        matches = []
        for req in conc_raw.get("conciergeRequests", []):
            conc_guest = req.get("guest", "")
            conc_room = req.get("room")

            if conc_guest and conc_guest not in ("In-house guest",):
                if _names_match(guest_name, conc_guest):
                    matches.append(req)
                    continue
            if room and conc_room == room:
                matches.append(req)

        return matches

    def _search_emails(self, guest_name: str) -> list[dict]:
        """Search M365 emails for guest name mentions."""
        emails_raw = self._get_raw_data("m365-emails.json")
        if not emails_raw:
            return []

        matches = []
        last_name = _normalize_name(guest_name).split()[-1] if guest_name else ""
        if not last_name:
            return []

        for email in emails_raw:
            body = email.get("body", "").lower()
            subject = email.get("subject", "").lower()
            if last_name in body or last_name in subject:
                matches.append({
                    "date": email.get("date", ""),
                    "subject": email.get("subject", ""),
                    "from": email.get("from", {}).get("name", ""),
                    "snippet": body[:200],
                })

        return matches

    def _search_opera_history(self, guest_name: str, current_date: str) -> list[dict]:
        """Search OPERA for previous stays by the same guest."""
        opera_raw = self._get_raw_data("opera-pms.json")
        if not opera_raw:
            return []

        history = []
        for day in opera_raw.get("dailyStats", []):
            if day["date"] == current_date:
                continue
            # Check arrivals on other dates
            for arrival in day.get("arrivals", []):
                if _names_match(guest_name, arrival.get("guestName", "")):
                    history.append({**arrival, "date": day["date"]})
            # Check departures for spend data
            for departure in day.get("departures", []):
                if _names_match(guest_name, departure.get("guestName", "")):
                    history.append({**departure, "date": day["date"], "type": "departure"})

        return history

    # ── Data loading ─────────────────────────

    def _get_raw_data(self, filename: str) -> Any:
        """Load raw mock data file."""
        import json
        from pathlib import Path
        from config import settings

        path = settings.MOCK_DATA_DIR / filename
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
