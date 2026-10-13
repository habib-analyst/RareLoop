#!/usr/bin/env python3
"""Minimal web UI for RareLoop — Python standard library only (http.server).

Run:   python3 web/app.py [--port 8765]
Then open http://localhost:8765 in a browser.
"""

import argparse
import html
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import config, disclaimer
from src.agent import run_agent
from src.qloo_client import QlooClient

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>RareLoop — rare-disease specialist finder</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:760px;margin:2em auto;padding:0 1em;line-height:1.5}}
.mock{{background:#fff3cd;border:1px solid #e0c36a;padding:.6em 1em;border-radius:8px}}
.card{{border:1px solid #ddd;border-radius:10px;padding:1em;margin:1em 0}}
.disclaimer{{font-size:.85em;color:#555;border-top:1px solid #ddd;margin-top:2em;padding-top:1em}}
textarea{{width:100%;height:90px}} input[type=text]{{width:60%}}
button{{padding:.6em 1.4em;font-size:1em}}
</style></head><body>
<h1>RareLoop</h1>
<p>Describe symptoms or a suspected rare condition; the agent finds relevant
specialists via the Qloo API, ranks them, and explains <em>why each fits
this patient</em>.</p>
<div class="mock">{backend_note}</div>
<form method="post" action="/search">
<p><textarea name="text" placeholder="e.g. my shoulders dislocate easily, my skin is very stretchy...">{text}</textarea></p>
<p>Preferred city (optional): <input type="text" name="location" value="{location}"></p>
<p><button type="submit">Find specialists</button></p>
</form>
{results}
<div class="disclaimer">{disclaimer}</div>
</body></html>"""


def render_result(r: dict) -> str:
    e = html.escape
    parts = []
    if r.get("emergency"):
        parts.append("<div class='card'><h2>Possible emergency</h2>")
        parts.append(f"<p>{e(r['guidance'])}</p></div>")
        return "".join(parts)
    if not r.get("condition"):
        return f"<div class='card'><p>{e(r['note'])}</p></div>"
    parts.append(f"<h2>Suspected area: {e(r['condition']['name'])}</h2>")
    parts.append(f"<p>Relevant specialties: {e(', '.join(r['specialties']))}</p>")
    for m in r["matches"]:
        parts.append("<div class='card'>")
        parts.append(f"<h3>{e(m['name'])}</h3>")
        parts.append(f"<p>{e(m['specialty'])} — {e(m['city'])}, {e(m['country'])} "
                     f"| rating {m['rating']}/5 | match score {m['score']}</p>")
        parts.append("<p><b>Why this specialist for you:</b></p><ul>")
        for line in m["explanation"]:
            parts.append(f"<li>{e(line)}</li>")
        parts.append("</ul></div>")
    parts.append("<h3>Questions to ask at the appointment</h3><ul>")
    for q in r["suggested_questions"]:
        parts.append(f"<li>{e(q)}</li>")
    parts.append("</ul>")
    return "".join(parts)


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: str):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        note = ("MOCK MODE — sample specialist data for demo only. "
                "Set QLOO_API_KEY for live Qloo results."
                if not config.is_live() else
                "LIVE MODE — results from the Qloo API.")
        self._send(PAGE.format(backend_note=html.escape(note), text="",
                               location="", results="",
                               disclaimer=html.escape(disclaimer.DISCLAIMER_SHORT)))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        text = form.get("text", [""])[0]
        location = form.get("location", [""])[0].strip() or None
        result = run_agent(text, location=location, client=QlooClient(), top_n=3)
        note = ("MOCK MODE — sample specialist data for demo only."
                if not config.is_live() else "LIVE MODE — Qloo API results.")
        self._send(PAGE.format(
            backend_note=html.escape(note),
            text=html.escape(text), location=html.escape(location or ""),
            results=render_result(result),
            disclaimer=html.escape(disclaimer.DISCLAIMER_FULL).replace("\n", "<br>")))

    def log_message(self, *a):  # keep console output clean
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    print(f"RareLoop web UI on http://localhost:{args.port} "
          f"({config.describe()})")
    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
