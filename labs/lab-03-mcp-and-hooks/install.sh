#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Lab 03 Setup] Ensuring Labs 01 & 02 prerequisites and solutions are applied..."
bash "$ROOT_DIR/labs/lab-02-rules-and-skills/install.sh"
bash "$ROOT_DIR/labs/lab-02-rules-and-skills/apply_solution.sh"

echo "[Lab 03 Ready] Ready to complete mcp_server/telecom_mcp.py, .agents/mcp_config.json, and .agents/hooks.json."
