#!/usr/bin/env python3
"""RareLoop CLI demo.

Interactive mode:
    python3 demo/cli.py

One-shot:
    python3 demo/cli.py --text "my shoulders dislocate easily, stretchy skin" \\
        --location Lahore

JSON output (for piping into other tools):
    python3 demo/cli.py --text "..." --location Lahore --json
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import config
from src.agent import run_agent
from src.qloo_client import QlooClient


def render(result: dict) -> str:
    out = []
    out.append(f"[RareLoop backend: {config.describe()}]")
    out.append("")
    if result.get("emergency"):
        out.append("!! POSSIBLE EMERGENCY — specialist matching skipped.")
        out.append(f"Detected red-flag phrases: {', '.join(result['red_flags'])}")
        out.append("")
        out.append(result["guidance"])
        out.append("")
        out.append(result["disclaimer"])
        return "\n".join(out)

    if not result.get("condition"):
        out.append(result["note"])
        out.append("")
        out.append(result["disclaimer"])
        return "\n".join(out)

    out.append(f"Suspected area (discuss with a clinician): {result['condition']['name']}")
    if result.get("matched_features"):
        out.append(f"Key features picked up: {', '.join(result['matched_features'])}")
    out.append(f"Relevant specialties: {', '.join(result['specialties'])}")
    if result.get("location"):
        out.append(f"Location preference: {result['location']}")
    out.append("")
    out.append(f"Top {len(result['matches'])} specialist matches "
               f"({result['data_note']}):")
    out.append("=" * 70)
    for i, m in enumerate(result["matches"], 1):
        out.append(f"{i}. {m['name']}")
        out.append(f"   {m['specialty']} — {m['city']}, {m['country']} "
                   f"| rating {m['rating']}/5 | match score {m['score']}")
        out.append("   Why this specialist for YOU:")
        for line in m["explanation"]:
            out.append(f"   {line}")
        out.append("")
    out.append("Questions to ask at the appointment:")
    for q in result["suggested_questions"]:
        out.append(f"  - {q}")
    out.append("")
    out.append(result["disclaimer"])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="RareLoop rare-disease specialist finder")
    ap.add_argument("--text", help="symptom description (otherwise interactive)")
    ap.add_argument("--location", help="preferred city, e.g. Lahore")
    ap.add_argument("--top", type=int, default=3, help="number of matches to show")
    ap.add_argument("--json", action="store_true", help="emit raw JSON result")
    ap.add_argument("--live", action="store_true",
                    help="force live Qloo backend (requires QLOO_API_KEY)")
    args = ap.parse_args()

    backend = "live" if args.live else "auto"
    client = QlooClient(backend=backend)

    text = args.text
    location = args.location
    if not text:
        print("RareLoop — describe the symptoms or suspected condition.")
        print("(This is an informational aid, not a diagnosis.)")
        text = input("\nPatient > ").strip()
        if not location:
            location = input("Preferred city (optional) > ").strip() or None
    if not text:
        print("No description given — exiting.")
        return

    result = run_agent(text, location=location, client=client, top_n=args.top)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print()
        print(render(result))


if __name__ == "__main__":
    main()
