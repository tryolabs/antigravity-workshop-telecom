# Lab 04 — Optimized Antigravity Prompts Cheat Sheet (English)

> **Goal**: Use **Google Antigravity Multi-Agent Orchestration** (`/teamwork`, `/boost`, `/plan`, Subagents, and Auxiliary Pane inspection) to build the **TMF622 B2B Order Feasibility & 5G Network Slice Remediation Engine** in `src/services/order_feasibility.py` and verify it via the FastAPI endpoints (`/api/v1/orders/feasibility-check` and `/api/v1/slices/remediate`).

---

## 1. Discovery & Multi-Agent Context Prompt (`@` Mentions)

```text
@src/services/order_feasibility.py @src/main.py @src/models.py @tests/test_lab04_capstone.py @GEMINI.md @.agents/rules/telecom-standards.md
We need to implement our Capstone TMF622 B2B Sales Order Feasibility & 5G Slice QoS Remediation service in `src/services/order_feasibility.py`.
Inspect the data schema in `data/seed_telecom_data.py` (`tmf622_sales_orders`, `ran_telemetry`, `b2b_contracts`), the API endpoints in `src/main.py`, and the exact test requirements in `tests/test_lab04_capstone.py`.
```

---

## 2. Multi-Agent Teamwork Prompt (`/teamwork`)

Use `/teamwork` to spawn specialized parallel subagents (e.g., an **OSS 3GPP RAN Slice Architect**, a **BSS Commercial TMF622 Engineer**, and a **QA Verification Subagent**):

```text
/teamwork Coordinate a team of subagents to implement and verify the Lab 04 Capstone in `src/services/order_feasibility.py`:
1. Agent 1 (3GPP RAN Slice Feasibility): Implement `evaluate_order_feasibility(order_id, db_path)` checking all candidate cells in `ran_telemetry` for `target_tac` and `requested_slice_sst`. Classify cells as feasible when `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms`, and `available_bandwidth_mbps >= requested_bandwidth_mbps`. Return `READY_TO_ACTIVATE` (all matching cells healthy & feasible), `REQUIRES_SLICE_REMEDIATION` (at least one matching cell congested/breaching latency, but a feasible neighbor cell exists in the same TAC+SST), or `REJECTED` (no feasible cell exists), and update `tmf622_sales_orders.order_status`.
2. Agent 2 (Commercial Remediation & Decimal Impact): Implement `remediate_slice_for_order(order_id, steering_mode, db_path)` which raises `ValueError` if the order is `REJECTED`, updates the congested cell in `ran_telemetry` to `HEALTHY` (`prb_utilization_pct = 64.0`, `pdcp_latency_ms = round(max_latency_ms * 0.75, 2)`, `availability_pct = 99.995`), transitions the order in `tmf622_sales_orders` to `order_status = 'READY_TO_ACTIVATE'` and `sales_stage = 'PROVISIONED'`, and calculates `protected_annual_revenue_usd` (`estimated_mrr_usd * 12`), `avoided_sla_penalty_usd` (`sla_penalty_per_hour_usd * breach_hours_mtd`), and `total_commercial_value_preserved_usd` using `Decimal`.
3. Agent 3 (QA & Full-Stack Verification): Run `./labs/lab-04-multi-agent-capstone/verify.sh` and confirm all 4 lab test suites pass 100%.
```

---

## 3. Deep Strategic Reasoning Prompt (`/boost`)

Alternatively, use `/boost` for deep multi-perspective architectural reasoning and verification:

```text
/boost Design, implement, and rigorously verify `evaluate_order_feasibility` and `remediate_slice_for_order` in @src/services/order_feasibility.py so that `POST /api/v1/orders/feasibility-check` and `POST /api/v1/slices/remediate` satisfy every 3GPP TS 28.552, TMF622, and `Decimal` billing rule in @tests/test_lab04_capstone.py.
```

---

## 4. Instructive Inline Edit Prompt (`Cmd+I` / `Ctrl+I`)

Inside `src/services/order_feasibility.py`, select `evaluate_order_feasibility` and `remediate_slice_for_order` and press `Cmd+I` / `Ctrl+I`:

```text
Implement `evaluate_order_feasibility` and `remediate_slice_for_order` using `fetch_one`, `fetch_all`, and `execute_write` from `src.database` and `Decimal` (`ROUND_HALF_UP`) so all tests in `tests/test_lab04_capstone.py` pass.
```

---

## 5. Live NOC Dashboard & Browser Automation Prompt (`/browser`)

Once `./labs/lab-04-multi-agent-capstone/verify.sh` passes:

```text
/browser Start the Telecom Nexus FastAPI server on port 8001, open `http://localhost:8001`, click "Check Feasibility" and "Remediate Slice" on `ORD-TMF622-9001` (Goldman Sachs Low-Latency Trading Backup), and confirm the order transitions to `READY_TO_ACTIVATE` and preserves $600,000.00 in total commercial value ($504,000.00 ARR + $96,000.00 avoided SLA penalty).
```

---

## 6. Long-Running Autonomous Goal Prompt (`/goal`)

```text
/goal Evaluate feasibility across all 15 TMF622 B2B sales orders in `telecom_nexus.db`, automatically remediate every order with status `REQUIRES_SLICE_REMEDIATION`, re-run the executive SLA & revenue audit (`scripts/run_sla_audit.py`), and do not stop until all 5 congested 5G RAN cells are restored to `HEALTHY` and all 4 pytest suites pass.
```
