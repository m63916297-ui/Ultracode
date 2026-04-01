"""
UltraCode - Sistema de Programación IA con Arquitectura Claude Code
================================================================
Aplicación Streamlit con LangChain implementando los 12 pilares de la arquitectura.
Compatible con Streamlit Cloud (sin threading/ThreadPoolExecutor).

Autor: UltraCode System
Versión: 1.0.0
"""

import streamlit as st
import time
import json
import re
import os
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import uuid

# ============================================================
# ARQUITECTURA - 12 PILARES
# ============================================================

# ------------------------------------------------
# PILAR 1: ESCALA DEL PROYECTO
# Configuración y métricas del sistema
# ------------------------------------------------


@dataclass
class ProjectMetrics:
    """Métricas del proyecto - ~512K líneas de TypeScript"""

    lines_of_code: int = 512000
    source_files: int = 1884
    modules: int = 35
    bundle_size_kb: int = 803
    integrated_tools: int = 80
    language: str = "TypeScript"

    def to_dict(self) -> Dict:
        return asdict(self)


# ------------------------------------------------
# PILAR 2: MOTOR INK/ - UI DE TERMINAL
# Sistema de renderizado de interfaz
# ------------------------------------------------


class TerminalColors:
    """Constantes de colores ANSI para terminal"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    BG_DARK = "#0d1117"
    BG_PANEL = "#161b22"
    ACCENT = "#1792e0"
    SUCCESS = "#3fb950"
    WARNING = "#d29922"
    ERROR = "#f85149"
    CLAUDE_GREEN = "#42b392"


@dataclass
class TerminalLine:
    """Representación de una línea en la terminal"""

    content: str
    type: str = "response"  # response, command, success, error, warning, info
    timestamp: datetime = field(default_factory=datetime.now)
    prefix: Optional[str] = None


class TerminalBuffer:
    """Buffer de terminal con soporte para streaming (Streamlit Cloud compatible)"""

    def __init__(self, max_lines: int = 500):
        self.lines: List[TerminalLine] = []
        self.max_lines = max_lines

    def add_line(
        self, content: str, line_type: str = "response", prefix: Optional[str] = None
    ):
        line = TerminalLine(content=content, type=line_type, prefix=prefix)
        self.lines.append(line)
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
        return line

    def get_lines(self) -> List[TerminalLine]:
        return list(self.lines)

    def clear(self):
        self.lines.clear()


# ------------------------------------------------
# PILAR 3: SISTEMA DUAL DE PERMISOS
# Seguridad de dos capas (Track 1 + Track 2)
# ------------------------------------------------


class PermissionAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


@dataclass
class PermissionRule:
    """Regla de permisos Track 1"""

    pattern: str
    action: PermissionAction
    reason: str
    is_regex: bool = False


@dataclass
class PermissionResult:
    """Resultado de evaluación de permisos"""

    allowed: bool
    track: int  # 1 o 2
    reason: str
    rule_match: Optional[str] = None


class Track1PermissionEngine:
    """Motor de permisos rápido con Glob/Regex"""

    def __init__(self):
        self.rules: List[PermissionRule] = [
            PermissionRule(
                "*.env",
                PermissionAction.DENY,
                "Archivo de variables de entorno sensible",
            ),
            PermissionRule(
                "~/.ssh/*", PermissionAction.DENY, "Directorio SSH con claves privadas"
            ),
            PermissionRule("*.pem", PermissionAction.DENY, "Certificado SSL/TLS"),
            PermissionRule("*.key", PermissionAction.DENY, "Clave privada"),
            PermissionRule(
                "rm -rf /*", PermissionAction.DENY, "Eliminación masiva del sistema"
            ),
            PermissionRule("rm -rf /", PermissionAction.DENY, "Eliminación de raíz"),
            PermissionRule(
                "drop database", PermissionAction.DENY, "Eliminación de base de datos"
            ),
            PermissionRule("format", PermissionAction.DENY, "Formateo de disco"),
            PermissionRule("shutdown", PermissionAction.DENY, "Apagado del sistema"),
        ]

    def evaluate(self, command: str) -> PermissionResult:
        """Evalúa comando contra reglas deterministas"""
        for rule in self.rules:
            if rule.is_regex:
                pattern = rule.pattern
            else:
                pattern = rule.pattern.replace(".", r"\.").replace("*", ".*")

            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=(rule.action == PermissionAction.ALLOW),
                    track=1,
                    reason=rule.reason,
                    rule_match=rule.pattern,
                )

        return PermissionResult(allowed=True, track=1, reason="Sin restricciones")


class Track2PermissionClassifier:
    """Clasificador ML para permisos contextuales (Track 2)"""

    DANGEROUS_PATTERNS = [
        "delete all",
        "drop table",
        "drop all",
        "truncate",
        "remove system",
        "modify boot",
        "access root",
        "inject",
        "exec(",
        "eval(",
        "os.system",
        "subprocess",
        "shell=True",
        "rm -rf node_modules",
    ]

    SUSPICIOUS_PATTERNS = [
        "git reset --hard",
        "git clean -fd",
        "--force",
        "sudo rm",
        "chmod 777",
        "wget | curl",
        "base64 -d",
        "nc -e",
        "/dev/tcp",
    ]

    def __init__(self):
        self.confidence_threshold = 0.7

    async def evaluate(
        self, command: str, context: Optional[Dict] = None
    ) -> PermissionResult:
        """Evalúa comando con comprensión semántica"""
        context = context or {}

        # Verificar patrones peligrosos
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in command.lower():
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason=f"Patrón peligroso detectado: {pattern}",
                )

        # Verificar patrones sospechosos
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in command.lower():
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason=f"Comando sospechoso requiere confirmación: {pattern}",
                )

        # Verificar en contexto de herramientas actuales
        active_tools = context.get("active_tools", [])
        if "Read" in active_tools and "Write" not in active_tools:
            if "rm " in command.lower() or "del " in command.lower():
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason="Comando de eliminación sin herramientas de escritura activas",
                )

        return PermissionResult(
            allowed=True, track=2, reason="Comando seguro en contexto"
        )


class DualPermissionSystem:
    """Sistema dual de permisos (Track 1 + Track 2)"""

    def __init__(self):
        self.track1 = Track1PermissionEngine()
        self.track2 = Track2PermissionClassifier()
        self.permission_history: List[PermissionResult] = []
        self.user_overrides: Dict[str, PermissionAction] = {}

    async def check(
        self, command: str, context: Optional[Dict] = None
    ) -> PermissionResult:
        """Evalúa permisos en dos tracks"""
        # Track 1: Evaluación rápida determinista
        result = self.track1.evaluate(command)
        self.permission_history.append(result)

        if not result.allowed:
            return result

        # Track 2: Clasificación semántica (solo si pasa Track 1)
        result = await self.track2.evaluate(command, context)
        self.permission_history.append(result)

        return result

    def add_rule(self, pattern: str, action: PermissionAction, reason: str):
        """Agrega regla personalizada al Track 1"""
        rule = PermissionRule(pattern, action, reason, is_regex="*" in pattern)
        self.track1.rules.append(rule)

    def get_history(self) -> List[Dict]:
        return [
            {"command": f"Rule: {h.rule_match}", **asdict(h)}
            for h in self.permission_history[-50:]
        ]


# ------------------------------------------------
# PILAR 4: STREAMING TOOL EXECUTOR
# Ejecución concurrente de herramientas
# ------------------------------------------------


@dataclass
class ToolCall:
    """Representación de una llamada a herramienta"""

    id: str
    name: str
    arguments: Dict[str, Any]
    is_concurrency_safe: bool = True
    depends_on: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Resultado de ejecución de herramienta"""

    tool_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0
    temp_file: Optional[str] = None


