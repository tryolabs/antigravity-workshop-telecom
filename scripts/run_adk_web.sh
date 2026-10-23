#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${ADK_WEB_PORT:-8080}"

if [[ "${1:-}" == "--check" ]] || [[ "${1:-}" == "--dry-run" ]]; then
  echo "[ADK Web Check] Validating adk_agents/telecom_nexus/agent.py and root_agent..."
  ./.venv/bin/python -c "from adk_agents.telecom_nexus.agent import root_agent, get_gemini_enterprise_connection_config; print('Loaded root_agent:', getattr(root_agent, 'name', 'ok')); cfg = get_gemini_enterprise_connection_config(); assert 'discovery_engine_agent_endpoint' in cfg; print('[OK] ADK root_agent & Gemini Enterprise config verified!')"
  exit 0
fi

./.venv/bin/adk telemetry disable >/dev/null 2>&1 || true

echo "=================================================================="
echo "  Launching Google ADK Development UI (adk web)"
echo "  Agent Directory : $ROOT_DIR/adk_agents"
echo "  Selected Agent  : telecom_nexus (root_agent)"
echo "  ADK Dev UI URL  : http://localhost:${PORT}"
echo "=================================================================="
exec ./.venv/bin/adk web "$ROOT_DIR/adk_agents" --port "$PORT"
