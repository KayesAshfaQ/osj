#!/usr/bin/env python3
"""Loopback-only HTTP fixture for Flutter browser tests; never a production API."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    state = {"sessions": 0, "deleted": 0, "preflights": 0, "authorizations": []}
    fail_next = False

    def reply(self, status: int, payload: object = None) -> None:
        self.send_response(status)
        origin = self.headers.get("Origin", "")
        if urlsplit(origin).hostname in {"localhost", "127.0.0.1"}:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "authorization, content-type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if payload is not None:
            self.wfile.write(json.dumps(payload).encode())

    def do_OPTIONS(self) -> None:
        Handler.state["preflights"] += 1
        self.reply(204)

    def do_GET(self) -> None:
        if self.path == "/__test__/state":
            self.reply(200, Handler.state)
        elif self.path == "/health":
            self.reply(200, {"status": "ready"})
        else:
            self.reply(404)

    def do_POST(self) -> None:
        # Consume each body so requests can reuse the connection safely.
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        if self.path == "/__test__/reset":
            Handler.state = {"sessions": 0, "deleted": 0, "preflights": 0, "authorizations": []}
            Handler.fail_next = False
            self.reply(200, {})
        elif self.path == "/__test__/fail-next":
            Handler.fail_next = True
            self.reply(200, {})
        elif self.path == "/api/chat/sessions":
            Handler.state["sessions"] += 1
            self.reply(201, {"token": f"token-{Handler.state['sessions']}", "expires_at": "2030-01-01T00:00:00Z"})
        elif self.path == "/api/chat":
            Handler.state["authorizations"].append(self.headers.get("Authorization"))
            if Handler.fail_next:
                Handler.fail_next = False
                self.reply(503, {"detail": "Service unavailable"})
            else:
                number = len(Handler.state["authorizations"])
                self.reply(
                    200,
                    {
                        "request_id": f"r{number}",
                        "outcome": "answered",
                        "answer": f"Verified response {number}",
                        "sources": [
                            {
                                "source_id": "s1",
                                "act_title": "Code of Criminal Procedure",
                                "section_number": "54",
                                "provenance_url": None,
                            }
                        ],
                    },
                )
        else:
            self.reply(404)

    def do_DELETE(self) -> None:
        if self.path == "/api/chat/sessions/current":
            Handler.state["deleted"] += 1
            self.reply(204)
        else:
            self.reply(404)

    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Browser fixture ready on http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
