# Lab 03: Telemetría OSS/BSS en Vivo con FastMCP, Lifecycle Hooks y Seguridad Gemini Enterprise

**Duración**: 50 minutos  
**Impartido por**: **Tryolabs** (Impulsado por Google Antigravity & Gemini Enterprise)  
**Capacidades de Antigravity Practicadas**: Model Context Protocol (`mcp_config.json` + FastMCP), Lifecycle Hooks (`hooks.json` `PreToolUse` y `PostToolUse`), Controles de Seguridad del Cliente Antigravity (Sandbox, Tool Execution Policy, Allowlists/Denylists) y Gobernanza en Google Cloud **Gemini Enterprise**.

> 📄 **Archivo de Prompts Rápidos**: Consulta [PROMPTS.es.md](./PROMPTS.es.md) ([English](./PROMPTS.md)) para copiar y pegar los prompts optimizados.

---

## 1. Escenario y Arquitectura de Seguridad Empresarial

Los operadores de telecomunicaciones gestionan infraestructura crítica (gNodeBs 5G RAN, funciones de tasación CHF) e información regulada de suscriptores (**CPNI**: `IMSI`, `MSISDN`, `IMEI`). Conectar agentes de IA a bases de datos OSS/BSS requiere dos capas de gobernanza:

### Capa 1: Gobernanza en Google Cloud y Gemini Enterprise (Plano Cloud)
Cuando los participantes autentican Antigravity con su licencia corporativa de **Gemini Enterprise**:
1. **IAM y Gestión de Licencias**: El acceso se controla mediante Google Cloud IAM (`roles/cloudaicompanion.user`) federado con el SSO corporativo (Workspace / Cloud Identity / Okta / Entra ID).
2. **Cloud Audit Logs (`cloudaicompanion.googleapis.com`)**: Los administradores auditan eventos `Admin Activity` y `Data Access` en **Google Cloud Logging** para trazabilidad y cumplimiento, sin registrar código propietario ni datos sensibles de suscriptores.
3. **Cero Entrenamiento y Perímetro VPC-SC**: El código, los prompts y la telemetría 3GPP/BSS **nunca** se utilizan para entrenar modelos fundacionales, cuentan con indemnización de propiedad intelectual de Google Cloud y pueden protegerse con **VPC Service Controls (VPC-SC)**.

### Capa 2: Controles de Seguridad en el Cliente Antigravity y Workspace (Plano Local)
Dentro de **Antigravity 2.0** y **Antigravity IDE** (`Settings` -> `Global` y `Project-Level Settings`):
1. **Tool Execution Policy**: Permite elegir entre `strict`, `request-review`, `proceed-in-sandbox` o `always-proceed`.
2. **Terminal Sandbox**: Aísla los comandos de terminal ejecutados por el agente dentro de un sandbox a nivel de sistema operativo.
3. **Políticas de Acceso a Archivos e Internet**: Restringe `Non-Workspace File Access` (`deny`/`ask`) e `Internet Access Policy` (`deny`/`ask`), además de `Command Allowlist / Denylist` y `Browser Allowlist`.
4. **Lifecycle Hooks Determinísticos (`.agents/hooks.json`)**: Interceptan cada llamada a herramientas (`PreToolUse` / `PostToolUse`) mediante `scripts/audit_hook.py` para bloquear comandos SQL destructivos (`DROP TABLE`, `TRUNCATE`, `DELETE FROM b2b_contracts`) antes de que se ejecuten.

---

## 2. Preparación del Laboratorio

Ejecuta el instalador del Lab 03 (que aplica automáticamente las soluciones de los Labs 01 y 02):

```bash
./labs/lab-03-mcp-and-hooks/install.sh
```

---

## 3. Instrucciones Paso a Paso

### Paso 3.1: Completar las 4 Herramientas FastMCP en `mcp_server/telecom_mcp.py`
Abre [mcp_server/telecom_mcp.py](../../mcp_server/telecom_mcp.py). `query_ran_cell_health` ya está implementada. Usa Antigravity (ver [PROMPTS.es.md](./PROMPTS.es.md)) para implementar las tres funciones `@mcp.tool()` restantes:
1. `calculate_contract_penalty_exposure(contract_id: str | None = None)`
2. `inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False)` — **Importante**: Enmascara `imsi` y `msisdn` como `masked_imsi` y `masked_msisdn` (ej. `3104***0001`) para proteger la privacidad CPNI.
3. `evaluate_slice_capacity(target_tac: str, requested_slice_sst: int, requested_bandwidth_mbps: int, max_latency_ms: float)`

### Paso 3.2: Registrar el Servidor MCP en `.agents/mcp_config.json`
Crea `.agents/mcp_config.json`:

```json
{
  "mcpServers": {
    "telecom-nexus-mcp": {
      "command": "./.venv/bin/python",
      "args": ["mcp_server/telecom_mcp.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Paso 3.3: Configurar Hooks `PreToolUse` y `PostToolUse` en `.agents/hooks.json`
Inspecciona [scripts/audit_hook.py](../../scripts/audit_hook.py) y crea `.agents/hooks.json` para validar cada ejecución de `run_command` y registrar la auditoría en `data/logs/hook_audit.log`.

---

## 4. Verificación

Ejecuta el script de verificación del Lab 03:

```bash
./labs/lab-03-mcp-and-hooks/verify.sh
```

> **¿Necesitas la solución de referencia?** Ejecuta `./labs/lab-03-mcp-and-hooks/apply_solution.sh`.
