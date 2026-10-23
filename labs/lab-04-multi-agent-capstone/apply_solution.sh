#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"

cp "$LAB_DIR/solution/order_feasibility.py" "$ROOT_DIR/src/services/order_feasibility.py"
cp "$LAB_DIR/solution/adk_a2a_orchestrator.py" "$ROOT_DIR/src/agents/adk_a2a_orchestrator.py"
echo "[Lab 04 Solution Applied] Installed src/services/order_feasibility.py and src/agents/adk_a2a_orchestrator.py."
