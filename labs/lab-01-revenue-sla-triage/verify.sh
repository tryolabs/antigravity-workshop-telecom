#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo "  Verifying Lab 01: Revenue Assurance (CDR) & 5G Slice SLA Triage"
echo "=================================================================="
./.venv/bin/pytest tests/test_lab01_triage.py
echo "=================================================================="
echo "  [PASS] Lab 01 Verification Succeeded 100%!"
echo "=================================================================="
