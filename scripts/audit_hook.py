#!/usr/bin/env python3
"""
Antigravity Lifecycle Hook Validator (`scripts/audit_hook.py`) for Telecom Nexus (Lab 3).

Implements the Antigravity `hooks.json` stdin/stdout JSON contract:
- On `PreToolUse`:
  Inspects `toolCall.args.CommandLine` (or file arguments) and blocks destructive database
  commands (`DROP TABLE`, `TRUNCATE`, `DELETE FROM b2b_contracts`, `rm -rf data/telecom_nexus.db`).
  Returns `{"decision": "allow" | "deny", "reason": "..."}` on stdout.
- On `PostToolUse`:
  Appends an audit trail record to `data/logs/hook_audit.log` and outputs `{}` on stdout.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = PROJECT_ROOT / "data" / "logs" / "hook_audit.log"

DESTRUCTIVE_PATTERNS = [
    r"\bDROP\s+TABLE\b",
    r"\bTRUNCATE\s+TABLE\b",
    r"\bDELETE\s+FROM\s+b2b_contracts\b",
    r"\bDELETE\s+FROM\s+ran_telemetry\b",
    r"\brm\s+-rf\s+.*telecom_nexus\.db",
]


def evaluate_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    tool_call = payload.get("toolCall", {}) or {}
    args = tool_call.get("args", {}) or payload.get("tool_input", {}) or {}
    cmd = str(
        args.get("CommandLine")
        or args.get("command")
        or payload.get("CommandLine")
        or payload.get("command")
        or ""
    )

    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, cmd, flags=re.IGNORECASE):
            return {
                "decision": "deny",
                "reason": (
                    f"Blocked by Telecom Compliance Hook: command matches prohibited "
                    f"destructive pattern ({pattern}) on production OSS/BSS data."
                ),
            }

    return {
        "decision": "allow",
        "reason": "Command passed Telecom 3GPP/BSS compliance check.",
    }


def record_audit_event(event_type: str, payload: dict[str, Any], result: dict[str, Any]) -> None:
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        tool_call = payload.get("toolCall", {}) or {}
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "tool_name": tool_call.get("name", "unknown"),
            "decision": result.get("decision", "post_logged"),
        }
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Telecom Nexus Antigravity Hook Validator")
    parser.add_argument("--event", default="PreToolUse", choices=["PreToolUse", "PostToolUse"])
    args = parser.parse_args()

    raw_stdin = sys.stdin.read().strip()
    payload: dict[str, Any] = {}
    if raw_stdin:
        try:
            payload = json.loads(raw_stdin)
        except json.JSONDecodeError:
            payload = {}

    if args.event == "PreToolUse":
        out = evaluate_pre_tool_use(payload)
        record_audit_event("PreToolUse", payload, out)
        sys.stdout.write(json.dumps(out) + "\n")
    else:
        out = {}
        record_audit_event("PostToolUse", payload, out)
        sys.stdout.write(json.dumps(out) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
