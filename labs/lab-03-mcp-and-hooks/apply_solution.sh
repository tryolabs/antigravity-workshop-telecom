#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"

mkdir -p "$ROOT_DIR/.agents"
cp "$LAB_DIR/solution/telecom_mcp.py" "$ROOT_DIR/mcp_server/telecom_mcp.py"
cp "$LAB_DIR/solution/mcp_config.json" "$ROOT_DIR/.agents/mcp_config.json"
cp "$LAB_DIR/solution/hooks.json" "$ROOT_DIR/.agents/hooks.json"
echo "[Lab 03 Solution Applied] Installed mcp_server/telecom_mcp.py, .agents/mcp_config.json, and .agents/hooks.json."
