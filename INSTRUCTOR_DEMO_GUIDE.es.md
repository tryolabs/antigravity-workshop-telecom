# Guía de Demostración para el Instructor: Telecom Nexus — Taller Antigravity

<p align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

**Plataforma**: Telecom Nexus — Plataforma de SLA de Network Slicing 5G, Aseguramiento de Ingresos CDR e Inteligencia de Contratos B2B  
**Presentado por**: Tryolabs — Práctica de IA para Telecom OSS/BSS  
**Duración Total**: 120–150 Minutos (Formato Modular de 4 Laboratorios)  
**Idiomas**: [English](INSTRUCTOR_DEMO_GUIDE.md) | Español (`INSTRUCTOR_DEMO_GUIDE.es.md`)

---

## 1. Narrativa Ejecutiva y Posicionamiento del Taller

Al presentar este taller ante CTOs de Telecomunicaciones, VPs de Ingeniería de Red, Directores de Aseguramiento de Ingresos (Revenue Assurance) y Arquitectos Principales, enmarque el desafío en torno a la **Brecha entre OSS y BSS**:

1. **Los Equipos Técnicos de OSS** operan con KPIs de Red de Acceso por Radio (RAN) 5G bajo **3GPP TS 28.552** (`DL_PRB_UTIL_PCT`, `RAN_LATENCY_MS`, `PACKET_LOSS_PCT`), alarmas de celda en JSONL y registros de llamadas/datos (CDRs) bajo **3GPP TS 32.298 / GSMA TAP3.12**.
2. **Los Equipos Comerciales de BSS** operan con Órdenes de Venta Empresariales B2B bajo **TM Forum TMF622**, estructuras de penalización SLA para slices **URLLC / eMBB / mMTC** y Planes Tarifarios Comerciales.
3. **Por Qué Fallan los Asistentes de Código Genéricos en Telecom**: Los asistentes genéricos desconocen sus tarifas propietarias de roaming, no pueden consultar bases de datos de telemetría 5G RAN en vivo de forma segura y carecen de los hooks de cumplimiento exigidos por **SOX Sección 404** y **FCC CPNI**.

En este taller, los participantes transforman **Google Antigravity** de un asistente de programación de propósito general en una **Plataforma de Ingeniería Autónoma OSS/BSS de Grado Telecom** a lo largo de cuatro laboratorios progresivos.

---

## 2. Lista de Verificación Previa (15 Minutos Antes de la Sesión)

Ejecute estos comandos en `/Users/hcorrea/Workspace/agy_agy_workshop/antigravity-workshop-telecom` antes de que se conecten los participantes:

