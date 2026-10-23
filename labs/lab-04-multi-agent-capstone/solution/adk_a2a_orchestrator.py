"""
Lab 4 Reference Solution: Google ADK Multi-Agent System & A2A (Agent2Agent) Protocol Orchestrator.

Implements:
1. Google ADK Multi-Agent Hierarchy (`RANSliceCapacityAgent`, `BSSCommercialSLAAgent`,
   and `TelecomNexusOrchestratorAgent`) with both `google.adk.agents` (`LlmAgent`)
   binding and a deterministic local execution engine for 100% offline testability.
2. A2A (Agent2Agent) Protocol Discovery Card (`GET /.well-known/agent.json`) and
   JSON-RPC 2.0 Task Execution Engine (`POST /api/v1/a2a` supporting `tasks/send` and `message/send`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Any
import uuid

from src.database import fetch_one
from src.services.cdr_rating import audit_cdr_revenue_leakage
from src.services.order_feasibility import (
    evaluate_order_feasibility,
    remediate_slice_for_order,
)
from src.services.sla_monitor import evaluate_contract_sla_compliance

try:
    from google.adk.agents import LlmAgent  # type: ignore

    ADK_SDK_AVAILABLE = True
except ImportError:
    LlmAgent = None  # type: ignore
    ADK_SDK_AVAILABLE = False


class RANSliceCapacityAgent:
    """
    OSS Technical Subagent (3GPP TS 28.552 5G RAN Slice Admission & Steering).
    Wraps physical RAN cell PRB utilization, PDCP latency, and neighbor offload tools.
    """

    name: str = "ran_slice_capacity_agent"
    model: str = "gemini-2.5-pro"
    description: str = (
        "OSS Technical Agent that evaluates 3GPP 5G RAN PRB utilization, PDCP latency, "
        "and neighbor cell offload feasibility for TMF622 slice orders."
    )

    def __init__(self) -> None:
        self.tools = [evaluate_order_feasibility, remediate_slice_for_order]

    def assess_order_ran_slice(self, order_id: str, auto_remediate: bool = False) -> dict[str, Any]:
        initial_feasibility = evaluate_order_feasibility(order_id)
        remediation_result: dict[str, Any] | None = None

        if auto_remediate and initial_feasibility.get("feasibility_status") == "REQUIRES_SLICE_REMEDIATION":
            remediation_result = remediate_slice_for_order(
                order_id=order_id,
                steering_mode="NEIGHBOR_OFFLOAD_AND_PRB_REALLOC",
            )
            final_feasibility = evaluate_order_feasibility(order_id)
        else:
            final_feasibility = initial_feasibility

        return {
            "agent_name": self.name,
            "domain": "OSS_3GPP_RAN_TELEMETRY",
            "order_id": order_id,
            "initial_feasibility_status": initial_feasibility["feasibility_status"],
            "final_feasibility_status": final_feasibility["feasibility_status"],
            "target_tac": final_feasibility["target_tac"],
            "requested_slice_sst": final_feasibility["requested_slice_sst"],
            "requested_bandwidth_mbps": final_feasibility["requested_bandwidth_mbps"],
            "max_latency_ms": final_feasibility["max_latency_ms"],
            "recommended_cell_id": final_feasibility["recommended_cell_id"],
            "congested_cell_id": initial_feasibility["congested_cell_id"],
            "auto_remediation_executed": remediation_result is not None,
            "remediation_details": remediation_result,
            "technical_recommendation": (
                f"Status={final_feasibility['feasibility_status']} "
                f"(Serving Cell={final_feasibility['recommended_cell_id']})"
            ),
        }


class BSSCommercialSLAAgent:
    """
    BSS Business Subagent (Enterprise B2B SLA Risk, CDR Revenue Assurance & TMF622 Valuation).
    Evaluates customer SLA compliance posture, CDR leakage, and Annual Contract Value (ACV).
    """

    name: str = "bss_commercial_sla_agent"
    model: str = "gemini-2.5-pro"
    description: str = (
        "BSS Commercial Agent that evaluates enterprise contract SLA breach posture, "
        "TAP3 CDR revenue leakage, and TMF622 Annual Contract Value (ACV) protection."
    )

    def __init__(self) -> None:
        self.tools = [evaluate_contract_sla_compliance, audit_cdr_revenue_leakage]

    def assess_commercial_impact(self, order_id: str, oss_result: dict[str, Any]) -> dict[str, Any]:
        order_row = fetch_one("SELECT * FROM tmf622_sales_orders WHERE order_id = ?", (order_id,))
        if not order_row:
            raise ValueError(f"TMF622 Sales Order '{order_id}' not found.")

        contract_row = fetch_one(
            "SELECT * FROM b2b_contracts WHERE contract_id = ?",
            (order_row["contract_id"],),
        )

        mrr = Decimal(str(order_row["estimated_mrr_usd"]))
        annual_contract_value = (mrr * Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if contract_row:
            penalty_hr = Decimal(str(contract_row["sla_penalty_per_hour_usd"]))
            breach_hrs = Decimal(str(contract_row["breach_hours_mtd"]))
            sla_penalty_risk = (penalty_hr * breach_hrs).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            sla_penalty_risk = (mrr * Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        sla_summary = evaluate_contract_sla_compliance()
        cdr_summary = audit_cdr_revenue_leakage()

        enterprise_name = order_row["enterprise_name"]
        matching_breaches = [
            b
            for b in sla_summary["breached_contracts"]
            if b.get("enterprise_name", "").lower() == enterprise_name.lower()
            or b.get("tac") == order_row["target_tac"]
            or b.get("contract_id") == order_row["contract_id"]
        ]

        final_status = oss_result["final_feasibility_status"]
        if final_status == "READY_TO_ACTIVATE":
            commercial_decision = "APPROVE_IMMEDIATELY"
            priority_tier = "P1_REVENUE_CAPTURE"
        elif final_status == "REQUIRES_SLICE_REMEDIATION":
            commercial_decision = "APPROVE_WITH_AUTOMATED_RAN_STEERING"
            priority_tier = "P1_SLA_PROTECTED_EXPANSION"
        else:
            commercial_decision = "HOLD_REQUIRES_RAN_CAPACITY_CAPEX"
            priority_tier = "P2_CAPEX_BACKLOG"

        return {
            "agent_name": self.name,
            "domain": "BSS_COMMERCIAL_SLA_AND_REVENUE",
            "order_id": order_id,
            "contract_id": order_row["contract_id"],
            "enterprise_name": enterprise_name,
            "monthly_recurring_revenue_usd": float(mrr),
            "annual_contract_value_usd": float(annual_contract_value),
            "avoided_sla_penalty_risk_usd": float(sla_penalty_risk),
            "total_commercial_value_usd": float(annual_contract_value + sla_penalty_risk),
            "regional_active_sla_breaches_count": len(matching_breaches),
            "platform_active_sla_exposure_usd": sla_summary["total_penalty_exposure_usd"],
            "platform_cdr_leakage_identified_usd": cdr_summary["total_leakage_usd"],
            "commercial_decision": commercial_decision,
            "priority_tier": priority_tier,
        }


class TelecomNexusOrchestratorAgent:
    """
    Root Google ADK Multi-Agent Coordinator (`LlmAgent` hierarchy) that orchestrates:
      Step 1 -> `RANSliceCapacityAgent` (OSS 3GPP TS 28.552 RAN evaluation & optional slice steering)
      Step 2 -> `BSSCommercialSLAAgent` (BSS TMF622 commercial valuation & SLA risk scoring)
    """

    name: str = "telecom_nexus_orchestrator"
    model: str = "gemini-2.5-pro"

    def __init__(self) -> None:
        self.ran_agent = RANSliceCapacityAgent()
        self.bss_agent = BSSCommercialSLAAgent()
        self.sub_agents = [self.ran_agent, self.bss_agent]
        self.adk_hierarchy = self._build_adk_hierarchy()

    def _build_adk_hierarchy(self) -> dict[str, Any]:
        """Builds the Google ADK agent descriptor (and native ADK objects when google-adk is installed)."""
        adk_native_constructed = False
        if ADK_SDK_AVAILABLE and LlmAgent is not None:
            try:
                ran_llm = LlmAgent(
                    name=self.ran_agent.name,
                    model=self.ran_agent.model,
                    description=self.ran_agent.description,
                    tools=self.ran_agent.tools,
                )
                bss_llm = LlmAgent(
                    name=self.bss_agent.name,
                    model=self.bss_agent.model,
                    description=self.bss_agent.description,
                    tools=self.bss_agent.tools,
                )
                LlmAgent(
                    name=self.name,
                    model=self.model,
                    description="Telecom Nexus Root OSS+BSS Multi-Agent Coordinator",
                    sub_agents=[ran_llm, bss_llm],
                )
                adk_native_constructed = True
            except Exception:
                adk_native_constructed = False

        return {
            "framework": "google-adk",
            "pattern": "CoordinatorSubAgents",
            "root_agent": self.name,
            "adk_sdk_installed": ADK_SDK_AVAILABLE,
            "adk_native_graph_constructed": adk_native_constructed,
            "sub_agents": [
                {
                    "name": self.ran_agent.name,
                    "role": "OSS Technical 5G RAN Slice Agent",
                    "tools": [fn.__name__ for fn in self.ran_agent.tools],
                },
                {
                    "name": self.bss_agent.name,
                    "role": "BSS Commercial SLA & Revenue Agent",
                    "tools": [fn.__name__ for fn in self.bss_agent.tools],
                },
            ],
        }

    def run_order_assessment(self, order_id: str, auto_remediate: bool = False) -> dict[str, Any]:
        oss_assessment = self.ran_agent.assess_order_ran_slice(
            order_id=order_id,
            auto_remediate=auto_remediate,
        )
        bss_assessment = self.bss_agent.assess_commercial_impact(
            order_id=order_id,
            oss_result=oss_assessment,
        )

        summary_markdown = (
            f"### Telecom Nexus ADK Multi-Agent Decision (`{order_id}`)\n"
            f"- **Enterprise Customer**: {bss_assessment['enterprise_name']}\n"
            f"- **OSS RAN Technical Status (`{self.ran_agent.name}`)**: `{oss_assessment['final_feasibility_status']}` "
            f"(TAC `{oss_assessment['target_tac']}`, Serving Cell `{oss_assessment['recommended_cell_id']}`)\n"
            f"- **BSS Commercial Decision (`{self.bss_agent.name}`)**: `{bss_assessment['commercial_decision']}` "
            f"(Protected ACV: `${bss_assessment['annual_contract_value_usd']:,.2f}`, "
            f"Avoided SLA Penalty Risk: `${bss_assessment['avoided_sla_penalty_risk_usd']:,.2f}`)\n"
        )

        return {
            "orchestrator_name": self.name,
            "adk_architecture": self.adk_hierarchy,
            "order_id": order_id,
            "oss_technical_assessment": oss_assessment,
            "bss_commercial_assessment": bss_assessment,
            "executive_decision": {
                "commercial_decision": bss_assessment["commercial_decision"],
                "feasibility_status": oss_assessment["final_feasibility_status"],
                "recommended_cell_id": oss_assessment["recommended_cell_id"],
                "auto_remediation_executed": oss_assessment["auto_remediation_executed"],
                "protected_annual_contract_value_usd": bss_assessment["annual_contract_value_usd"],
                "avoided_sla_penalty_risk_usd": bss_assessment["avoided_sla_penalty_risk_usd"],
                "total_commercial_value_usd": bss_assessment["total_commercial_value_usd"],
            },
            "agent_trace": [
                {
                    "step": 1,
                    "agent": self.ran_agent.name,
                    "status": "COMPLETED",
                    "output_status": oss_assessment["final_feasibility_status"],
                },
                {
                    "step": 2,
                    "agent": self.bss_agent.name,
                    "status": "COMPLETED",
                    "output_decision": bss_assessment["commercial_decision"],
                },
            ],
            "summary_markdown": summary_markdown,
        }


def get_a2a_agent_card(base_url: str = "http://localhost:8001") -> dict[str, Any]:
    """
    Returns the standard A2A (Agent2Agent) Protocol Discovery Card
    exposed at `GET /.well-known/agent.json` and `GET /api/v1/a2a/agent-card`.
    """
    clean_base = base_url.rstrip("/")
    return {
        "name": "TelecomNexus-OSS-BSS-Orchestrator",
        "description": (
            "Multi-Agent 5G Network Slice SLA, CDR Revenue Assurance & TMF622 Order Feasibility "
            "Orchestrator built with Google ADK (Agent Development Kit) and the A2A Protocol."
        ),
        "url": f"{clean_base}/api/v1/a2a",
        "version": "2.0.0",
        "protocolVersion": "0.2.1",
        "provider": {
            "organization": "Tryolabs — Telecom OSS/BSS AI Practice",
            "url": "https://tryolabs.com",
        },
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/markdown"],
        "skills": [
            {
                "id": "tmf622_order_feasibility",
                "name": "TMF622 5G Network Slice Order Feasibility",
                "description": (
                    "Coordinates RANSliceCapacityAgent (3GPP TS 28.552) and BSSCommercialSLAAgent "
                    "to evaluate TMF622 B2B 5G network slice orders and compute ACV protection."
                ),
                "tags": ["3gpp", "tmf622", "5g-slicing", "oss-bss", "adk"],
                "examples": [
                    "Evaluate TMF622 order ORD-TMF622-9001 for 5G slice admission and commercial SLA impact.",
                    "Check order feasibility for ORD-TMF622-9003.",
                ],
            },
            {
                "id": "autonomous_slice_remediation",
                "name": "Autonomous 5G RAN Slice Offload & PRB Remediation",
                "description": (
                    "Executes closed-loop neighbor cell traffic steering and PRB reallocation "
                    "to unblock contended TMF622 B2B slice orders."
                ),
                "tags": ["3gpp-ts-28552", "ran-steering", "self-organizing-network", "a2a"],
                "examples": [
                    "Evaluate and auto-remediate congested slice for order ORD-TMF622-9001.",
                ],
            },
            {
                "id": "sla_revenue_assurance",
                "name": "B2B SLA Penalty Exposure & TAP3 CDR Revenue Assurance",
                "description": (
                    "Audits active enterprise B2B SLA contracts against 5G RAN telemetry and "
                    "quantifies unbilled GSMA TAP3.12 roaming CDR revenue leakage."
                ),
                "tags": ["gsma-tap3", "cdr-rating", "sla-compliance", "sox-404"],
                "examples": [
                    "Run full OSS/BSS commercial SLA and CDR revenue leakage assessment.",
                ],
            },
        ],
    }


def _extract_order_params_from_a2a_params(params: dict[str, Any]) -> tuple[str, bool]:
    """Extracts (order_id, auto_remediate) from an A2A JSON-RPC `params` payload."""
    order_id = str(params.get("order_id", "")).strip()
    auto_remediate = bool(params.get("auto_remediate", False))

    message = params.get("message") or {}
    metadata = params.get("metadata") or message.get("metadata") or {}
    if not order_id and metadata.get("order_id"):
        order_id = str(metadata["order_id"]).strip()
    if "auto_remediate" in metadata:
        auto_remediate = bool(metadata["auto_remediate"])

    parts = message.get("parts") or []
    for part in parts:
        if not isinstance(part, dict):
            continue
        part_data = part.get("data")
        if isinstance(part_data, dict):
            if not order_id and part_data.get("order_id"):
                order_id = str(part_data["order_id"]).strip()
            if "auto_remediate" in part_data:
                auto_remediate = bool(part_data["auto_remediate"])

        part_text = str(part.get("text", ""))
        if part_text:
            match = re.search(r"ORD-TMF622-\d+", part_text, re.IGNORECASE)
            if match and not order_id:
                order_id = match.group(0).upper()
            if re.search(r"\b(remediate|auto_remediate|offload|steer)\b", part_text, re.IGNORECASE):
                auto_remediate = True

    if not order_id:
        order_id = "ORD-TMF622-9001"

    return order_id, auto_remediate


def handle_a2a_jsonrpc_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processes an incoming A2A (Agent2Agent) JSON-RPC 2.0 request (`tasks/send` or `message/send`)
    and delegates execution to `TelecomNexusOrchestratorAgent`.
    """
    jsonrpc_version = payload.get("jsonrpc", "2.0")
    request_id = payload.get("id", str(uuid.uuid4()))
    method = payload.get("method", "tasks/send")
    params = payload.get("params") or {}

    if method not in ("tasks/send", "message/send", "tasks/get"):
        return {
            "jsonrpc": jsonrpc_version,
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Unsupported A2A JSON-RPC method '{method}'. Supported: tasks/send, message/send.",
            },
        }

    task_id = str(params.get("id") or f"task-{uuid.uuid4().hex[:10]}")
    session_id = str(params.get("sessionId") or f"session-{uuid.uuid4().hex[:10]}")

    try:
        order_id, auto_remediate = _extract_order_params_from_a2a_params(params)
        orchestrator = TelecomNexusOrchestratorAgent()
        decision = orchestrator.run_order_assessment(
            order_id=order_id,
            auto_remediate=auto_remediate,
        )
    except ValueError as exc:
        return {
            "jsonrpc": jsonrpc_version,
            "id": request_id,
            "error": {
                "code": -32602,
                "message": str(exc),
            },
        }

    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "jsonrpc": jsonrpc_version,
        "id": request_id,
        "result": {
            "id": task_id,
            "sessionId": session_id,
            "status": {
                "state": "completed",
                "timestamp": now_iso,
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "type": "text",
                            "text": decision["summary_markdown"],
                        }
                    ],
                },
            },
            "artifacts": [
                {
                    "name": "oss_bss_multi_agent_decision",
                    "description": "Coordinated Google ADK Multi-Agent OSS Technical + BSS Commercial Decision",
                    "parts": [
                        {
                            "type": "data",
                            "data": decision,
                        },
                        {
                            "type": "text",
                            "text": decision["summary_markdown"],
                        },
                    ],
                    "index": 0,
                }
            ],
            "history": decision["agent_trace"],
        },
    }
