"""
Executor Module - Streaming Tool Executor
=======================================
Implementación del pilar 4 - Ejecución concurrente de herramientas.
"""

import os
import json
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


@dataclass
class ToolCall:
    """Representación de una llamada a herramienta"""

    id: str
    name: str
    arguments: Dict[str, Any]
    is_concurrency_safe: bool = True
    depends_on: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class ToolResult:
    """Resultado de ejecución de herramienta"""

    tool_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0
    temp_file: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolDefinition:
    """Definición de herramienta"""

    name: str
    description: str
    parameters: Dict
    is_concurrency_safe: bool = True
    requires_confirmation: bool = False
    category: str = "general"


class ToolExecutor:
    """Ejecutor base de herramientas"""

    def __init__(self, temp_dir: str = "/tmp/ultracode"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Ejecuta una herramienta"""
        raise NotImplementedError

    def save_result(self, tool_id: str, data: Any) -> str:
        """Guarda resultado en disco"""
        file_path = os.path.join(self.temp_dir, f"result_{tool_id}.json")
        with open(file_path, "w") as f:
            json.dump({"tool_id": tool_id, "output": str(data)}, f)
        return file_path


class StreamingToolExecutor(ToolExecutor):
    """
    Ejecutor de herramientas con streaming y concurrencia.

    Implementa el patrón StreamingToolExecutor de Claude Code con:
    - Ejecución concurrente de herramientas isConcurrencySafe
    - Buffer ordenado para mantener coherencia
    - Deferred loading de resultados
    """

    def __init__(self, permission_system=None, max_workers: int = 10):
        super().__init__()
        self.permission_system = permission_system
        self.registered_tools: Dict[str, ToolDefinition] = {}
        self.execution_buffer: Dict[str, ToolResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tool_functions: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []

        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Registra herramientas integradas"""
        tools = [
            ToolDefinition(
                name="Read",
                description="Lee contenido de archivos del sistema",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Ruta del archivo"}
                    },
                },
                is_concurrency_safe=True,
                category="filesystem",
            ),
            ToolDefinition(
                name="Write",
                description="Escribe contenido en archivos",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                },
                is_concurrency_safe=False,
                category="filesystem",
            ),
            ToolDefinition(
                name="Edit",
                description="Edita líneas específicas de un archivo",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "oldString": {"type": "string"},
                        "newString": {"type": "string"},
                    },
                },
                is_concurrency_safe=False,
                category="filesystem",
            ),
            ToolDefinition(
                name="Grep",
                description="Busca patrones en archivos",
                parameters={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                    },
                },
                is_concurrency_safe=True,
                category="search",
            ),
            ToolDefinition(
                name="Glob",
                description="Encuentra archivos por patrón Glob",
                parameters={
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                },
                is_concurrency_safe=True,
                category="search",
            ),
            ToolDefinition(
                name="Bash",
                description="Ejecuta comandos de shell",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Comando a ejecutar",
                        }
                    },
                },
                is_concurrency_safe=False,
                requires_confirmation=True,
                category="system",
            ),
            ToolDefinition(
                name="WebSearch",
                description="Busca información en la web",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                },
                is_concurrency_safe=True,
                category="web",
            ),
            ToolDefinition(
                name="TodoWrite",
                description="Gestiona lista de tareas",
                parameters={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "complete", "remove"],
                        },
                        "task": {"type": "string"},
                    },
                },
                is_concurrency_safe=True,
                category="productivity",
            ),
        ]

        for tool in tools:
            self.register_tool(tool)

    def register_tool(self, tool: ToolDefinition):
        """Registra una nueva herramienta"""
        self.registered_tools[tool.name] = tool

    def register_function(self, name: str, func: Callable):
        """Registra función para una herramienta"""
        self._tool_functions[name] = func

    def add_callback(self, callback: Callable):
        """Agrega callback para eventos de ejecución"""
        self._callbacks.append(callback)

    async def execute(self, tool_call: ToolCall, context: Dict = None) -> ToolResult:
        """Ejecuta una herramienta individual"""
        start_time = time.time()

        # Verificar permisos si está configurado
        if self.permission_system:
            perm_result = await self.permission_system.check(
                f"{tool_call.name} {tool_call.arguments}", tool_call.name, context
            )
            if not perm_result.allowed:
                return ToolResult(
                    tool_id=tool_call.id,
                    success=False,
                    output=None,
                    error=f"Permiso denegado: {perm_result.reason}",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

        # Obtener función de herramienta
        tool_func = self._tool_functions.get(tool_call.name)
        if not tool_func:
            # Usar función por defecto
            tool_func = self._get_default_tool(tool_call.name)

        try:
            # Ejecutar
            output = await tool_func(tool_call.arguments)

            # Guardar resultado en disco
            temp_file = self.save_result(tool_call.id, output)

            result = ToolResult(
                tool_id=tool_call.id,
                success=True,
                output=output,
                execution_time_ms=(time.time() - start_time) * 1000,
                temp_file=temp_file,
            )

            # Notificar callbacks
            for callback in self._callbacks:
                try:
                    callback("tool_completed", result)
                except:
                    pass

            return result

        except Exception as e:
            return ToolResult(
                tool_id=tool_call.id,
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def execute_concurrent(
        self, tool_calls: List[ToolCall], context: Dict = None
    ) -> List[ToolResult]:
        """
        Ejecuta múltiples herramientas con concurrencia.

        Implementa Buffered Ordering: los resultados se almacenan
        temporalmente y se liberan en el orden original solicitado.
        """
        # Clasificar por isConcurrencySafe
        safe_calls = [
            tc for tc in tool_calls if tc.is_concurrency_safe and not tc.depends_on
        ]
        unsafe_calls = [
            tc for tc in tool_calls if not tc.is_concurrency_safe or tc.depends_on
        ]

        results = []
        result_order = {}  # tool_id -> result

        # Ejecutar seguros en paralelo
        futures = {
            self.executor.submit(self._execute_async, tc, context): tc
            for tc in safe_calls
        }

        for future in as_completed(futures):
            tool_call = futures[future]
            try:
                result = future.result()
                result_order[result.tool_id] = result
            except Exception as e:
                result_order[tool_call.id] = ToolResult(
                    tool_id=tool_call.id, success=False, output=None, error=str(e)
                )

        # Ejecutar no-seguros secuencialmente
        for tc in unsafe_calls:
            result = await self.execute(tc, context)
            result_order[result.tool_id] = result

        # Retornar en orden original
        for tc in tool_calls:
            results.append(result_order.get(tc.id))

        return results

    def _execute_async(self, tool_call: ToolCall, context: Dict) -> ToolResult:
        """Ejecuta de forma asíncrona para ThreadPool"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.execute(tool_call, context))
        finally:
            loop.close()

    def _get_default_tool(self, name: str) -> Callable:
        """Obtiene función por defecto para herramienta"""
        tools = {
            "Read": self._tool_read,
            "Write": self._tool_write,
            "Edit": self._tool_edit,
            "Grep": self._tool_grep,
            "Glob": self._tool_glob,
            "Bash": self._tool_bash,
            "WebSearch": self._tool_websearch,
            "TodoWrite": self._tool_todowrite,
        }
        return tools.get(name, self._tool_unknown)

    async def _tool_read(self, args: Dict) -> str:
        """Herramienta Read - Lee archivos"""
        path = args.get("path", "")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(100000)  # Limitar a 100KB
        return f"[Error] Archivo no encontrado: {path}"

    async def _tool_write(self, args: Dict) -> str:
        """Herramienta Write - Escribe archivos"""
        path = args.get("path", "")
        content = args.get("content", "")
        os.makedirs(
            os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[OK] Archivo escrito: {path}"

    async def _tool_edit(self, args: Dict) -> str:
        """Herramienta Edit - Edita archivos"""
        path = args.get("path", "")
        old = args.get("oldString", "")
        new = args.get("newString", "")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if old in content:
                content = content.replace(old, new)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"[OK] Archivo editado: {path}"
            return f"[Error] Texto no encontrado: {old[:50]}..."
        return f"[Error] Archivo no encontrado: {path}"

    async def _tool_grep(self, args: Dict) -> str:
        """Herramienta Grep - Busca patrones"""
        import re

        pattern = args.get("pattern", "")
        path = args.get("path", ".")
        results = []
        for root, _, files in os.walk(path):
            for file in files[:50]:  # Limitar a 50 archivos
                if file.endswith((".py", ".js", ".ts", ".tsx", ".md", ".txt", ".json")):
                    fpath = os.path.join(root, file)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    results.append(f"{fpath}:{i}: {line.strip()[:100]}")
                                    if len(results) >= 100:
                                        break
                    except:
                        pass
        return "\n".join(results) if results else "[Sin coincidencias]"

    async def _tool_glob(self, args: Dict) -> str:
        """Herramienta Glob - Encuentra archivos"""
        import re

        pattern = args.get("pattern", "")
        results = []
        pattern_regex = (
            pattern.replace(".", r"\.").replace("**/", "**/").replace("*", "[^/]*")
        )
        for root, _, files in os.walk("."):
            for file in files:
                if re.search(pattern.replace("**/", ".*").replace("*", ".*"), file):
                    results.append(os.path.join(root, file))
                    if len(results) >= 100:
                        break
        return "\n".join(results) if results else "[Sin coincidencias]"

    async def _tool_bash(self, args: Dict) -> str:
        """Herramienta Bash - Ejecuta comandos"""
        import subprocess

        command = args.get("command", "")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout or result.stderr
        except subprocess.TimeoutExpired:
            return "[Error] Timeout: Comando excedió 30 segundos"
        except Exception as e:
            return f"[Error] {str(e)}"

    async def _tool_websearch(self, args: Dict) -> str:
        """Herramienta WebSearch - Busca en web"""
        return f"[Simulación] Búsqueda para: {args.get('query', '')}\n[Requiere API key para implementación real]"

    async def _tool_todowrite(self, args: Dict) -> str:
        """Herramienta TodoWrite - Gestiona tareas"""
        action = args.get("action", "")
        task = args.get("task", "")
        return f"[OK] Todo {action}: {task}"

    async def _tool_unknown(self, args: Dict) -> str:
        """Herramienta desconocida"""
        return "[Error] Herramienta desconocida"

    def get_tools(self) -> List[ToolDefinition]:
        """Obtiene lista de herramientas"""
        return list(self.registered_tools.values())

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Obtiene herramienta por nombre"""
        return self.registered_tools.get(name)