```bash
# 1. Aprovisionar el entorno virtual de Python y sembrar los datos deterministas OSS/BSS
./install.sh

# 2. Asegurar que el repositorio esté en el estado inicial del Laboratorio 1 (con los bugs intencionales)
./labs/lab-01-revenue-sla-triage/install.sh

# 3. Iniciar el Panel Web OSS/BSS de FastAPI en una pestaña de terminal dedicada
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

Abra `http://127.0.0.1:8000` en su navegador y verifique que:
- El logotipo de **Tryolabs** se muestra en el encabezado superior izquierdo.
- **Unbilled CDR Leakage** muestra inicialmente **`$0.00`** (Bug #1 activo).
- **Active SLA Penalty Exposure** muestra inicialmente **`$259,500.00`** (Bug #2 activo — incluye el contrato suspendido `CTR-B2B-1007`).

---

## 3. Inmersión Profunda en Seguridad y Gobernanza Empresarial (15 Minutos)

> **Consejo para el Instructor**: Los responsables de CISO y Gobernanza Cloud en Telecom preguntarán cómo se gobierna Antigravity en entornos regulados. Presente esta arquitectura de dos capas antes de iniciar el Laboratorio 1.

### Capa 1: Gobernanza en Google Cloud y Gemini Enterprise
Cuando Antigravity se despliega con **Gemini Enterprise en Google Cloud**:
1. **Control de Acceso con Cloud IAM**: El acceso de desarrolladores se gobierna mediante Google Cloud IAM (`roles/cloudaicompanion.user`) integrado con proveedores de identidad corporativos (Okta, Microsoft Entra ID, Google Workspace SSO).
2. **Cloud Audit Logs**: Cada acción administrativa y solicitud de API hacia `cloudaicompanion.googleapis.com` se registra en Google Cloud Audit Logs y puede exportarse a **BigQuery** o **Chronicle SIEM** para operaciones de seguridad telecom.
3. **Garantía de Cero Entrenamiento con Datos del Cliente**: El código fuente, los prompts, la telemetría 3GPP y los contratos BSS **nunca** se utilizan para entrenar modelos fundacionales de Google.
4. **Protección de Red y Propiedad Intelectual**: Soporta perímetros de **VPC Service Controls (VPC-SC)**, Private Google Access e **Indemnización de Propiedad Intelectual de IA Generativa de Google Cloud**.

### Capa 2: Controles de Seguridad del Cliente y Espacio de Trabajo de Antigravity
En la estación de trabajo del ingeniero y dentro del repositorio, Antigravity aplica políticas granulares en tiempo de ejecución:
1. **Política de Ejecución de Herramientas (`Turbo` / `Auto` / `Ask`)**: Controla si los comandos de terminal se ejecutan automáticamente o requieren aprobación humana explícita.
2. **Sandbox de Terminal (macOS Seatbelt / Linux Bubblewrap)**: Restringe operaciones de archivos y red a nivel de sistema operativo ejecutadas por subprocesos de shell.
3. **Bloqueo de Acceso a Archivos Fuera del Workspace**: Impide que el agente lea archivos fuera del directorio del proyecto (`/Users/hcorrea/Workspace/agy_agy_workshop/antigravity-workshop-telecom`).
4. **Política de Acceso a Internet (`enabled` / `allowlist` / `disabled`)**: Previene conexiones salientes hacia endpoints externos no autorizados.
5. **Lista Blanca y Lista Negra de Comandos (Allowlist & Denylist)**: Bloquea explícitamente comandos destructivos (`rm -rf`, `DROP TABLE`, credenciales de producción).
6. **Lista Blanca del Navegador (Browser Allowlist)**: Restringe el agente `/browser` únicamente a portales internos OSS/BSS aprobados (`127.0.0.1:8000`).
7. **Hooks Deterministas del Espacio de Trabajo (`.agents/hooks.json`)**: Hooks de pre-ejecución (`PreRunCommand`) y post-edición (`PostEditFile`) que aplican pistas de auditoría SOX 404 y FCC CPNI (construidos en vivo en el **Laboratorio 03**).

---

## 4. Guía de Demostración en Vivo Minuto a Minuto

### Módulo 1: Laboratorio 01 — Aseguramiento de Ingresos 5G y Triaje de SLA de Network Slicing (30 Min)

#### Contexto del Escenario (5 Min)
Muestre el panel en vivo en `http://127.0.0.1:8000`. Señale dos anomalías reportadas por el NOC y Finanzas:
1. **Alerta de Finanzas**: Los socios de roaming enviaron 250 CDRs TAP3.12 con excedentes de Ultra-Baja Latencia 5G (`5G_URLLC_ROAM`), pero el panel muestra **`$0.00` de Fuga No Facturada**.
2. **Alerta Legal/B2B**: El panel muestra **`$259,500.00`** en exposición a penalizaciones SLA, incluyendo `$35,000` para **Apex Logistics (`CTR-B2B-1007`)**, cuyo estado de contrato es **`SUSPENDED`**.

#### Pasos de Demostración en Vivo (15 Min)
1. Ejecute pytest en la terminal para mostrar las pruebas fallidas:
   ```bash
   ./.venv/bin/pytest tests/test_lab01_triage.py -v
   ```
2. Abra Antigravity y pegue el **Prompt 1** de `labs/lab-01-revenue-sla-triage/PROMPTS.es.md`.
3. Observe cómo Antigravity inspecciona `src/services/cdr_rating.py` (detectando el bug `overage_gb * 0.0`) y `src/services/sla_monitor.py` (detectando la falta de verificación `c.status != 'ACTIVE'`).
4. Pegue el **Prompt 2** para aplicar las correcciones y ejecutar las pruebas.
5. Actualice `http://127.0.0.1:8000` (o use `/browser`) para mostrar:
   - **Fuga de CDR No Facturada**: **`~$55,392.45`** en **125 CDRs de roaming no facturados**
   - **Exposición Activa a Penalizaciones SLA**: **`$224,500.00`** en **5 contratos ACTIVE incumplidos** (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`).

#### Comando de Respaldo para el Instructor
```bash
./labs/lab-01-revenue-sla-triage/apply_solution.sh
./labs/lab-01-revenue-sla-triage/verify.sh
```

---

### Módulo 2: Laboratorio 02 — Reglas de Dominio Telecom, Habilidades (Skills) y Flujos de Trabajo (30 Min)

#### Contexto del Escenario (5 Min)
Pregunte a la audiencia: *"¿Cómo garantizamos que el agente de cada ingeniero siga automáticamente los umbrales de 3GPP TS 28.552, enmascare los identificadores IMSI/MSISDN según FCC CPNI y calcule las penalizaciones SLA de manera idéntica?"*

#### Pasos de Demostración en Vivo (15 Min)
1. Prepare el estado del Laboratorio 02:
   ```bash
   ./labs/lab-02-rules-and-skills/install.sh
   ```
2. Recorra las plantillas iniciales en `.agents/rules/telecom-3gpp-governance.md`, `.agents/skills/telecom-sla-auditor/SKILL.md` y `.agents/workflows/slice-sla-triage.md`.
3. Use los prompts de `labs/lab-02-rules-and-skills/PROMPTS.es.md` para completar la regla, la habilidad y el flujo de trabajo, y luego ejecute `/slice-sla-triage` para generar `data/exports/sla_audit_report.json`.
4. Abra `data/exports/sla_audit_report.json` y destaque:
   - `"total_penalty_exposure_usd": 224500.0`
   - Cada contrato incumplido (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`) vinculado a su alarma de causa raíz `RRC_CONGESTION_ALERT`.

#### Comando de Respaldo para el Instructor
```bash
./labs/lab-02-rules-and-skills/apply_solution.sh
./labs/lab-02-rules-and-skills/verify.sh
```

---

### Módulo 3: Laboratorio 03 — Servidor MCP OSS/BSS en Vivo y Hooks de Cumplimiento SOX/CPNI (30 Min)

#### Contexto del Escenario (5 Min)
Explique que los archivos estáticos no son suficientes: los agentes necesitan **acceso en vivo y de solo lectura** a las bases de datos OSS/BSS mediante el **Model Context Protocol (MCP)**, combinado con **hooks deterministas de cumplimiento** que bloqueen SQL destructivo (`DROP TABLE`, `DELETE FROM cdrs`) antes de su ejecución.

#### Pasos de Demostración en Vivo (15 Min)
1. Prepare el estado del Laboratorio 03:
   ```bash
   ./labs/lab-03-mcp-and-hooks/install.sh
   ```
2. Muestre `mcp_server/telecom_mcp.py` y las 4 herramientas OSS/BSS (`query_ran_slice_health`, `inspect_cdr_leakage_by_tariff`, `evaluate_b2b_contract_sla`, `check_tmf622_order_feasibility`).
3. Use `labs/lab-03-mcp-and-hooks/PROMPTS.es.md` para implementar `check_tmf622_order_feasibility`, configurar `.mcp.json` y conectar `.agents/hooks.json` con `scripts/audit_hook.py`.
4. Pruebe en vivo el hook de cumplimiento en la terminal para demostrar que bloquea SQL destructivo:
   ```bash
   echo '{"command": "sqlite3 data/telecom_nexus.db \"DROP TABLE cdrs;\""}' | python3 scripts/audit_hook.py --event PreRunCommand
   echo "Exit code: $?" # Devuelve Exit code: 2 (¡BLOQUEADO!)
   ```
5. Muestre `data/logs/hook_audit.log` con el registro de auditoría en formato JSON.

#### Comando de Respaldo para el Instructor
```bash
./labs/lab-03-mcp-and-hooks/apply_solution.sh
./labs/lab-03-mcp-and-hooks/verify.sh
```

---

### Módulo 4: Laboratorio 04 — Capstone Multi-Agente OSS/BSS: Factibilidad de Órdenes TMF622 y Informe Ejecutivo (30 Min)

#### Contexto del Escenario (5 Min)
Una los mundos de OSS Técnico y BSS Comercial. La Mesa de Ventas Empresariales tiene **8 órdenes B2B TMF622 de Network Slicing 5G pendientes** por valor de millones en ingresos anuales. ¿Qué órdenes puede aceptar de forma segura la RAN 5G ahora mismo y cuáles deben retenerse para expansión de capacidad RAN?

#### Pasos de Demostración en Vivo (15 Min)
1. Prepare el estado del Laboratorio 04:
   ```bash
   ./labs/lab-04-multi-agent-capstone/install.sh
   ```
2. Muestre los dos subagentes especializados en `.agents/agents/`:
   - `ran-oss-investigator.md` (Investigador de capacidad RAN 3GPP TS 28.552 y alarmas)
   - `bss-revenue-auditor.md` (Auditor de factibilidad de órdenes TMF622, fuga de CDRs TAP3.12 y riesgo SLA)
3. Ejecute el prompt de orquestación multi-agente (o `/teamwork` / `/plan`) de `labs/lab-04-multi-agent-capstone/PROMPTS.es.md` para producir `data/exports/executive_oss_bss_advisory.md`.
4. Revise el Informe Ejecutivo generado con la audiencia:
   - **3 Órdenes Factibles (`APPROVE_IMMEDIATELY`)**: `ORD-TMF622-9003`, `ORD-TMF622-9005`, `ORD-TMF622-9008`
   - **5 Órdenes con Contención (`HOLD_REQUIRES_RAN_EXPANSION`)**: `ORD-TMF622-9001`, `ORD-TMF622-9002`, `ORD-TMF622-9004`, `ORD-TMF622-9006`, `ORD-TMF622-9007`

#### Comando de Respaldo para el Instructor
```bash
./labs/lab-04-multi-agent-capstone/apply_solution.sh
./labs/lab-04-multi-agent-capstone/verify.sh
```

---

## 5. Restablecimiento del Repositorio Después de la Demostración

Para restablecer el repositorio al estado inicial limpio del Laboratorio 01 para la siguiente cohorte del taller:

```bash
./labs/lab-01-revenue-sla-triage/install.sh
rm -f data/exports/sla_audit_report.json data/exports/executive_oss_bss_advisory.md data/logs/hook_audit.log
```
