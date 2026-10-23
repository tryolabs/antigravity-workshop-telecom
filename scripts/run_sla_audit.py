#!/usr/bin/env python3
"""
CLI Helper for Lab 2 Skill (`sla-revenue-audit`).
Generates both JSON and Markdown executive audit reports in `data/exports/`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.contract_auditor import (
    format_executive_audit_markdown,
    generate_executive_audit_report,
)


def main() -> int:
    exports_dir = PROJECT_ROOT / "data" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    report = generate_executive_audit_report()
    md_content = format_executive_audit_markdown(report)

    json_path = exports_dir / "sla_revenue_audit_report.json"
    md_path = exports_dir / "sla_revenue_audit_report.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(md_content, encoding="utf-8")

    print(f"[SLA & Revenue Audit] Report generated successfully:")
    print(f"  - JSON:     {json_path}")
    print(f"  - Markdown: {md_path}")
    print(f"  - Total CDR Revenue Leakage:     ${report['total_cdr_leakage_usd']:,.2f}")
    print(f"  - Total SLA Penalty Exposure:    ${report['total_sla_penalty_exposure_usd']:,.2f}")
    print(f"  - Combined Commercial Risk:      ${report['total_combined_commercial_risk_usd']:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
