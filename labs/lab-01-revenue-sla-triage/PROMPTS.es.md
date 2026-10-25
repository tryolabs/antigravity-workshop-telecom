<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 01 — Guía de Prompts Optimizados para Antigravity (Español)

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_01_INSTRUCTIONS_ES.pdf) | [EN](./LAB_01_INSTRUCTIONS_EN.pdf)

> **Objetivo**: Utilizar **Google Antigravity** (Antigravity 2.0 Desktop App, Antigravity IDE o el CLI `agy`) para diagnosticar y reparar dos incidentes críticos de producción en **Telecom Nexus**:
> 1. **Fuga de Ingresos en Tasación de CDRs ($54,000+ no facturados)** en `src/services/cdr_rating.py` (3GPP TS 32.298 / GSMA TAP3.12).
> 2. **Bug de Comparación Invertida de Latencia SLA en Slices 5G y Filtro de Contratos** en `src/services/sla_monitor.py` (3GPP TS 28.552).

---

## 1. Prompt de Descubrimiento y Diagnóstico de Causa Raíz (Usando `@` Mentions)

Copia y pega este prompt en el **Chat Canvas / Sidebar Chat de Antigravity**:

```text
@data/logs/ran_alarms.jsonl @src/services/cdr_rating.py @src/services/sla_monitor.py @tests/test_lab01_triage.py
Tenemos dos incidentes críticos OSS/BSS reportados en nuestro flujo de alarmas 3GPP (`ALM-BSS-8006` y `ALM-3GPP-8001`..`8005`):
1. Nuestro motor de tasación de CDRs GSMA TAP3 / 3GPP está sub-facturando sesiones de datos empresariales y omitiendo el recargo de roaming en 5G Standalone (`NR_5G`).
2. Nuestro monitor de SLA para Slices 5G B2B está reportando erróneamente los contratos en incumplimiento e incluyendo contratos no activos.

Ejecuta `./.venv/bin/pytest tests/test_lab01_triage.py` para reproducir los fallos y explica las causas raíz exactas en `cdr_rating.py` y `sla_monitor.py`.
```

---

## 2. Prompt en Modo Planificación (`/plan`)

Usa `/plan` para revisar el plan paso a paso de Antigravity antes de modificar código:

```text
/plan Crea un plan de remediación paso a paso para corregir `src/services/cdr_rating.py` y `src/services/sla_monitor.py` de modo que:
1. `cdr_rating.py` convierta `uplink_bytes + downlink_bytes` a Gigabytes binarios (`Decimal(1024 ** 3)`) en lugar de Terabytes (`1024 ** 4`) y aplique `roaming_markup_pct` siempre que `roaming_plmn != "310-410"` para todos los valores de `rat_type` (`NR_5G` y `EUTRAN_4G`), redondeando con `Decimal` `ROUND_HALF_UP` a `0.01`.
2. `sla_monitor.py` consulte únicamente los contratos con `status = 'ACTIVE'` en `b2b_contracts` y evalúe `latency_breach = worst_latency > committed_latency`.
3. Verifica la solución ejecutando `./labs/lab-01-revenue-sla-triage/verify.sh`.
```

---

## 3. Prompts de Edición Inline (`Cmd+I` / `Ctrl+I` en Antigravity IDE)

Si deseas corregir cada bug usando el **Comando Inline** directamente en el editor:

### A. En `src/services/cdr_rating.py` (Selecciona las líneas 19-48 y presiona `Cmd+I` / `Ctrl+I`)
```text
Corrige BYTES_DIVISOR para usar Gigabytes binarios `Decimal(1024 ** 3)` según 3GPP TS 32.298, y aplica el multiplicador de recargo por roaming siempre que `roaming_plmn != HOME_PLMN` sin importar el `rat_type` (incluyendo `NR_5G`). Mantén toda la aritmética en `Decimal` redondeada mediante `round_money()`.
```

### B. En `src/services/sla_monitor.py` (Selecciona las líneas 29-65 y presiona `Cmd+I` / `Ctrl+I`)
```text
Filtra `b2b_contracts` para consultar únicamente filas con `status = 'ACTIVE'`, y corrige `latency_breach` para que el incumplimiento ocurra cuando `worst_latency > committed_latency`.
```

---

## 4. Prompt de Implementación Autónoma y Verificación

```text
Aplica las correcciones en @src/services/cdr_rating.py y @src/services/sla_monitor.py, luego ejecuta `./labs/lab-01-revenue-sla-triage/verify.sh` y muestra una tabla resumen con:
1. Total de CDRs auditados, cantidad de CDRs sub-facturados y total de fuga de ingresos recuperada ($ USD).
2. Los 5 contratos B2B ACTIVOS en incumplimiento de SLA, sus celdas 5G RAN degradadas, latencia PDCP observada vs comprometida, y la exposición exacta a penalidades SLA ($224,500.00 en total).
```

---

## 5. Prompts Avanzados (`/grill-me`, `/browser`, `/learn`)

### Entrevista de Diseño Interactiva (`/grill-me`)
```text
/grill-me Entrevístame sobre cómo evolucionar nuestro motor CHF de tasación 5G Standalone para soportar bloques escalonados de sobreconsumo, degradación dinámica de QoS 5QI y conciliación bilateral GSMA BCE con las redes visitadas 234-15 y 262-01.
```

### Inspección del Dashboard NOC en Vivo (`/browser`)
```text
/browser Inicia el servidor FastAPI (`./.venv/bin/uvicorn src.main:app --port 8001`), abre `http://localhost:8001` y verifica que las tarjetas KPI muestren la Fuga de Ingresos CDR recuperada y los $224,500.00 de Exposición a Penalidades SLA B2B.
```

### Persistir Aprendizaje del Dominio (`/learn`)
```text
/learn Recuerda que en Telecom Nexus la conversión de bytes a GiB siempre debe usar `Decimal(1024 ** 3)`, el recargo por roaming aplica a todos los PLMNs visitados (`!= '310-410'`) tanto en `NR_5G` como en `EUTRAN_4G`, y las penalidades SLA solo aplican a contratos B2B con estado `ACTIVE`.
```
