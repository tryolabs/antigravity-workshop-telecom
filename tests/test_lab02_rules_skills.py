"""
Lab 2 Verification Tests: Antigravity Workspace Rules (`GEMINI.md`, `.agents/rules/`)
and Custom Skills (`.agents/skills/sla-revenue-audit/SKILL.md`).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_gemini_md_exists_and_defines_telecom_architecture() -> None:
    gemini_path = PROJECT_ROOT / "GEMINI.md"
    assert gemini_path.exists(), "GEMINI.md must exist at the repository root."
    content = gemini_path.read_text(encoding="utf-8")
    assert len(content) > 200, "GEMINI.md is too short."
    assert "Decimal" in content, "GEMINI.md must mandate Python Decimal for financial calculations."
    assert "3GPP" in content or "s_nssai_sst" in content, "GEMINI.md must reference 3GPP slice context."


def test_telecom_standards_rule_exists_in_agents_rules() -> None:
    rule_path = PROJECT_ROOT / ".agents" / "rules" / "telecom-standards.md"
    assert rule_path.exists(), ".agents/rules/telecom-standards.md must exist."
    content = rule_path.read_text(encoding="utf-8")
    for keyword in ("3GPP", "TAP3", "TMF622", "Decimal"):
        assert keyword in content, f"Expected '{keyword}' in .agents/rules/telecom-standards.md"


def test_sla_revenue_audit_skill_has_valid_yaml_frontmatter() -> None:
    skill_path = PROJECT_ROOT / ".agents" / "skills" / "sla-revenue-audit" / "SKILL.md"
    assert skill_path.exists(), ".agents/skills/sla-revenue-audit/SKILL.md must exist."
    content = skill_path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), "SKILL.md must begin with YAML frontmatter '---'."
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have closing '---' for YAML frontmatter."
    frontmatter = parts[1]
    assert "name: sla-revenue-audit" in frontmatter, "Frontmatter must declare 'name: sla-revenue-audit'."
    assert "description:" in frontmatter, "Frontmatter must include 'description:'."
    assert "run_sla_audit.py" in content, "SKILL.md must reference scripts/run_sla_audit.py."


def test_run_sla_audit_script_generates_executive_reports() -> None:
    script_path = PROJECT_ROOT / "scripts" / "run_sla_audit.py"
    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Report generated successfully" in res.stdout

    json_report_path = PROJECT_ROOT / "data" / "exports" / "sla_revenue_audit_report.json"
    md_report_path = PROJECT_ROOT / "data" / "exports" / "sla_revenue_audit_report.md"
    assert json_report_path.exists()
    assert md_report_path.exists()

    report = json.loads(json_report_path.read_text(encoding="utf-8"))
    assert report["total_sla_penalty_exposure_usd"] == 224500.0
    assert report["total_cdr_leakage_usd"] > 45000.0
    assert len(report["contract_risk_matrix"]) == 10
