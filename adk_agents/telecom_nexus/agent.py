"""
Google ADK Multi-Agent Definition for `adk web adk_agents` & Gemini Enterprise Integration.

Launch locally in the ADK Development UI:
    ./scripts/run_adk_web.sh
    # Opens http://localhost:8080 -> Select "telecom_nexus" agent!

Supports both local Gemini API (`GOOGLE_API_KEY`) and Google Cloud Vertex AI / Gemini Enterprise:
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    export GOOGLE_CLOUD_PROJECT="your-telecom-gcp-project"
    export GOOGLE_CLOUD_LOCATION="us-central1"
    export GEMINI_ENTERPRISE_APP_ID="telecom-nexus-enterprise-app"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.adk_a2a_orchestrator import (
    TelecomNexusOrchestratorAgent,
    get_a2a_agent_card,
    handle_a2a_jsonrpc_request,
)
from src.services.cdr_rating import audit_cdr_revenue_leakage
from src.services.order_feasibility import (
    evaluate_order_feasibility,
    list_sales_orders,
    remediate_slice_for_order,
)
from src.services.sla_monitor import evaluate_contract_sla_compliance

DEFAULT_MODEL = os.environ.get("TELECOM_ADK_MODEL", "gemini-2.5-pro")


def tool_evaluate_tmf622_order_feasibility(order_id: str) -> dict[str, Any]:
    """
    Evaluates 3GPP TS 28.552 5G RAN slice admission feasibility for a TMF622 B2B sales order
    (e.g., ORD-TMF622-9001, ORD-TMF622-9003, ORD-TMF622-9011).
    """
    return evaluate_order_feasibility(order_id=order_id)


def tool_execute_5g_slice_remediation(order_id: str) -> dict[str, Any]:
    """
    Executes closed-loop 5G RAN neighbor cell traffic steering and PRB reallocation
    to unblock a contended TMF622 B2B network slice order (e.g., ORD-TMF622-9001).
    """
    return remediate_slice_for_order(
        order_id=order_id,
        steering_mode="NEIGHBOR_OFFLOAD_AND_PRB_REALLOC",
    )


def tool_list_pending_tmf622_orders() -> dict[str, Any]:
    """Lists all TMF622 B2B 5G Network Slice orders and their current feasibility status."""
    orders = list_sales_orders()
    return {"count": len(orders), "orders": orders}


def tool_audit_b2b_sla_and_cdr_leakage() -> dict[str, Any]:
    """
    Runs a combined BSS commercial audit of active B2B SLA contract penalty exposure
    and unbilled GSMA TAP3.12 5G roaming CDR revenue leakage.
    """
    sla = evaluate_contract_sla_compliance()
    cdr = audit_cdr_revenue_leakage()
    return {
        "active_sla_penalty_exposure_usd": sla["total_penalty_exposure_usd"],
        "breached_contracts_count": sla["breached_contracts_count"],
        "breached_contracts": sla["breached_contracts"],
        "unbilled_cdr_leakage_usd": cdr["total_leakage_usd"],
        "underbilled_cdr_count": cdr["underbilled_cdr_count"],
    }


def tool_dispatch_a2a_order_task(order_id: str, auto_remediate: bool = False) -> dict[str, Any]:
    """
    Dispatches a standards-compliant A2A (Agent2Agent) JSON-RPC 2.0 `tasks/send` request
    to the Telecom Nexus A2A Orchestrator and returns the completed A2A Task artifact.
    """
    rpc_payload = {
        "jsonrpc": "2.0",
        "id": f"adk-a2a-{order_id}",
        "method": "tasks/send",
        "params": {
            "id": f"task-{order_id.lower()}",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "data",
                        "data": {
                            "order_id": order_id,
                            "auto_remediate": auto_remediate,
                        },
                    }
                ],
            },
        },
    }
    return handle_a2a_jsonrpc_request(rpc_payload)


def get_gemini_enterprise_connection_config() -> dict[str, Any]:
    """Returns the active Vertex AI & Gemini Enterprise binding configuration."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "telecom-nexus-enterprise")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    app_id = os.environ.get("GEMINI_ENTERPRISE_APP_ID", "telecom-nexus-assistant")
    raw_vertex = os.environ.get("TELECOM_USE_VERTEXAI", "TRUE").strip().upper()
    use_vertex = raw_vertex in ("TRUE", "1", "YES")
    return {
        "use_vertexai": use_vertex,
        "google_cloud_project": project_id,
        "google_cloud_location": location,
        "gemini_enterprise_app_id": app_id,
        "discovery_engine_agent_endpoint": (
            f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}"
            f"/locations/{location}/collections/default_collection/engines/{app_id}"
            f"/assistants/default_assistant/agents"
        ),
        "a2a_agent_card": get_a2a_agent_card(),
    }


