"""Configuration and backend selection.

This module is the SINGLE wiring point for the Qloo API key.

- Backend is "live" if and only if the QLOO_API_KEY environment variable is
  set and non-empty. Otherwise the agent runs in "mock" mode with realistic
  sample data through the exact same client interface.
- Swapping mock -> live is a one-line change::

      export QLOO_API_KEY="your-key-here"

  No code changes, no config files, no restarts of anything except the process
  itself.
"""

import os

QLOO_API_KEY_ENV = "QLOO_API_KEY"
QLOO_API_BASE_ENV = "QLOO_API_BASE"

# Hackathon endpoint (per Qloo hackathon docs/SDKs). Override with
# QLOO_API_BASE if the key issued to you targets a different environment.
DEFAULT_API_BASE = "https://hackathon.api.qloo.com/v2"


def get_api_key() -> str:
    """Return the Qloo API key from the environment ("" if unset)."""
    return os.environ.get(QLOO_API_KEY_ENV, "").strip()


def get_api_base() -> str:
    """Return the Qloo API base URL (hackathon default)."""
    return os.environ.get(QLOO_API_BASE_ENV, DEFAULT_API_BASE).rstrip("/")


def get_backend() -> str:
    """Return "live" when a key is present, else "mock"."""
    return "live" if get_api_key() else "mock"


def is_live() -> bool:
    return get_backend() == "live"


def describe() -> str:
    backend = get_backend()
    if backend == "live":
        return f"live Qloo API @ {get_api_base()} (key present)"
    return "MOCK mode — no QLOO_API_KEY set; using built-in sample data"
