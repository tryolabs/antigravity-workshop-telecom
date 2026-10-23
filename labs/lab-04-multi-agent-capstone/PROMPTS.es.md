<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Prompts de Antigravity del Laboratorio 04: Multi-Agente ADK, Protocolo A2A, ADK Dev UI y Gemini Enterprise

[English](PROMPTS.md) | **Español** | [Guía del Laboratorio 04](README.es.md)

---

## Prompt 1: Implementar Factibilidad de Órdenes TMF622 y Remediación Autónoma de Slices 5G

> Copie y pegue este prompt en Google Antigravity (también puede anteponer `/plan` para planificación arquitectónica paso a paso):

```text
Inspecciona `src/services/order_feasibility.py`, `src/models.py` y `tests/test_lab04_capstone.py`.

Implementa `evaluate_order_feasibility(order_id)` y `remediate_slice_for_order(order_id, steering_mode)` en `src/services/order_feasibility.py` siguiendo todas las reglas de `GEMINI.md` y `.agents/rules/telecom-standards.md`:

1. En `evaluate_order_feasibility(order_id)`:
   - Consulta `sales_orders` por `order_id` (lanza `ValueError` si no existe).
   - Consulta `ran_telemetry` para las celdas que coincidan con `tac = target_tac` y `s_nssai_sst = requested_slice_sst`.
   - Una celda es factible si `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms` y `available_bandwidth_mbps >= requested_bandwidth_mbps`.
   - Si una celda congestionada (`prb_utilization_pct >= 80.0` o `pdcp_latency_ms > max_latency_ms`) tiene una celda vecina factible en `neighbor_cells`, devuelve `feasibility_status = "REQUIRES_SLICE_REMEDIATION"`, `requires_remediation = True`, `congested_cell_id` y `recommended_cell_id` (la celda vecina).
   - De lo contrario, si existe una celda factible sin congestión, devuelve `feasibility_status = "READY_TO_ACTIVATE"`, `requires_remediation = False` y `recommended_cell_id`.
   - Si ninguna celda puede satisfacer los requisitos de ancho de banda/latencia, devuelve `feasibility_status = "REJECTED"`.
   - Calcula `protected_annual_revenue_usd` como `monthly_recurring_revenue_usd * 12` usando `Decimal`.

2. En `remediate_slice_for_order(order_id, steering_mode)`:
   - Verifica que la orden esté actualmente en estado `REQUIRES_SLICE_REMEDIATION` (de lo contrario lanza `ValueError`).
   - Descarga tráfico de la celda congestionada hacia la celda vecina objetivo en `ran_telemetry` (reduciendo `prb_utilization_pct` de la celda congestionada a `58.5%`, reduciendo su `pdcp_latency_ms` y actualizando `sales_orders.status = 'READY_TO_ACTIVATE'` y `sales_stage = 'PROVISIONED'`).
   - Devuelve el resumen de remediación incluyendo `protected_annual_revenue_usd` (`MRR * 12`), `avoided_sla_penalty_usd` (`MRR * 2`) y `total_commercial_value_preserved_usd` (`MRR * 14`).
```

---

## Prompt 2: Diseñar el Sistema Multi-Agente Google ADK y los Endpoints del Protocolo A2A

> Copie y pegue este prompt en Google Antigravity (o use `/teamwork` para coordinar el diseño de los agentes OSS y BSS):

```text
Inspecciona `src/agents/adk_a2a_orchestrator.py`, `adk_agents/telecom_nexus/agent.py`, `src/main.py` y `tests/test_lab04_capstone.py`.

Completa `src/agents/adk_a2a_orchestrator.py` para implementar nuestro Sistema Multi-Agente con Google ADK y el servidor del Protocolo A2A (Agent2Agent):

1. `RANSliceCapacityAgent`:
   - Implementa `assess_order_ran_slice(order_id, auto_remediate=False)` usando `evaluate_order_feasibility` y (cuando `auto_remediate=True` y el estado sea `REQUIRES_SLICE_REMEDIATION`) `remediate_slice_for_order`.
   - Devuelve `agent_name = "ran_slice_capacity_agent"`, `initial_feasibility_status`, `final_feasibility_status`, `target_tac`, `recommended_cell_id` y `auto_remediation_executed`.

2. `BSSCommercialSLAAgent`:
   - Implementa `assess_commercial_impact(order_id, oss_result)` consultando `sales_orders`, `evaluate_contract_sla_compliance()` y `audit_cdr_revenue_leakage()`.
   - Calcula `annual_contract_value_usd` (`MRR * 12`) y `avoided_sla_penalty_risk_usd` (`MRR * 2`) con `Decimal`.
   - Asigna `final_feasibility_status` a `commercial_decision`:
     - `READY_TO_ACTIVATE` -> `APPROVE_IMMEDIATELY`
     - `REQUIRES_SLICE_REMEDIATION` -> `APPROVE_WITH_AUTOMATED_RAN_STEERING`
     - `REJECTED` -> `HOLD_REQUIRES_RAN_CAPACITY_CAPEX`

3. `TelecomNexusOrchestratorAgent`:
   - Coordina `RANSliceCapacityAgent` (Paso 1) y `BSSCommercialSLAAgent` (Paso 2) usando Google ADK (jerarquía `SequentialAgent` / `LlmAgent` de `google-adk` con ejecución local determinista).
   - Devuelve `orchestrator_name`, `adk_architecture`, `oss_technical_assessment`, `bss_commercial_assessment`, `executive_decision` y `agent_trace`.

4. Integración del Protocolo A2A:
   - Implementa `get_a2a_agent_card(base_url)` devolviendo la Agent Card para `TelecomNexus-OSS-BSS-Orchestrator` con las habilidades (`skills`) `tmf622_order_feasibility`, `autonomous_slice_remediation` y `sla_revenue_assurance`.
   - Implementa `handle_a2a_jsonrpc_request(payload)` soportando JSON-RPC 2.0 `"tasks/send"` y `"message/send"`, extrayendo `order_id` y `auto_remediate` de las partes del mensaje A2A y devolviendo una Tarea A2A completada con `status.state = "completed"` y `artifacts`.

Finalmente, ejecuta `./.venv/bin/pytest tests/test_lab04_capstone.py -v` y `./scripts/run_adk_web.sh --check` para verificar que todas las pruebas pasen.
```

---

## Prompt 3: Probar con ADK Web UI (`adk web`) y Validar el Despliegue en Terraform + Gemini Enterprise

```text
1. Valida el paquete de agentes para ADK Web UI (`adk_agents/telecom_nexus/agent.py`) y la configuración de Discovery Engine para Gemini Enterprise ejecutando:
   ./scripts/run_adk_web.sh --check

2. Valida nuestro Dockerfile, la infraestructura de Terraform (`infra/terraform/`) y el payload de registro del agente A2A en Gemini Enterprise (`deploy/register_gemini_enterprise_agent.sh`) en modo dry-run local:
   ./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run

3. Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` para confirmar que las 21 pruebas de los Laboratorios 01, 02, 03 y 04 pasan al 100%.
```
