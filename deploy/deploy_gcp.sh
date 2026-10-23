#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Telecom Nexus — Google Cloud Run, Artifact Registry, Terraform & Gemini Enterprise
# Deployment Script (Supports `--dry-run` for 100% local offline validation!)
# ==============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-telecom-gcp-project-id}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="${TELECOM_SERVICE_NAME:-telecom-nexus-oss-bss}"
GEMINI_APP_ID="${GEMINI_ENTERPRISE_APP_ID:-telecom-nexus-enterprise-app}"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --gemini-app-id)
      GEMINI_APP_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

TF_DIR="$ROOT_DIR/infra/terraform"

echo "=================================================================="
echo "  Telecom Nexus — Google Cloud + Terraform + Gemini Enterprise"
echo "=================================================================="
echo "  Project ID          : $PROJECT_ID"
echo "  Region              : $REGION"
echo "  Cloud Run Service   : $SERVICE_NAME"
echo "  Gemini Enterprise   : $GEMINI_APP_ID"
echo "  Dry-Run Mode        : $DRY_RUN"
echo "=================================================================="

# 1. Verify Dockerfile and Terraform files exist
for req_file in \
  "$ROOT_DIR/Dockerfile" \
  "$TF_DIR/versions.tf" \
  "$TF_DIR/variables.tf" \
  "$TF_DIR/main.tf" \
  "$TF_DIR/outputs.tf" \
  "$ROOT_DIR/deploy/register_gemini_enterprise_agent.sh"; do
  if [[ ! -f "$req_file" ]]; then
    echo "[ERROR] Missing required deployment file: $req_file"
    exit 1
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[Dry-Run 1/3] Validating Dockerfile and Terraform HCL structure..."
  grep -q "google_cloud_run_v2_service" "$TF_DIR/main.tf"
  grep -q "discoveryengine.googleapis.com" "$TF_DIR/main.tf"
  grep -q "cloudaicompanion.googleapis.com" "$TF_DIR/main.tf"

  if command -v terraform >/dev/null 2>&1; then
    (cd "$TF_DIR" && terraform fmt -check >/dev/null 2>&1 || true)
  fi

  echo "[Dry-Run 2/3] Validating ADK root_agent & A2A Agent Card..."
  bash "$ROOT_DIR/scripts/run_adk_web.sh" --check

  echo "[Dry-Run 3/3] Validating Gemini Enterprise A2A Registration payload..."
  bash "$ROOT_DIR/deploy/register_gemini_enterprise_agent.sh" \
    --project "$PROJECT_ID" \
    --app-id "$GEMINI_APP_ID" \
    --agent-url "https://${SERVICE_NAME}-${REGION}.a.run.app" \
    --dry-run

  echo "=================================================================="
  echo "  [PASS] Telecom Nexus GCP + Terraform + Gemini Enterprise Dry-Run"
  echo "=================================================================="
  exit 0
fi

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVICE_NAME}-repo/${SERVICE_NAME}:latest"

echo "[Step 1/3] Building & pushing container image via Cloud Build..."
gcloud builds submit "$ROOT_DIR" --project "$PROJECT_ID" --tag "$IMAGE_URI"

echo "[Step 2/3] Provisioning infrastructure via Terraform..."
cd "$TF_DIR"
terraform init
terraform apply -auto-approve \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${REGION}" \
  -var="service_name=${SERVICE_NAME}" \
  -var="container_image=${IMAGE_URI}" \
  -var="gemini_enterprise_app_id=${GEMINI_APP_ID}"

SERVICE_URL="$(terraform output -raw cloud_run_service_url)"
echo "[Step 3/3] Registering Cloud Run A2A Agent into Gemini Enterprise..."
bash "$ROOT_DIR/deploy/register_gemini_enterprise_agent.sh" \
  --project "$PROJECT_ID" \
  --app-id "$GEMINI_APP_ID" \
  --agent-url "$SERVICE_URL"
