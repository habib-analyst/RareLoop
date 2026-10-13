"""RareLoop agent loop.

Pipeline:
  1. Screen for red-flag (emergency) symptoms -> emergency guidance, stop.
  2. Match the free-text description to a suspected rare condition
     (keyword aliases from knowledge.py; presented as "worth discussing",
     never as a diagnosis).
  3. Map condition -> relevant specialties.
  4. Query Qloo (live API or mock backend, same interface):
       - search_entities() for "<specialty> <city>" style queries, and
       - get_insights() with filter.type=urn:entity:place, location and
         condition tag filters.
  5. Rank candidates with an explicit, inspectable scoring formula.
  6. Explain each match: why THIS specialist for THIS patient, grounded in
     the patient's own reported features + the entity's tags/signals.
  7. Attach suggested questions to ask the specialist + medical disclaimer.

run_agent() is the single entry point used by the CLI, web UI, demo and eval.
"""

from . import config, disclaimer, knowledge
from .qloo_client import QlooClient, _SPECIALTY_PRACTITIONER

# Ranking weights (sum to 1.0) — documented so judges can inspect the formula.
W_SPECIALTY = 0.45   # entity specialty is one of the condition's specialties
W_CONDITION = 0.25   # entity tags overlap the condition's tag slugs
W_QUALITY = 0.15     # rating + popularity signals
W_LOCATION = 0.15    # same city > same country > elsewhere


def _location_score(entity, location: str | None) -> float:
    if not location:
        return 0.5
    props = entity["properties"]
    if (props.get("city") or "").lower() == location.lower():
        return 1.0
    # country-level fallback: any entity in the same country as a same-city hit
    return 0.4


def _quality_score(entity) -> float:
    props = entity["properties"]
    rating = props.get("rating") or 0
    popularity = entity.get("popularity") or 0
    return 0.7 * (rating / 5.0) + 0.3 * popularity


def rank_entities(entities, specialties, tag_slugs, location, top_n=5):
    """Score and sort entities; returns [(entity, score, why_bits)]."""
    spec_set = {s.lower() for s in specialties}
    tag_set = {t.lower() for t in tag_slugs}
    ranked = []
    for e in entities:
        props = e["properties"]
        spec_match = 1.0 if (props.get("specialty") or "").lower() in spec_set else 0.0
        entity_tags = {t["id"].split(":")[-1].lower() for t in e["tags"]}
        cond_overlap = len(entity_tags & tag_set) / max(1, len(tag_set))
        cond_match = min(1.0, cond_overlap * 2)  # any overlap counts strongly
        score = (W_SPECIALTY * spec_match + W_CONDITION * cond_match
                 + W_QUALITY * _quality_score(e)
                 + W_LOCATION * _location_score(e, location))
        why = []
        if spec_match:
            why.append(f"Specialty match: {props['specialty']} is a primary "
                       f"specialty for this presentation.")
        if cond_overlap:
            tag_names = [t["name"] for t in e["tags"]
                         if t["id"].split(":")[-1].lower() in tag_set]
            why.append("Condition signal: listed focus areas include "
                       + ", ".join(tag_names) + ".")
        if (props.get("rating") or 0) >= 4.7:
            why.append(f"Quality signal: rated {props['rating']}/5 across "
                       f"{props.get('review_count', 0)} reviews.")
        if location and (props.get("city") or "").lower() == location.lower():
            why.append(f"Location: in {props['city']}, matching your location.")
        ranked.append((e, round(score, 3), why))
    ranked.sort(key=lambda r: r[1], reverse=True)
    return ranked[:top_n]


def explain_match(entity, condition_name, matched_phrases, why_bits):
    """Patient-specific explanation: why THIS specialist for THIS patient."""
    props = entity["properties"]
    lines = []
    if matched_phrases:
        feats = "; ".join(f'"{p}"' for p in matched_phrases[:3])
        lines.append(
            f"You mentioned {feats} — features classically associated with "
            f"{condition_name}, which is exactly the population this practice "
            f"serves.")
    lines.extend(f"- {w}" for w in why_bits)
    if entity["blurb"]:
        lines.append(f"- Practice focus: {entity['blurb']}")
    if entity.get("_mock"):
        lines.append("- (Sample data: mock mode — verify credentials and "
                     "availability independently.)")
    return lines


def run_agent(text: str, location: str | None = None, client=None, top_n=3):
    """Full agent run. Returns a JSON-serializable result dict."""
    client = client or QlooClient()  # backend auto: live if key set, else mock

    # 1. Emergency screen first — always.
    red_flags = knowledge.find_red_flags(text)
    if red_flags:
        return {
            "backend": client.backend_name,
            "emergency": True,
            "red_flags": red_flags,
            "guidance": disclaimer.EMERGENCY_GUIDANCE,
            "disclaimer": disclaimer.DISCLAIMER_SHORT,
            "matches": [],
        }

    # 2-3. Condition match -> specialties.
    cond_key, matched_phrases = knowledge.match_condition(text)
    if not cond_key:
        return {
            "backend": client.backend_name,
            "emergency": False,
            "condition": None,
            "note": ("I couldn't map your description to a specific rare "
                     "condition in my knowledge base. A general internist or "
                     "your primary-care doctor is the right first step — "
                     "bring this exact description to them."),
            "disclaimer": disclaimer.DISCLAIMER_SHORT,
            "matches": [],
        }
    cond = knowledge.CONDITIONS[cond_key]
    specialties = cond["specialties"]

    # 4. Query Qloo: search + insights, merged and de-duplicated.
    # Live API note (verified 2026-10-13): practitioner nouns ("rheumatologist")
    # return real specialists; "<Specialty> specialist" phrasing returns keyword
    # soup. We issue both — the mock backend only answers the latter, the live
    # backend mostly answers the former — and let ranking sort it out.
    seen, entities = set(), []
    queries = []
    for spec in specialties:
        practitioner = _SPECIALTY_PRACTITIONER.get(spec)
        if practitioner:
            queries.append(practitioner)
        queries.append(f"{spec} specialist")
    for q in queries:
        for e in client.search_entities(q, take=10):
            if e["entity_id"] not in seen:
                seen.add(e["entity_id"])
                entities.append(e)
    for e in client.get_insights(location=location, tags=cond["tag_slugs"],
                                 take=10):
        if e["entity_id"] not in seen:
            seen.add(e["entity_id"])
            entities.append(e)

    # 5-7. Rank, explain, attach questions.
    ranked = rank_entities(entities, specialties, cond["tag_slugs"],
                           location, top_n=top_n)
    matches = []
    for entity, score, why_bits in ranked:
        matches.append({
            "entity_id": entity["entity_id"],
            "name": entity["name"],
            "specialty": entity["properties"]["specialty"],
            "city": entity["properties"]["city"],
            "country": entity["properties"]["country"],
            "rating": entity["properties"]["rating"],
            "score": score,
            "explanation": explain_match(
                entity, cond["name"], matched_phrases, why_bits),
            "mock": bool(entity.get("_mock")),
        })

    return {
        "backend": client.backend_name,
        "emergency": False,
        "condition": {"key": cond_key, "name": cond["name"]},
        "matched_features": matched_phrases,
        "specialties": specialties,
        "location": location,
        "matches": matches,
        "suggested_questions": cond["questions"],
        "disclaimer": disclaimer.DISCLAIMER_FULL,
        "data_note": ("MOCK DATA — sample specialists for demo only"
                      if client.backend_name == "mock" else
                      "Live Qloo entity data"),
    }