try:
    from google.adk.agents import LlmAgent

    ran_slice_agent = LlmAgent(
        name="ran_slice_capacity_agent",
        model=DEFAULT_MODEL,
        description=(
            "OSS Technical Subagent for 3GPP TS 28.552 5G RAN Slice feasibility, PRB utilization, "
            "PDCP latency evaluation, and closed-loop neighbor cell traffic steering."
        ),
        instruction=(
            "You are the 5G RAN OSS Technical Investigator. Use your tools to inspect 3GPP TS 28.552 "
            "cell PRB utilization (< 80%), PDCP latency, and available bandwidth for TMF622 slice orders. "
            "When a cell is congested (>80% PRB) and a healthy neighbor cell exists in the same TAC, "
            "recommend or execute autonomous neighbor offload remediation."
        ),
        tools=[
            tool_evaluate_tmf622_order_feasibility,
            tool_execute_5g_slice_remediation,
            tool_list_pending_tmf622_orders,
        ],
    )

    bss_commercial_agent = LlmAgent(
        name="bss_commercial_sla_agent",
        model=DEFAULT_MODEL,
        description=(
            "BSS Commercial Subagent for Enterprise B2B SLA penalty exposure, GSMA TAP3.12 CDR "
            "revenue assurance, and TMF622 Annual Contract Value (ACV) prioritization."
        ),
        instruction=(
            "You are the BSS Commercial & Revenue Assurance Auditor. Quantify active B2B SLA penalty "
            "exposure, unbilled 5G roaming CDR revenue leakage, and Annual Contract Value (MRR * 12) "
            "protected by fulfilling TMF622 enterprise slice orders. Always preserve subscriber CPNI privacy."
        ),
        tools=[
            tool_audit_b2b_sla_and_cdr_leakage,
            tool_list_pending_tmf622_orders,
        ],
    )

    a2a_bridge_agent = LlmAgent(
        name="a2a_protocol_bridge_agent",
        model=DEFAULT_MODEL,
        description=(
            "A2A (Agent2Agent) Protocol Bridge Agent that dispatches JSON-RPC 2.0 `tasks/send` "
            "requests and exposes the Telecom Nexus Agent Card to Gemini Enterprise."
        ),
        instruction=(
            "You bridge the ADK multi-agent system with external peer agents and Gemini Enterprise "
            "over the A2A Protocol (`/.well-known/agent.json` and `/api/v1/a2a`)."
        ),
        tools=[
            tool_dispatch_a2a_order_task,
            get_gemini_enterprise_connection_config,
        ],
    )

    root_agent = LlmAgent(
        name="telecom_nexus_orchestrator",
        model=DEFAULT_MODEL,
        description=(
            "Telecom Nexus Root OSS/BSS Multi-Agent Coordinator for 5G Network Slice SLA, "
            "CDR Revenue Assurance, and TMF622 Order Feasibility (ADK + A2A + Gemini Enterprise)."
        ),
        instruction=(
            "You are the Telecom Nexus Root Coordinator Agent engineered by Tryolabs. "
            "Coordinate `ran_slice_capacity_agent` (Technical OSS), `bss_commercial_sla_agent` "
            "(Commercial BSS), and `a2a_protocol_bridge_agent` (A2A Protocol & Gemini Enterprise) "
            "to evaluate TMF622 B2B 5G slice orders, remediate RAN congestion, and protect carrier revenue."
        ),
        sub_agents=[ran_slice_agent, bss_commercial_agent, a2a_bridge_agent],
        tools=[
            tool_evaluate_tmf622_order_feasibility,
            tool_execute_5g_slice_remediation,
            tool_audit_b2b_sla_and_cdr_leakage,
            tool_dispatch_a2a_order_task,
            get_gemini_enterprise_connection_config,
        ],
    )
except Exception:
    root_agent = TelecomNexusOrchestratorAgent()  # type: ignore
