# Lab 03 — Guía de Prompts Optimizados para Antigravity (Español)

> **Objetivo**: Conectar **Google Antigravity** (gobernado por **Gemini Enterprise** e impartido por **Tryolabs**) a bases de datos Telecom OSS/BSS en vivo mediante **Model Context Protocol (FastMCP)** e imponer controles determinísticos de seguridad CPNI y de base de datos mediante **Lifecycle Hooks (`hooks.json`)**.

---

## 1. Prompt de Descubrimiento (`@` Mentions)

```text
@mcp_server/telecom_mcp.py @scripts/audit_hook.py @tests/test_lab03_mcp_hooks.py
Inspecciona el servidor FastMCP inicial en `mcp_server/telecom_mcp.py`, el validador de hooks de cumplimiento en `scripts/audit_hook.py` y las pruebas en `tests/test_lab03_mcp_hooks.py`. Lista las 3 herramientas MCP pendientes de implementar en `telecom_mcp.py` y los esquemas exactos requeridos para `.agents/mcp_config.json` y `.agents/hooks.json`.
```

---

## 2. Prompt en Modo Planificación (`/plan`)

```text
/plan Crea un plan de implementación para el Lab 03 que:
1. Complete `mcp_server/telecom_mcp.py` implementando:
   - `calculate_contract_penalty_exposure(contract_id: str | None = None)` usando `evaluate_contract_sla_compliance()` y `Decimal`.
   - `inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False)` usando `rate_cdr_record()` y enmascarando `imsi` (`masked_imsi`) y `msisdn` (`masked_msisdn`) con `***` para cumplimiento CPNI.
   - `evaluate_slice_capacity(target_tac: str, requested_slice_sst: int, requested_bandwidth_mbps: int, max_latency_ms: float)` retornando `READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION` o `REJECTED`.
2. Cree `.agents/mcp_config.json` registrando `telecom-nexus-mcp` por Stdio (`./.venv/bin/python mcp_server/telecom_mcp.py`).
3. Cree `.agents/hooks.json` vinculando `PreToolUse` (`matcher: "run_command"`) y `PostToolUse` (`matcher: "run_command|edit_file|write_file"`) con `scripts/audit_hook.py`.
```

---

## 3. Prompt de Edición Inline (`Cmd+I` / `Ctrl+I`)

Abre `mcp_server/telecom_mcp.py`, selecciona las tres funciones `@mcp.tool()` pendientes y presiona `Cmd+I` / `Ctrl+I`:

```text
Implementa `calculate_contract_penalty_exposure`, `inspect_unbilled_cdrs` (enmascarando IMSI y MSISDN con `***` en `masked_imsi` y `masked_msisdn`) y `evaluate_slice_capacity` utilizando `src.services.sla_monitor`, `src.services.cdr_rating` y `src.database.fetch_all` para que pasen todas las pruebas en `tests/test_lab03_mcp_hooks.py`.
```

---

## 4. Prompt de Implementación Autónoma y Verificación

```text
Implementa las 3 herramientas MCP pendientes en @mcp_server/telecom_mcp.py, crea `.agents/mcp_config.json` y `.agents/hooks.json`, y ejecuta `./labs/lab-03-mcp-and-hooks/verify.sh`.
```

---

## 5. Prompt para Probar Herramientas MCP y Hooks de Seguridad

Una vez que `verify.sh` pase, prueba las herramientas MCP y el hook `PreToolUse` desde el Chat de Antigravity:

```text
1. Usa nuestras herramientas Telecom MCP (o invoca las funciones en `mcp_server/telecom_mcp.py`) para inspeccionar `TAC-NY-001` slice `SST=2`, calcular la exposición a penalidades de `CTR-B2B-1002`, e inspeccionar los CDRs de roaming sub-facturados con IMSIs enmascarados.
2. Prueba nuestro hook `PreToolUse` simulando una llamada a `scripts/audit_hook.py --event PreToolUse` con un comando SQL destructivo (`DROP TABLE b2b_contracts;`) y muestra cómo retorna `"decision": "deny"` y registra el evento en `data/logs/hook_audit.log`.
```

---

## 6. Prompts Avanzados de Seguridad y Gobernanza (`/boost`, `/grill-me`, `/schedule`)

### Revisión Profunda de Arquitectura de Seguridad (`/boost`)
```text
/boost Realiza un modelado de amenazas integral para Telecom OSS/BSS combinando nuestros hooks locales `.agents/hooks.json`, el Terminal Sandbox de Antigravity y la gobernanza corporativa de Google Cloud Gemini Enterprise (`roles/cloudaicompanion.user`, Cloud Audit Logs en `cloudaicompanion.googleapis.com` y VPC Service Controls).
```

### Monitoreo Programado de SLA y Hooks (`/schedule`)
```text
/schedule Cada 10 minutos, ejecuta `query_ran_cell_health` en los 5 TACs y revisa `data/logs/hook_audit.log` en busca de ejecuciones denegadas.
```
