#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Lab 02 Setup] Ensuring Lab 01 prerequisites and solutions are applied..."
bash "$ROOT_DIR/labs/lab-01-revenue-sla-triage/install.sh"
bash "$ROOT_DIR/labs/lab-01-revenue-sla-triage/apply_solution.sh"

echo "[Lab 02 Ready] Ready to author GEMINI.md, .agents/rules/telecom-standards.md, and .agents/skills/sla-revenue-audit/SKILL.md."
