#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  bash "$ROOT_DIR/install.sh"
fi

echo "[Lab 01 Setup] Resetting Telecom Nexus to Lab 01 Starter State..."
cp "$LAB_DIR/starter/cdr_rating.py" "$ROOT_DIR/src/services/cdr_rating.py"
cp "$LAB_DIR/starter/sla_monitor.py" "$ROOT_DIR/src/services/sla_monitor.py"
cp "$ROOT_DIR/labs/lab-03-mcp-and-hooks/starter/telecom_mcp.py" "$ROOT_DIR/mcp_server/telecom_mcp.py"
cp "$ROOT_DIR/labs/lab-04-multi-agent-capstone/starter/order_feasibility.py" "$ROOT_DIR/src/services/order_feasibility.py"

rm -f "$ROOT_DIR/GEMINI.md"
rm -f "$ROOT_DIR/.agents/rules/telecom-standards.md"
rm -rf "$ROOT_DIR/.agents/skills/sla-revenue-audit"
rm -f "$ROOT_DIR/.agents/mcp_config.json"
rm -f "$ROOT_DIR/.agents/hooks.json"

./.venv/bin/python data/seed_telecom_data.py
echo "[Lab 01 Ready] Starter bugs active in src/services/cdr_rating.py and src/services/sla_monitor.py."
