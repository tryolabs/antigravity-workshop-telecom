"""
Lab 3 Verification Tests: FastMCP Telecom Server (`mcp_server/telecom_mcp.py`),
MCP Configuration (`.agents/mcp_config.json`), and Lifecycle Hooks (`.agents/hooks.json`).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from mcp_server.telecom_mcp import (
    calculate_contract_penalty_exposure,
    evaluate_slice_capacity,
    inspect_unbilled_cdrs,
    query_ran_cell_health,
)


def test_mcp_config_json_is_valid() -> None:
    mcp_cfg_path = PROJECT_ROOT / ".agents" / "mcp_config.json"
    assert mcp_cfg_path.exists(), ".agents/mcp_config.json must exist."
    data = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
    assert "mcpServers" in data, "mcp_config.json must contain 'mcpServers' root key."
    assert "telecom-nexus-mcp" in data["mcpServers"], "mcpServers must register 'telecom-nexus-mcp'."
    server_cfg = data["mcpServers"]["telecom-nexus-mcp"]
    assert "command" in server_cfg
    assert "args" in server_cfg
    assert any("telecom_mcp.py" in a for a in server_cfg["args"])


def test_hooks_json_and_audit_hook_script() -> None:
    hooks_path = PROJECT_ROOT / ".agents" / "hooks.json"
    assert hooks_path.exists(), ".agents/hooks.json must exist."
    hooks_data = json.loads(hooks_path.read_text(encoding="utf-8"))
    assert len(hooks_data) >= 1

    # Verify audit_hook.py blocks destructive SQL commands on PreToolUse
    hook_script = PROJECT_ROOT / "scripts" / "audit_hook.py"
    bad_payload = json.dumps(
        {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "sqlite3 data/telecom_nexus.db 'DROP TABLE b2b_contracts;'"},
            },
            "stepIdx": 3,
        }
    )
    proc_deny = subprocess.run(
        [sys.executable, str(hook_script), "--event", "PreToolUse"],
        input=bad_payload,
        capture_output=True,
        text=True,
        check=True,
    )
    out_deny = json.loads(proc_deny.stdout)
    assert out_deny["decision"] == "deny"

    # Verify audit_hook.py allows safe commands
    safe_payload = json.dumps(
        {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "pytest tests/test_lab01_triage.py"},
            },
            "stepIdx": 4,
        }
    )
    proc_allow = subprocess.run(
        [sys.executable, str(hook_script), "--event", "PreToolUse"],
        input=safe_payload,
        capture_output=True,
        text=True,
        check=True,
    )
    out_allow = json.loads(proc_allow.stdout)
    assert out_allow["decision"] == "allow"


def test_mcp_tools_execute_accurately_against_sqlite() -> None:
    ran = query_ran_cell_health(tac="TAC-NY-001", s_nssai_sst=2)
    assert ran["matched_cells_count"] == 2
    assert "CELL-NY-001-B" in ran["congested_cell_ids"]

    penalty = calculate_contract_penalty_exposure(contract_id="CTR-B2B-1002")
    assert penalty["matched_count"] == 1
    assert penalty["total_penalty_exposure_usd"] == 96000.0

    cdrs = inspect_unbilled_cdrs(roaming_only=True)
    assert cdrs["underbilled_cdr_count"] > 40
    assert cdrs["total_leakage_usd"] > 15000.0
    sample = cdrs["underbilled_records"][0]
    assert "***" in sample["masked_imsi"]
    assert "***" in sample["masked_msisdn"]

    cap = evaluate_slice_capacity(
        target_tac="TAC-NY-001",
        requested_slice_sst=2,
        requested_bandwidth_mbps=150,
        max_latency_ms=5.0,
    )
    assert cap["feasibility_status"] == "REQUIRES_SLICE_REMEDIATION"
    assert cap["recommended_cell_id"] == "CELL-NY-001-C"
