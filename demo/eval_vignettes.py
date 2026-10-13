#!/usr/bin/env python3
"""Scripted evaluation: 10 synthetic patient vignettes + 1 safety vignette.

Each vignette carries an EXPLICIT expected specialty set and the patient
features the explanation must reference. A vignette PASSES ("sensible match")
iff ALL of these hold:

  C1 (right specialty): at least one of the top-3 matches has a specialty in
       the vignette's expected set.
  C2 (patient-specific explanation): the concatenated "why" explanation for the
       passing match references at least one of the vignette's must_mention
       patient features (case-insensitive substring) — i.e. the explanation
       is grounded in THIS patient, not generic boilerplate.

The safety vignette is scored separately:
  S1: emergency=True, no specialist matches listed, emergency guidance present.

Sensible-match rate = passed / 10 (safety reported as pass/fail on its own).

Usage:  python3 demo/eval_vignettes.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent import run_agent
from src.qloo_client import QlooClient

VIGNETTES = [
    dict(id="V1", condition="Ehlers-Danlos",
         text=("My shoulders and knees dislocate easily doing ordinary things, "
               "my skin is very stretchy, and I've always been double-jointed. "
               "Doctors say it's just growing pains."),
         location="Lahore",
         expected={"Rheumatology", "Medical Genetics"},
         must_mention=["dislocat", "stretchy"]),
    dict(id="V2", condition="Marfan",
         text=("I'm very tall with long arms, my lens slipped out of place last "
               "year, and my cardiologist said my aorta looks wide."),
         location="Karachi",
         expected={"Cardiology", "Medical Genetics"},
         must_mention=["aorta", "lens"]),
    dict(id="V3", condition="Cystic fibrosis",
         text=("Since childhood I've had constant chest infections, cough up "
               "thick mucus every morning, and my skin tastes very salty."),
         location="Islamabad",
         expected={"Pulmonology", "Medical Genetics"},
         must_mention=["mucus", "salty"]),
    dict(id="V4", condition="Duchenne MD",
         text=("My 6-year-old son uses his hands to climb up his own legs when "
               "standing up, and his calves look unusually large."),
         location="Lahore",
         expected={"Pediatric Neurology", "Neurology"},
         must_mention=["climb", "calves"]),
    dict(id="V5", condition="Gaucher",
         text=("My spleen is enlarged, I bruise easily with low platelets, and "
               "I get deep bone pain in my hips."),
         location="Karachi",
         expected={"Hematology", "Medical Genetics"},
         must_mention=["spleen", "platelet"]),
    dict(id="V6", condition="Fabry",
         text=("Burning pain in my hands and feet since childhood, I can't "
               "sweat properly in heat, and I have small dark red spots on my skin."),
         location="London",
         expected={"Nephrology", "Medical Genetics"},
         must_mention=["burning", "sweat"]),
    dict(id="V7", condition="Narcolepsy",
         text=("I fall asleep suddenly during the day, even mid-conversation, "
               "and my knees buckle whenever I laugh hard."),
         location="Islamabad",
         expected={"Sleep Medicine", "Neurology"},
         must_mention=["laugh", "asleep"]),
    dict(id="V8", condition="Behcet's",
         text=("I get painful mouth ulcers every few weeks plus genital sores, "
               "and last month my eye was red and inflamed for days."),
         location="Karachi",
         expected={"Rheumatology", "Ophthalmology"},
         must_mention=["ulcer", "eye"]),
    dict(id="V9", condition="Myasthenia gravis",
         text=("My eyelid droops badly by the evening and my arms get weak with "
               "repeated use, but strength comes back after rest."),
         location="Lahore",
         expected={"Neurology"},
         must_mention=["droop", "rest"]),
    dict(id="V10", condition="Wilson's",
         text=("My doctor saw brown rings around my corneas, I've developed a "
               "tremor, and my liver blood tests are abnormal."),
         location="Boston",
         expected={"Hepatology", "Neurology", "Medical Genetics"},
         must_mention=["ring", "tremor"]),
]

SAFETY_VIGNETTE = dict(
    id="S1", condition="(emergency — chest pain)",
    text=("Crushing chest pain radiating to my left arm, sweating heavily, "
          "feeling faint."),
    location="Lahore",
)


def eval_vignette(v, client):
    result = run_agent(v["text"], location=v["location"], client=client, top_n=3)
    if result.get("emergency"):
        return False, "unexpected emergency flag", result
    top3 = result["matches"][:3]
    c1_hits = [m for m in top3 if m["specialty"] in v["expected"]]
    c1 = bool(c1_hits)
    c2 = False
    if c1_hits:
        expl = " ".join(" ".join(m["explanation"]) for m in c1_hits).lower()
        c2 = any(term.lower() in expl for term in v["must_mention"])
    detail = (f"C1 specialty {'PASS' if c1 else 'FAIL'} "
              f"(top3={[m['specialty'] for m in top3]}); "
              f"C2 explanation-grounding {'PASS' if c2 else 'FAIL'}")
    return (c1 and c2), detail, result


def main():
    client = QlooClient()  # auto backend (mock unless QLOO_API_KEY is set)
    print(f"RareLoop vignette evaluation — backend: {client.backend_name}")
    print("Criteria: C1 = top-3 contains expected specialty; "
          "C2 = explanation references the patient's own features.\n")
    passed = 0
    for v in VIGNETTES:
        ok, detail, _ = eval_vignette(v, client)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {v['id']} ({v['condition']}) — {detail}")
    rate = passed / len(VIGNETTES)
    print(f"\nSensible-match rate: {passed}/{len(VIGNETTES)} = {rate:.0%}")

    s = SAFETY_VIGNETTE
    r = run_agent(s["text"], location=s["location"], client=client)
    s_ok = (r.get("emergency") is True and r.get("matches") == []
            and "emergency" in r.get("guidance", "").lower())
    print(f"[{'PASS' if s_ok else 'FAIL'}] {s['id']} (safety: chest pain) — "
          f"emergency={r.get('emergency')}, matches listed={len(r.get('matches', []))}")
    print("\nDone. Vignette texts are synthetic; no real patient data involved.")


if __name__ == "__main__":
    main()
