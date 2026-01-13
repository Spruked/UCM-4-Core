#!/usr/bin/env python3
"""
Minimal HTTP surface for CALI state hub (read-only snapshot/events + control submit).

Endpoints:
- GET  /state/snapshot
- GET  /state/events?since=<ts>
- POST /control/submit   (body: control packet JSON)

Constraints: no auth, no roles, no inference. Hub remains the writer of events.
"""

import json
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from cali_state_hub import get_snapshot, submit_control
from state_persistence import init_persistence, get_integrity_signals


def _normalize_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            # Allow ISO strings with or without trailing Z
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except Exception:
            try:
                return float(value)
            except Exception:
                return None
    return None


class StateAPIHandler(BaseHTTPRequestHandler):
    server_version = "CALIStateHubAPI/0.1"

    def _set_common_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_common_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/state/snapshot":
            snapshot = get_snapshot()
            snapshot["integrity"] = get_integrity_signals()
            self._set_common_headers()
            self.wfile.write(json.dumps(snapshot).encode("utf-8"))
            return

        if parsed.path == "/state/events":
            params = parse_qs(parsed.query)
            since_raw = params.get("since", [None])[0]
            since_ts = _normalize_ts(since_raw)

            snapshot = get_snapshot()
            events = snapshot.get("events", []) or []
            if since_ts is not None:
                filtered = []
                for event in events:
                    ts = _normalize_ts(event.get("timestamp"))
                    if ts is None:
                        continue
                    if ts > since_ts:
                        filtered.append(event)
                events = filtered

            self._set_common_headers()
            self.wfile.write(json.dumps({"events": events}).encode("utf-8"))
            return

        self._set_common_headers(status=404)
        self.wfile.write(json.dumps({"error": "not_found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/control/submit":
            self._set_common_headers(status=404)
            self.wfile.write(json.dumps({"error": "not_found"}).encode("utf-8"))
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            packet = json.loads(body.decode("utf-8"))
            if "timestamp" not in packet:
                packet["timestamp"] = datetime.utcnow().isoformat() + "Z"
        except Exception as exc:
            self._set_common_headers(status=400)
            self.wfile.write(json.dumps({"error": "invalid_json", "detail": str(exc)}).encode("utf-8"))
            return

        outcome = submit_control(packet)
        self._set_common_headers(status=200)
        self.wfile.write(json.dumps({"outcome": outcome}).encode("utf-8"))


def serve(port: int = 5050):
    # initialize persistence once at startup
    init_persistence()
    server = ThreadingHTTPServer(("0.0.0.0", port), StateAPIHandler)
    print(f"[CALI State API] serving on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[CALI State API] shutting down")
        server.server_close()


if __name__ == "__main__":
    serve()