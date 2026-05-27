"""Lightweight stdio MCP-style server for SCM Analytics Studio.

This uses JSON-RPC messages over stdin/stdout and exposes the app's local
tools/skills to MCP-capable clients without adding a runtime dependency.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from modules.integration_gateway import (
    inspect_dataset,
    integration_catalog,
    run_skill_on_file,
    run_tool_on_file,
)


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required or []}


MCP_TOOLS = [
    {
        "name": "scm_catalog",
        "description": "List SCM Analytics Studio local tools and workflow skills.",
        "inputSchema": _schema({}),
    },
    {
        "name": "scm_inspect_dataset",
        "description": "Load a CSV/XLSX/XLS file and return quality, mapping, and preview metadata.",
        "inputSchema": _schema({
            "input_path": {"type": "string"},
            "sheet": {"type": "string"},
            "mapping_template": {"type": "string"},
        }, ["input_path"]),
    },
    {
        "name": "scm_run_tool",
        "description": "Run one local SCM tool on a file.",
        "inputSchema": _schema({
            "input_path": {"type": "string"},
            "tool": {"type": "string"},
            "params": {"type": "object"},
            "sheet": {"type": "string"},
            "mapping_template": {"type": "string"},
        }, ["input_path", "tool"]),
    },
    {
        "name": "scm_run_skill",
        "description": "Run one guided workflow skill on a file.",
        "inputSchema": _schema({
            "input_path": {"type": "string"},
            "skill": {"type": "string"},
            "params": {"type": "object"},
            "sheet": {"type": "string"},
            "mapping_template": {"type": "string"},
        }, ["input_path", "skill"]),
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "scm_catalog":
        result = integration_catalog()
    elif name == "scm_inspect_dataset":
        result = inspect_dataset(arguments["input_path"], arguments.get("sheet"), arguments.get("mapping_template"))
    elif name == "scm_run_tool":
        result = run_tool_on_file(
            arguments["input_path"],
            arguments["tool"],
            arguments.get("params", {}),
            arguments.get("sheet"),
            arguments.get("mapping_template"),
        )
    elif name == "scm_run_skill":
        result = run_skill_on_file(
            arguments["input_path"],
            arguments["skill"],
            arguments.get("params", {}),
            arguments.get("sheet"),
            arguments.get("mapping_template"),
        )
    else:
        raise ValueError(f"Unknown MCP tool: {name}")
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "scm-analytics-studio", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {"tools": MCP_TOOLS}
        elif method == "tools/call":
            params = message.get("params", {})
            result = call_tool(params.get("name"), params.get("arguments", {}))
        elif method in {"notifications/initialized", "initialized"}:
            return None
        else:
            raise ValueError(f"Unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(exc)}}


def main() -> int:
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = handle(json.loads(line))
            if response is not None:
                print(json.dumps(response, default=str), flush=True)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
