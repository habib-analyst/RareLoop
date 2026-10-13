"""Qloo API client with swappable live / mock backends.

Public interface (identical in both modes)::

    client = QlooClient()                      # backend chosen by config.get_backend()
    client.search_entities(query, entity_type, take) -> [entity, ...]
    client.get_insights(entity_type, location, tags, take) -> [entity, ...]
    client.get_entity(entity_id) -> entity | None

An *entity* is a normalized dict::

    {
      "entity_id": str,
      "name": str,
      "type": "urn:entity:place",
      "properties": {"specialty":..., "city":..., "country":...,
                     "rating": float, "review_count": int, "address": str},
      "tags": [{"id": str, "name": str}, ...],
      "popularity": float,   # 0..1
      "affinity": float,     # 0..1
      "_mock": bool,         # True only in mock mode
    }

LIVE mode uses these real Qloo v2 endpoints (hackathon base
https://hackathon.api.qloo.com/v2, header X-Api-Key):
  - GET /search?query=&types=urn:entity:place&take=
  - GET /insights?filter.type=urn:entity:place&filter.location.query=
        &filter.tags=&take=
  - GET /entities/{entity_id}
See docs/QLOO_WIRING.md for the exact wiring and verification checklist.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from . import config
from . import mock_data


def normalize_entity(raw: dict) -> dict:
    """Adapt a raw live-API entity payload to the internal entity shape.

    Defensive: Qloo payloads nest fields under properties/tags; missing keys
    degrade to None/[] instead of raising.

    Real-API notes (verified 2026-10-13 against hackathon.api.qloo.com/v2):
    - /search returns {"results": [entity, ...]} (a LIST); /insights returns
      {"results": {"entities": [...]}} (a DICT). Handled in LiveQlooBackend.
    - Entities carry type="urn:entity" + subtype="urn:entity:place".
    - No specialty field exists; it is DERIVED from name/disambiguation/tags
      via _SPECIALTY_KEYWORDS (heuristic — a hospital mentioning "Neurology"
      is treated as a neurology place).
    - Rating lives in properties.business_rating; review_count is absent.
    - City/country come from properties.localities (place="city"/"country").
    """
    props = raw.get("properties") or {}
    tags = raw.get("tags") or []
    tag_names = [t.get("name") or "" for t in tags if isinstance(t, dict)]
    text = " ".join([
        raw.get("name") or "",
        raw.get("disambiguation") or "",
        props.get("description") or "",
        " ".join(tag_names),
    ])
    etype = raw.get("subtype") or raw.get("type") or raw.get("entity_type")
    city, country = _extract_city_country(props)
    return {
        "entity_id": raw.get("entity_id") or raw.get("id"),
        "name": raw.get("name"),
        "type": etype,
        "properties": {
            "address": props.get("address"),
            "city": city,
            "country": country,
            "specialty": props.get("specialty") or derive_specialty(text),
            "rating": props.get("rating") or props.get("business_rating"),
            "review_count": props.get("review_count"),
        },
        "tags": [{"id": t.get("id"), "name": t.get("name")} for t in tags
                 if isinstance(t, dict)],
        "popularity": raw.get("popularity"),
        "affinity": raw.get("affinity") or raw.get("query", {}).get("affinity"),
        "blurb": props.get("description") or raw.get("disambiguation"),
        "_mock": False,
    }


# --- live-API shape adapters (verified 2026-10-13) --------------------------
# Specialty names from knowledge.py CONDITIONS, mapped to the text signals
# the real Qloo graph actually carries (practitioner nouns in entity names).
# Order matters: more specific entries first ("Pediatric Neurology" before
# "Neurology") so the first match wins.
_SPECIALTY_KEYWORDS = {
    "Pediatric Neurology": ["pediatric neurolog", "paediatric neurolog",
                            "child neurolog"],
    "Sleep Medicine": ["sleep medicine", "sleep specialist", "sleep clinic",
                       "sleep disorder"],
    "Medical Genetics": ["medical genetic", "clinical genetic", "geneticist",
                         "genetics clinic", "genetic counsel"],
    "Rheumatology": ["rheumatolog"],
    "Cardiology": ["cardiolog"],
    "Pulmonology": ["pulmonolog", "respiratory medicine", "chest physician"],
    "Hematology": ["hematolog", "haematolog"],
    "Hepatology": ["hepatolog", "liver specialist"],
    "Nephrology": ["nephrolog"],
    "Ophthalmology": ["ophthalmolog", "eye specialist"],
    "Neurology": ["neurolog"],
}

# Practitioner-noun query per specialty. The live /search endpoint matches
# practitioner nouns ("rheumatologist" -> real rheumatologists) far better
# than "<Specialty> specialist" phrasing (which returns keyword soup:
# coffee shops, biryani specialists, ...). Verified 2026-10-13.
_SPECIALTY_PRACTITIONER = {
    "Rheumatology": "rheumatologist",
    "Medical Genetics": "geneticist",
    "Cardiology": "cardiologist",
    "Pulmonology": "pulmonologist",
    "Pediatric Neurology": "pediatric neurologist",
    "Neurology": "neurologist",
    "Hematology": "hematologist",
    "Hepatology": "hepatologist",
    "Nephrology": "nephrologist",
    "Ophthalmology": "ophthalmologist",
    "Sleep Medicine": "sleep specialist",
}


def derive_specialty(text: str) -> str | None:
    """Heuristic: map free text (name/disambiguation/tags) to a specialty."""
    low = (text or "").lower()
    for specialty, keywords in _SPECIALTY_KEYWORDS.items():
        if any(k in low for k in keywords):
            return specialty
    return None


def _extract_city_country(props: dict) -> tuple:
    """City/country from properties.localities (real API shape)."""
    city = country = None
    for loc in props.get("localities") or []:
        if not isinstance(loc, dict):
            continue
        place, name = loc.get("place"), loc.get("name")
        if place in ("city", "town", "village", "suburb") and not city:
            city = name
        elif place == "country" and not country:
            country = name
    return city, country


def _entity_list(data: dict) -> list:
    """Unwrap the results envelope: list (search) or {"entities": [...]}."""
    results = (data or {}).get("results")
    if isinstance(results, list):
        return results
    if isinstance(results, dict):
        ents = results.get("entities")
        return ents if isinstance(ents, list) else []
    return []


class LiveQlooBackend:
    """Thin wrapper over the real Qloo v2 HTTP API (stdlib urllib)."""

    def __init__(self, api_key: str, api_base: str, timeout: int = 20):
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.api_base}{path}?{urlencode(params)}"
        req = Request(url, headers={
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "RareLoop/0.1 (Qloo Agentic AI Hackathon)",
        })
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"Qloo API HTTP {e.code}: {body}") from e
        except URLError as e:
            raise RuntimeError(f"Qloo API unreachable: {e.reason}") from e

    def search_entities(self, query, entity_type="urn:entity:place", take=10):
        data = self._get("/search", {
            "query": query, "types": entity_type, "take": take})
        return [normalize_entity(r) for r in _entity_list(data)[:take]]

    def get_insights(self, entity_type="urn:entity:place", location=None,
                     tags=None, take=10):
        params = {"filter.type": entity_type, "take": take}
        if location:
            params["filter.location.query"] = location
        if tags:
            params["filter.tags"] = ",".join(tags)
        data = self._get("/insights", params)
        return [normalize_entity(r) for r in _entity_list(data)[:take]]

    def get_entity(self, entity_id):
        data = self._get(f"/entities/{entity_id}", {})
        results = (data or {}).get("results")
        if isinstance(results, dict) and results.get("entity_id"):
            raw = results
        elif isinstance(results, list) and results:
            raw = results[0]
        elif isinstance(data, dict) and data.get("entity_id"):
            raw = data
        else:
            raw = None
        return normalize_entity(raw) if raw else None


class MockQlooBackend:
    """Same interface, realistic fictional data. Used when no API key is set.

    Every returned entity carries "_mock": True and ids prefixed "mock:".
    """

    def search_entities(self, query, entity_type="urn:entity:place", take=10):
        return mock_data.search_mock(query, take=take)

    def get_insights(self, entity_type="urn:entity:place", location=None,
                     tags=None, take=10):
        query = " ".join((tags or []))
        if not query:
            query = "specialist clinic"
        results = mock_data.search_mock(query, city=location, take=take)
        # Re-rank: entities whose tags overlap the requested tag slugs first.
        wanted = {(t or "").lower() for t in (tags or [])}
        def key(e):
            overlap = sum(1 for tg in e["tags"]
                          if tg["id"].split(":")[-1] in wanted
                          or tg["name"].lower() in wanted)
            same_city = (location and e["properties"]["city"].lower()
                         == location.lower())
            return (overlap, 1 if same_city else 0, e["affinity"])
        results.sort(key=key, reverse=True)
        return results

    def get_entity(self, entity_id):
        for e in mock_data.SPECIALISTS:
            if e["entity_id"] == entity_id:
                return dict(e, _mock=True)
        return None


class QlooClient:
    """Backend-agnostic client. `backend="auto"` (default) reads config."""

    def __init__(self, backend: str = "auto", api_key: str | None = None,
                 api_base: str | None = None, timeout: int = 20):
        resolved = config.get_backend() if backend == "auto" else backend
        if resolved == "live":
            key = api_key or config.get_api_key()
            if not key:
                raise ValueError(
                    "backend='live' requested but QLOO_API_KEY is not set")
            self.backend = LiveQlooBackend(
                key, api_base or config.get_api_base(), timeout)
        elif resolved == "mock":
            self.backend = MockQlooBackend()
        else:
            raise ValueError(f"unknown backend: {backend!r}")
        self.backend_name = resolved

    # -- identical interface in both modes ---------------------------------
    def search_entities(self, query, entity_type="urn:entity:place", take=10):
        return self.backend.search_entities(query, entity_type, take)

    def get_insights(self, entity_type="urn:entity:place", location=None,
                     tags=None, take=10):
        return self.backend.get_insights(entity_type, location, tags, take)

    def get_entity(self, entity_id):
        return self.backend.get_entity(entity_id)
