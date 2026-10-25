<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 02 — Guía de Prompts Optimizados para Antigravity (Español)

> **Idioma / Language:** [Español](./PROMPTS.es.md) | [English](./PROMPTS.md) • **Guía del Lab:** [README.es.md](./README.es.md) | [README.md](./README.md) • **PDF:** [ES](./LAB_02_INSTRUCTIONS_ES.pdf) | [EN](./LAB_02_INSTRUCTIONS_EN.pdf)

> **Objetivo**: Utilizar **Google Antigravity** (asociado a tu licencia de **Gemini Enterprise** e impartido por **Tryolabs**) para codificar la gobernanza técnica y comercial Telecom (3GPP/GSMA/TMF) en:
> 1. Constitución del Workspace (`GEMINI.md`)
> 2. Regla Modular (`.agents/rules/telecom-standards.md`)
> 3. Skill Bajo Demanda con Divulgación Progresiva (`.agents/skills/sla-revenue-audit/SKILL.md`)

---

## 1. Prompt de Descubrimiento y Exploración (`@` Mentions)

```text
@src/services/contract_auditor.py @scripts/run_sla_audit.py @tests/test_lab02_rules_skills.py
Inspecciona cómo Telecom Nexus combina la telemetría 5G RAN (`ran_telemetry`), el aseguramiento de ingresos CDR GSMA TAP3 (`cdr_records`) y los contratos B2B SLA (`b2b_contracts`) para generar reportes ejecutivos de riesgo. Revisa además qué valida `tests/test_lab02_rules_skills.py` para `GEMINI.md`, `.agents/rules/telecom-standards.md` y `.agents/skills/sla-revenue-audit/SKILL.md`.
```

---

## 2. Prompt en Modo Planificación (`/plan`)

```text
/plan Diseña los tres archivos de personalización de Antigravity requeridos para el Lab 02:
1. `GEMINI.md` en la raíz del repositorio definiendo la arquitectura OSS/BSS, el uso obligatorio de `Decimal` (`ROUND_HALF_UP`), la conversión GiB `1024 ** 3`, y el filtro de contratos `ACTIVE`.
2. `.agents/rules/telecom-standards.md` aplicando los estándares 3GPP TS 28.552 (PRB < 80%, latencia PDCP), 3GPP TS 32.298 / GSMA TAP3.12, estados de órdenes TMF622, precisión financiera `Decimal`, y protección de privacidad CPNI (IMSI/MSISDN).
3. `.agents/skills/sla-revenue-audit/SKILL.md` con frontmatter YAML válido (`name: sla-revenue-audit`, `description: ...`) instruyendo a Antigravity cómo ejecutar `scripts/run_sla_audit.py` y validar `data/exports/sla_revenue_audit_report.json` y `.md`.
```

---

## 3. Prompt de Edición Inline (`Cmd+I` / `Ctrl+I`)

Abre `.agents/skills/sla-revenue-audit/SKILL.md` en Antigravity IDE y presiona `Cmd+I` / `Ctrl+I`:

```text
Genera un archivo SKILL.md completo para Antigravity con frontmatter YAML (`name: sla-revenue-audit` y un campo `description` en tercera persona indicando cuándo activar el skill) seguido de un runbook de 4 pasos que ejecute `./.venv/bin/pytest tests/test_lab01_triage.py`, corra `./.venv/bin/python scripts/run_sla_audit.py`, y verifique `data/exports/sla_revenue_audit_report.json` y `data/exports/sla_revenue_audit_report.md`.
```

---

## 4. Prompt de Implementación e Invocación del Skill

Primero, pide a Antigravity que cree los tres archivos:

```text
Crea `GEMINI.md`, `.agents/rules/telecom-standards.md` y `.agents/skills/sla-revenue-audit/SKILL.md` según nuestro plan, y luego ejecuta `./labs/lab-02-rules-and-skills/verify.sh`.
```

Luego, prueba invocar tu nuevo **Skill** en lenguaje natural:

```text
Utiliza el skill `sla-revenue-audit` para ejecutar una auditoría completa de SLA en Slices 5G y aseguramiento de ingresos CDR GSMA TAP3, y resume los 3 contratos empresariales B2B de mayor riesgo financiero a partir del reporte ejecutivo generado.
```

---

## 5. Prompts Avanzados (`/grill-me`, `/learn`, `/compact`)

### Entrevista de Gobernanza y Reglas (`/grill-me`)
```text
/grill-me Entrevístame para refinar `.agents/rules/telecom-standards.md` de modo que cubra 3GPP Release 18 NWDAF, enmascaramiento CPNI de suscriptores y descomposición de órdenes TMF622/TMF641.
```

### Persistir Reglas de Reporteo (`/learn`)
```text
/learn Siempre que generes reportes ejecutivos de SLA B2B en Telecom Nexus, ordena los contratos por `total_commercial_risk_usd` de forma descendente y resalta tanto `degraded_cell_id` como `primary_tac`.
```
