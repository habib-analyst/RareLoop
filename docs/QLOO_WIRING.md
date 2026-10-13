# Qloo API Wiring Guide

The single wiring point for the real Qloo API. Read this when the API key lands.

## 1. Where the key goes (one-line change)

```bash
export QLOO_API_KEY="paste-the-real-key-here"
```

That's it. `src/config.py::get_backend()` returns `"live"` if and only if
`QLOO_API_KEY` is set and non-empty; otherwise the client uses the mock
backend. No code edits, no config files. Every entry point (`demo/cli.py`,
`demo/scripted_demo.py`, `demo/eval_vignettes.py`, `web/app.py`) picks this
up automatically because they all construct `QlooClient()` with
`backend="auto"`.

Optional: if the issued key targets a different environment, override the base URL:

```bash
export QLOO_API_BASE="https://api.qloo.com/v2"   # default: https://hackathon.api.qloo.com/v2
```

Never commit a real key. `.env.example` shows the expected variables; load them
with `export $(cat .env | xargs)` or your shell's equivalent.

## 2. Endpoints used (all real Qloo v2 endpoints)

| Method | Path | Key params | Purpose in RareLoop |
|---|---|---|---|
| GET | `/search` | `query`, `types=urn:entity:place`, `take` | Find clinics/practices by "<specialty> specialist" text |
| GET | `/insights` | `filter.type=urn:entity:place`, `filter.location.query`, `filter.tags`, `take` | Taste/entity recommendations: places near the patient matching condition tags |
| GET | `/entities/{entity_id}` | — | (Available via `client.get_entity()`; not yet used in the agent loop — reserved for a detail view) |

Auth: `X-Api-Key: <QLOO_API_KEY>` header on every request (see
`LiveQlooBackend._get` in `src/qloo_client.py`).

Entity URN used throughout: `urn:entity:place` — clinics, hospitals and
specialty practices are *places* in Qloo's entity graph.

## 3. What a real response looks like vs the mock

Both backends return the **normalized entity shape** (see
`normalize_entity()` in `src/qloo_client.py`), so agent/ranker/explainer code
is backend-agnostic:

```json
{
  "entity_id": "…",
  "name": "…",
  "type": "urn:entity:place",
  "properties": {
    "address": "…", "city": "…", "country": "…",
    "specialty": "…", "rating": 4.8, "review_count": 214
  },
  "tags": [{"id": "urn:tag:…", "name": "…"}],
  "popularity": 0.82,
  "affinity": 0.91,
  "_mock": false
}
```

Differences to expect in **live** mode:

- `entity_id` values are opaque Qloo ids (mock ids are prefixed `mock:`).
- `_mock` is `false`; mock mode sets it `true` and every UI labels mock data.
- `properties.specialty` may be absent — the live ranker path relies more on
  tag overlap and the search query itself. `normalize_entity()` degrades
  missing fields to `None`/`[]` instead of raising.
- `tags` use real Qloo tag URNs (e.g. `urn:tag:genre:…` style ids), not the
  `urn:tag:mock:<slug>` ids in the sample data. Condition matching in live
  mode therefore keys off tag *names* and the search query, not mock slugs.
- `rating`/`review_count`/`popularity` come from Qloo's signals where
  available; the ranker's quality term handles missing values gracefully.

## 4. Verify once the key lands (checklist)

```bash
cd ~/workspace/earning/hackathons/builds/qloo-rare-disease-agent

# 1. Key is picked up and backend flips to live
export QLOO_API_KEY="your-key"
python3 -c "from src import config; print(config.describe())"
# expect: live Qloo API @ https://hackathon.api.qloo.com/v2 (key present)

# 2. Raw endpoint sanity (auth + shape)
curl -s -H "X-Api-Key: $QLOO_API_KEY" \
  "https://hackathon.api.qloo.com/v2/search?query=cardiology%20clinic&types=urn:entity:place&take=3" \
  | python3 -m json.tool | head -40

# 3. Insights endpoint sanity
curl -s -H "X-Api-Key: $QLOO_API_KEY" \
  "https://hackathon.api.qloo.com/v2/insights?filter.type=urn:entity:place&filter.location.query=Lahore&take=3" \
  | python3 -m json.tool | head -40

# 4. Full agent run against the live API
python3 demo/cli.py --text "my shoulders dislocate easily, my skin is very stretchy" \
  --location Lahore

# 5. Re-run the vignette eval in live mode and compare with the mock baseline (10/10)
python3 demo/eval_vignettes.py
```

Verify:
- [ ] `/search` returns `results.entities` (array); each has `name` + `properties`.
- [ ] `/insights` honors `filter.type=urn:entity:place` and `filter.location.query`.
- [ ] Tag ids/names in live payloads map sensibly onto the condition tag slugs in `src/knowledge.py`; adjust `tag_slugs`/aliases if Qloo's taxonomy differs (this is the most likely live-mode tuning).
- [ ] `normalize_entity()` handles the real payload without exceptions (watch for renamed fields).
- [ ] Live vignette eval score recorded in BUILD_LOG.md next to the mock baseline.
- [ ] No mock-labeled output appears when `QLOO_API_KEY` is set.

## 5. Known unknowns (to confirm against the live API)

- Exact `/search` parameter names (`query`/`types`/`take` per hackathon SDKs and
  docs — confirm if a 400 comes back).
- Whether `filter.tags` on `/insights` accepts tag URNs, names, or both.
- Whether place entities carry medical-category tags natively, or whether
  specialty relevance must come from the search query + tag names (the agent is
  written to work either way).

## 4. Live verification (2026-10-13 — key received, wired, eval re-run)

Real API shapes (differ from what the scaffold assumed — now handled):
- `GET /search` → `{"results": [...]}` — results is a LIST of entities.
- `GET /insights` → `{"success","results":{"entities":[...]},"query"}` — results is a DICT.
- Entity: `type="urn:entity"` + `subtype="urn:entity:place"`; NO `specialty`
  field (derived from name/disambiguation/tags via keyword map in
  `qloo_client.py`); rating is `properties.business_rating`; city/country
  from `properties.localities`; blurb from `properties.description`.
- Query strategy: practitioner nouns (`rheumatologist`) return real doctors;
  `"<Specialty> specialist"` phrasing returns keyword soup. Agent issues both
  (mock backend only answers the latter) and ranking sorts it out.

Eval result on LIVE backend: 10/10 vignettes pass (C1+C2) + safety vignette
pass. Mock backend unaffected: still 10/10. `normalize_entity` now sets
`blurb` (live crashed on its absence before this fix).
