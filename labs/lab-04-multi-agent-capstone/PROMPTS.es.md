# Lab 04 — Guía de Prompts Optimizados para Antigravity (Español)

> **Objetivo**: Utilizar la **Orquestación Multi-Agente de Google Antigravity** (`/teamwork`, `/boost`, `/plan`, Subagentes e inspección del Panel Auxiliar) para construir el **Motor de Factibilidad de Órdenes B2B TMF622 y Remediación de QoS en Slices 5G** en `src/services/order_feasibility.py` y verificarlo mediante los endpoints FastAPI (`/api/v1/orders/feasibility-check` y `/api/v1/slices/remediate`).

---

## 1. Prompt de Descubrimiento y Contexto (`@` Mentions)

```text
@src/services/order_feasibility.py @src/main.py @src/models.py @tests/test_lab04_capstone.py @GEMINI.md @.agents/rules/telecom-standards.md
Necesitamos implementar nuestro servicio Capstone de Factibilidad de Órdenes de Venta B2B TMF622 y Remediación de QoS en Slices 5G en `src/services/order_feasibility.py`.
Inspecciona el esquema de datos en `data/seed_telecom_data.py` (`tmf622_sales_orders`, `ran_telemetry`, `b2b_contracts`), los endpoints en `src/main.py` y los requisitos exactos de prueba en `tests/test_lab04_capstone.py`.
```

---

## 2. Prompt de Orquestación Multi-Agente (`/teamwork`)

Usa `/teamwork` para lanzar subagentes especializados en paralelo (un **Arquitecto 3GPP RAN Slice**, un **Ingeniero Comercial BSS TMF622** y un **Subagente de Verificación QA**):

```text
/teamwork Coordina un equipo de subagentes para implementar y verificar el Capstone del Lab 04 en `src/services/order_feasibility.py`:
1. Agente 1 (Factibilidad 3GPP RAN Slice): Implementa `evaluate_order_feasibility(order_id, db_path)` evaluando las celdas candidatas en `ran_telemetry` para `target_tac` y `requested_slice_sst`. Clasifica una celda como factible cuando `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms` y `available_bandwidth_mbps >= requested_bandwidth_mbps`. Retorna `READY_TO_ACTIVATE` (todas las celdas del slice saludables y factibles), `REQUIRES_SLICE_REMEDIATION` (al menos una celda congestionada o incumpliendo latencia, pero existe una celda vecina factible en el mismo TAC+SST) o `REJECTED` (ninguna celda cumple), actualizando `tmf622_sales_orders.order_status`.
2. Agente 2 (Remediación Comercial e Impacto Decimal): Implementa `remediate_slice_for_order(order_id, steering_mode, db_path)` que lance `ValueError` si la orden es `REJECTED`, actualice la celda congestionada en `ran_telemetry` a `HEALTHY` (`prb_utilization_pct = 64.0`, `pdcp_latency_ms = round(max_latency_ms * 0.75, 2)`, `availability_pct = 99.995`), actualice la orden en `tmf622_sales_orders` a `order_status = 'READY_TO_ACTIVATE'` y `sales_stage = 'PROVISIONED'`, y calcule `protected_annual_revenue_usd` (`estimated_mrr_usd * 12`), `avoided_sla_penalty_usd` (`sla_penalty_per_hour_usd * breach_hours_mtd`) y `total_commercial_value_preserved_usd` usando `Decimal`.
3. Agente 3 (Verificación QA Integral): Ejecuta `./labs/lab-04-multi-agent-capstone/verify.sh` y confirma que las 4 suites de pruebas pasen al 100%.
```

---

## 3. Prompt de Razonamiento Estratégico Profundo (`/boost`)

Alternativamente, usa `/boost` para razonamiento profundo multi-perspectiva:

```text
/boost Diseña, implementa y verifica rigurosamente `evaluate_order_feasibility` y `remediate_slice_for_order` en @src/services/order_feasibility.py para que `POST /api/v1/orders/feasibility-check` y `POST /api/v1/slices/remediate` cumplan todas las reglas 3GPP TS 28.552, TMF622 y `Decimal` en @tests/test_lab04_capstone.py.
```

---

## 4. Prompt de Edición Inline (`Cmd+I` / `Ctrl+I`)

Dentro de `src/services/order_feasibility.py`, selecciona `evaluate_order_feasibility` y `remediate_slice_for_order` y presiona `Cmd+I` / `Ctrl+I`:

```text
Implementa `evaluate_order_feasibility` y `remediate_slice_for_order` usando `fetch_one`, `fetch_all` y `execute_write` de `src.database` y `Decimal` (`ROUND_HALF_UP`) para que pasen todas las pruebas en `tests/test_lab04_capstone.py`.
```

---

## 5. Prompt de Automatización de Navegador en el Dashboard NOC (`/browser`)

Una vez que `./labs/lab-04-multi-agent-capstone/verify.sh` pase:

```text
/browser Inicia el servidor FastAPI de Telecom Nexus en el puerto 8001, abre `http://localhost:8001`, haz clic en "Check Feasibility" y "Remediate Slice" en la orden `ORD-TMF622-9001` (Goldman Sachs Low-Latency Trading Backup), y confirma que la orden pase a `READY_TO_ACTIVATE` preservando $600,000.00 en valor comercial total ($504,000.00 ARR + $96,000.00 en penalidades SLA evitadas).
```

---

## 6. Prompt de Ejecución Autónoma Prolongada (`/goal`)

```text
/goal Evalúa la factibilidad de las 15 órdenes de venta B2B TMF622 en `telecom_nexus.db`, remedia automáticamente cada orden con estado `REQUIRES_SLICE_REMEDIATION`, vuelve a ejecutar la auditoría ejecutiva (`scripts/run_sla_audit.py`) y no te detengas hasta que las 5 celdas 5G RAN congestionadas queden en estado `HEALTHY` y las 4 suites de pytest pasen.
```
