#!/usr/bin/env python3
"""
Hotel Intel — Daily Recap & Guest Intelligence.

CLI entry point. Supports two modes:
  - recap:       Collect data, process KPIs, generate daily recap via LLM
  - guest-intel: Match today's arrivals across systems, build profiles, generate briefs
  - both:        Run both modules

Usage:
    python main.py                              # Default: recap mode
    python main.py --mode guest-intel           # Guest intelligence only
    python main.py --mode both                  # Both modules
    python main.py --mode guest-intel --dry-run # Show profiles without LLM
    python main.py --date 2026-02-12            # Specific date
    python main.py --provider anthropic         # Override LLM provider
    python main.py --output console             # Output mode
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure app directory is on the path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from collectors import ALL_COLLECTORS
from processor import process
from generator import generate_recap
from delivery import get_delivery


DEFAULT_DATE = "2026-02-13"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hotel Intel — Daily recap & guest intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode", "-m",
        default="recap",
        choices=["recap", "guest-intel", "both"],
        help="Operating mode (default: recap)",
    )
    parser.add_argument(
        "--date", "-d",
        default=DEFAULT_DATE,
        help=f"Target date in YYYY-MM-DD format (default: {DEFAULT_DATE})",
    )
    parser.add_argument(
        "--provider", "-p",
        default=None,
        choices=["openai", "anthropic", "mistral", "local"],
        help="LLM provider override (default: from .env)",
    )
    parser.add_argument(
        "--output", "-o",
        default=settings.DEFAULT_OUTPUT,
        choices=["console", "email", "telegram"],
        help=f"Delivery channel (default: {settings.DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect & process data but skip LLM generation (dumps JSON/profiles)",
    )
    return parser.parse_args()


def collect_all(target_date: str) -> dict:
    """Run all collectors and return their outputs keyed by short name."""
    collector_map = {
        "opera": 0,    # OperaCollector
        "spa": 1,      # SpaCollector
        "fb": 2,       # FBCollector
        "incidents": 3, # IncidentsCollector
        "concierge": 4, # ConciergeCollector
        "villas": 5,    # VillasCollector
        "m365": 6,      # M365Collector
    }

    results = {}
    names = list(collector_map.keys())

    for i, CollectorClass in enumerate(ALL_COLLECTORS):
        name = names[i]
        try:
            collector = CollectorClass()
            data = collector.collect(target_date)
            results[name] = data
            status = "✓" if data.get("available", False) else "⚠ no data"
            print(f"  [{status}] {CollectorClass.SOURCE_NAME}")
        except Exception as e:
            print(f"  [✗] {CollectorClass.SOURCE_NAME}: {e}", file=sys.stderr)
            results[name] = {"source": CollectorClass.SOURCE_NAME, "available": False, "error": str(e)}

    return results


def run_recap(collector_data: dict, target_date: str, args: argparse.Namespace) -> None:
    """Run Module 1: Daily Recap."""
    print("⚙️  Processing KPIs...")
    summary = process(collector_data, target_date)
    print(f"   Occupancy: {summary['occupancy_pct']}% | ADR: {summary['currency']}{summary['adr']:,.0f} | RevPAR: {summary['currency']}{summary['revpar']:,.0f}")
    print(f"   Total Revenue: {summary['currency']}{summary['total_revenue']:,.0f} | F&B Covers: {summary['fb_total_covers']} | Spa Bookings: {summary['spa_bookings']}")
    print()

    if args.dry_run:
        print("🔍 Dry run — processed data:")
        print(json.dumps(summary, indent=2, default=str))
        return

    provider = args.provider or settings.LLM_PROVIDER
    print(f"🤖 Generating recap via {provider}...")
    try:
        recap = generate_recap(summary, provider_override=args.provider)
    except Exception as e:
        print(f"\n❌ LLM generation failed: {e}", file=sys.stderr)
        print("   Tip: run with --dry-run to see processed data without LLM", file=sys.stderr)
        return
    print()

    print(f"📤 Delivering via {args.output}...")
    channel = get_delivery(args.output)
    channel.deliver(recap, subject=f"Hotel Intel — {settings.HOTEL_NAME} — {target_date}")


def run_guest_intel(collector_data: dict, target_date: str, args: argparse.Namespace) -> None:
    """Run Module 2: Guest Intelligence."""
    from guest_intel import GuestMatcher, ProfileBuilder, ProfileStore, ArrivalBriefGenerator

    # Step 1: Match arrivals across all systems
    print("🔍 Matching today's arrivals across all systems...")
    matcher = GuestMatcher(collector_data)
    matches = matcher.match_arrivals(target_date)

    if not matches:
        print("   No arrivals found for today.")
        return

    for match in matches:
        systems_found = []
        if match.spa_records:
            systems_found.append(f"spa({len(match.spa_records)})")
        if match.fb_records:
            systems_found.append(f"fb({len(match.fb_records)})")
        if match.incident_records:
            systems_found.append(f"incidents({len(match.incident_records)})")
        if match.concierge_records:
            systems_found.append(f"concierge({len(match.concierge_records)})")
        if match.email_mentions:
            systems_found.append(f"email({len(match.email_mentions)})")
        if match.opera_history:
            systems_found.append(f"history({len(match.opera_history)})")

        cross_refs = ", ".join(systems_found) if systems_found else "no cross-references"
        print(f"   ✓ {match.guest_name} (Room {match.room}) — {cross_refs}")
    print()

    # Step 2: Build/update profiles
    print("👤 Building guest profiles...")
    store = ProfileStore()
    builder = ProfileBuilder(store)
    profiles = builder.build_profiles(matches, target_date)

    for profile in profiles:
        builder.finalize_spend(profile)
        store.save(profile)  # Save with finalized spend

    for profile in profiles:
        visits = profile.get("total_visits", 0)
        spend = profile.get("spend_history", {}).get("total", 0)
        status = "returning" if visits > 1 else "new"
        print(f"   ✓ {profile['names'][0]} — {status} guest, {visits} visit(s), {settings.CURRENCY}{spend:,.0f} total spend")
    print()

    # Step 3: Generate arrival briefs
    if args.dry_run:
        print("🔍 Dry run — guest profiles & briefs (no LLM):")
        alert_gen = ArrivalBriefGenerator()
        briefs = alert_gen.generate_briefs_dry_run(profiles)
        print()
        for brief in briefs:
            print(brief["brief"])
            if brief["flags"]:
                print(f"   Flags: {', '.join(brief['flags'])}")
            print()
        return

    provider = args.provider or settings.LLM_PROVIDER
    print(f"🤖 Generating arrival briefs via {provider}...")
    alert_gen = ArrivalBriefGenerator()
    try:
        briefs = alert_gen.generate_briefs(profiles, provider_override=args.provider)
    except Exception as e:
        print(f"\n❌ Brief generation failed: {e}", file=sys.stderr)
        print("   Tip: run with --dry-run to see profiles without LLM", file=sys.stderr)
        return
    print()

    # Deliver briefs
    print(f"📤 Delivering arrival briefs via {args.output}...")
    output_parts = [f"🎯 **Guest Intelligence — Arrival Briefs — {target_date}**\n"]
    output_parts.append(f"*{len(briefs)} guest(s) arriving today*\n")
    output_parts.append("---\n")

    for brief in briefs:
        output_parts.append(brief["brief"])
        output_parts.append("\n---\n")

    full_output = "\n".join(output_parts)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_output += f"\n*Generated by Hotel Intel Guest Intelligence · {timestamp}*"

    channel = get_delivery(args.output)
    channel.deliver(full_output, subject=f"Guest Intel — {settings.HOTEL_NAME} — {target_date}")


def main():
    args = parse_args()
    target_date = args.date

    print(f"🏨 Hotel Intel — {settings.HOTEL_NAME}")
    print(f"📅 Date: {target_date} | Mode: {args.mode}")
    print()

    # ── Collect data (shared across modules) ──
    print("📡 Collecting data...")
    collector_data = collect_all(target_date)
    print()

    # ── Run requested module(s) ──────────────
    if args.mode in ("recap", "both"):
        print("═" * 50)
        print("📊 MODULE 1: DAILY RECAP")
        print("═" * 50)
        run_recap(collector_data, target_date, args)
        print()

    if args.mode in ("guest-intel", "both"):
        print("═" * 50)
        print("👤 MODULE 2: GUEST INTELLIGENCE")
        print("═" * 50)
        run_guest_intel(collector_data, target_date, args)
        print()

    print("✅ Done!")


if __name__ == "__main__":
    main()
