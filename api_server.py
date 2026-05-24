"""Local HTTP API for SCM Analytics Studio integrations."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from modules.integration_gateway import (
    inspect_dataset,
    integration_catalog,
    run_skill_on_file,
    run_tool_on_file,
)


class SCMAPIHandler(BaseHTTPRequestHandler):
    server_version = "SCMAnalyticsStudioAPI/1.0"

    def _send(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/health":
                self._send({"status": "ok"})
            elif path == "/catalog":
                self._send(integration_catalog())
            elif path == "/tools":
                self._send({"tools": integration_catalog()["tools"]})
            elif path == "/skills":
                self._send({"skills": integration_catalog()["skills"]})
            else:
                self._send({"error": "Not found"}, 404)
        except Exception as exc:
            self._send({"error": str(exc)}, 500)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/inspect":
                result = inspect_dataset(payload["input_path"], payload.get("sheet"), payload.get("mapping_template"))
            elif path == "/run-tool":
                result = run_tool_on_file(
                    payload["input_path"],
                    payload["tool"],
                    payload.get("params", {}),
                    payload.get("sheet"),
                    payload.get("mapping_template"),
                )
            elif path == "/run-skill":
                result = run_skill_on_file(
                    payload["input_path"],
                    payload["skill"],
                    payload.get("params", {}),
                    payload.get("sheet"),
                    payload.get("mapping_template"),
                )
            else:
                self._send({"error": "Not found"}, 404)
                return
            self._send(result)
        except Exception as exc:
            self._send({"error": str(exc)}, 500)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local SCM Analytics Studio HTTP API.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), SCMAPIHandler)
    print(f"SCM Analytics Studio API running at http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
