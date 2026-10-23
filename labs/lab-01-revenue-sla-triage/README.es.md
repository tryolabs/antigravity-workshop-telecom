# Lab 01: Triage de SLA en Slices 5G y Aseguramiento de Ingresos (CDR)

**Duración**: 45 minutos  
**Capacidades de Antigravity Practicadas**: Menciones de contexto `@`, Modo `/plan`, Comando Inline (`Cmd+I` / `Ctrl+I`), Antigravity Tab (Supercomplete), Diffs Visuales, Ejecución de Pruebas en Terminal, `/browser` y `/learn`.

> 📄 **Archivo de Prompts Rápidos**: Consulta [PROMPTS.es.md](./PROMPTS.es.md) ([English](./PROMPTS.md)) para copiar y pegar los prompts optimizados.

---

## 1. Escenario y Contexto de Negocio

Eres Ingeniero Principal OSS/BSS en guardia para **Telecom Nexus**. Dos alarmas críticas acaban de activarse en `data/logs/ran_alarms.jsonl`:
1. **`ALM-BSS-8006` (Anomalía de Aseguramiento de Ingresos)**: Las sesiones de datos B2B empresariales están siendo severamente sub-facturadas.
   - En [src/services/cdr_rating.py](../../src/services/cdr_rating.py), `BYTES_DIVISOR` fue configurado por error en `Decimal(1024 ** 4)` (¡Terabytes!) en lugar de `Decimal(1024 ** 3)` (Gigabytes / GiB según **3GPP TS 32.298**).
   - Además, el recargo por roaming en redes visitadas (`roaming_plmn != "310-410"`) solo se aplica cuando `rat_type == "EUTRAN_4G"`, omitiendo los cargos de roaming en todas las sesiones **5G Standalone (`NR_5G`)**.
2. **`ALM-3GPP-8001` .. `ALM-3GPP-8005` (Incumplimientos de SLA en Slices 5G)**:
   - En [src/services/sla_monitor.py](../../src/services/sla_monitor.py), `evaluate_contract_sla_compliance()` no filtra `WHERE status = 'ACTIVE'` (penalizando por error el contrato `TERMINATED` `CTR-B2B-1011` y el contrato `DRAFT` `CTR-B2B-1012`).
   - Peor aún, la comparación de latencia está invertida (`worst_latency < committed_latency` en lugar de `worst_latency > committed_latency`), marcando slices saludables de baja latencia como incumplidos e ignorando las celdas congestionadas.

---

## 2. Preparación del Laboratorio

Ejecuta el instalador del Lab 01 desde la raíz del repositorio:

```bash
./labs/lab-01-revenue-sla-triage/install.sh
```

Confirma que los bugs iniciales hacen fallar las pruebas del Lab 01:

```bash
./.venv/bin/pytest tests/test_lab01_triage.py
```

---

## 3. Instrucciones Paso a Paso con Google Antigravity

### Paso 3.1: Diagnosticar Causas Raíz con Menciones `@`
Abre Antigravity y pega el **Prompt de Descubrimiento** de [PROMPTS.es.md](./PROMPTS.es.md):

```text
@data/logs/ran_alarms.jsonl @src/services/cdr_rating.py @src/services/sla_monitor.py @tests/test_lab01_triage.py
Tenemos dos incidentes críticos OSS/BSS reportados en nuestro flujo de alarmas 3GPP (`ALM-BSS-8006` y `ALM-3GPP-8001`..`8005`):
1. Nuestro motor de tasación de CDRs GSMA TAP3 / 3GPP está sub-facturando sesiones de datos empresariales y omitiendo el recargo de roaming en 5G Standalone (`NR_5G`).
2. Nuestro monitor de SLA para Slices 5G B2B está reportando erróneamente los contratos en incumplimiento e incluyendo contratos no activos.

Ejecuta `./.venv/bin/pytest tests/test_lab01_triage.py` para reproducir los fallos y explica las causas raíz exactas en `cdr_rating.py` y `sla_monitor.py`.
```

### Paso 3.2: Generar y Revisar un Plan con `/plan`
Pide a Antigravity que planifique la solución antes de editar archivos:

```text
/plan Crea un plan de remediación paso a paso para corregir `src/services/cdr_rating.py` y `src/services/sla_monitor.py` de modo que pasen todas las pruebas en `tests/test_lab01_triage.py`.
```

### Paso 3.3: Corregir `src/services/cdr_rating.py` y `src/services/sla_monitor.py`
Aprueba el plan en el Chat Canvas o usa `Cmd+I` / `Ctrl+I` inline en el editor:
1. En `src/services/cdr_rating.py`:
   - Cambia `BYTES_DIVISOR = Decimal(1024 ** 4)` a `BYTES_PER_GB = Decimal(1024 ** 3)`.
   - Cambia `if roaming_plmn != HOME_PLMN and rat_type == "EUTRAN_4G":` a `if roaming_plmn != HOME_PLMN:`.
2. En `src/services/sla_monitor.py`:
   - Filtra los contratos mediante `WHERE status = 'ACTIVE'`.
   - Cambia `latency_breach = worst_latency < committed_latency` a `latency_breach = worst_latency > committed_latency`.

---

## 4. Verificación

Ejecuta el script de verificación del Lab 01:

```bash
./labs/lab-01-revenue-sla-triage/verify.sh
```

> **¿Necesitas aplicar la solución de referencia?** Ejecuta `./labs/lab-01-revenue-sla-triage/apply_solution.sh` en cualquier momento.
