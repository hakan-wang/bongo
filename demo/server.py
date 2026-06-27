"""
Plumbline demo server — dependency-free (Python stdlib only).

Run:   python3 demo/server.py
Open:  http://localhost:8200

Serves the dashboard (index.html) and an /api/run endpoint that runs the real demo
engine (demo/scenarios.py) and returns the full trace + scoreboard as JSON.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import scenarios  # local

PORT = int(os.environ.get("BONGO_PORT", "8200"))
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/run"):
            return self._send(200, scenarios.run_all())
        # serve the dashboard for everything else
        path = "index.html" if self.path in ("/", "") else self.path.lstrip("/")
        full = os.path.join(HERE, os.path.basename(path))
        if os.path.exists(full) and full.endswith(".html"):
            with open(full, "rb") as f:
                return self._send(200, f.read().decode(), "text/html")
        return self._send(404, {"error": "not found"})


if __name__ == "__main__":
    print(f"\n  Plumbline dashboard:  http://localhost:{PORT}\n  (Ctrl+C to stop)\n")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
