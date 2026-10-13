# RareLoop — rare-disease specialist-finder agent on the Qloo API

**Qloo Agentic AI Hackathon ($25,000)** · built by Habib Ur Rehman
([habib-analyst](https://github.com/habib-analyst)) · registered solo on Devpost.

Rare-disease patients wait **years** for the right specialist — not because
specialists don't exist, but because patients can't find them. RareLoop is an
agentic loop that takes a free-text symptom description, screens for
emergencies, maps the presentation to candidate rare conditions and
specialties, queries the **Qloo API** for relevant clinics/practices as place
entities, ranks them with an explicit inspectable formula, and explains
**why each specialist fits THIS patient** — grounded in the patient's own
reported features — plus suggested questions to ask at the appointment.

> **Status: scaffold + full architecture, mock-data mode.** The Qloo API key
> is not in hand yet, so the agent runs against realistic fictional sample
> data through the *exact same client interface* as the live API. Setting the
> key is a one-line change (`export QLOO_API_KEY=…`) — see
> [docs/QLOO_WIRING.md](docs/QLOO_WIRING.md). Mock output is always labeled.

## The <5-minute demo

```bash
cd ~/workspace/earning/hackathons/builds/qloo-rare-disease-agent

# 1. Scripted end-to-end conversation (runs in ~1s)
python3 demo/scripted_demo.py

# 2. Interactive CLI
python3 demo/cli.py

# 3. One-shot query
python3 demo/cli.py --text "my shoulders dislocate easily, my skin is very stretchy" --location Lahore

# 4. Vignette evaluation (10 synthetic cases + safety check)
python3 demo/eval_vignettes.py

# 5. Minimal web UI (stdlib only) → http://localhost:8765
python3 web/app.py
```

No dependencies to install (`requirements.txt` is stdlib-only), $0 spend.

## Architecture

```
patient text
    │
    ▼
┌─────────────┐   ┌──────────────┐   ┌───────────────────┐
│ emergency   │──▶│ condition    │──▶│ specialty mapping │
│ screen      │   │ match        │   │ (knowledge.py)    │
└─────────────┘   └──────────────┘   └─────────┬─────────┘
                                               ▼
                                    ┌───────────────────┐
                                    │ QlooClient        │  ◀── QLOO_API_KEY
                                    │ ┌───────────────┐ │      present? live
                                    │ │ Live backend  │ │      : mock
                                    │ │ (urllib→/v2)  │ │
                                    │ ├───────────────┤ │
                                    │ │ Mock backend  │ │  identical interface
                                    │ │ (14 fictional │ │  identical shapes
                                    │ │  specialists) │ │
                                    │ └───────────────┘ │
                                    │ search_entities / get_insights / get_entity
                                    └─────────┬─────────┘
                                              ▼
                                    ┌───────────────────┐
                                    │ rank (explicit    │
                                    │ weights) → explain│  "why THIS specialist
                                    │ (patient-grounded)│   for THIS patient"
                                    └─────────┬─────────┘
                                              ▼
                              matches + questions + medical disclaimer
```

- **Judge hook:** explanation quality. Every match carries a *why* grounded in
  the patient's own words ("You mentioned 'double-jointed'; 'dislocat' — …"),
  specialty fit, Qloo tag signals, and quality/location signals — plus 3
  condition-specific questions to ask the specialist.
- **Safety:** red-flag symptoms (chest pain, stroke signs, …) short-circuit to
  emergency guidance with **no** specialist list. A medical disclaimer ships on
  every surface. The agent never diagnoses — it suggests "worth discussing
  with a clinician."

## Mock vs live wiring

| | Mock mode (now) | Live mode (key set) |
|---|---|---|
| Backend | `MockQlooBackend`, 14 fictional specialists | `LiveQlooBackend` → `https://hackathon.api.qloo.com/v2` |
| Endpoints | same method signatures | `GET /search`, `GET /insights`, `GET /entities/{id}`, `X-Api-Key` auth |
| Entity shape | normalized dict, `_mock: true`, ids `mock:…` | same normalized dict via `normalize_entity()`, `_mock: false` |
| Labeling | every UI says "MOCK DATA — sample … for demo only" | "Live Qloo entity data" |

Swap: `export QLOO_API_KEY="…"`. Full details: [docs/QLOO_WIRING.md](docs/QLOO_WIRING.md).

## Evaluation

`demo/eval_vignettes.py` — 10 synthetic patient vignettes (EDS, Marfan, CF,
Duchenne, Gaucher, Fabry, narcolepsy, Behçet's, myasthenia gravis, Wilson's).
A vignette passes iff **C1**: a top-3 match has the expected specialty, **and
C2**: the explanation references the patient's own reported features.
Separate safety vignette (chest pain → emergency guidance, no matches).

**Result (mock mode, 2026-10-12): sensible-match rate 10/10 = 100%; safety
check PASS.** (Two matcher gaps found and fixed during the build: V4/V9
initially failed on phrase coverage — see BUILD_LOG.md.)

## Layout

```
├── src/
│   ├── config.py        # THE wiring point: QLOO_API_KEY → live/mock backend
│   ├── qloo_client.py   # QlooClient + LiveQlooBackend + MockQlooBackend (same interface)
│   ├── mock_data.py     # 14 fictional specialists, Qloo-shaped entities
│   ├── knowledge.py     # 10 rare conditions → specialties, aliases, questions; red flags
│   ├── agent.py         # agent loop: screen → match → query → rank → explain
│   └── disclaimer.py    # medical disclaimers + emergency guidance
├── demo/
│   ├── cli.py             # interactive / one-shot / --json CLI
│   ├── scripted_demo.py   # <5-min scripted judge demo
│   └── eval_vignettes.py  # 10-vignette evaluation + safety check
├── web/app.py             # minimal web UI (stdlib http.server)
├── docs/QLOO_WIRING.md    # key placement, endpoints, mock-vs-live, verify checklist
├── README.md · BUILD_LOG.md · LICENSE (MIT) · requirements.txt · .env.example
```

## What's missing

- **The real Qloo API key** — requested, not yet received. Everything above runs
  in mock mode until `QLOO_API_KEY` is set.
- Live-mode verification (endpoint param names, tag taxonomy mapping) — checklist
  in `docs/QLOO_WIRING.md`.
- Devpost submission (build-only per instructions; deadline per brief: Oct 31,
  2026 08:45 PKT — the hackathon matrix notes Oct 30, confirm before submitting).
