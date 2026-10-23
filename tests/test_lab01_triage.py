"""
Lab 1 Verification Tests: Revenue Assurance (CDR Rating) & 5G Slice SLA Triage.
"""

from __future__ import annotations

from decimal import Decimal

from data.seed_telecom_data import seed_all
from src.services.cdr_rating import audit_cdr_revenue_leakage, rate_cdr_record
from src.services.sla_monitor import evaluate_contract_sla_compliance


def test_cdr_byte_to_gib_conversion_and_home_rating() -> None:
    """10 GiB on Home PLMN (310-410) at $12.00/GB must equal $120.00."""
    ten_gib_bytes = 10 * (1024 ** 3)
    sample_cdr = {
        "uplink_bytes": ten_gib_bytes // 2,
        "downlink_bytes": ten_gib_bytes - (ten_gib_bytes // 2),
        "base_rate_per_gb_usd": 12.00,
        "roaming_markup_pct": 50.0,
        "roaming_plmn": "310-410",
        "rat_type": "NR_5G",
    }
    rated = rate_cdr_record(sample_cdr)
    assert rated == Decimal("120.00"), f"Expected Decimal('120.00'), got {rated}"


def test_cdr_5g_standalone_roaming_markup_applied() -> None:
    """10 GiB on Visiting PLMN (234-15 Vodafone UK) over NR_5G at $12.00/GB + 50% markup = $180.00."""
    ten_gib_bytes = 10 * (1024 ** 3)
    sample_cdr = {
        "uplink_bytes": ten_gib_bytes // 2,
        "downlink_bytes": ten_gib_bytes - (ten_gib_bytes // 2),
        "base_rate_per_gb_usd": 12.00,
        "roaming_markup_pct": 50.0,
        "roaming_plmn": "234-15",
        "rat_type": "NR_5G",
    }
    rated = rate_cdr_record(sample_cdr)
    assert rated == Decimal("180.00"), (
        f"NR_5G roaming markup was not applied properly! Expected 180.00, got {rated}"
    )


def test_audit_cdr_revenue_leakage_detects_all_anomalies(tmp_path) -> None:
    db_file = tmp_path / "test_telecom.db"
    seed_stats = seed_all(db_file)
    audit = audit_cdr_revenue_leakage(db_path=db_file)

    assert audit["total_cdrs_audited"] == 250
    assert audit["underbilled_cdr_count"] > 90
    assert abs(audit["total_leakage_usd"] - seed_stats["revenue_leakage_usd"]) < 0.05
    assert audit["total_leakage_usd"] > 45000.0


def test_sla_compliance_filters_active_contracts_and_detects_high_latency(tmp_path) -> None:
    db_file = tmp_path / "test_telecom.db"
    seed_all(db_file)
    sla = evaluate_contract_sla_compliance(db_path=db_file)

    # Must evaluate ONLY the 10 ACTIVE contracts (excluding TERMINATED CTR-B2B-1011 & DRAFT CTR-B2B-1012)
    assert sla["evaluated_contracts_count"] == 10, (
        f"Expected 10 ACTIVE contracts evaluated, got {sla['evaluated_contracts_count']}"
    )
    assert sla["breached_contracts_count"] == 5
    assert sla["compliant_contracts_count"] == 5

    breached_ids = {c["contract_id"] for c in sla["breached_contracts"]}
    assert breached_ids == {
        "CTR-B2B-1001",
        "CTR-B2B-1002",
        "CTR-B2B-1004",
        "CTR-B2B-1006",
        "CTR-B2B-1009",
    }
    assert "CTR-B2B-1011" not in breached_ids
    assert "CTR-B2B-1012" not in breached_ids

    # Exact Decimal penalty exposure across the 5 breached active contracts = $224,500.00
    assert sla["total_penalty_exposure_usd"] == 224500.00
