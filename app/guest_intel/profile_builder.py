"""
Guest Intelligence — Profile Builder.

Takes match results from the matcher and builds/updates unified guest profiles.
Aggregates data from all sources into a single coherent profile structure.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from .matcher import MatchResult, _normalize_name
from .profile_store import ProfileStore


def _generate_guest_id(name: str, date: str) -> str:
    """Generate a deterministic guest ID from name."""
    normalized = _normalize_name(name)
    hash_input = normalized.encode("utf-8")
    short_hash = hashlib.sha256(hash_input).hexdigest()[:8]
    return f"GID-{short_hash}"


class ProfileBuilder:
    """Builds and updates guest profiles from cross-system match results."""

    def __init__(self, store: ProfileStore):
        self.store = store

    def build_profiles(self, matches: list[MatchResult], target_date: str) -> list[dict]:
        """
        Build or update profiles for all matched guests.

        Args:
            matches: List of MatchResult from the matcher.
            target_date: ISO date string.

        Returns:
            List of updated profile dicts.
        """
        profiles = []
        for match in matches:
            profile = self._build_single(match, target_date)
            self.store.save(profile)
            profiles.append(profile)
        return profiles

    def _build_single(self, match: MatchResult, target_date: str) -> dict:
        """Build or update a single guest profile from match results."""
        guest_id = _generate_guest_id(match.guest_name, target_date)

        # Always start fresh from current data to avoid double-counting.
        # In production with real historical data, we'd do incremental updates.
        profile = self._empty_profile(guest_id, match.guest_name)

        # Update from OPERA arrival data
        self._merge_opera(profile, match)

        # Update from OPERA history
        self._merge_opera_history(profile, match.opera_history)

        # Update from spa records
        self._merge_spa(profile, match.spa_records)

        # Update from F&B records
        self._merge_fb(profile, match.fb_records)

        # Update from incidents
        self._merge_incidents(profile, match.incident_records)

        # Update from concierge
        self._merge_concierge(profile, match.concierge_records)

        # Update from email mentions
        self._merge_emails(profile, match.email_mentions)

        # Compute derived fields
        profile["total_visits"] = len(profile["visits"])
        if profile["visits"]:
            profile["first_visit"] = min(v["checkin"] for v in profile["visits"])
        profile["last_updated"] = target_date

        return profile

    def _empty_profile(self, guest_id: str, name: str) -> dict:
        """Create an empty profile structure."""
        return {
            "guest_id": guest_id,
            "names": [name],
            "emails": [],
            "phones": [],
            "nationality": None,
            "vip_level": None,
            "visits": [],
            "preferences": {
                "dietary": [],
                "wines": [],
                "room_type": None,
                "pillow_type": None,
                "spa_treatments": [],
                "preferred_therapists": [],
                "special_requests": [],
            },
            "spend_history": {
                "total": 0,
                "rooms": 0,
                "fb": 0,
                "spa": 0,
                "concierge": 0,
                "other": 0,
            },
            "incidents": [],
            "concierge_history": [],
            "special_occasions": [],
            "notes": [],
            "first_visit": None,
            "total_visits": 0,
            "last_updated": None,
        }

    def _merge_opera(self, profile: dict, match: MatchResult) -> None:
        """Merge OPERA arrival data into profile."""
        if not match.opera_data:
            return

        data = match.opera_data

        # Update name list
        name = data.get("guestName", "")
        if name and name not in profile["names"]:
            profile["names"].append(name)

        # Nationality
        if data.get("nationality"):
            profile["nationality"] = data["nationality"]

        # VIP level
        if data.get("vip"):
            profile["vip_level"] = data["vip"]

        # Current visit
        visit = {
            "checkin": data.get("date", ""),
            "room": data.get("roomNo"),
            "room_type": data.get("roomType"),
            "rate": data.get("rate", 0),
            "nights": data.get("nights", 0),
            "confirmation": data.get("confirmationNo", ""),
        }
        # Compute checkout
        if visit["checkin"] and visit["nights"]:
            try:
                checkin_dt = datetime.strptime(visit["checkin"], "%Y-%m-%d")
                from datetime import timedelta
                checkout_dt = checkin_dt + timedelta(days=visit["nights"])
                visit["checkout"] = checkout_dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Add visit if not already present (by confirmation number)
        existing_confs = {v.get("confirmation") for v in profile["visits"]}
        if visit["confirmation"] and visit["confirmation"] not in existing_confs:
            profile["visits"].append(visit)

        # Room type preference
        if data.get("roomType"):
            profile["preferences"]["room_type"] = data["roomType"]

        # Notes from OPERA
        notes = data.get("notes", "")
        if notes:
            # Extract dietary info
            lower_notes = notes.lower()
            if "vegetarian" in lower_notes and "vegetarian" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("vegetarian")
            if "vegan" in lower_notes and "vegan" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("vegan")
            if "halal" in lower_notes and "halal" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("halal")
            if "kosher" in lower_notes and "kosher" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("kosher")
            if "allerg" in lower_notes and "feather" in lower_notes:
                profile["preferences"]["pillow_type"] = "hypoallergenic"

            if notes not in profile["notes"]:
                profile["notes"].append(notes)

        # Update room spend
        if visit.get("rate") and visit.get("nights"):
            profile["spend_history"]["rooms"] += visit["rate"] * visit["nights"]

    def _merge_opera_history(self, profile: dict, history: list[dict]) -> None:
        """Merge historical OPERA records into profile."""
        for record in history:
            if record.get("type") == "departure":
                # Departure record has totalSpend
                total_spend = record.get("totalSpend", 0)
                if total_spend:
                    # This is cumulative, tracked separately
                    pass
                continue

            # Historical arrival
            visit = {
                "checkin": record.get("date", ""),
                "room": record.get("roomNo"),
                "room_type": record.get("roomType"),
                "rate": record.get("rate", 0),
                "nights": record.get("nights", 0),
                "confirmation": record.get("confirmationNo", ""),
            }
            existing_confs = {v.get("confirmation") for v in profile["visits"]}
            if visit["confirmation"] and visit["confirmation"] not in existing_confs:
                profile["visits"].append(visit)

            if record.get("vip"):
                profile["vip_level"] = record["vip"]

    def _merge_spa(self, profile: dict, records: list[dict]) -> None:
        """Merge spa booking data into profile."""
        spa_spend = 0
        treatments_seen = set(profile["preferences"]["spa_treatments"])
        therapists_seen = set(profile["preferences"]["preferred_therapists"])

        for record in records:
            if record.get("status") == "completed":
                revenue = record.get("revenue", 0)
                spa_spend += revenue

                # Track treatments
                treatment = record.get("treatment", "")
                if treatment and treatment not in treatments_seen:
                    treatments_seen.add(treatment)

                # Track therapists
                therapists = record.get("therapist", [])
                for t in therapists:
                    if t not in therapists_seen:
                        therapists_seen.add(t)

        profile["preferences"]["spa_treatments"] = list(treatments_seen)
        profile["preferences"]["preferred_therapists"] = list(therapists_seen)
        profile["spend_history"]["spa"] += spa_spend

    def _merge_fb(self, profile: dict, records: list[dict]) -> None:
        """Merge F&B data into profile."""
        for record in records:
            notes = record.get("notes", "")
            if notes and notes not in profile["notes"]:
                profile["notes"].append(f"F&B: {notes}")

    def _merge_incidents(self, profile: dict, records: list[dict]) -> None:
        """Merge incident records into profile."""
        existing_ids = {i.get("id") for i in profile["incidents"]}

        for record in records:
            inc_id = record.get("id", "")
            if inc_id in existing_ids:
                continue

            incident = {
                "id": inc_id,
                "date": record.get("date", ""),
                "category": record.get("category", ""),
                "description": record.get("description", ""),
                "resolution": record.get("resolution"),
                "resolved": record.get("status") == "resolved",
                "priority": record.get("priority", ""),
            }
            profile["incidents"].append(incident)
            existing_ids.add(inc_id)

    def _merge_concierge(self, profile: dict, records: list[dict]) -> None:
        """Merge concierge request data into profile."""
        existing_ids = {c.get("id") for c in profile["concierge_history"]}
        concierge_spend = 0

        for record in records:
            req_id = record.get("id", "")
            if req_id in existing_ids:
                continue

            entry = {
                "id": req_id,
                "date": record.get("date", ""),
                "type": record.get("type", ""),
                "details": record.get("details", ""),
                "status": record.get("status", ""),
            }
            profile["concierge_history"].append(entry)
            existing_ids.add(req_id)

            cost = record.get("cost", 0)
            if cost:
                concierge_spend += cost

            # Extract special occasions
            details_lower = record.get("details", "").lower()
            if "birthday" in details_lower:
                occasion = f"Birthday mentioned ({record.get('date', '')})"
                if occasion not in profile["special_occasions"]:
                    profile["special_occasions"].append(occasion)
            if "anniversar" in details_lower:
                occasion = f"Anniversary mentioned ({record.get('date', '')})"
                if occasion not in profile["special_occasions"]:
                    profile["special_occasions"].append(occasion)

            # Extract dietary from concierge
            if "vegetarian" in details_lower and "vegetarian" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("vegetarian")
            if "no shellfish" in details_lower and "no shellfish" not in profile["preferences"]["dietary"]:
                profile["preferences"]["dietary"].append("no shellfish")

            # Special requests
            if record.get("type") == "special_request":
                detail = record.get("details", "")
                if detail and detail not in profile["preferences"]["special_requests"]:
                    profile["preferences"]["special_requests"].append(detail)

        profile["spend_history"]["concierge"] += concierge_spend

    def _merge_emails(self, profile: dict, records: list[dict]) -> None:
        """Merge email mention data into profile."""
        for record in records:
            note = f"Email mention: {record.get('subject', '')} (from {record.get('from', '')})"
            if note not in profile["notes"]:
                profile["notes"].append(note)

    def finalize_spend(self, profile: dict) -> None:
        """Recompute total spend from components."""
        spend = profile["spend_history"]
        spend["total"] = (
            spend.get("rooms", 0) +
            spend.get("fb", 0) +
            spend.get("spa", 0) +
            spend.get("concierge", 0) +
            spend.get("other", 0)
        )
