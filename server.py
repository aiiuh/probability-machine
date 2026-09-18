"""Loopback-only experiment workbench. No server-side participant storage."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from probability_machine import plan

ROOT = Path(__file__).resolve().parent
MAX_BODY = 100_000

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Do not log participant activity.

    def reply(self, status, body, kind="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(body)

    def json_reply(self, status, data):
        self.reply(status, json.dumps(data, allow_nan=False).encode())

    def valid_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def do_GET(self):
        if not self.valid_host():
            return self.json_reply(403, {"error": "loopback host required"})
        routes = {"/": ("web/index.html", "text/html; charset=utf-8"),
                  "/app.js": ("web/app.js", "text/javascript; charset=utf-8"),
                  "/style.css": ("web/style.css", "text/css; charset=utf-8"),
                  "/sample.json": ("examples/layout.json", "application/json")}
        if self.path not in routes:
            return self.json_reply(404, {"error": "not found"})
        path, kind = routes[self.path]
        self.reply(200, (ROOT/path).read_bytes(), kind)

    def do_POST(self):
        if not self.valid_host() or self.path != "/api/plan":
            return self.json_reply(403, {"error": "invalid host or endpoint"})
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers['Host']}":
            return self.json_reply(403, {"error": "cross-origin request rejected"})
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self.json_reply(415, {"error": "JSON required"})
        try:
            size = int(self.headers.get("Content-Length", "-1"))
            if not 0 < size <= MAX_BODY:
                return self.json_reply(413, {"error": "body must be 1..100000 bytes"})
            self.connection.settimeout(5)
            data = json.loads(self.rfile.read(size), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            result = plan(data)
            self.json_reply(200, result)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            self.json_reply(400, {"error": str(exc)})
        except (TimeoutError, OSError):
            self.json_reply(408, {"error": "request timeout"})

if __name__ == "__main__":
    print("Probability Machine: http://127.0.0.1:8765 — Ctrl-C to stop")
    print("Local-only. No provider API calls. Participant records remain in browser memory until exported.")
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
