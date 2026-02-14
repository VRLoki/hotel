"""
Guest Intelligence — Arrival Alerts & Briefs.

Generates LLM-powered arrival briefs for each guest checking in today.
Briefs are concise, actionable summaries for hotel staff.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from config import settings


GUEST_BRIEF_SYSTEM_PROMPT = """\
You are Hotel Intel's Guest Intelligence module for a luxury hotel.
You produce concise, actionable guest arrival briefs for hotel staff.

Style guidelines:
- Professional, warm tone befitting a luxury property
- Lead with the most important information (VIP status, dietary needs, past issues)
- Highlight anything staff should act on before or during the guest's stay
- For returning guests: emphasize history, preferences, and past issues to avoid
- For new guests: note any preferences from their current booking data
- Keep each brief to 3-5 sentences maximum
- Use specific details (room numbers, treatment names, restaurant preferences)
- Flag any unresolved issues from past stays
- Mention lifetime spend for high-value returning guests
- Note special occasions (birthdays, anniversaries) if during stay
"""


def build_guest_brief_prompt(profile: dict) -> str:
    """Build an LLM prompt to generate a guest arrival brief."""
    visits = profile.get("visits", [])
    total_visits = profile.get("total_visits", len(visits))
    is_returning = total_visits > 1

    # Determine current visit
    current_visit = visits[-1] if visits else {}

    prompt = f"""Generate a concise arrival brief for hotel staff about this guest.

## GUEST PROFILE

```json
{json.dumps(profile, indent=2, default=str)}
```

## CONTEXT

- Guest: {profile.get('names', ['Unknown'])[0]}
- {"Returning guest" if is_returning else "First-time guest"} ({total_visits} total visit{"s" if total_visits != 1 else ""})
- Room: {current_visit.get('room', 'TBD')} ({current_visit.get('room_type', '')})
- Stay: {current_visit.get('nights', '?')} nights
- Nationality: {profile.get('nationality', 'Unknown')}
- VIP Level: {profile.get('vip_level', 'None')}
- Currency: {settings.CURRENCY}

## INSTRUCTIONS

Write a brief (3-5 sentences) that a front desk manager, concierge chief, or F&B manager
would find immediately useful. Start with an emoji indicator:
- 🆕 for first-time guests
- ⭐ for returning guests
- 👑 for VIP guests

Include:
1. Guest status (new/returning, VIP level, nationality)
2. Key preferences and dietary needs (if any)
3. Current bookings for this stay (spa, dining, concierge)
4. Past issues to be aware of (if returning)
5. Any special occasions or notable arrangements

Be specific — use names, room numbers, treatment names, restaurant names from the data.
Do NOT invent information not present in the profile.
"""
    return prompt


class ArrivalBriefGenerator:
    """Generates LLM-powered arrival briefs for today's guests."""

    def generate_briefs(
        self,
        profiles: list[dict],
        provider_override: str | None = None,
    ) -> list[dict]:
        """
        Generate arrival briefs for a list of guest profiles.

        Args:
            profiles: List of guest profile dicts.
            provider_override: Override LLM provider.

        Returns:
            List of dicts with guest_id, name, and brief text.
        """
        from llm import get_provider

        provider_name = provider_override or settings.LLM_PROVIDER
        llm = get_provider(provider_name)

        briefs = []
        for profile in profiles:
            guest_name = profile.get("names", ["Unknown"])[0]
            try:
                prompt = build_guest_brief_prompt(profile)
                brief_text = llm.generate(
                    prompt=prompt,
                    system_prompt=GUEST_BRIEF_SYSTEM_PROMPT,
                )
                briefs.append({
                    "guest_id": profile.get("guest_id"),
                    "name": guest_name,
                    "room": profile["visits"][-1].get("room") if profile.get("visits") else None,
                    "brief": brief_text.strip(),
                    "flags": self._extract_flags(profile),
                })
            except Exception as e:
                briefs.append({
                    "guest_id": profile.get("guest_id"),
                    "name": guest_name,
                    "room": profile["visits"][-1].get("room") if profile.get("visits") else None,
                    "brief": f"[Brief generation failed: {e}]",
                    "flags": self._extract_flags(profile),
                })

        return briefs

    def generate_briefs_dry_run(self, profiles: list[dict]) -> list[dict]:
        """
        Generate structured briefs without LLM (for dry-run mode).

        Returns a summary of each profile's key data points.
        """
        briefs = []
        for profile in profiles:
            guest_name = profile.get("names", ["Unknown"])[0]
            visits = profile.get("visits", [])
            current = visits[-1] if visits else {}
            total_visits = profile.get("total_visits", len(visits))

            # Build a simple text brief
            lines = []
            prefix = "🆕" if total_visits <= 1 else "⭐"
            if profile.get("vip_level"):
                prefix = "👑"

            lines.append(
                f"{prefix} **{guest_name}** — Room {current.get('room', '?')} "
                f"({current.get('room_type', '?')}) · {current.get('nights', '?')} nights "
                f"· {profile.get('nationality', '?')}"
            )

            if profile.get("vip_level"):
                lines.append(f"   VIP Level: {profile['vip_level']}")

            if total_visits > 1:
                lines.append(f"   Returning guest — visit #{total_visits}")

            dietary = profile.get("preferences", {}).get("dietary", [])
            if dietary:
                lines.append(f"   🥗 Dietary: {', '.join(dietary)}")

            spa = profile.get("preferences", {}).get("spa_treatments", [])
            if spa:
                lines.append(f"   💆 Spa: {', '.join(spa)}")

            incidents = profile.get("incidents", [])
            if incidents:
                latest = incidents[-1]
                lines.append(
                    f"   ⚠️ Past issue: {latest.get('description', '')[:80]}"
                )

            spend = profile.get("spend_history", {})
            if spend.get("total", 0) > 0:
                lines.append(f"   💰 Lifetime spend: {settings.CURRENCY}{spend['total']:,.0f}")

            briefs.append({
                "guest_id": profile.get("guest_id"),
                "name": guest_name,
                "room": current.get("room"),
                "brief": "\n".join(lines),
                "flags": self._extract_flags(profile),
            })

        return briefs

    @staticmethod
    def _extract_flags(profile: dict) -> list[str]:
        """Extract actionable flags from a profile."""
        flags = []
        total_visits = profile.get("total_visits", 0)

        if total_visits <= 1:
            flags.append("first_visit")
        if total_visits >= 3:
            flags.append("loyal_guest")
        if profile.get("vip_level"):
            flags.append(f"vip_{profile['vip_level']}")

        dietary = profile.get("preferences", {}).get("dietary", [])
        if dietary:
            flags.extend([f"dietary_{d}" for d in dietary])

        unresolved = [
            i for i in profile.get("incidents", [])
            if not i.get("resolved", True)
        ]
        if unresolved:
            flags.append("unresolved_incident")

        spend = profile.get("spend_history", {}).get("total", 0)
        if spend > 20000:
            flags.append("high_value")

        if profile.get("special_occasions"):
            flags.append("special_occasion")

        return flags
