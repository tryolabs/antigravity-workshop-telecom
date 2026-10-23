#!/usr/bin/env python3
"""
Telecom Nexus FastMCP Server (Starter State for Labs 1-2; Extended in Lab 3).

Exposes live SQLite OSS (5G RAN Telemetry, 3GPP Alarms) and BSS (B2B SLA Contracts,
GSMA TAP3 CDRs, TMF622 Orders) tools over the Model Context Protocol (MCP).
"""

from __future__ import annotations

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

mcp = FastMCP("telecom-nexus-mcp")


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
    Lab 3 Task: Implement this MCP tool to return B2B SLA compliance and financial penalty
    exposure (USD) for a specific ACTIVE contract_id or across all ACTIVE contracts.
    """
    raise NotImplementedError(
        "Lab 3: Implement calculate_contract_penalty_exposure() in mcp_server/telecom_mcp.py"
    )


@mcp.tool()
def inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False) -> dict[str, Any]:
    """
    Lab 3 Task: Implement this MCP tool to inspect underbilled GSMA TAP3 / 3GPP CDR records
    (with CPNI-compliant masked IMSI/MSISDN) and quantify revenue leakage in USD.
    """
    raise NotImplementedError(
        "Lab 3: Implement inspect_unbilled_cdrs() in mcp_server/telecom_mcp.py"
    )


@mcp.tool()
def evaluate_slice_capacity(target_tac: str, requested_slice_sst: int, requested_bandwidth_mbps: int, max_latency_ms: float) -> dict[str, Any]:
    """
    Lab 3 Task: Implement this MCP tool to evaluate whether a target TAC and 3GPP Slice SST
    can admit a new B2B order (`prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms`,
    and `available_bandwidth_mbps >= requested_bandwidth_mbps`).
    """
    raise NotImplementedError(
        "Lab 3: Implement evaluate_slice_capacity() in mcp_server/telecom_mcp.py"
    )


if __name__ == "__main__":
    mcp.run()
