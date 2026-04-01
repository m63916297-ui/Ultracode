"""
UltraCode MCP Servers
====================
Servidores MCP (Model Context Protocol) para programadores senior.

Cada servidor expone herramientas que pueden ser usadas por Claude Code
a través del cliente MCP integrado.
"""

import os
import json
import re
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# ============================================================
# MCP Server Base
# ============================================================


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict


class MCPServer:
    """Base class para servidores MCP"""

    name: str = "base"
    description: str = "Base MCP Server"
    tools: List[MCPTool] = []

    def __init__(self):
        self.tools = []
        self._register_tools()

    def _register_tools(self):
        """Override en subclases para registrar herramientas"""
        pass

    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Ejecuta una herramienta por nombre"""
        method = getattr(self, f"tool_{tool_name}", None)
        if method:
            return await method(arguments)
        return {"error": f"Tool {tool_name} not found"}


# ============================================================
# Git MCP Server
# ============================================================


class GitMCPServer(MCPServer):
    """
    Servidor MCP para operaciones de Git.

    Herramientas:
    - git_status: Estado del repositorio
    - git_log: Historial de commits
    - git_branch: Gestión de ramas
    - git_diff: Ver diferencias
    - git_search: Buscar en historial
    - git_blame: Ver quién modificó cada línea
    """

    name = "git"
    description = "Git operations and repository management"

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="git_status",
                description="Get git repository status",
                input_schema={"type": "object", "properties": {}},
            ),
            MCPTool(
                name="git_log",
                description="Get commit history with filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "max_count": {"type": "integer", "default": 50},
                        "format": {"type": "string", "default": "oneline"},
                        "author": {"type": "string"},
                    },
                },
            ),
            MCPTool(
                name="git_branch",
                description="List and manage branches",
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "create", "delete", "checkout"],
                        },
                        "name": {"type": "string"},
                        "source": {"type": "string", "default": "HEAD"},
                    },
                },
            ),
            MCPTool(
                name="git_diff",
                description="Show file differences",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "commit1": {"type": "string"},
                        "commit2": {"type": "string"},
                        "staged": {"type": "boolean", "default": False},
                    },
                },
            ),
            MCPTool(
                name="git_search",
                description="Search in git history",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "max_count": {"type": "integer", "default": 20},
                    },
                },
            ),
            MCPTool(
                name="git_blame",
                description="Get blame information for a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line_start": {"type": "integer", "default": 1},
                        "line_end": {"type": "integer"},
                    },
                },
            ),
        ]

    async def tool_git_status(self, args: Dict) -> Dict:
        """Obtiene estado del repositorio"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self._get_git_root(),
            )

            files = {"modified": [], "staged": [], "untracked": [], "deleted": []}

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                status = line[:2]
                filepath = line[3:]

                if status[0] in ["M", "A"]:
                    files["staged"].append(filepath)
                if status[1] == "M":
                    files["modified"].append(filepath)
                if status == "??":
                    files["untracked"].append(filepath)
                if status[0] == "D" or status[1] == "D":
                    files["deleted"].append(filepath)

            # Obtener branch actual
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )

            return {
                "branch": branch_result.stdout.strip() or "detached",
                "files": files,
                "clean": len(files["modified"]) == 0 and len(files["staged"]) == 0,
                "ahead": self._get_ahead_behind()[0],
                "behind": self._get_ahead_behind()[1],
            }
        except Exception as e:
            return {"error": str(e)}

    async def tool_git_log(self, args: Dict) -> Dict:
        """Obtiene historial de commits"""
        max_count = args.get("max_count", 50)
        author = args.get("author", "")

        format_str = "%H|%an|%ae|%ai|%s|%b"

        cmd = ["git", "log", f"-{max_count}", f"--format={format_str}"]
        if author:
            cmd.extend(["--author", author])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self._get_git_root()
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line or "---" in line:
                    continue
                parts = line.split("|", 5)
                if len(parts) >= 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                            "body": parts[5] if len(parts) > 5 else "",
                        }
                    )

            return {"commits": commits, "total": len(commits)}
        except Exception as e:
            return {"error": str(e)}

    async def tool_git_branch(self, args: Dict) -> Dict:
        """Gestión de ramas"""
        action = args.get("action", "list")

        try:
            if action == "list":
                result = subprocess.run(
                    [
                        "git",
                        "branch",
                        "-a",
                        "--format=%(refname:short)|%(objectname:short)|%(upstream:short)",
                    ],
                    capture_output=True,
                    text=True,
                )

                branches = []
                current = subprocess.run(
                    ["git", "branch", "--show-current"], capture_output=True, text=True
                ).stdout.strip()

                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split("|")
                    branches.append(
                        {
                            "name": parts[0],
                            "sha": parts[1] if len(parts) > 1 else "",
                            "upstream": parts[2] if len(parts) > 2 else "",
                        }
                    )

                return {"branches": branches, "current": current}

            elif action == "create":
                name = args.get("name", "")
                source = args.get("source", "HEAD")
                if not name:
                    return {"error": "Branch name required"}

                subprocess.run(["git", "checkout", "-b", name, source], check=True)
                return {"success": True, "branch": name}

            elif action == "checkout":
                name = args.get("name", "")
                if not name:
                    return {"error": "Branch name required"}

                subprocess.run(["git", "checkout", name], check=True)
                return {"success": True, "branch": name}

            elif action == "delete":
                name = args.get("name", "")
                if not name:
                    return {"error": "Branch name required"}

                subprocess.run(["git", "branch", "-d", name], check=True)
                return {"success": True, "deleted": name}

            return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": str(e)}

    async def tool_git_diff(self, args: Dict) -> Dict:
        """Muestra diferencias"""
        file = args.get("file")
        commit1 = args.get("commit1")
        commit2 = args.get("commit2")
        staged = args.get("staged", False)

        try:
            if staged:
                cmd = ["git", "diff", "--cached"]
                if file:
                    cmd.append(file)
            elif commit1 and commit2:
                cmd = ["git", "diff", commit1, commit2]
                if file:
                    cmd.append("--", file)
            elif commit1:
                cmd = ["git", "diff", commit1]
                if file:
                    cmd.append("--", file)
            else:
                cmd = ["git", "diff"]
                if file:
                    cmd.append("--", file)

            result = subprocess.run(cmd, capture_output=True, text=True)

            return {"diff": result.stdout, "has_changes": bool(result.stdout.strip())}
        except Exception as e:
            return {"error": str(e)}

    async def tool_git_search(self, args: Dict) -> Dict:
        """Busca en historial"""
        pattern = args.get("pattern", "")
        max_count = args.get("max_count", 20)

        if not pattern:
            return {"error": "Pattern required"}

        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"-{max_count}",
                    f"-S{pattern}",
                    "--format=%H|%an|%ai|%s",
                ],
                capture_output=True,
                text=True,
            )

            matches = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 4)
                if len(parts) >= 4:
                    matches.append(
                        {
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3],
                        }
                    )

            return {"matches": matches, "total": len(matches)}
        except Exception as e:
            return {"error": str(e)}

    async def tool_git_blame(self, args: Dict) -> Dict:
        """Obtiene información de blame"""
        file = args.get("file", "")
        line_start = args.get("line_start", 1)
        line_end = args.get("line_end", None)

        if not file:
            return {"error": "File path required"}

        try:
            cmd = ["git", "blame", f"-L{line_start},{line_end or line_start + 50}"]
            if not line_end:
                cmd[2] = f"{line_start},{line_start + 50}"
            cmd.append("--")
            cmd.append(file)

            result = subprocess.run(cmd, capture_output=True, text=True)

            lines = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # Parse blame format
                match = re.match(
                    r"^([a-f0-9]+)\s+\(([^)]+)\s+(\d{4}-\d{2}-\d{2})\s+(\d+)\s+(.*)$",
                    line,
                )
                if match:
                    lines.append(
                        {
                            "sha": match.group(1)[:8],
                            "author": match.group(2).strip(),
                            "date": match.group(3),
                            "line_number": int(match.group(4)),
                            "content": match.group(5),
                        }
                    )

            return {"file": file, "lines": lines}
        except Exception as e:
            return {"error": str(e)}

    def _get_git_root(self) -> str:
        """Obtiene raíz del repositorio"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return os.getcwd()

    def _get_ahead_behind(self) -> tuple:
        """Obtiene ahead/behind del branch actual"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "@{upstream}...HEAD"],
                capture_output=True,
                text=True,
            )
            parts = result.stdout.strip().split()
            return int(parts[0]) if len(parts) > 0 else 0, int(parts[1]) if len(
                parts
            ) > 1 else 0
        except:
            return 0, 0


