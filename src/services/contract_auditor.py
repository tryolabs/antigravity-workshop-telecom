"""
Combined Technical (OSS/3GPP RAN) + Commercial (BSS/SLA & CDR Revenue Assurance) Auditor.
Used by Lab 2 Skill (`sla-revenue-audit`) and REST API endpoints.
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import PROJECT_ROOT
from src.services.cdr_rating import audit_cdr_revenue_leakage
from src.services.sla_monitor import evaluate_contract_sla_compliance


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_active_ran_alarms() -> list[dict[str, Any]]:
    alarms_path = PROJECT_ROOT / "data" / "logs" / "ran_alarms.jsonl"
    if not alarms_path.exists():
        return []
    alarms: list[dict[str, Any]] = []
    with alarms_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                alarms.append(json.loads(line))
    return alarms


def generate_executive_audit_report(db_path: Path | None = None) -> dict[str, Any]:
    """
    Combines CDR Revenue Assurance audit, B2B SLA penalty exposure, and 3GPP RAN alarms
    into a unified Executive Risk & Revenue Intelligence Report.
    """
    cdr_audit = audit_cdr_revenue_leakage(db_path=db_path)
    sla_audit = evaluate_contract_sla_compliance(db_path=db_path)
    alarms = load_active_ran_alarms()

    leakage_dec = Decimal(str(cdr_audit["total_leakage_usd"]))
    penalty_dec = Decimal(str(sla_audit["total_penalty_exposure_usd"]))
    combined_risk_dec = round_money(leakage_dec + penalty_dec)

    leakage_by_contract = cdr_audit.get("leakage_by_contract", {})
    contract_risk_matrix: list[dict[str, Any]] = []

    all_evaluated = sla_audit["breached_contracts"] + sla_audit["compliant_contracts"]
    for item in sorted(all_evaluated, key=lambda x: x["contract_id"]):
        cid = item["contract_id"]
        c_leakage = Decimal(str(leakage_by_contract.get(cid, 0.0)))
        c_penalty = Decimal(str(item["penalty_exposure_usd"]))
        c_total_risk = round_money(c_leakage + c_penalty)
        contract_risk_matrix.append(
            {
                "contract_id": cid,
                "enterprise_name": item["enterprise_name"],
                "account_tier": item["account_tier"],
                "primary_tac": item["primary_tac"],
                "s_nssai_sst": item["s_nssai_sst"],
                "is_sla_breached": item["is_breached"],
                "degraded_cell_id": item["degraded_cell_id"],
                "observed_worst_latency_ms": item["observed_worst_latency_ms"],
                "committed_latency_ms": item["committed_latency_ms"],
                "sla_penalty_exposure_usd": float(c_penalty),
                "cdr_revenue_leakage_usd": float(round_money(c_leakage)),
                "total_commercial_risk_usd": float(c_total_risk),
            }
        )

    contract_risk_matrix.sort(key=lambda r: r["total_commercial_risk_usd"], reverse=True)

    return {
        "platform": "Telecom Nexus 5G OSS/BSS Intelligence",
        "standards": ["3GPP TS 28.552", "3GPP TS 32.298", "GSMA TAP3.12", "TMF622"],
        "total_cdr_leakage_usd": float(round_money(leakage_dec)),
        "total_sla_penalty_exposure_usd": float(round_money(penalty_dec)),
        "total_combined_commercial_risk_usd": float(combined_risk_dec),
        "underbilled_cdr_count": cdr_audit["underbilled_cdr_count"],
        "breached_contracts_count": sla_audit["breached_contracts_count"],
        "active_ran_alarms_count": len(alarms),
        "contract_risk_matrix": contract_risk_matrix,
        "active_alarms": alarms,
    }


def format_executive_audit_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Telecom Nexus — Executive 5G SLA & Revenue Assurance Audit Report",
        "",
        "## 1. Executive Commercial & Network Summary",
        f"- **Total Combined Commercial Exposure**: `${report['total_combined_commercial_risk_usd']:,.2f}`",
        f"- **Unbilled CDR Revenue Leakage (GSMA TAP3 / 3GPP TS 32.298)**: `${report['total_cdr_leakage_usd']:,.2f}` ({report['underbilled_cdr_count']} underbilled CDRs)",
        f"- **Active B2B SLA Penalty Exposure (3GPP TS 28.552 Slice QoS)**: `${report['total_sla_penalty_exposure_usd']:,.2f}` ({report['breached_contracts_count']} breached active contracts)",
        f"- **Active 3GPP RAN & Core Alarms**: `{report['active_ran_alarms_count']}`",
        "",
        "## 2. B2B Enterprise Contract Risk Matrix (Top Priority First)",
        "| Contract ID | Enterprise | Tier | TAC | Slice SST | SLA Status | Worst Latency (Committed) | SLA Penalty ($) | CDR Leakage ($) | Total Risk ($) |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | ---: | ---: | ---: |",
    ]
    for row in report["contract_risk_matrix"]:
        status_badge = "BREACHED" if row["is_sla_breached"] else "COMPLIANT"
        lines.append(
            f"| `{row['contract_id']}` | {row['enterprise_name']} | {row['account_tier']} | "
            f"`{row['primary_tac']}` | SST-{row['s_nssai_sst']} | **{status_badge}** | "
            f"{row['observed_worst_latency_ms']}ms ({row['committed_latency_ms']}ms) | "
            f"${row['sla_penalty_exposure_usd']:,.2f} | ${row['cdr_revenue_leakage_usd']:,.2f} | "
            f"**${row['total_commercial_risk_usd']:,.2f}** |"
        )
    lines.extend(
        [
            "",
            "## 3. Recommended NOC & Commercial Remediation Actions",
            "1. **5G NR Roaming & GiB Rating Patch**: Deploy `Decimal(1024**3)` volume conversion and `NR_5G` visiting PLMN markup in `src/services/cdr_rating.py` to recover unbilled TAP3 revenue.",
            "2. **Dynamic 5G Slice Traffic Steering**: Offload congested URLLC (`SST=2`) and eMBB (`SST=1`) bearers on `CELL-NY-001-B`, `CELL-CHI-002-B`, `CELL-DAL-003-A`, and `CELL-MIA-005-B` to healthy neighbor cells.",
        ]
    )
    return "\n".join(lines) + "\n"
