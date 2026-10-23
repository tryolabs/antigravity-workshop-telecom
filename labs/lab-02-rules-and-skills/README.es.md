<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 02: Estándares Telecom con Rules y Custom Skills en Antigravity

**Duración**: 45 minutos  
**Impartido por**: **Tryolabs** (Impulsado por Google Antigravity & Gemini Enterprise)  
**Capacidades de Antigravity Practicadas**: Reglas del Workspace (`GEMINI.md`, `.agents/rules/*.md`), Skills con Divulgación Progresiva (`.agents/skills/<name>/SKILL.md`), Menciones `@`, `/plan`, `/learn` y `/grill-me`.

> 📄 **Archivo de Prompts Rápidos**: Consulta [PROMPTS.es.md](./PROMPTS.es.md) ([English](./PROMPTS.md)) para copiar y pegar los prompts optimizados.

---

## 1. Escenario y Objetivo Arquitectónico

En el Lab 01 corregiste dos bugs críticos de OSS/BSS. ¿Cómo garantizas que **cada desarrollador y cada sesión de agente de IA** en tu organización Telecom cumpla automáticamente con:
- **3GPP TS 28.552** (PRB 5G RAN `< 80%` y reglas de latencia PDCP en Slices)
- **3GPP TS 32.298 y GSMA TAP3.12** (Conversión GiB `Decimal(1024 ** 3)` y recargo de roaming en PLMNs visitados para `NR_5G`)
- **TMF622** (Ciclo de vida de órdenes B2B)
- **Privacidad CPNI del Suscriptor** (Enmascaramiento de IMSI y MSISDN)

En **Google Antigravity**, esto se logra mediante dos primitivas complementarias:
1. **Rules (`GEMINI.md` y `.agents/rules/telecom-standards.md`)**: Reglas jerárquicas cargadas automáticamente para imponer estilos de código, aritmética `Decimal` y cumplimiento 3GPP/TMF.
2. **Skills (`.agents/skills/sla-revenue-audit/SKILL.md`)**: Runbooks modulares que utilizan **Divulgación Progresiva (Progressive Disclosure)**: inicialmente solo se inyectan el `name` y `description` del bloque YAML; el contenido completo y el script `scripts/run_sla_audit.py` solo se cargan cuando la tarea lo requiere.

---

## 2. Preparación del Laboratorio

Ejecuta el instalador del Lab 02 (que aplica automáticamente la solución del Lab 01 primero):

```bash
./labs/lab-02-rules-and-skills/install.sh
```

---

## 3. Instrucciones Paso a Paso

### Paso 3.1: Crear `GEMINI.md` en la Raíz del Repositorio
Usa Antigravity (ver [PROMPTS.es.md](./PROMPTS.es.md)) para crear `GEMINI.md` en la raíz del proyecto, especificando:
- La arquitectura OSS (`ran_telemetry`, `ran_alarms.jsonl`) y BSS (`b2b_contracts`, `cdr_records`, `tmf622_sales_orders`).
- Uso obligatorio de `Decimal` (`ROUND_HALF_UP` a `0.01`) para cálculos monetarios.
- Conversión binaria GiB (`1024 ** 3`) y tipos de slice `3GPP` (`s_nssai_sst` 1, 2, 3).

### Paso 3.2: Crear `.agents/rules/telecom-standards.md`
Crea `.agents/rules/telecom-standards.md` documentando:
- Estándares `3GPP` TS 28.552 y TS 32.298
- Reglas de roaming `TAP3` en `NR_5G` y `EUTRAN_4G`
- Clasificación de factibilidad `TMF622` (`READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION`, `REJECTED`)
- Precisión financiera `Decimal` y protección de privacidad CPNI (IMSI/MSISDN)

### Paso 3.3: Crear `.agents/skills/sla-revenue-audit/SKILL.md`
Crea `.agents/skills/sla-revenue-audit/SKILL.md` comenzando con frontmatter YAML:

```markdown
---
name: sla-revenue-audit
description: >-
  Executes a combined 5G Network Slice SLA compliance and GSMA TAP3 CDR revenue assurance
  audit across OSS and BSS, generating an executive risk matrix in JSON and Markdown formats.
---
```

En el cuerpo de `SKILL.md`, instruye al agente a ejecutar `./.venv/bin/python scripts/run_sla_audit.py` e inspeccionar `data/exports/sla_revenue_audit_report.json` y `data/exports/sla_revenue_audit_report.md`.

---

## 4. Verificación

Ejecuta el script de verificación del Lab 02:

```bash
./labs/lab-02-rules-and-skills/verify.sh
```

> **¿Necesitas la solución de referencia?** Ejecuta `./labs/lab-02-rules-and-skills/apply_solution.sh`.