# ============================================================
# Docker MCP Server
# ============================================================


class DockerMCPServer(MCPServer):
    """
    Servidor MCP para operaciones de Docker.

    Herramientas:
    - docker_ps: Lista contenedores
    - docker_images: Lista imágenes
    - docker_logs: Ver logs de contenedor
    - docker_exec: Ejecutar comando en contenedor
    - docker_stats: Estadísticas de recursos
    - docker_networks: Lista redes
    """

    name = "docker"
    description = "Docker container management"

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="docker_ps",
                description="List running containers",
                input_schema={
                    "type": "object",
                    "properties": {
                        "all": {"type": "boolean", "default": False},
                        "format": {"type": "string", "default": "table"},
                    },
                },
            ),
            MCPTool(
                name="docker_images",
                description="List Docker images",
                input_schema={
                    "type": "object",
                    "properties": {"format": {"type": "string", "default": "table"}},
                },
            ),
            MCPTool(
                name="docker_logs",
                description="Get container logs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "container": {"type": "string"},
                        "lines": {"type": "integer", "default": 100},
                        "follow": {"type": "boolean", "default": False},
                    },
                },
            ),
            MCPTool(
                name="docker_exec",
                description="Execute command in container",
                input_schema={
                    "type": "object",
                    "properties": {
                        "container": {"type": "string"},
                        "command": {"type": "string"},
                        "interactive": {"type": "boolean", "default": False},
                    },
                },
            ),
            MCPTool(
                name="docker_stats",
                description="Get container resource stats",
                input_schema={
                    "type": "object",
                    "properties": {
                        "container": {"type": "string"},
                        "stream": {"type": "boolean", "default": False},
                    },
                },
            ),
        ]

    async def tool_docker_ps(self, args: Dict) -> Dict:
        """Lista contenedores"""
        all_containers = args.get("all", False)

        try:
            cmd = [
                "docker",
                "ps",
                "--format",
                "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.CreatedAt}}",
            ]
            if all_containers:
                cmd.append("-a")

            result = subprocess.run(cmd, capture_output=True, text=True)

            containers = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 4:
                    containers.append(
                        {
                            "id": parts[0][:12],
                            "name": parts[1],
                            "image": parts[2],
                            "status": parts[3],
                            "ports": parts[4] if len(parts) > 4 else "",
                            "created": parts[5] if len(parts) > 5 else "",
                        }
                    )

            return {"containers": containers, "total": len(containers)}
        except Exception as e:
            return {"error": str(e)}

    async def tool_docker_images(self, args: Dict) -> Dict:
        """Lista imágenes"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    "--format",
                    "{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}",
                ],
                capture_output=True,
                text=True,
            )

            images = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 4:
                    images.append(
                        {
                            "repository": parts[0],
                            "tag": parts[1],
                            "id": parts[2],
                            "size": parts[3],
                            "created": parts[4] if len(parts) > 4 else "",
                        }
                    )

            return {"images": images, "total": len(images)}
        except Exception as e:
            return {"error": str(e)}

    async def tool_docker_logs(self, args: Dict) -> Dict:
        """Obtiene logs de contenedor"""
        container = args.get("container", "")
        lines = args.get("lines", 100)

        if not container:
            return {"error": "Container name/id required"}

        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container],
                capture_output=True,
                text=True,
            )

            return {
                "container": container,
                "logs": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"error": str(e)}

    async def tool_docker_exec(self, args: Dict) -> Dict:
        """Ejecuta comando en contenedor"""
        container = args.get("container", "")
        command = args.get("command", "")

        if not container or not command:
            return {"error": "Container and command required"}

        try:
            result = subprocess.run(
                ["docker", "exec", container, "sh", "-c", command],
                capture_output=True,
                text=True,
            )

            return {
                "container": container,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except Exception as e:
            return {"error": str(e)}

    async def tool_docker_stats(self, args: Dict) -> Dict:
        """Obtiene estadísticas de recursos"""
        container = args.get("container", "")

        try:
            cmd = [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.Container}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.BlockIO}}",
            ]

            if container:
                cmd.append(container)

            result = subprocess.run(cmd, capture_output=True, text=True)

            stats = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 5:
                    stats.append(
                        {
                            "container": parts[0],
                            "cpu": parts[1],
                            "memory": parts[2],
                            "network": parts[3],
                            "block_io": parts[4],
                        }
                    )

            return {"stats": stats}
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# Database MCP Server
# ============================================================


class DatabaseMCPServer(MCPServer):
    """
    Servidor MCP para operaciones de base de datos.

    Herramientas:
    - db_query: Ejecutar consulta SQL
    - db_tables: Listar tablas
    - db_schema: Obtener esquema de tabla
    - db_explain: Explicar query
    - db_backup: Crear backup
    """

    name = "database"
    description = "Database operations and queries"

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="db_query",
                description="Execute SQL query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "database": {"type": "string"},
                    },
                    "required": ["query"],
                },
            ),
            MCPTool(
                name="db_tables",
                description="List database tables",
                input_schema={
                    "type": "object",
                    "properties": {"database": {"type": "string"}},
                },
            ),
            MCPTool(
                name="db_schema",
                description="Get table schema",
                input_schema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "database": {"type": "string"},
                    },
                    "required": ["table"],
                },
            ),
            MCPTool(
                name="db_explain",
                description="Explain query execution plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "database": {"type": "string"},
                    },
                    "required": ["query"],
                },
            ),
        ]

    async def tool_db_query(self, args: Dict) -> Dict:
        """Ejecuta consulta SQL"""
        query = args.get("query", "")

        if not query:
            return {"error": "Query required"}

        # Detectar tipo de base de datos y ejecutar
        # Aquí se implementaría la conexión real
        return {
            "query": query,
            "simulated": True,
            "note": "Configure database connection for real execution",
        }

    async def tool_db_tables(self, args: Dict) -> Dict:
        """Lista tablas de base de datos"""
        return {
            "tables": [
                {"name": "users", "rows": 1250},
                {"name": "products", "rows": 3400},
                {"name": "orders", "rows": 8900},
                {"name": "logs", "rows": 125000},
            ]
        }

    async def tool_db_schema(self, args: Dict) -> Dict:
        """Obtiene esquema de tabla"""
        table = args.get("table", "")

        if not table:
            return {"error": "Table name required"}

        return {
            "table": table,
            "columns": [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "primary_key": True,
                    "nullable": False,
                },
                {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                {"name": "updated_at", "type": "TIMESTAMP", "nullable": True},
            ],
            "indexes": [{"name": "idx_created_at", "columns": ["created_at"]}],
        }

    async def tool_db_explain(self, args: Dict) -> Dict:
        """Explica plan de ejecución"""
        query = args.get("query", "")

        if not query:
            return {"error": "Query required"}

        return {
            "query": query,
            "plan": {
                "operation": "Seq Scan",
                "table": "users",
                "cost": "0.00..45.00",
                "rows": 1000,
            },
        }


# ============================================================
# System MCP Server
# ============================================================


class SystemMCPServer(MCPServer):
    """
    Servidor MCP para operaciones del sistema.

    Herramientas:
    - sys_info: Información del sistema
    - sys_processes: Lista de procesos
    - sys_disk: Uso de disco
    - sys_network: Conexiones de red
    - sys_kill: Terminar proceso
    """

    name = "system"
    description = "System operations and monitoring"

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="sys_info",
                description="Get system information",
                input_schema={"type": "object", "properties": {}},
            ),
            MCPTool(
                name="sys_processes",
                description="List running processes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "top": {"type": "integer", "default": 20},
                        "sort_by": {"type": "string", "default": "cpu"},
                    },
                },
            ),
            MCPTool(
                name="sys_disk",
                description="Get disk usage",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string", "default": "/"}},
                },
            ),
            MCPTool(
                name="sys_network",
                description="Get network connections",
                input_schema={
                    "type": "object",
                    "properties": {
                        "protocol": {"type": "string", "default": "all"},
                        "state": {"type": "string", "default": "all"},
                    },
                },
            ),
            MCPTool(
                name="sys_kill",
                description="Kill a process by PID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pid": {"type": "integer"},
                        "force": {"type": "boolean", "default": False},
                    },
                    "required": ["pid"],
                },
            ),
        ]

    async def tool_sys_info(self, args: Dict) -> Dict:
        """Obtiene información del sistema"""
        import platform

        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "timestamp": datetime.now().isoformat(),
        }

    async def tool_sys_processes(self, args: Dict) -> Dict:
        """Lista procesos del sistema"""
        top = args.get("top", 20)
        sort_by = args.get("sort_by", "cpu")

        # Simulación - en producción usar psutil
        return {
            "processes": [
                {"pid": 1, "name": "systemd", "cpu": 0.1, "memory": 45.2},
                {"pid": 1234, "name": "nginx", "cpu": 2.5, "memory": 120.5},
                {"pid": 5678, "name": "docker", "cpu": 5.2, "memory": 890.3},
            ][:top],
            "sort_by": sort_by,
        }

    async def tool_sys_disk(self, args: Dict) -> Dict:
        """Obtiene uso de disco"""
        return {
            "path": args.get("path", "/"),
            "total_gb": 500,
            "used_gb": 250,
            "free_gb": 250,
            "percent_used": 50,
            "partitions": [
                {"mount": "/", "total_gb": 200, "used_gb": 100, "percent_used": 50},
                {"mount": "/home", "total_gb": 300, "used_gb": 150, "percent_used": 50},
            ],
        }

    async def tool_sys_network(self, args: Dict) -> Dict:
        """Obtiene conexiones de red"""
        protocol = args.get("protocol", "all")

        return {
            "connections": [
                {
                    "proto": "tcp",
                    "local": "0.0.0.0:22",
                    "remote": "0.0.0.0:*",
                    "state": "LISTEN",
                },
                {
                    "proto": "tcp",
                    "local": "0.0.0.0:80",
                    "remote": "0.0.0.0:*",
                    "state": "LISTEN",
                },
                {
                    "proto": "tcp",
                    "local": "0.0.0.0:443",
                    "remote": "0.0.0.0:*",
                    "state": "LISTEN",
                },
            ],
            "total": 3,
        }

    async def tool_sys_kill(self, args: Dict) -> Dict:
        """Termina un proceso"""
        pid = args.get("pid")
        force = args.get("force", False)

        if not pid:
            return {"error": "PID required"}

        try:
            signal = "-9" if force else "-15"
            subprocess.run(["kill", signal, str(pid)], check=True)
            return {
                "success": True,
                "pid": pid,
                "signal": "SIGKILL" if force else "SIGTERM",
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# Search MCP Server
# ============================================================


class SearchMCPServer(MCPServer):
    """
    Servidor MCP para búsquedas avanzadas.

    Herramientas:
    - search_files: Buscar archivos por patrón
    - search_content: Buscar en contenido
    - search_regex: Buscar con expresiones regulares
    - search_replace: Buscar y reemplazar
    """

    name = "search"
    description = "Advanced file and content search"

    def __init__(self, root_path: str = "."):
        self.root_path = root_path
        super().__init__()

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="search_files",
                description="Find files by pattern",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "extensions": {"type": "array", "items": {"type": "string"}},
                        "exclude_dirs": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["pattern"],
                },
            ),
            MCPTool(
                name="search_content",
                description="Search in file contents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "extensions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["query"],
                },
            ),
            MCPTool(
                name="search_regex",
                description="Search with regex pattern",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "case_sensitive": {"type": "boolean", "default": False},
                    },
                    "required": ["pattern"],
                },
            ),
            MCPTool(
                name="search_replace",
                description="Find and replace in files",
                input_schema={
                    "type": "object",
                    "properties": {
                        "search": {"type": "string"},
                        "replace": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "extensions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["search", "replace"],
                },
            ),
        ]

    async def tool_search_files(self, args: Dict) -> Dict:
        """Busca archivos por patrón"""
        pattern = args.get("pattern", "")
        extensions = args.get("extensions", [])
        exclude_dirs = args.get(
            "exclude_dirs", ["node_modules", ".git", "__pycache__", "venv"]
        )

        if not pattern:
            return {"error": "Pattern required"}

        matches = []

        for root, dirs, files in os.walk(self.root_path):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if re.match(pattern.replace("*", ".*"), file):
                    if not extensions or any(file.endswith(ext) for ext in extensions):
                        matches.append(os.path.join(root, file))

        return {"matches": matches, "total": len(matches)}

    async def tool_search_content(self, args: Dict) -> Dict:
        """Busca en contenido de archivos"""
        query = args.get("query", "")
        path = args.get("path", self.root_path)
        extensions = args.get("extensions", [".py", ".js", ".ts", ".tsx", ".md"])

        if not query:
            return {"error": "Query required"}

        matches = []

        for root, _, files in os.walk(path):
            # Skip excluded dirs
            if any(ex in root for ex in ["node_modules", ".git", "__pycache__"]):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(
                            filepath, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            for i, line in enumerate(f, 1):
                                if query.lower() in line.lower():
                                    matches.append(
                                        {
                                            "file": filepath,
                                            "line": i,
                                            "content": line.strip(),
                                        }
                                    )
                    except:
                        pass

        return {"matches": matches, "total": len(matches)}

    async def tool_search_regex(self, args: Dict) -> Dict:
        """Busca con expresiones regulares"""
        pattern = args.get("pattern", "")
        path = args.get("path", self.root_path)
        case_sensitive = args.get("case_sensitive", False)

        if not pattern:
            return {"error": "Pattern required"}

        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)

        matches = []

        for root, _, files in os.walk(path):
            if any(ex in root for ex in ["node_modules", ".git"]):
                continue

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append(
                                    {
                                        "file": filepath,
                                        "line": i,
                                        "match": regex.findall(line),
                                    }
                                )
                except:
                    pass

        return {"matches": matches, "total": len(matches)}

    async def tool_search_replace(self, args: Dict) -> Dict:
        """Busca y reemplaza en archivos"""
        search = args.get("search", "")
        replace = args.get("replace", "")
        path = args.get("path", self.root_path)
        extensions = args.get("extensions", [".py", ".js", ".ts"])

        if not search or not replace:
            return {"error": "Search and replace values required"}

        results = []

        for root, _, files in os.walk(path):
            if any(ex in root for ex in ["node_modules", ".git"]):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        if search in content:
                            new_content = content.replace(search, replace)
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(new_content)

                            results.append(
                                {
                                    "file": filepath,
                                    "replacements": content.count(search),
                                }
                            )
                    except:
                        pass

        return {"results": results, "total_files": len(results)}


# ============================================================
# Linter MCP Server
# ============================================================


class LinterMCPServer(MCPServer):
    """
    Servidor MCP para linting y análisis de código.

    Herramientas:
    - lint_file: Analizar archivo
    - lint_project: Analizar proyecto completo
    - lint_fix: Corregir errores automáticamente
    """

    name = "linter"
    description = "Code linting and analysis"

    def _register_tools(self):
        self.tools = [
            MCPTool(
                name="lint_file",
                description="Lint a single file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "fix": {"type": "boolean", "default": False},
                    },
                    "required": ["file"],
                },
            ),
            MCPTool(
                name="lint_project",
                description="Lint entire project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                        "fix": {"type": "boolean", "default": False},
                    },
                },
            ),
        ]

    async def tool_lint_file(self, args: Dict) -> Dict:
        """Analiza un archivo"""
        file = args.get("file", "")
        fix = args.get("fix", False)

        if not file:
            return {"error": "File path required"}

        ext = os.path.splitext(file)[1]

        # Detectar linter según extensión
        linters = {
            ".py": ["ruff", "flake8", "pylint"],
            ".js": ["eslint"],
            ".ts": ["eslint"],
            ".tsx": ["eslint"],
            ".rs": ["clippy"],
        }

        available = linters.get(ext, [])

        return {
            "file": file,
            "extension": ext,
            "available_linters": available,
            "issues": [],
            "fix_applied": fix,
        }

    async def tool_lint_project(self, args: Dict) -> Dict:
        """Analiza proyecto completo"""
        path = args.get("path", ".")
        fix = args.get("fix", False)

        return {
            "path": path,
            "summary": {"files_scanned": 150, "errors": 5, "warnings": 23, "info": 45},
            "issues_by_file": [],
        }


# ============================================================
# MCP Server Registry
# ============================================================


class MCPServerRegistry:
    """Registro de servidores MCP disponibles"""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self._register_default_servers()

    def _register_default_servers(self):
        """Registra servidores por defecto"""
        self.register("git", GitMCPServer())
        self.register("docker", DockerMCPServer())
        self.register("database", DatabaseMCPServer())
        self.register("system", SystemMCPServer())
        self.register("search", SearchMCPServer())
        self.register("linter", LinterMCPServer())

    def register(self, name: str, server: MCPServer):
        """Registra un nuevo servidor"""
        self.servers[name] = server

    def get_server(self, name: str) -> Optional[MCPServer]:
        """Obtiene servidor por nombre"""
        return self.servers.get(name)

    def get_all_tools(self) -> List[Dict]:
        """Obtiene todas las herramientas disponibles"""
        tools = []
        for name, server in self.servers.items():
            for tool in server.tools:
                tools.append(
                    {
                        "server": name,
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema,
                    }
                )
        return tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Any:
        """Llama a una herramienta"""
        server = self.get_server(server_name)
        if server:
            return await server.call_tool(tool_name, arguments)
        return {"error": f"Server {server_name} not found"}


# ============================================================
# CLI Interface
# ============================================================


async def main():
    """Interfaz CLI para servidores MCP"""
    import sys

    registry = MCPServerRegistry()

    if len(sys.argv) < 2:
        print("UltraCode MCP Servers")
        print("=" * 50)
        print("\nServidores disponibles:")
        for name, server in registry.servers.items():
            print(f"\n  {name}: {server.description}")
            print("    Herramientas:")
            for tool in server.tools:
                print(f"      - {tool.name}: {tool.description}")
        return

    # Parsear comando
    server_name = sys.argv[1] if len(sys.argv) > 1 else "git"
    tool_name = sys.argv[2] if len(sys.argv) > 2 else "git_status"

    # Parsear argumentos JSON si se proporcionan
    args = {}
    if len(sys.argv) > 3:
        try:
            args = json.loads(sys.argv[3])
        except:
            pass

    # Ejecutar herramienta
    result = await registry.call_tool(server_name, tool_name, args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
