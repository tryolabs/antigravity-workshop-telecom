#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo "  Verifying Lab 04: Multi-Agent TMF622 Feasibility & Remediation"
echo "=================================================================="
./.venv/bin/pytest
echo "=================================================================="
echo "  [PASS] All 4 Labs (Lab 01 - Lab 04) Verified 100%!"
echo "=================================================================="
