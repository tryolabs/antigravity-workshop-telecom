"""
CDR Rating & Revenue Assurance Engine (3GPP TS 32.298 / GSMA TAP3.12).

Domain Rules:
1. Total billable volume in Gigabytes (GiB) = (uplink_bytes + downlink_bytes) / (1024 ** 3).
2. Base charge = volume_gb * base_rate_per_gb_usd.
3. Roaming Markup: Home PLMN is '310-410'. Any visiting/roaming PLMN (roaming_plmn != '310-410')
   across ANY radio access technology (both 'NR_5G' and 'EUTRAN_4G') must apply:
   multiplier = 1.0 + (roaming_markup_pct / 100.0).
4. All monetary outputs must use Python Decimal quantized to 0.01 with ROUND_HALF_UP.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import fetch_all

HOME_PLMN = "310-410"
BYTES_PER_GB = Decimal(1024 ** 3)


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rate_cdr_record(cdr: dict[str, Any]) -> Decimal:
    """
    Calculates the expected rated charge (USD) for a single 3GPP/TAP3 CDR dictionary.
    """
    total_bytes = Decimal(int(cdr["uplink_bytes"]) + int(cdr["downlink_bytes"]))
    volume_gb = total_bytes / BYTES_PER_GB

    base_rate = Decimal(str(cdr["base_rate_per_gb_usd"]))
    markup_pct = Decimal(str(cdr["roaming_markup_pct"]))
    roaming_plmn = str(cdr["roaming_plmn"])

    if roaming_plmn != HOME_PLMN:
        multiplier = Decimal("1.0") + (markup_pct / Decimal("100.0"))
    else:
        multiplier = Decimal("1.0")

    rated_charge = volume_gb * base_rate * multiplier
    return round_money(rated_charge)


def audit_cdr_revenue_leakage(db_path: Path | None = None) -> dict[str, Any]:
    """
    Audits all CDR records in SQLite against the rating engine and quantifies
    unbilled revenue leakage by B2B contract and RAT type.
    """
    cdrs = fetch_all("SELECT * FROM cdr_records ORDER BY cdr_id", db_path=db_path)

    total_billed = Decimal("0.00")
    total_recalculated = Decimal("0.00")
    total_leakage = Decimal("0.00")
    underbilled_records: list[dict[str, Any]] = []
    leakage_by_contract: dict[str, Decimal] = {}

    for cdr in cdrs:
        billed = round_money(Decimal(str(cdr["billed_amount_usd"])))
        recalculated = rate_cdr_record(cdr)
        total_billed += billed
        total_recalculated += recalculated

        delta = round_money(recalculated - billed)
        if delta > Decimal("0.01"):
            total_leakage += delta
            cid = cdr["contract_id"]
            leakage_by_contract[cid] = round_money(
                leakage_by_contract.get(cid, Decimal("0.00")) + delta
            )
            underbilled_records.append(
                {
                    "cdr_id": cdr["cdr_id"],
                    "contract_id": cid,
                    "imsi": cdr["imsi"],
                    "rat_type": cdr["rat_type"],
                    "roaming_plmn": cdr["roaming_plmn"],
                    "billed_amount_usd": float(billed),
                    "expected_amount_usd": float(recalculated),
                    "leakage_usd": float(delta),
                }
            )

    return {
        "total_cdrs_audited": len(cdrs),
        "underbilled_cdr_count": len(underbilled_records),
        "total_billed_usd": float(round_money(total_billed)),
        "total_expected_usd": float(round_money(total_recalculated)),
        "total_leakage_usd": float(round_money(total_leakage)),
        "leakage_by_contract": {k: float(v) for k, v in sorted(leakage_by_contract.items())},
        "sample_underbilled_cdrs": underbilled_records[:15],
    }
