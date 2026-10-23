"""
5G Network Slice SLA Compliance & Commercial Penalty Exposure Service.

Domain Rules:
1. Only B2B Contracts with status == 'ACTIVE' are eligible for SLA compliance monitoring
   and financial penalty exposure calculation (exclude 'TERMINATED' and 'DRAFT').
2. For each active contract, inspect all 5G RAN cells in `ran_telemetry` matching
   the contract's `primary_tac` and `s_nssai_sst`.
3. A contract is in SLA Breach if:
   - worst_pdcp_latency_ms > committed_latency_ms, OR
   - min_availability_pct < committed_availability_pct.
4. Financial Penalty Exposure (USD) for a breached active contract:
   sla_penalty_per_hour_usd * breach_hours_mtd (using Decimal, ROUND_HALF_UP to 0.01).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import fetch_all


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def evaluate_contract_sla_compliance(db_path: Path | None = None) -> dict[str, Any]:
    """
    Evaluates ACTIVE B2B SLA contracts against 5G RAN cell telemetry and calculates
    total financial penalty exposure.
    """
    contracts = fetch_all(
        "SELECT * FROM b2b_contracts WHERE status = 'ACTIVE' ORDER BY contract_id",
        db_path=db_path,
    )
    cells = fetch_all("SELECT * FROM ran_telemetry ORDER BY cell_id", db_path=db_path)

    total_penalty_exposure = Decimal("0.00")
    breached_contracts: list[dict[str, Any]] = []
    compliant_contracts: list[dict[str, Any]] = []

    for contract in contracts:
        matching_cells = [
            c
            for c in cells
            if c["tac"] == contract["primary_tac"]
            and int(c["s_nssai_sst"]) == int(contract["s_nssai_sst"])
        ]
        if not matching_cells:
            continue

        worst_latency = max(float(c["pdcp_latency_ms"]) for c in matching_cells)
        min_avail = min(float(c["availability_pct"]) for c in matching_cells)
        worst_cell = max(matching_cells, key=lambda c: float(c["pdcp_latency_ms"]))

        committed_latency = float(contract["committed_latency_ms"])
        committed_avail = float(contract["committed_availability_pct"])

        latency_breach = worst_latency > committed_latency
        availability_breach = min_avail < committed_avail
        is_breached = latency_breach or availability_breach

        if is_breached:
            rate_hr = Decimal(str(contract["sla_penalty_per_hour_usd"]))
            hours = Decimal(str(contract["breach_hours_mtd"]))
            penalty_usd = round_money(rate_hr * hours)
        else:
            penalty_usd = Decimal("0.00")

        record = {
            "contract_id": contract["contract_id"],
            "enterprise_name": contract["enterprise_name"],
            "account_tier": contract["account_tier"],
            "status": contract["status"],
            "primary_tac": contract["primary_tac"],
            "s_nssai_sst": contract["s_nssai_sst"],
            "committed_latency_ms": committed_latency,
            "observed_worst_latency_ms": worst_latency,
            "committed_availability_pct": committed_avail,
            "observed_min_availability_pct": min_avail,
            "degraded_cell_id": worst_cell["cell_id"],
            "breach_hours_mtd": float(contract["breach_hours_mtd"]),
            "sla_penalty_per_hour_usd": float(contract["sla_penalty_per_hour_usd"]),
            "penalty_exposure_usd": float(penalty_usd),
            "is_breached": is_breached,
        }

        if is_breached:
            total_penalty_exposure = round_money(total_penalty_exposure + penalty_usd)
            breached_contracts.append(record)
        else:
            compliant_contracts.append(record)

    return {
        "evaluated_contracts_count": len(breached_contracts) + len(compliant_contracts),
        "breached_contracts_count": len(breached_contracts),
        "compliant_contracts_count": len(compliant_contracts),
        "total_penalty_exposure_usd": float(total_penalty_exposure),
        "breached_contracts": breached_contracts,
        "compliant_contracts": compliant_contracts,
    }
