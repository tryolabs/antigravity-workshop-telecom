"""
Lab 4 Capstone Verification Tests:
TMF622 B2B Sales Order Feasibility & 5G Network Slice QoS Remediation API (`src/services/order_feasibility.py` & `src/main.py`).
"""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from data.seed_telecom_data import seed_all
from src.main import app


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
