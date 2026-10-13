#!/usr/bin/env python3
"""Scripted <5-minute demo conversation for judges.

Runs the full RareLoop flow end-to-end in mock mode:
  patient describes symptoms -> agent screens, matches, queries Qloo (mock),
  ranks, explains each pick patient-specifically, suggests questions.

Usage:  python3 demo/scripted_demo.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import config
from src.agent import run_agent
from src.qloo_client import QlooClient
from demo.cli import render

PATIENT_TURNS = [
    ("patient",
     "Hi. For years my shoulders and knees have dislocated doing ordinary "
     "things, my skin stretches way more than normal, and I've always been "
     "double-jointed. Doctors keep saying it's just growing pains. "
     "I'm in Lahore — who should I actually see?"),
]

PAUSE = 0.4  # small beat between turns; total runtime stays well under 5 min


def say(who: str, text: str):
    print(f"\n{'=' * 70}\n{who.upper()}:\n{text}\n")
    time.sleep(PAUSE)


def main():
    start = time.time()
    print("RareLoop — scripted demo (mock Qloo backend, clearly labeled)")
    print(f"Backend: {config.describe()}")
    client = QlooClient()  # auto -> mock without a key

    for who, text in PATIENT_TURNS:
        say(who, text)
        print("AGENT (working: emergency screen -> condition match -> "
              "Qloo search+insights -> rank -> explain)...")
        time.sleep(PAUSE)
        result = run_agent(text, location="Lahore", client=client, top_n=3)
        say("agent", render(result))

    elapsed = time.time() - start
    print(f"\n[demo finished in {elapsed:.1f}s — full flow, "
          f"{'under' if elapsed < 300 else 'OVER'} the 5-minute budget]")


if __name__ == "__main__":
    main()
