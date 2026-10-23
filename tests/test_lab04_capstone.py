"""
Lab 4 Capstone Verification Tests:
1. TMF622 B2B Sales Order Feasibility & 5G Network Slice QoS Remediation API (`src/services/order_feasibility.py` & `src/main.py`)
2. Google ADK (Agent Development Kit) Multi-Agent Orchestrator (`src/agents/adk_a2a_orchestrator.py` & `adk_agents/telecom_nexus/agent.py`)
3. A2A (Agent2Agent) Protocol Discovery Card (`GET /.well-known/agent.json`) & JSON-RPC 2.0 Task Engine (`POST /api/v1/a2a`)
4. ADK Web Dev UI (`scripts/run_adk_web.sh`), Terraform Infrastructure (`infra/terraform/`), & Gemini Enterprise Registration (`deploy/deploy_gcp.sh --dry-run`).
"""

from __future__ import annotations

from pathlib import Path
import subprocess

from fastapi.testclient import TestClient
import pytest

from adk_agents.telecom_nexus.agent import (
    get_gemini_enterprise_connection_config,
    root_agent,
)
from data.seed_telecom_data import seed_all
from src.agents.adk_a2a_orchestrator import TelecomNexusOrchestratorAgent
from src.main import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    db_file = tmp_path / "capstone_telecom.db"
    seed_all(db_file)
    monkeypatch.setenv("TELECOM_NEXUS_DB", str(db_file))
    return db_file


def test_order_feasibility_ready_to_activate(isolated_db) -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/orders/feasibility-check",
        json={"order_id": "ORD-TMF622-9003"},
    )
    assert res.status_code == 200, f"Unexpected status {res.status_code}: {res.text}"
    body = res.json()
    assert body["order_id"] == "ORD-TMF622-9003"
    assert body["feasibility_status"] == "READY_TO_ACTIVATE"
    assert body["requires_remediation"] is False
    assert body["recommended_cell_id"] in ("CELL-LAX-004-A", "CELL-LAX-004-B")


