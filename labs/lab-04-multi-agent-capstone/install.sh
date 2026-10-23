#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Lab 04 Setup] Ensuring Labs 01, 02 & 03 prerequisites and solutions are applied..."
bash "$ROOT_DIR/labs/lab-03-mcp-and-hooks/install.sh"
bash "$ROOT_DIR/labs/lab-03-mcp-and-hooks/apply_solution.sh"

echo "[Lab 04 Ready] Ready to build the Multi-Agent Capstone in src/services/order_feasibility.py."