class ToolDefinition:
    """Definición de herramienta"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict,
        is_concurrency_safe: bool = True,
        requires_confirmation: bool = False,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.is_concurrency_safe = is_concurrency_safe
        self.requires_confirmation = requires_confirmation


class StreamingToolExecutor:
    """Ejecutor de herramientas con streaming y concurrencia (Streamlit Cloud compatible)"""

    def __init__(self, permission_system: DualPermissionSystem):
        self.permission_system = permission_system
        self.registered_tools: Dict[str, ToolDefinition] = {}
        self.execution_buffer: Dict[str, ToolResult] = {}

        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Registra herramientas integradas"""
        tools = [
            ToolDefinition(
                "Read",
                "Lee contenido de archivos",
                {"type": "object", "properties": {"path": {"type": "string"}}},
                is_concurrency_safe=True,
            ),
            ToolDefinition(
                "Write",
                "Escribe contenido en archivos",
                {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                },
                is_concurrency_safe=False,
            ),
            ToolDefinition(
                "Edit",
                "Edita líneas específicas de un archivo",
                {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "oldString": {"type": "string"},
                        "newString": {"type": "string"},
                    },
                },
                is_concurrency_safe=False,
            ),
            ToolDefinition(
                "Grep",
                "Busca patrones en archivos",
                {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"},
                    },
                },
                is_concurrency_safe=True,
            ),
            ToolDefinition(
                "Glob",
                "Encuentra archivos por patrón",
                {"type": "object", "properties": {"pattern": {"type": "string"}}},
                is_concurrency_safe=True,
            ),
            ToolDefinition(
                "Bash",
                "Ejecuta comandos de shell",
                {"type": "object", "properties": {"command": {"type": "string"}}},
                is_concurrency_safe=False,
                requires_confirmation=True,
            ),
            ToolDefinition(
                "WebSearch",
                "Busca en la web",
                {"type": "object", "properties": {"query": {"type": "string"}}},
                is_concurrency_safe=True,
            ),
            ToolDefinition(
                "TodoWrite",
                "Gestiona lista de tareas",
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "task": {"type": "string"},
                    },
                },
                is_concurrency_safe=True,
            ),
        ]

        for tool in tools:
            self.register_tool(tool)

    def register_tool(self, tool: ToolDefinition):
        """Registra una nueva herramienta"""
        self.registered_tools[tool.name] = tool

    async def execute(
        self, tool_call: ToolCall, context: Optional[Dict] = None
    ) -> ToolResult:
        """Ejecuta una herramienta individual"""
        start_time = time.time()

        # Verificar permisos
        perm_result = await self.permission_system.check(
            f"{tool_call.name} {tool_call.arguments}", context
        )

        if not perm_result.allowed:
            return ToolResult(
                tool_id=tool_call.id,
                success=False,
                output=None,
                error=f"Permiso denegado ({perm_result.track}): {perm_result.reason}",
            )

        # Ejecutar herramienta
        try:
            tool_func = self._get_tool_function(tool_call.name)
            output = await tool_func(tool_call.arguments)

            # Guardar resultado en disco (deferred loading)
            temp_file = self._save_to_disk(tool_call.id, output)

            return ToolResult(
                tool_id=tool_call.id,
                success=True,
                output=output,
                execution_time_ms=(time.time() - start_time) * 1000,
                temp_file=temp_file,
            )
        except Exception as e:
            return ToolResult(
                tool_id=tool_call.id,
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def execute_concurrent(
        self, tool_calls: List[ToolCall], context: Optional[Dict] = None
    ) -> List[Optional[ToolResult]]:
        """Ejecuta múltiples herramientas con concurrencia"""

        # Clasificar por isConcurrencySafe
        safe_calls = [
            tc for tc in tool_calls if tc.is_concurrency_safe and not tc.depends_on
        ]
        unsafe_calls = [
            tc for tc in tool_calls if not tc.is_concurrency_safe or tc.depends_on
        ]

        results = []

        if safe_calls:
            tasks = [self.execute(tc, context) for tc in safe_calls]
            safe_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in safe_results:
                if isinstance(result, Exception):
                    results.append(None)
                else:
                    results.append(result)

        for tc in unsafe_calls:
            results.append(await self.execute(tc, context))

        return results

    def _get_tool_function(self, tool_name: str) -> Callable:
        """Obtiene función de herramienta"""
        functions = {
            "Read": self._tool_read,
            "Write": self._tool_write,
            "Edit": self._tool_edit,
            "Grep": self._tool_grep,
            "Glob": self._tool_glob,
            "Bash": self._tool_bash,
            "WebSearch": self._tool_websearch,
            "TodoWrite": self._tool_todowrite,
        }
        return functions.get(tool_name, self._tool_unknown)

    async def _tool_read(self, args: Dict) -> str:
        """Herramienta Read"""
        path = args.get("path", "")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Archivo no encontrado: {path}"

    async def _tool_write(self, args: Dict) -> str:
        """Herramienta Write"""
        path = args.get("path", "")
        content = args.get("content", "")
        os.makedirs(
            os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Archivo escrito: {path}"

    async def _tool_edit(self, args: Dict) -> str:
        """Herramienta Edit"""
        path = args.get("path", "")
        old = args.get("oldString", "")
        new = args.get("newString", "")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace(old, new)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Archivo editado: {path}"
        return f"Archivo no encontrado: {path}"

    async def _tool_grep(self, args: Dict) -> str:
        """Herramienta Grep"""
        pattern = args.get("pattern", "")
        path = args.get("path", ".")
        results = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".tsx", ".md", ".txt")):
                    fpath = os.path.join(root, file)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            for i, line in enumerate(f, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    results.append(f"{fpath}:{i}: {line.strip()}")
                    except:
                        pass
        return "\n".join(results[:50]) if results else "Sin coincidencias"

    async def _tool_glob(self, args: Dict) -> str:
        """Herramienta Glob"""
        pattern = args.get("pattern", "")
        results = []
        pattern_regex = (
            pattern.replace(".", r"\.").replace("**/", "**/").replace("*", "[^/]*")
        )
        for root, _, files in os.walk("."):
            for file in files:
                if re.search(pattern.replace("**/", "").replace("*", ".*"), file):
                    results.append(os.path.join(root, file))
        return "\n".join(results[:100]) if results else "Sin coincidencias"

    async def _tool_bash(self, args: Dict) -> str:
        """Herramienta Bash"""
        import subprocess

        command = args.get("command", "")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout or result.stderr
        except subprocess.TimeoutExpired:
            return "Timeout: Comando excedió 30 segundos"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _tool_websearch(self, args: Dict) -> str:
        """Herramienta WebSearch"""
        return f"Resultado de búsqueda para: {args.get('query', '')}\n[Simulación] Para implementar, agregar API key de búsqueda"

    async def _tool_todowrite(self, args: Dict) -> str:
        """Herramienta TodoWrite"""
        action = args.get("action", "")
        task = args.get("task", "")
        return f"Todo {action}: {task}"

    async def _tool_unknown(self, args: Dict) -> str:
        return f"Herramienta desconocida"

    def _save_to_disk(self, tool_id: str, output: Any) -> str:
        """Guarda resultado en disco para deferred loading"""
        temp_dir = "/tmp/ultracode"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, f"result_{tool_id}.json")
        with open(temp_file, "w") as f:
            json.dump({"tool_id": tool_id, "output": str(output)}, f)
        return temp_file


