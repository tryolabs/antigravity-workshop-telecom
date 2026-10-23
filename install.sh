#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo "  Telecom Nexus — Antigravity Workshop Environment Installer"
echo "=================================================================="

if [ ! -d ".venv" ]; then
  echo "[1/3] Creating Python virtual environment (.venv)..."
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
else
  echo "[1/3] Using existing Python virtual environment (.venv)..."
fi

echo "[2/3] Checking / installing Python dependencies..."
if ./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk" >/dev/null 2>&1; then
  echo "      [OK] Pre-provisioned .venv detected with all required packages (zero-install mode)."
elif [ -d "wheelhouse" ]; then
  echo "      [Offline Mode] Installing from local ./wheelhouse..."
  ./.venv/bin/pip install --quiet --no-index --find-links ./wheelhouse -r requirements.txt
elif command -v uv >/dev/null 2>&1; then
  uv pip install --python ./.venv/bin/python -r requirements.txt
else
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

echo "[3/3] Seeding deterministic 3GPP RAN, TAP3 CDR & B2B SLA database..."
./.venv/bin/python data/seed_telecom_data.py
chmod +x scripts/*.py 2>/dev/null || true

echo ""
echo "Setup complete! Start the live Telecom NOC Dashboard anytime with:"
echo "  ./.venv/bin/uvicorn src.main:app --reload --port 8001"
echo "=================================================================="
