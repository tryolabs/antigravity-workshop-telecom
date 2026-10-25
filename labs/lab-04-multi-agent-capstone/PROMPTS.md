<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 04 Antigravity Prompts: Multi-Agent ADK, A2A Protocol, ADK Dev UI & Gemini Enterprise

> **Language / Idioma:** [English](./PROMPTS.md) | [Español](./PROMPTS.es.md) • **Lab Guide:** [README.md](./README.md) | [README.es.md](./README.es.md) • **PDF:** [EN](./LAB_04_INSTRUCTIONS_EN.pdf) | [ES](./LAB_04_INSTRUCTIONS_ES.pdf)

---

## Prompt 1: Implement TMF622 Order Feasibility & Autonomous 5G Slice Remediation

> Copy and paste this prompt into Google Antigravity (you can also prefix with `/plan` for step-by-step architectural planning):

```text
Inspect `src/services/order_feasibility.py`, `src/models.py`, and `tests/test_lab04_capstone.py`.

Implement `evaluate_order_feasibility(order_id)` and `remediate_slice_for_order(order_id, steering_mode)` in `src/services/order_feasibility.py` following all rules in `GEMINI.md` and `.agents/rules/telecom-standards.md`:

1. In `evaluate_order_feasibility(order_id)`:
   - Query `sales_orders` by `order_id` (raise `ValueError` if not found).
   - Query `ran_telemetry` for cells matching `tac = target_tac` and `s_nssai_sst = requested_slice_sst`.
   - A cell is feasible if `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms`, and `available_bandwidth_mbps >= requested_bandwidth_mbps`.
   - If a congested cell (`prb_utilization_pct >= 80.0` or `pdcp_latency_ms > max_latency_ms`) has a feasible neighbor cell in `neighbor_cells`, return `feasibility_status = "REQUIRES_SLICE_REMEDIATION"`, `requires_remediation = True`, `congested_cell_id`, and `recommended_cell_id` (the neighbor cell).
   - Otherwise, if a feasible cell exists without congestion, return `feasibility_status = "READY_TO_ACTIVATE"`, `requires_remediation = False`, and `recommended_cell_id`.
   - If no cell can satisfy the bandwidth/latency requirements, return `feasibility_status = "REJECTED"`.
   - Compute `protected_annual_revenue_usd` as `monthly_recurring_revenue_usd * 12` using `Decimal`.

2. In `remediate_slice_for_order(order_id, steering_mode)`:
   - Verify the order is currently `REQUIRES_SLICE_REMEDIATION` (otherwise raise `ValueError`).
   - Offload traffic from the congested cell to the target neighbor cell in `ran_telemetry` (reducing the congested cell's `prb_utilization_pct` to `58.5%`, reducing its `pdcp_latency_ms`, and updating `sales_orders.status = 'READY_TO_ACTIVATE'` and `sales_stage = 'PROVISIONED'`).
   - Return the remediation summary including `protected_annual_revenue_usd` (`MRR * 12`), `avoided_sla_penalty_usd` (`MRR * 2`), and `total_commercial_value_preserved_usd` (`MRR * 14`).
```

---

## Prompt 2: Design the Google ADK Multi-Agent System & A2A Protocol Endpoints

> Copy and paste this prompt into Google Antigravity (or use `/teamwork` to coordinate OSS and BSS agent design):

```text
Inspect `src/agents/adk_a2a_orchestrator.py`, `adk_agents/telecom_nexus/agent.py`, `src/main.py`, and `tests/test_lab04_capstone.py`.

Complete `src/agents/adk_a2a_orchestrator.py` to implement our Google ADK Multi-Agent System and A2A (Agent2Agent) Protocol server:

1. `RANSliceCapacityAgent`:
   - Implement `assess_order_ran_slice(order_id, auto_remediate=False)` using `evaluate_order_feasibility` and (when `auto_remediate=True` and status is `REQUIRES_SLICE_REMEDIATION`) `remediate_slice_for_order`.
   - Return `agent_name = "ran_slice_capacity_agent"`, `initial_feasibility_status`, `final_feasibility_status`, `target_tac`, `recommended_cell_id`, and `auto_remediation_executed`.

2. `BSSCommercialSLAAgent`:
   - Implement `assess_commercial_impact(order_id, oss_result)` querying `sales_orders`, `evaluate_contract_sla_compliance()`, and `audit_cdr_revenue_leakage()`.
   - Calculate `annual_contract_value_usd` (`MRR * 12`) and `avoided_sla_penalty_risk_usd` (`MRR * 2`) with `Decimal`.
   - Map `final_feasibility_status` to `commercial_decision`:
     - `READY_TO_ACTIVATE` -> `APPROVE_IMMEDIATELY`
     - `REQUIRES_SLICE_REMEDIATION` -> `APPROVE_WITH_AUTOMATED_RAN_STEERING`
     - `REJECTED` -> `HOLD_REQUIRES_RAN_CAPACITY_CAPEX`

3. `TelecomNexusOrchestratorAgent`:
   - Coordinate `RANSliceCapacityAgent` (Step 1) and `BSSCommercialSLAAgent` (Step 2) using Google ADK (`google-adk` `SequentialAgent` / `LlmAgent` hierarchy with deterministic local execution).
   - Return `orchestrator_name`, `adk_architecture`, `oss_technical_assessment`, `bss_commercial_assessment`, `executive_decision`, and `agent_trace`.

4. A2A Protocol Integration:
   - Implement `get_a2a_agent_card(base_url)` returning the Agent Card for `TelecomNexus-OSS-BSS-Orchestrator` with skills `tmf622_order_feasibility`, `autonomous_slice_remediation`, and `sla_revenue_assurance`.
   - Implement `handle_a2a_jsonrpc_request(payload)` supporting JSON-RPC 2.0 `"tasks/send"` and `"message/send"`, extracting `order_id` and `auto_remediate` from the A2A message parts, and returning a completed A2A Task with `status.state = "completed"` and `artifacts`.

Finally, run `./.venv/bin/pytest tests/test_lab04_capstone.py -v` and `./scripts/run_adk_web.sh --check` to verify all tests pass!
```

---

## Prompt 3: Test with ADK Web UI (`adk web`) & Validate Terraform + Gemini Enterprise Deployment

```text
1. Validate our ADK Web UI agent package (`adk_agents/telecom_nexus/agent.py`) and Gemini Enterprise Discovery Engine configuration by running:
   ./scripts/run_adk_web.sh --check

2. Validate our Dockerfile, Terraform infrastructure (`infra/terraform/`), and Gemini Enterprise A2A agent registration payload (`deploy/register_gemini_enterprise_agent.sh`) in local dry-run mode:
   ./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run

3. Run `./labs/lab-04-multi-agent-capstone/verify.sh` to confirm all 21 tests across Labs 01, 02, 03, and 04 pass 100%!
```
