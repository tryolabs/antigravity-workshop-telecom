#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Register Telecom Nexus A2A Multi-Agent System into Google Gemini Enterprise
# (Discovery Engine Assistant Agents API: v1alpha)
# ==============================================================================

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-telecom-nexus-enterprise}"
LOCATION="${GEMINI_ENTERPRISE_LOCATION:-global}"
APP_ID="${GEMINI_ENTERPRISE_APP_ID:-telecom-nexus-enterprise-app}"
AGENT_URL="${TELECOM_NEXUS_CLOUD_RUN_URL:-https://telecom-nexus-oss-bss-uc.a.run.app}"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --location)
      LOCATION="$2"
      shift 2
      ;;
    --app-id)
      APP_ID="$2"
      shift 2
      ;;
    --agent-url)
      AGENT_URL="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

CleanUrl="${AGENT_URL%/}"
DISCOVERY_ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"

PAYLOAD=$(cat <<EOF
{
  "displayName": "Telecom Nexus 5G OSS/BSS & SLA Orchestrator",
  "description": "Multi-Agent 5G Network Slice SLA, TAP3 CDR Revenue Assurance & TMF622 Order Feasibility Agent (Google ADK + A2A Protocol).",
  "a2aAgentDefinition": {
    "agentCardUri": "${CleanUrl}/.well-known/agent.json",
    "endpointUri": "${CleanUrl}/api/v1/a2a"
  }
}
EOF
)

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[Gemini Enterprise Registration Dry-Run]"
  echo "Target Discovery Engine Endpoint : $DISCOVERY_ENDPOINT"
  echo "A2A Agent Card URI               : ${CleanUrl}/.well-known/agent.json"
  echo "A2A JSON-RPC Endpoint URI        : ${CleanUrl}/api/v1/a2a"
  echo "Registration Payload:"
  echo "$PAYLOAD"
  echo "[OK] Gemini Enterprise A2A Agent registration payload validated."
  exit 0
fi

TOKEN="$(gcloud auth print-access-token)"
curl -sS -X POST "$DISCOVERY_ENDPOINT" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  -d "$PAYLOAD"
echo ""
echo "[OK] Registered Telecom Nexus A2A Agent with Gemini Enterprise App '${APP_ID}'."
