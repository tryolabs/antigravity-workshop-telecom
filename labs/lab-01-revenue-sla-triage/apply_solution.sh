#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"

cp "$LAB_DIR/solution/cdr_rating.py" "$ROOT_DIR/src/services/cdr_rating.py"
cp "$LAB_DIR/solution/sla_monitor.py" "$ROOT_DIR/src/services/sla_monitor.py"
echo "[Lab 01 Solution Applied] Fixed src/services/cdr_rating.py and src/services/sla_monitor.py."
