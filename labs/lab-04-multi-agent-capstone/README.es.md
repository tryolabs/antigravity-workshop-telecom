# Lab 04: Capstone Multi-Agente — Factibilidad de Órdenes TMF622 y Remediación de Slices 5G

**Duración**: 60 minutos  
**Impartido por**: **Tryolabs** (Impulsado por Google Antigravity & Gemini Enterprise)  
**Capacidades de Antigravity Practicadas**: Orquestación Multi-Agente (`/teamwork`, Subagentes), Razonamiento Estratégico Profundo (`/boost`), Ejecución Autónoma de Objetivos (`/goal`), Automatización de Navegador (`/browser`) e Inspección del Panel Auxiliar (Subagents, Background Tasks, Artifacts, Files Changed).

> 📄 **Archivo de Prompts Rápidos**: Consulta [PROMPTS.es.md](./PROMPTS.es.md) ([English](./PROMPTS.md)) para copiar y pegar los prompts optimizados.

---

## 1. Escenario del Capstone

Quince **Órdenes de Venta B2B Empresariales TMF622** (`ORD-TMF622-9001` .. `9015`) esperan en la cola de aprovisionamiento.
- Algunas órdenes apuntan a códigos de área (`TAC-LAX-004`, `TAC-CHI-002` SST=3) con celdas 5G saludables y pueden activarse de inmediato (`READY_TO_ACTIVATE`).
- Varias órdenes estratégicas (como `ORD-TMF622-9001` para **Goldman Sachs Low-Latency Trading Backup** en `TAC-NY-001` `SST=2`, con un valor de **$42,000/mes MRR / $504,000 ARR**) están bloqueadas porque el sector primario `CELL-NY-001-B` está congestionado (`88.2%` PRB, `14.8ms` de latencia PDCP frente a `5.0ms` máximo), aunque el sector vecino `CELL-NY-001-C` en el mismo TAC y slice URLLC está saludable (`44.0%` PRB, `3.4ms` de latencia, `448 Mbps` libres).
- Dos órdenes (`ORD-TMF622-9011` que solicita `950 Mbps @ 1.2ms` y `ORD-TMF622-9014` que solicita `750 Mbps @ 2.0ms`) exceden la capacidad física de la interfaz de radio 5G en todas las celdas de su TAC y deben clasificarse como `REJECTED`.

Tu misión en el Lab 04 es utilizar las **capacidades Multi-Agente de Antigravity** (`/teamwork` o `/boost`) para implementar `evaluate_order_feasibility()` y `remediate_slice_for_order()` en [src/services/order_feasibility.py](../../src/services/order_feasibility.py), habilitando los endpoints FastAPI:
- `POST /api/v1/orders/feasibility-check`
- `POST /api/v1/slices/remediate`

---

## 2. Preparación del Laboratorio

Ejecuta el instalador del Lab 04 (que aplica automáticamente las soluciones de los Labs 01, 02 y 03):

```bash
./labs/lab-04-multi-agent-capstone/install.sh
```

---

## 3. Instrucciones Paso a Paso

### Paso 3.1: Lanzar un Flujo Multi-Agente (`/teamwork` o `/boost`)
Copia el prompt `/teamwork` o `/boost` desde [PROMPTS.es.md](./PROMPTS.es.md) en Antigravity. Observa el **Panel Auxiliar HTML** en Antigravity 2.0 mientras los subagentes inspeccionan el esquema OSS/BSS, implementan `src/services/order_feasibility.py` y ejecutan las pruebas de verificación.

### Paso 3.2: Verificar las Reglas Técnicas y Comerciales Implementadas
1. **`evaluate_order_feasibility(order_id, db_path)`**:
   - Consulta `ran_telemetry` para `tac = target_tac` y `s_nssai_sst = requested_slice_sst`.
   - Evalúa `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms` y `available_bandwidth_mbps >= requested_bandwidth_mbps`.
   - Clasifica la orden como `READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION` o `REJECTED` y actualiza `tmf622_sales_orders.order_status`.
2. **`remediate_slice_for_order(order_id, steering_mode, db_path)`**:
   - Lanza `ValueError` si la orden es `REJECTED` (lo cual `src/main.py` traduce a HTTP `400`).
   - Redirige el tráfico del slice y rebalancea el PRB en la celda congestionada (`prb_utilization_pct = 64.0`, `pdcp_latency_ms = round(max_latency_ms * 0.75, 2)`, `availability_pct = 99.995`, `status = 'HEALTHY'`).
   - Actualiza `tmf622_sales_orders` a `order_status = 'READY_TO_ACTIVATE'` y `sales_stage = 'PROVISIONED'`.
   - Calcula `protected_annual_revenue_usd`, `avoided_sla_penalty_usd` y `total_commercial_value_preserved_usd` usando `Decimal`.

---

## 4. Verificación Completa del Workshop

Ejecuta el script de verificación del Lab 04 (que corre todas las pruebas de los Labs 01, 02, 03 y 04):

```bash
./labs/lab-04-multi-agent-capstone/verify.sh
```

> **¿Necesitas la solución de referencia?** Ejecuta `./labs/lab-04-multi-agent-capstone/apply_solution.sh`.