def test_order_feasibility_requires_slice_remediation(isolated_db) -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/orders/feasibility-check",
        json={"order_id": "ORD-TMF622-9001"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["feasibility_status"] == "REQUIRES_SLICE_REMEDIATION"
    assert body["requires_remediation"] is True
    assert body["congested_cell_id"] == "CELL-NY-001-B"
    assert body["recommended_cell_id"] == "CELL-NY-001-C"
    assert body["protected_annual_revenue_usd"] == 504000.0


def test_order_feasibility_rejected_when_exceeding_physical_limits(isolated_db) -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/orders/feasibility-check",
        json={"order_id": "ORD-TMF622-9011"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["feasibility_status"] == "REJECTED"
    assert body["requires_remediation"] is False
    assert body["recommended_cell_id"] is None


def test_slice_remediation_end_to_end_unblocks_order_and_heals_ran_cell(isolated_db) -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/slices/remediate",
        json={
            "order_id": "ORD-TMF622-9001",
            "steering_mode": "NEIGHBOR_OFFLOAD_AND_PRB_REALLOC",
        },
    )
    assert res.status_code == 200, f"Remediation failed: {res.text}"
    body = res.json()
    assert body["order_id"] == "ORD-TMF622-9001"
    assert body["previous_status"] == "REQUIRES_SLICE_REMEDIATION"
    assert body["new_order_status"] == "READY_TO_ACTIVATE"
    assert body["sales_stage"] == "PROVISIONED"
    assert body["remediated_congested_cell_id"] == "CELL-NY-001-B"
    assert body["target_serving_cell_id"] == "CELL-NY-001-C"
    assert body["protected_annual_revenue_usd"] == 504000.0
    assert body["avoided_sla_penalty_usd"] == 96000.0
    assert body["total_commercial_value_preserved_usd"] == 600000.0

    # Verify that re-checking feasibility on ORD-TMF622-9001 now reports READY_TO_ACTIVATE
    recheck = client.post(
        "/api/v1/orders/feasibility-check",
        json={"order_id": "ORD-TMF622-9001"},
    )
    assert recheck.status_code == 200
    assert recheck.json()["feasibility_status"] == "READY_TO_ACTIVATE"


def test_slice_remediation_returns_400_for_unfeasible_order(isolated_db) -> None:
    client = TestClient(app)
    res = client.post(
        "/api/v1/slices/remediate",
        json={"order_id": "ORD-TMF622-9011"},
    )
    assert res.status_code == 400


def test_adk_multi_agent_orchestrator_handoff(isolated_db) -> None:
    orchestrator = TelecomNexusOrchestratorAgent()
    result = orchestrator.run_order_assessment("ORD-TMF622-9001", auto_remediate=False)

    assert result["orchestrator_name"] == "telecom_nexus_orchestrator"
    assert result["adk_architecture"]["framework"] == "google-adk"
    assert len(result["adk_architecture"]["sub_agents"]) == 2
    assert result["oss_technical_assessment"]["agent_name"] == "ran_slice_capacity_agent"
    assert result["oss_technical_assessment"]["final_feasibility_status"] == "REQUIRES_SLICE_REMEDIATION"
    assert result["bss_commercial_assessment"]["agent_name"] == "bss_commercial_sla_agent"
    assert result["bss_commercial_assessment"]["commercial_decision"] == "APPROVE_WITH_AUTOMATED_RAN_STEERING"
    assert result["bss_commercial_assessment"]["annual_contract_value_usd"] == 504000.0
    assert len(result["agent_trace"]) == 2


def test_a2a_agent_discovery_card_endpoint(isolated_db) -> None:
    client = TestClient(app)
    res = client.get("/.well-known/agent.json")
    assert res.status_code == 200, f"A2A Agent Card failed: {res.text}"
    card = res.json()
    assert card["name"] == "TelecomNexus-OSS-BSS-Orchestrator"
    assert card["url"].endswith("/api/v1/a2a")
    skill_ids = {s["id"] for s in card["skills"]}
    assert {
        "tmf622_order_feasibility",
        "autonomous_slice_remediation",
        "sla_revenue_assurance",
    }.issubset(skill_ids)


def test_a2a_jsonrpc_tasks_send_multi_agent_execution(isolated_db) -> None:
    client = TestClient(app)
    rpc_request = {
        "jsonrpc": "2.0",
        "id": "rpc-req-9001",
        "method": "tasks/send",
        "params": {
            "id": "a2a-task-9001",
            "sessionId": "session-telecom-01",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Evaluate and remediate TMF622 order ORD-TMF622-9001 across OSS RAN and BSS SLA agents.",
                    }
                ],
            },
        },
    }
    res = client.post("/api/v1/a2a", json=rpc_request)
    assert res.status_code == 200, f"A2A tasks/send failed: {res.text}"
    body = res.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "rpc-req-9001"
    task = body["result"]
    assert task["id"] == "a2a-task-9001"
    assert task["status"]["state"] == "completed"
    assert len(task["artifacts"]) == 1

    decision_data = task["artifacts"][0]["parts"][0]["data"]
    assert decision_data["order_id"] == "ORD-TMF622-9001"
    assert decision_data["executive_decision"]["auto_remediation_executed"] is True
    assert decision_data["executive_decision"]["feasibility_status"] == "READY_TO_ACTIVATE"
    assert decision_data["executive_decision"]["commercial_decision"] == "APPROVE_IMMEDIATELY"


def test_adk_web_agent_package_and_gemini_enterprise_config(isolated_db) -> None:
    assert getattr(root_agent, "name", None) == "telecom_nexus_orchestrator"
    cfg = get_gemini_enterprise_connection_config()
    assert cfg["use_vertexai"] is True
    assert "discoveryengine.googleapis.com/v1alpha/projects/" in cfg["discovery_engine_agent_endpoint"]
    assert cfg["a2a_agent_card"]["name"] == "TelecomNexus-OSS-BSS-Orchestrator"


def test_terraform_and_gcp_deploy_dry_run() -> None:
    tf_main = (PROJECT_ROOT / "infra" / "terraform" / "main.tf").read_text(encoding="utf-8")
    assert "google_cloud_run_v2_service" in tf_main
    assert "discoveryengine.googleapis.com" in tf_main
    assert "cloudaicompanion.googleapis.com" in tf_main

    proc = subprocess.run(
        ["bash", str(PROJECT_ROOT / "deploy" / "deploy_gcp.sh"), "--dry-run"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"deploy_gcp.sh --dry-run failed:\n{proc.stdout}\n{proc.stderr}"
    assert "[PASS] Telecom Nexus GCP + Terraform + Gemini Enterprise Dry-Run" in proc.stdout