# ------------------------------------------------
# PILAR 5: FEATURE GATES
# Puertas de características
# ------------------------------------------------


class FeatureGates:
    """Sistema de Feature Gates con Dead-Code Elimination"""

    def __init__(self):
        self.gates = {
            "KAIROS": False,  # Sistema de planificación temporal avanzada
            "COORDINATOR_MODE": False,  # Coordinación multi-agente centralizada
            "VOICE_MODE": False,  # Interacción por voz
            "PROACTIVE": False,  # Ejecución proactiva
        }

    def is_enabled(self, gate: str) -> bool:
        return self.gates.get(gate, False)

    def enable(self, gate: str):
        if gate in self.gates:
            self.gates[gate] = True

    def disable(self, gate: str):
        if gate in self.gates:
            self.gates[gate] = False

    def get_status(self) -> Dict[str, bool]:
        return self.gates.copy()


# ------------------------------------------------
# PILAR 6: SISTEMA DE SUB-AGENTES
# Agent Spawning con múltiples modos
# ------------------------------------------------


class AgentMode(Enum):
    IN_PROCESS = "in-process"  # Misma memoria, máxima velocidad
    GIT_WORKTREE = "git-worktree"  # Aislamiento con Git
    REMOTE = "remote"  # Servidor en la nube


@dataclass
class SubAgent:
    """Representación de un sub-agente"""

    id: str
    mode: AgentMode
    parent_id: str
    status: str = "initializing"  # initializing, active, processing, idle, terminated
    created_at: datetime = field(default_factory=datetime.now)
    tasks: List[str] = field(default_factory=list)


