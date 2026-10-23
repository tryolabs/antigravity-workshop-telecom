"""
TMF622 B2B Sales Order Feasibility & 5G Network Slice QoS Remediation Service (Lab 4 Solution).

Domain Rules (3GPP TS 28.552 / TMF622):
1. A candidate 5G RAN cell in `target_tac` with matching `s_nssai_sst == requested_slice_sst`
   is feasible if:
   - `prb_utilization_pct < 80.0`
   - `pdcp_latency_ms <= max_latency_ms`
   - `available_bandwidth_mbps >= requested_bandwidth_mbps`
2. Order Feasibility Outcomes:
   - `READY_TO_ACTIVATE`: At least one matching cell is feasible AND no matching cell in the
     TAC+slice is congested/breaching latency (`prb_utilization_pct >= 80.0` or `pdcp_latency_ms > max_latency_ms`).
   - `REQUIRES_SLICE_REMEDIATION`: At least one matching cell in the TAC+slice is congested or
     violating latency, BUT a healthy neighbor/candidate cell in the same TAC+slice meets all feasibility criteria.
   - `REJECTED`: No candidate cell in the TAC+slice can meet the requested bandwidth and latency constraints.
3. Slice Remediation (`remediate_slice_for_order`):
   - Steers traffic from the congested cell to the healthy neighbor cell, rebalancing PRB utilization
     below 80% and restoring PDCP latency below the SLA threshold.
   - Transitions the TMF622 order to `READY_TO_ACTIVATE` (`PROVISIONED`) and computes protected ARR
     and avoided SLA penalties using `Decimal`.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import execute_write, fetch_all, fetch_one


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def list_sales_orders(db_path: Path | None = None) -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM tmf622_sales_orders ORDER BY order_id", db_path=db_path)


def evaluate_order_feasibility(order_id: str, db_path: Path | None = None) -> dict[str, Any]:
    order = fetch_one(
        "SELECT * FROM tmf622_sales_orders WHERE order_id = ?",
        (order_id,),
        db_path=db_path,
    )
    if not order:
        raise ValueError(f"TMF622 Order not found: {order_id}")

    contract = fetch_one(
        "SELECT * FROM b2b_contracts WHERE contract_id = ?",
        (order["contract_id"],),
        db_path=db_path,
    )

    candidate_cells = fetch_all(
        "SELECT * FROM ran_telemetry WHERE tac = ? AND s_nssai_sst = ? ORDER BY pdcp_latency_ms ASC",
        (order["target_tac"], int(order["requested_slice_sst"])),
        db_path=db_path,
    )

    req_bw = int(order["requested_bandwidth_mbps"])
    max_lat = float(order["max_latency_ms"])

    feasible_cells = [
        c
        for c in candidate_cells
        if float(c["prb_utilization_pct"]) < 80.0
        and float(c["pdcp_latency_ms"]) <= max_lat
        and int(c["available_bandwidth_mbps"]) >= req_bw
    ]
    congested_cells = [
        c
        for c in candidate_cells
        if float(c["prb_utilization_pct"]) >= 80.0 or float(c["pdcp_latency_ms"]) > max_lat
    ]

    if not feasible_cells:
        feasibility_status = "REJECTED"
        requires_remediation = False
        recommended_cell_id = None
        congested_cell_id = congested_cells[0]["cell_id"] if congested_cells else None
    elif congested_cells:
        feasibility_status = "REQUIRES_SLICE_REMEDIATION"
        requires_remediation = True
        recommended_cell_id = feasible_cells[0]["cell_id"]
        congested_cell_id = max(congested_cells, key=lambda c: float(c["prb_utilization_pct"]))["cell_id"]
    else:
        feasibility_status = "READY_TO_ACTIVATE"
        requires_remediation = False
        recommended_cell_id = feasible_cells[0]["cell_id"]
        congested_cell_id = None

    execute_write(
        "UPDATE tmf622_sales_orders SET order_status = ? WHERE order_id = ?",
        (feasibility_status, order_id),
        db_path=db_path,
    )

    mrr_dec = Decimal(str(order["estimated_mrr_usd"]))
    arr_dec = round_money(mrr_dec * Decimal("12"))
    penalty_hr_dec = (
        round_money(Decimal(str(contract["sla_penalty_per_hour_usd"])))
        if contract
        else Decimal("0.00")
    )

    return {
        "order_id": order["order_id"],
        "contract_id": order["contract_id"],
        "enterprise_name": order["enterprise_name"],
        "account_tier": order["account_tier"],
        "target_tac": order["target_tac"],
        "requested_slice_sst": int(order["requested_slice_sst"]),
        "requested_qos_5qi": int(order["requested_qos_5qi"]),
        "requested_bandwidth_mbps": req_bw,
        "max_latency_ms": max_lat,
        "estimated_mrr_usd": float(round_money(mrr_dec)),
        "protected_annual_revenue_usd": float(arr_dec),
        "avoided_sla_penalty_per_hour_usd": float(penalty_hr_dec),
        "feasibility_status": feasibility_status,
        "requires_remediation": requires_remediation,
        "congested_cell_id": congested_cell_id,
        "recommended_cell_id": recommended_cell_id,
        "candidate_cells_count": len(candidate_cells),
        "feasible_cells_count": len(feasible_cells),
    }


def remediate_slice_for_order(
    order_id: str,
    steering_mode: str = "NEIGHBOR_OFFLOAD_AND_PRB_REALLOC",
    db_path: Path | None = None,
) -> dict[str, Any]:
    check = evaluate_order_feasibility(order_id, db_path=db_path)
    if check["feasibility_status"] == "REJECTED":
        raise ValueError(
            f"Order {order_id} cannot be remediated via traffic steering: "
            "requested bandwidth/latency exceeds physical RAN slice capacity in target TAC."
        )

    contract = fetch_one(
        "SELECT * FROM b2b_contracts WHERE contract_id = ?",
        (check["contract_id"],),
        db_path=db_path,
    )

    congested_cell_id = check["congested_cell_id"]
    recommended_cell_id = check["recommended_cell_id"]

    if congested_cell_id:
        remediated_latency = round(float(check["max_latency_ms"]) * 0.75, 2)
        execute_write(
            """
            UPDATE ran_telemetry
            SET prb_utilization_pct = 64.0,
                pdcp_latency_ms = ?,
                availability_pct = 99.995,
                status = 'HEALTHY'
            WHERE cell_id = ?
            """,
            (remediated_latency, congested_cell_id),
            db_path=db_path,
        )

    execute_write(
        """
        UPDATE tmf622_sales_orders
        SET order_status = 'READY_TO_ACTIVATE',
            sales_stage = 'PROVISIONED'
        WHERE order_id = ?
        """,
        (order_id,),
        db_path=db_path,
    )

    mrr_dec = Decimal(str(check["estimated_mrr_usd"]))
    arr_dec = round_money(mrr_dec * Decimal("12"))
    if contract:
        penalty_hr = Decimal(str(contract["sla_penalty_per_hour_usd"]))
        breach_hrs = Decimal(str(contract["breach_hours_mtd"]))
        avoided_penalty_dec = round_money(penalty_hr * breach_hrs)
    else:
        avoided_penalty_dec = Decimal("0.00")

    total_value_dec = round_money(arr_dec + avoided_penalty_dec)

    return {
        "order_id": order_id,
        "contract_id": check["contract_id"],
        "enterprise_name": check["enterprise_name"],
        "target_tac": check["target_tac"],
        "requested_slice_sst": check["requested_slice_sst"],
        "steering_mode": steering_mode,
        "previous_status": check["feasibility_status"],
        "new_order_status": "READY_TO_ACTIVATE",
        "sales_stage": "PROVISIONED",
        "remediated_congested_cell_id": congested_cell_id,
        "target_serving_cell_id": recommended_cell_id,
        "protected_mrr_usd": float(round_money(mrr_dec)),
        "protected_annual_revenue_usd": float(arr_dec),
        "avoided_sla_penalty_usd": float(avoided_penalty_dec),
        "total_commercial_value_preserved_usd": float(total_value_dec),
    }
