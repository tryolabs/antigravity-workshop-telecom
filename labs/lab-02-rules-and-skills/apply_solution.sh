#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p "$ROOT_DIR/.agents/rules"
mkdir -p "$ROOT_DIR/.agents/skills/sla-revenue-audit"

cp "$LAB_DIR/solution/GEMINI.md" "$ROOT_DIR/GEMINI.md"
cp "$LAB_DIR/solution/telecom-standards.md" "$ROOT_DIR/.agents/rules/telecom-standards.md"
cp "$LAB_DIR/solution/SKILL.md" "$ROOT_DIR/.agents/skills/sla-revenue-audit/SKILL.md"

./.venv/bin/python scripts/run_sla_audit.py
echo "[Lab 02 Solution Applied] Installed GEMINI.md, .agents/rules/telecom-standards.md, and .agents/skills/sla-revenue-audit/SKILL.md."