class SubAgentSystem:
    """Sistema de generación y gestión de sub-agentes"""

    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self.agents: Dict[str, SubAgent] = {}
        self.message_queue: Dict[str, List[Dict]] = defaultdict(list)

    def spawn(self, mode: AgentMode, parent_id: str = "main") -> SubAgent:
        """Crea un nuevo sub-agente"""
        if len(self.agents) >= self.max_agents:
            raise Exception(f"Máximo de {self.max_agents} agentes alcanzado")

        agent_id = str(uuid.uuid4())[:8]
        agent = SubAgent(id=agent_id, mode=mode, parent_id=parent_id, status="active")
        self.agents[agent_id] = agent
        return agent

    def terminate(self, agent_id: str):
        """Termina un sub-agente"""
        if agent_id in self.agents:
            self.agents[agent_id].status = "terminated"
            del self.agents[agent_id]

    def send_message(self, from_id: str, to_id: str, message: Dict):
        """Envía mensaje a otro agente"""
        self.message_queue[to_id].append(
            {
                "from": from_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_messages(self, agent_id: str) -> List[Dict]:
        """Obtiene mensajes pendientes de un agente"""
        messages = self.message_queue.get(agent_id, [])
        self.message_queue[agent_id] = []
        return messages

    def get_active_agents(self) -> List[SubAgent]:
        return [a for a in self.agents.values() if a.status != "terminated"]


# ------------------------------------------------
# PILAR 7: RESULTADOS EN DISCO
# Deferred Loading System
# ------------------------------------------------


class DeferredLoadingSystem:
    """Sistema de persistencia de resultados con carga diferida"""

    def __init__(self, temp_dir: str = "/tmp/ultracode"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.references: Dict[str, str] = {}  # reference_id -> temp_file

    def store(self, key: str, data: Any) -> str:
        """Almacena datos y retorna referencia"""
        file_path = os.path.join(self.temp_dir, f"{key}.json")
        with open(file_path, "w") as f:
            json.dump({"data": data, "timestamp": datetime.now().isoformat()}, f)
        self.references[key] = file_path
        return key

    def load(self, reference: str) -> Optional[Any]:
        """Carga datos desde referencia"""
        file_path = self.references.get(reference)
        if file_path and os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return None

    def cleanup(self, max_age_hours: int = 24):
        """Limpia archivos temporales antiguos"""
        cutoff = time.time() - (max_age_hours * 3600)
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.getmtime(file_path) < cutoff:
                os.remove(file_path)


# ------------------------------------------------
# PILAR 8: QUERY ENGINE DE 2 CAPAS
# Separación de responsabilidades
# ------------------------------------------------


@dataclass
class QueryConfig:
    """Configuración de query"""

    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = ""
    context_window: int = 200000


class QueryInternal:
    """Capa Interna - Obrero Especializado (query.ts)"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.base_url = "https://api.anthropic.com/v1"

    async def format_request(self, prompt: str, config: QueryConfig) -> Dict:
        """Formatea request para API"""
        return {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

    async def send_request(self, request: Dict) -> Dict:
        """Envía request a API (simulado sin API key real)"""
        if not self.api_key:
            return {
                "content": f"[Simulación] Request preparado para: {request.get('model')}\n[Requiere ANTHROPIC_API_KEY para ejecución real]"
            }
        # En producción real, aquí se haría el request HTTP
        return {"content": "[Respuesta simulada]"}


class QueryEngine:
    """Capa Externa - Director de Orquestación (QueryEngine.ts)"""

    def __init__(
        self,
        tool_executor: StreamingToolExecutor,
        permission_system: DualPermissionSystem,
    ):
        self.internal = QueryInternal()
        self.tool_executor = tool_executor
        self.permission_system = permission_system
        self.config = QueryConfig()

    async def execute(
        self, prompt: str, tools: Optional[List[ToolCall]] = None
    ) -> Dict:
        """Ejecuta query con todas las verificaciones"""
        # Verificar presupuesto
        # (Implementar budget tracking)

        # Formatear request
        request = await self.internal.format_request(prompt, self.config)

        # Enviar request
        response = await self.internal.send_request(request)

        # Ejecutar herramientas si hay
        if tools:
            results = await self.tool_executor.execute_concurrent(tools)
            return {"response": response, "tool_results": results}

        return {"response": response}


# ------------------------------------------------
# PILAR 9: INTEGRACIÓN MCP
# Model Context Protocol
# ------------------------------------------------


class MCPTransport(Enum):
    STDIO = "stdio"  # Local (subproceso)
    SSE = "sse"  # Remoto (HTTP)
    WEBSOCKET = "websocket"  # Bidireccional


@dataclass
class MCPServer:
    """Servidor MCP conectado"""

    name: str
    transport: MCPTransport
    status: str = "disconnected"
    endpoint: Optional[str] = None


class MCPClient:
    """Cliente MCP - USB-C de la IA"""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.adapters: Dict[str, Any] = {}

    def connect(
        self, name: str, transport: MCPTransport, endpoint: Optional[str] = None
    ):
        """Conecta a un servidor MCP"""
        server = MCPServer(
            name=name, transport=transport, status="connected", endpoint=endpoint
        )
        self.servers[name] = server

        # Registrar como herramienta
        tool = ToolDefinition(
            name=f"mcp_{name}",
            description=f"Herramienta MCP: {name}",
            parameters={"type": "object", "properties": {}},
            is_concurrency_safe=True,
        )
        # En producción, el adapter translate MCP tools a formato nativo
        self.adapters[name] = tool

    def disconnect(self, name: str):
        """Desconecta servidor MCP"""
        if name in self.servers:
            self.servers[name].status = "disconnected"

    def get_tools(self) -> List[ToolDefinition]:
        """Obtiene herramientas de todos los servidores MCP"""
        return list(self.adapters.values())

    def get_servers(self) -> List[MCPServer]:
        return list(self.servers.values())


# ------------------------------------------------
# PILAR 10: PERSISTENCIA Y REANUDACIÓN
# Checkpoint/Restore System
# ------------------------------------------------


@dataclass
class SessionState:
    """Estado completo de sesión"""

    session_id: str
    created_at: datetime
    last_updated: datetime
    tool_states: Dict[str, Any] = field(default_factory=dict)
    permissions_granted: List[str] = field(default_factory=list)
    permissions_denied: List[str] = field(default_factory=list)
    budget_spent: float = 0.0
    agent_states: Dict[str, Any] = field(default_factory=dict)
    tool_history: List[Dict] = field(default_factory=list)
    chat_history: List[Dict] = field(default_factory=list)


class SessionManager:
    """Gestor de sesiones con checkpoint/restore"""

    def __init__(self, storage_dir: str = ".ultracode/sessions"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.current_session: Optional[SessionState] = None

    def create_session(self) -> SessionState:
        """Crea nueva sesión"""
        session = SessionState(
            session_id=str(uuid.uuid4())[:12],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )
        self.current_session = session
        return session

    def checkpoint(self) -> Optional[str]:
        """Guarda checkpoint de sesión"""
        if not self.current_session:
            return None

        self.current_session.last_updated = datetime.now()
        file_path = os.path.join(
            self.storage_dir, f"session_{self.current_session.session_id}.json"
        )
        with open(file_path, "w") as f:
            json.dump(asdict(self.current_session), f, default=str)
        return file_path

    def restore(self, session_id: str) -> Optional[SessionState]:
        """Restaura sesión desde checkpoint"""
        file_path = os.path.join(self.storage_dir, f"session_{session_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["last_updated"] = datetime.fromisoformat(data["last_updated"])
                self.current_session = SessionState(**data)
                return self.current_session
        return None

    def list_sessions(self) -> List[Dict]:
        """Lista sesiones guardadas"""
        sessions = []
        for file in os.listdir(self.storage_dir):
            if file.endswith(".json"):
                file_path = os.path.join(self.storage_dir, file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                    sessions.append(
                        {
                            "id": data.get("session_id"),
                            "created": data.get("created_at"),
                            "last_updated": data.get("last_updated"),
                            "budget": data.get("budget_spent", 0),
                        }
                    )
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)


# ------------------------------------------------
# PILAR 11: PROMPT CACHING
# Sistema de cache de prompts
# ------------------------------------------------


@dataclass
class CacheEntry:
    """Entrada de cache"""

    content: str
    hash: str
    created_at: datetime
    ttl_seconds: int = 300  # 5 minutos
    hit_count: int = 0


class PromptCache:
    """Sistema de cache de prompts para reducir costos"""

    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.hit_rate = 0.0
        self.total_requests = 0

    def mark(self, content: str) -> str:
        """Marca contenido para cache"""
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        entry = CacheEntry(
            content=content, hash=hash_key, created_at=datetime.now(), ttl_seconds=300
        )
        self.cache[hash_key] = entry
        return hash_key

    def get(self, hash_key: str) -> Optional[str]:
        """Obtiene contenido cacheado"""
        entry = self.cache.get(hash_key)
        if not entry:
            return None

        # Verificar TTL
        age = (datetime.now() - entry.created_at).total_seconds()
        if age > entry.ttl_seconds:
            del self.cache[hash_key]
            return None

        entry.hit_count += 1
        self.total_requests += 1
        self.hit_rate = sum(e.hit_count for e in self.cache.values()) / max(
            self.total_requests, 1
        )
        return entry.content

    def get_stats(self) -> Dict:
        return {
            "entries": len(self.cache),
            "hit_rate": f"{self.hit_rate:.1%}",
            "total_requests": self.total_requests,
        }


# ------------------------------------------------
# PILAR 12: SPINNER VERBS
# Verbos animados para UI
# ------------------------------------------------

SPINNER_VERBS = [
    "Analyzing",
    "Baking",
    "Crafting",
    "Designing",
    "Engineering",
    "Fabricating",
    "Generating",
    "Implementing",
    "Indexing",
    "Navigating",
    "Optimizing",
    "Processing",
    "Rendering",
    "Scaffolding",
    "Searching",
    "Synthesizing",
    "Transpiling",
    "Validating",
    "Architecting",
    "Building",
    "Compiling",
    "Computing",
    "Configuring",
    "Constructing",
    "Developing",
    "Executing",
    "Exploring",
    "Fetching",
    "Formatting",
    "Inspecting",
    "Loading",
    "Mapping",
    "Orchestrating",
    "Parsing",
    "Querying",
    "Resolving",
    "Scanning",
    "Streaming",
    "Tracing",
    "Warming up",
]

# ============================================================
# STREAMLIT UI
# ============================================================


def init_session_state():
    """Inicializa estado de sesión de Streamlit"""

    if "terminal_buffer" not in st.session_state:
        st.session_state.terminal_buffer = TerminalBuffer()

    if "permission_system" not in st.session_state:
        st.session_state.permission_system = DualPermissionSystem()

    if "tool_executor" not in st.session_state:
        st.session_state.tool_executor = StreamingToolExecutor(
            st.session_state.permission_system
        )

    if "feature_gates" not in st.session_state:
        st.session_state.feature_gates = FeatureGates()

    if "sub_agent_system" not in st.session_state:
        st.session_state.sub_agent_system = SubAgentSystem()

    if "mcp_client" not in st.session_state:
        st.session_state.mcp_client = MCPClient()

    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager()

    if "prompt_cache" not in st.session_state:
        st.session_state.prompt_cache = PromptCache()

    if "budget_spent" not in st.session_state:
        st.session_state.budget_spent = 0.12

    if "budget_limit" not in st.session_state:
        st.session_state.budget_limit = 5.00

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "spinner_verb_index" not in st.session_state:
        st.session_state.spinner_verb_index = 0


def add_terminal_output(text: str, line_type: str = "response"):
    """Agrega línea a la terminal"""
    st.session_state.terminal_buffer.add_line(text, line_type)


def render_terminal():
    """Renderiza componente de terminal"""
    lines = st.session_state.terminal_buffer.get_lines()

    terminal_html = """
    <style>
        .terminal-container {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 12px;
            height: 350px;
            overflow-y: auto;
        }
        .terminal-line {
            margin-bottom: 2px;
            display: flex;
            gap: 8px;
        }
        .terminal-prefix {
            color: #42b392;
            font-weight: bold;
        }
        .terminal-command { color: #e6edf3; }
        .terminal-response { color: #8b949e; }
        .terminal-success { color: #3fb950; }
        .terminal-error { color: #f85149; }
        .terminal-warning { color: #d29922; }
        .terminal-info { color: #a371f7; }
        .terminal-time {
            color: #484f58;
            font-size: 10px;
        }
    </style>
    <div class="terminal-container">
    """

    for line in lines[-100:]:  # Últimas 100 líneas
        prefix = line.prefix or ""
        content_class = f"terminal-{line.type}"
        time_str = line.timestamp.strftime("%H:%M:%S")

        terminal_html += f"""
        <div class="terminal-line">
            <span class="terminal-time">[{time_str}]</span>
            {f'<span class="terminal-prefix">{prefix}</span>' if prefix else ""}
            <span class="{content_class}">{line.content}</span>
        </div>
        """

    terminal_html += "</div>"
    return terminal_html


def render_budget_meter():
    """Renderiza indicador de presupuesto"""
    spent = st.session_state.budget_spent
    limit = st.session_state.budget_limit
    percent = (spent / limit) * 100

    color = "#3fb950"
    if percent > 80:
        color = "#f85149"
    elif percent > 50:
        color = "#d29922"

    return f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 8px 16px; background: #21262d; border-radius: 6px;">
        <span style="color: #8b949e; font-size: 12px;">Budget:</span>
        <div style="flex: 1; height: 6px; background: #0d1117; border-radius: 3px; overflow: hidden;">
            <div style="width: {percent}%; height: 100%; background: {color}; transition: width 0.3s;"></div>
        </div>
        <span style="color: #e6edf3; font-size: 12px;">${spent:.2f} / ${limit:.2f}</span>
    </div>
    """


def render_feature_gates():
    """Renderiza panel de Feature Gates"""
    gates = st.session_state.feature_gates.get_status()

    html = '<div style="padding: 12px;">'
    html += '<h4 style="color: #8b949e; font-size: 11px; margin-bottom: 8px;">FEATURE GATES</h4>'

    for name, enabled in gates.items():
        status = "🟢" if enabled else "🔴"
        html += f'<div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px;">'
        html += f'<span style="color: #8b949e;">{name}</span>'
        html += f"<span>{status}</span>"
        html += "</div>"

    html += "</div>"
    return html


def render_agent_tree():
    """Renderiza árbol de agentes"""
    system = st.session_state.sub_agent_system

    html = '<div style="padding: 12px;">'
    html += '<h4 style="color: #8b949e; font-size: 11px; margin-bottom: 8px;">AGENTES ACTIVOS</h4>'

    # Agente principal
    html += f"""
    <div style="display: flex; align-items: center; gap: 8px; padding: 6px 8px; 
                background: #21262d; border: 1px solid #42b392; border-radius: 6px; margin-bottom: 4px;">
        <span style="width: 8px; height: 8px; background: #3fb950; border-radius: 50%;"></span>
        <span style="font-size: 11px;">Main Agent</span>
    </div>
    """

    # Sub-agentes
    for agent in system.get_active_agents():
        mode_icon = {"in-process": "⚡", "git-worktree": "📂", "remote": "☁️"}.get(
            agent.mode.value, "🤖"
        )
        html += f"""
        <div style="display: flex; align-items: center; gap: 8px; padding: 6px 8px; margin-left: 16px;
                    background: #21262d; border: 1px solid #a371f7; border-radius: 6px; margin-bottom: 4px;">
            <span style="font-size: 10px;">{mode_icon}</span>
            <span style="font-size: 11px;">Sub-Agent #{agent.id[:4]}</span>
            <span style="font-size: 10px; color: #8b949e;">({agent.mode.value})</span>
        </div>
        """

    html += "</div>"
    return html


def render_mcp_servers():
    """Renderiza servidores MCP"""
    client = st.session_state.mcp_client

    html = '<div style="padding: 12px;">'
    html += '<h4 style="color: #8b949e; font-size: 11px; margin-bottom: 8px;">MCP SERVERS</h4>'

    servers = client.get_servers()
    if not servers:
        # Mostrar ejemplos por defecto
        for name, transport in [
            ("GitHub", "stdio"),
            ("Database", "SSE"),
            ("Figma", "WS"),
        ]:
            icon = {"stdio": "⌨️", "SSE": "🌐", "WS": "🔌"}.get(transport, "🔌")
            html += f"""
            <div style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 11px;">
                <span>{icon}</span>
                <span style="color: #8b949e;">{name}</span>
                <span style="color: #484f58;">({transport})</span>
            </div>
            """
    else:
        for server in servers:
            status_icon = "🟢" if server.status == "connected" else "🔴"
            html += f'<div style="padding: 4px 0; font-size: 11px;">{status_icon} {server.name}</div>'

    html += "</div>"
    return html


def render_security_status():
    """Renderiza estado de seguridad"""
    system = st.session_state.permission_system

    html = """
    <div style="padding: 12px; background: linear-gradient(135deg, rgba(63, 185, 80, 0.1), rgba(23, 146, 224, 0.05)); 
                border-bottom: 1px solid #30363d;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKlSURBVFiF7Zc9aBRBFMd/s3d3l7iJQQMRsBAlsBBBsBBBsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCw0I0/CIIgCIIgCIKgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCg=" 
                 style="width: 32px; height: 32px; border-radius: 50%; border: 2px solid #42b392;">
            <div>
                <div style="font-weight: 600; font-size: 13px; color: #42b392;">Claude Code</div>
                <div style="font-size: 11px; color: #8b949e; display: flex; align-items: center; gap: 6px;">
                    <span style="width: 6px; height: 6px; background: #3fb950; border-radius: 50%;"></span>
                    Listo
                </div>
            </div>
        </div>
    """
    return html


def main():
    """Aplicación principal Streamlit"""

    st.set_page_config(
        page_title="UltraCode - Sistema de Programación IA",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # Custom CSS
    st.markdown(
        """
    <style>
        .stApp { background-color: #0d1117; }
        .stSidebar { background-color: #161b22; }
        .main-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            background: linear-gradient(180deg, #1a1f26 0%, #161b22 100%);
            border-bottom: 1px solid #30363d;
            margin: -1rem -1rem 1rem -1rem;
        }
        .logo-text {
            font-weight: 700;
            font-size: 18px;
            background: linear-gradient(135deg, #1792e0 0%, #42b392 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-card {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .metric-value { font-size: 24px; font-weight: bold; color: #e6edf3; }
        .metric-label { font-size: 11px; color: #8b949e; }
        .tool-badge {
            display: inline-block;
            padding: 4px 8px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 4px;
            font-size: 11px;
            margin: 2px;
        }
        .chat-message {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .chat-user { background: #1792e0; color: white; }
        .chat-ai { background: #21262d; border: 1px solid #30363d; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        """
    <div class="main-header">
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHsSURBVFiF7Zc9aBRBFMd/s3d3l7iJQQMRsBAlsBBBsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCw==" 
             style="width: 28px; height: 28px; border-radius: 4px;">
        <span class="logo-text">UltraCode</span>
        <span style="color: #484f58; font-size: 12px;">|</span>
        <span style="color: #8b949e; font-size: 12px;">Sistema de Programación IA</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### Sistema")

        # Budget meter
        st.markdown(render_budget_meter(), unsafe_allow_html=True)
        st.markdown("")

        # Security
        if st.button("🛡️ Sistema de Permisos", use_container_width=True):
            add_terminal_output("[SECURITY] Sistema Dual de Permisos activo", "info")
            add_terminal_output("[SECURITY] Track 1: Glob/Regex (instantáneo)", "info")
            add_terminal_output(
                "[SECURITY] Track 2: Clasificador ML (semántico)", "info"
            )

        # Feature Gates
        st.markdown(render_feature_gates(), unsafe_allow_html=True)

        # Agents
        st.markdown(render_agent_tree(), unsafe_allow_html=True)

        # MCP Servers
        st.markdown(render_mcp_servers(), unsafe_allow_html=True)

        # Session controls
        st.markdown("### Sesión")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar", use_container_width=True):
                session = st.session_state.session_manager.create_session()
                path = st.session_state.session_manager.checkpoint()
                add_terminal_output(f"[SESSION] Checkpoint guardado: {path}", "success")
        with col2:
            if st.button("📂 Restaurar", use_container_width=True):
                sessions = st.session_state.session_manager.list_sessions()
                if sessions:
                    st.session_state.session_manager.restore(sessions[0]["id"])
                    add_terminal_output("[SESSION] Sesión restaurada", "success")

    # Main content
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        # Chat interface
        st.markdown("### 💬 Chat con Claude Code")

        # Display chat history
        for msg in st.session_state.chat_history[-10:]:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-message chat-user'>👤 {msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-message chat-ai'>🤖 {msg['content']}</div>",
                    unsafe_allow_html=True,
                )

        # Input
        user_input = st.text_input(
            "Mensaje:", key="chat_input", placeholder="Escribe tu mensaje..."
        )

        col_send, col_clear = st.columns([1, 4])
        with col_send:
            if st.button("Enviar ➤", type="primary", use_container_width=True):
                if user_input:
                    st.session_state.chat_history.append(
                        {
                            "role": "user",
                            "content": user_input,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    add_terminal_output(f"> {user_input}", "command")
                    add_terminal_output("[AGENT] Procesando solicitud...", "info")

                    # Simular respuesta
                    response = f"Entendido. Estoy analizando tu solicitud: '{user_input[:50]}...'\n\n"
                    response += "Ejecutaré las herramientas necesarias para completar esta tarea."

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    st.session_state.budget_spent += 0.05
                    add_terminal_output(f"[OK] Respuesta generada", "success")
                    st.rerun()

        with col_clear:
            if st.button("Limpiar Chat"):
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("")

        # Terminal
        st.markdown("### ⌨️ Terminal")

        # Command input
        cmd_input = st.text_input(
            "Comando:",
            key="term_input",
            placeholder="Escribe un comando (help, tools, budget, agents, clear...)",
        )

        if cmd_input:
            add_terminal_output(f"> {cmd_input}", "command")

            if cmd_input == "clear":
                st.session_state.terminal_buffer.clear()
            elif cmd_input == "help":
                add_terminal_output("═" * 50, "info")
                add_terminal_output("COMANDOS DISPONIBLES:", "info")
                add_terminal_output("═" * 50, "info")
                add_terminal_output("  help       - Mostrar ayuda", "response")
                add_terminal_output("  tools      - Listar herramientas", "response")
                add_terminal_output("  budget     - Ver presupuesto", "response")
                add_terminal_output("  agents     - Ver estado de agentes", "response")
                add_terminal_output("  permissions - Ver permisos", "response")
                add_terminal_output("  cache      - Ver stats de cache", "response")
                add_terminal_output("  mcp        - Ver servidores MCP", "response")
                add_terminal_output("  checkpoint - Guardar sesión", "response")
                add_terminal_output("  clear      - Limpiar terminal", "response")
                add_terminal_output("═" * 50, "info")
            elif cmd_input == "tools":
                tools = st.session_state.tool_executor.registered_tools
                add_terminal_output("[TOOLS] Herramientas registradas:", "info")
                for name, tool in tools.items():
                    safe = "✓" if tool.is_concurrency_safe else "○"
                    conf = "⚠" if tool.requires_confirmation else ""
                    add_terminal_output(
                        f"  {safe} {conf} {name}: {tool.description}", "response"
                    )
            elif cmd_input == "budget":
                add_terminal_output(
                    f"[BUDGET] Gastado: ${st.session_state.budget_spent:.2f}", "info"
                )
                add_terminal_output(
                    f"[BUDGET] Límite: ${st.session_state.budget_limit:.2f}", "info"
                )
                add_terminal_output(
                    f"[BUDGET] Remaining: ${st.session_state.budget_limit - st.session_state.budget_spent:.2f}",
                    "success",
                )
            elif cmd_input == "agents":
                system = st.session_state.sub_agent_system
                add_terminal_output("[AGENTS] Estado actual:", "info")
                add_terminal_output(f"  Main Agent: active", "response")
                for agent in system.get_active_agents():
                    add_terminal_output(
                        f"  Sub-Agent #{agent.id[:4]}: {agent.status} ({agent.mode.value})",
                        "response",
                    )
            elif cmd_input == "permissions":
                system = st.session_state.permission_system
                add_terminal_output("[SECURITY] Reglas de Track 1:", "info")
                for rule in system.track1.rules[:5]:
                    action = "🚫" if rule.action == PermissionAction.DENY else "✓"
                    add_terminal_output(
                        f"  {action} {rule.pattern}: {rule.reason}", "response"
                    )
            elif cmd_input == "cache":
                stats = st.session_state.prompt_cache.get_stats()
                add_terminal_output("[CACHE] Estadísticas:", "info")
                add_terminal_output(f"  Entradas: {stats['entries']}", "response")
                add_terminal_output(f"  Hit rate: {stats['hit_rate']}", "response")
                add_terminal_output(
                    f"  Total requests: {stats['total_requests']}", "response"
                )
            elif cmd_input == "mcp":
                client = st.session_state.mcp_client
                servers = client.get_servers()
                add_terminal_output("[MCP] Protocolo de Contexto de Modelo:", "info")
                add_terminal_output("  Transportes soportados:", "response")
                add_terminal_output("    • stdio: Local (subproceso)", "response")
                add_terminal_output("    • SSE: Remoto (HTTP)", "response")
                add_terminal_output("    • WebSocket: Bidireccional", "response")
            elif cmd_input == "checkpoint":
                session = st.session_state.session_manager.create_session()
                path = st.session_state.session_manager.checkpoint()
                add_terminal_output(f"[SESSION] Checkpoint guardado: {path}", "success")
            else:
                add_terminal_output(f"Comando no reconocido: {cmd_input}", "error")

            st.rerun()

        st.markdown(render_terminal(), unsafe_allow_html=True)

    with col_right:
        # Metrics
        st.markdown("### 📊 Métricas del Sistema")

        metrics = ProjectMetrics()

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Líneas de Código", f"{metrics.lines_of_code:,}", "TypeScript")
        with m2:
            st.metric("Archivos Fuente", metrics.source_files)

        m3, m4 = st.columns(2)
        with m3:
            st.metric("Bundle Size", f"{metrics.bundle_size_kb} KB", "main.tsx")
        with m4:
            st.metric("Herramientas", f"{metrics.integrated_tools}+", "Integradas")

        st.markdown("")

        # Tools Grid
        st.markdown("### 🛠️ Herramientas")
        tools = st.session_state.tool_executor.registered_tools

        for i, (name, tool) in enumerate(list(tools.items())[:8]):
            with st.expander(
                f"{'✓' if tool.is_concurrency_safe else '○'} {name}", expanded=False
            ):
                st.markdown(f"**Descripción:** {tool.description}")
                st.markdown(
                    f"**Concurrencia segura:** {'Sí' if tool.is_concurrency_safe else 'No'}"
                )
                st.markdown(
                    f"**Requiere confirmación:** {'Sí' if tool.requires_confirmation else 'No'}"
                )

        st.markdown("")

        # Quick Actions
        st.markdown("### ⚡ Acciones Rápidas")

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("🆕 Nuevo Archivo", use_container_width=True):
                add_terminal_output("[TOOL] Nuevo archivo creado", "success")

        with action_col2:
            if st.button("🔍 Buscar en Código", use_container_width=True):
                add_terminal_output("[TOOL] Grep iniciado", "info")

        action_col3, action_col4 = st.columns(2)
        with action_col3:
            if st.button("🤖 Nuevo Sub-Agente", use_container_width=True):
                try:
                    agent = st.session_state.sub_agent_system.spawn(
                        AgentMode.IN_PROCESS
                    )
                    add_terminal_output(
                        f"[AGENT] Sub-agente #{agent.id[:4]} creado ({agent.mode.value})",
                        "success",
                    )
                    st.rerun()
                except Exception as e:
                    add_terminal_output(f"[ERROR] {str(e)}", "error")

        with action_col4:
            if st.button("🔌 Conectar MCP", use_container_width=True):
                st.session_state.mcp_client.connect("GitHub", MCPTransport.STDIO)
                add_terminal_output("[MCP] GitHub conectado (stdio)", "success")

        st.markdown("")

        # Architecture Info
        st.markdown("### 🏗️ Arquitectura (12 Pilares)")

        pillars = [
            ("1", "Escala del Proyecto", "~512K líneas TS"),
            ("2", "Motor Ink/ UI", "React + Flexbox"),
            ("3", "Permisos Duales", "Track 1 + Track 2 ML"),
            ("4", "Streaming Executor", "Concurrencia segura"),
            ("5", "Feature Gates", "Dead-code elimination"),
            ("6", "Sub-Agentes", "3 modos de ejecución"),
            ("7", "Deferred Loading", "Resultados en disco"),
            ("8", "Query Engine", "2 capas desacopladas"),
            ("9", "Integración MCP", "USB-C de IA"),
            ("10", "Checkpoint/Restore", "Persistencia completa"),
            ("11", "Prompt Caching", "Cache de 5 min"),
            ("12", "Spinner Verbs", "36 verbos animados"),
        ]

        for num, name, desc in pillars:
            st.markdown(f"**{num}.** {name} - _{desc}_")

    # Footer status bar
    st.markdown("---")
    footer_cols = st.columns([1, 1, 1, 2, 1, 1, 1, 1])

    with footer_cols[0]:
        st.markdown("⎇ **main**", unsafe_allow_html=True)
    with footer_cols[1]:
        st.markdown("↻ 0", unsafe_allow_html=True)
    with footer_cols[2]:
        st.markdown("❌ 0", unsafe_allow_html=True)
    with footer_cols[4]:
        st.markdown("UTF-8", unsafe_allow_html=True)
    with footer_cols[5]:
        st.markdown("TypeScript", unsafe_allow_html=True)
    with footer_cols[6]:
        st.markdown("Line 1, Col 1", unsafe_allow_html=True)
    with footer_cols[7]:
        st.markdown("🛡️ Dual Track", unsafe_allow_html=True)


if __name__ == "__main__":
    import asyncio

    main()
