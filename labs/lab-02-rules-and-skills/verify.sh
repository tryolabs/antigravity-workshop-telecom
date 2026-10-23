#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo "  Verifying Lab 02: Antigravity Workspace Rules & Custom Skills"
echo "=================================================================="
./.venv/bin/pytest tests/test_lab01_triage.py tests/test_lab02_rules_skills.py
echo "=================================================================="
echo "  [PASS] Lab 02 Verification Succeeded 100%!"
echo "=================================================================="
