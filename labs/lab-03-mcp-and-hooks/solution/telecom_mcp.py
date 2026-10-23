#!/usr/bin/env python3
"""
Telecom Nexus FastMCP Server (Lab 3 Reference Solution).

Exposes 4 domain tools over MCP:
1. `query_ran_cell_health`: Inspects 3GPP 5G RAN cells by TAC and S-NSSAI SST.
2. `calculate_contract_penalty_exposure`: Computes B2B SLA compliance and Decimal penalty exposure.
3. `inspect_unbilled_cdrs`: Audits TAP3 CDR revenue leakage with CPNI-masked subscriber identifiers.
4. `evaluate_slice_capacity`: Checks 5G RAN slice admission feasibility and neighbor cell offload options.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer as FastMCP
from src.database import fetch_all
from src.services.cdr_rating import HOME_PLMN, rate_cdr_record
from src.services.sla_monitor import evaluate_contract_sla_compliance

mcp = FastMCP("telecom-nexus-mcp")


def _mask_identifier(value: str) -> str:
    val = str(value)
    if len(val) <= 6:
        return "***"
    return f"{val[:4]}***{val[-4:]}"


@mcp.tool()
def query_ran_cell_health(tac: str | None = None, s_nssai_sst: int | None = None) -> dict[str, Any]:
    """
    Queries 3GPP 5G RAN cell telemetry by Tracking Area Code (TAC) and/or Slice SST (1=eMBB, 2=URLLC, 3=mIoT).
    Returns PRB utilization %, PDCP latency (ms), RSRP/SINR, available bandwidth, and neighbor cell IDs.
    """
    cells = fetch_all("SELECT * FROM ran_telemetry ORDER BY cell_id")
    if tac:
        cells = [c for c in cells if c["tac"] == tac]
    if s_nssai_sst is not None:
        cells = [c for c in cells if int(c["s_nssai_sst"]) == int(s_nssai_sst)]

    congested = [c["cell_id"] for c in cells if float(c["prb_utilization_pct"]) >= 80.0]
    return {
        "matched_cells_count": len(cells),
        "congested_cell_ids": congested,
        "cells": cells,
    }


@mcp.tool()
def calculate_contract_penalty_exposure(contract_id: str | None = None) -> dict[str, Any]:
    """
    Computes B2B SLA compliance and financial penalty exposure (USD) across ACTIVE contracts
    (or filtered to a single contract_id).
    """
    sla_summary = evaluate_contract_sla_compliance()
    all_contracts = sla_summary["breached_contracts"] + sla_summary["compliant_contracts"]

    if contract_id:
        filtered = [c for c in all_contracts if c["contract_id"] == contract_id]
        total_exp = sum(
            (Decimal(str(c["penalty_exposure_usd"])) for c in filtered),
            Decimal("0.00"),
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "contract_id_filter": contract_id,
            "matched_count": len(filtered),
            "total_penalty_exposure_usd": float(total_exp),
            "contracts": filtered,
        }

    return sla_summary


@mcp.tool()
def inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False) -> dict[str, Any]:
    """
    Audits GSMA TAP3 / 3GPP CDR records for revenue leakage using Decimal arithmetic and
    masks subscriber IMSI/MSISDN fields for CPNI privacy compliance.
    """
    cdrs = fetch_all("SELECT * FROM cdr_records ORDER BY cdr_id")
    if contract_id:
        cdrs = [c for c in cdrs if c["contract_id"] == contract_id]
    if roaming_only:
        cdrs = [c for c in cdrs if c["roaming_plmn"] != HOME_PLMN]

    total_leakage = Decimal("0.00")
    underbilled: list[dict[str, Any]] = []

    for cdr in cdrs:
        billed = Decimal(str(cdr["billed_amount_usd"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected = rate_cdr_record(cdr)
        delta = (expected - billed).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if delta > Decimal("0.01"):
            total_leakage = (total_leakage + delta).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            underbilled.append(
                {
                    "cdr_id": cdr["cdr_id"],
                    "contract_id": cdr["contract_id"],
                    "masked_imsi": _mask_identifier(cdr["imsi"]),
                    "masked_msisdn": _mask_identifier(cdr["msisdn"]),
                    "rat_type": cdr["rat_type"],
                    "roaming_plmn": cdr["roaming_plmn"],
                    "billed_amount_usd": float(billed),
                    "expected_amount_usd": float(expected),
                    "leakage_usd": float(delta),
                }
            )

    return {
        "audited_cdr_count": len(cdrs),
        "underbilled_cdr_count": len(underbilled),
        "total_leakage_usd": float(total_leakage),
        "underbilled_records": underbilled[:25],
    }


@mcp.tool()
def evaluate_slice_capacity(
    target_tac: str,
    requested_slice_sst: int,
    requested_bandwidth_mbps: int,
    max_latency_ms: float,
) -> dict[str, Any]:
    """
    Evaluates 5G RAN slice admission feasibility in a target TAC and S-NSSAI SST.
    Checks PRB utilization (< 80%), PDCP latency (<= max_latency_ms), and available bandwidth.
    """
    cells = fetch_all(
        "SELECT * FROM ran_telemetry WHERE tac = ? AND s_nssai_sst = ? ORDER BY pdcp_latency_ms ASC",
        (target_tac, int(requested_slice_sst)),
    )
    feasible = [
        c
        for c in cells
        if float(c["prb_utilization_pct"]) < 80.0
        and float(c["pdcp_latency_ms"]) <= float(max_latency_ms)
        and int(c["available_bandwidth_mbps"]) >= int(requested_bandwidth_mbps)
    ]
    congested = [
        c
        for c in cells
        if float(c["prb_utilization_pct"]) >= 80.0 or float(c["pdcp_latency_ms"]) > float(max_latency_ms)
    ]

    if not feasible:
        status = "REJECTED"
    elif congested:
        status = "REQUIRES_SLICE_REMEDIATION"
    else:
        status = "READY_TO_ACTIVATE"

    return {
        "target_tac": target_tac,
        "requested_slice_sst": int(requested_slice_sst),
        "requested_bandwidth_mbps": int(requested_bandwidth_mbps),
        "max_latency_ms": float(max_latency_ms),
        "feasibility_status": status,
        "recommended_cell_id": feasible[0]["cell_id"] if feasible else None,
        "congested_cell_ids": [c["cell_id"] for c in congested],
        "feasible_cells": feasible,
    }


if __name__ == "__main__":
    mcp.run()
