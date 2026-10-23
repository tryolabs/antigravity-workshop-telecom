"""
FastAPI Application for Telecom Nexus:
5G Network Slice SLA, CDR Revenue Assurance & B2B Contract Intelligence Platform.
Run locally via:
    uvicorn src.main:app --reload --port 8001
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.agents.adk_a2a_orchestrator import (
    get_a2a_agent_card,
    handle_a2a_jsonrpc_request,
)
from src.database import fetch_all
from src.models import FeasibilityCheckRequest, SliceRemediateRequest
from src.services.cdr_rating import audit_cdr_revenue_leakage
from src.services.contract_auditor import (
    generate_executive_audit_report,
    load_active_ran_alarms,
)
from src.services.order_feasibility import (
    evaluate_order_feasibility,
    list_sales_orders,
    remediate_slice_for_order,
)
from src.services.sla_monitor import evaluate_contract_sla_compliance

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Telecom Nexus — 5G OSS/BSS & Commercial SLA Intelligence API",
    description=(
        "Google Antigravity Telecom Workshop: Combines 3GPP 5G RAN Telemetry, "
        "GSMA TAP3 CDR Revenue Assurance, Enterprise B2B SLA Contracts, and TMF622 Order Feasibility."
    ),
    version="2.0.0",
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_dashboard() -> Any:
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Telecom Nexus API is running.</h1>")


@app.get("/api/v1/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "telecom-nexus-oss-bss",
        "version": "2.0.0",
        "standards": ["3GPP TS 28.552", "3GPP TS 32.298", "GSMA TAP3.12", "TMF622"],
    }


@app.get("/api/v1/ran/telemetry")
def get_ran_telemetry(
    tac: str | None = Query(default=None, description="Filter by 5G Tracking Area Code"),
    sst: int | None = Query(default=None, description="Filter by 3GPP Slice/Service Type (1, 2, 3)"),
) -> dict[str, Any]:
    cells = fetch_all("SELECT * FROM ran_telemetry ORDER BY cell_id")
    if tac:
        cells = [c for c in cells if c["tac"] == tac]
    if sst is not None:
        cells = [c for c in cells if int(c["s_nssai_sst"]) == sst]
    return {"count": len(cells), "cells": cells}


@app.get("/api/v1/cdr/audit")
def get_cdr_revenue_audit() -> dict[str, Any]:
    return audit_cdr_revenue_leakage()


@app.get("/api/v1/sla/compliance")
def get_sla_compliance() -> dict[str, Any]:
    return evaluate_contract_sla_compliance()


@app.get("/api/v1/audit/executive-report")
def get_executive_report() -> dict[str, Any]:
    return generate_executive_audit_report()


@app.get("/api/v1/orders")
def get_sales_orders() -> dict[str, Any]:
    orders = list_sales_orders()
    return {"count": len(orders), "orders": orders}


@app.post("/api/v1/orders/feasibility-check")
def check_order_feasibility_endpoint(payload: FeasibilityCheckRequest) -> dict[str, Any]:
    try:
        return evaluate_order_feasibility(payload.order_id)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/slices/remediate")
def remediate_slice_endpoint(payload: SliceRemediateRequest) -> dict[str, Any]:
    try:
        return remediate_slice_for_order(
            order_id=payload.order_id,
            steering_mode=payload.steering_mode,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        msg = str(exc)
        status_code = 404 if "not found" in msg.lower() else 400
        raise HTTPException(status_code=status_code, detail=msg) from exc


@app.get("/api/v1/dashboard/summary")
def get_dashboard_summary() -> dict[str, Any]:
    cdr_audit = audit_cdr_revenue_leakage()
    sla_audit = evaluate_contract_sla_compliance()
    cells = fetch_all("SELECT * FROM ran_telemetry ORDER BY cell_id")
    orders = list_sales_orders()
    alarms = load_active_ran_alarms()
    return {
        "cdr_audit": cdr_audit,
        "sla_audit": sla_audit,
        "ran_cells": cells,
        "sales_orders": orders,
        "alarms": alarms,
    }


@app.get("/.well-known/agent.json")
@app.get("/api/v1/a2a/agent-card")
def serve_a2a_agent_card(request: Request) -> dict[str, Any]:
    base_url = str(request.base_url).rstrip("/")
    try:
        return get_a2a_agent_card(base_url=base_url)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


@app.post("/api/v1/a2a")
@app.post("/api/v1/a2a/tasks/send")
def execute_a2a_task(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return handle_a2a_jsonrpc_request(payload)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

