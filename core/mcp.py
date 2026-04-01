"""
MCP Client Module - Model Context Protocol
=========================================
Implementación del pilar 9 - Integración MCP.
"""

import json
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


class MCPTransport(Enum):
    """Tipos de transporte MCP"""

    STDIO = "stdio"  # Local (subproceso)
    SSE = "sse"  # Remoto (HTTP Server-Sent Events)
    WEBSOCKET = "websocket"  # Bidireccional en tiempo real


@dataclass
class MCPServer:
    """Servidor MCP conectado"""

    name: str
    transport: MCPTransport
    status: str = "disconnected"
    endpoint: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    tools: List[Dict] = field(default_factory=list)


@dataclass
class MCPTool:
    """Herramienta expuesta por servidor MCP"""

    name: str
    description: str
    input_schema: Dict
    server_name: str


class MCPClient:
    """
    Cliente MCP - "USB-C de la Inteligencia Artificial"

    Implementa el protocolo MCP para conectar con herramientas externas:
    - stdio: Local (subproceso) - Latencia mínima
    - SSE: Remoto (HTTP) - Push de datos
    - WebSocket: Bidireccional - Tiempo real
    """

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.adapters: Dict[str, Any] = {}
        self._tools: Dict[str, MCPTool] = {}
        self._message_handlers: Dict[str, List[Callable]] = {}

    def connect(
        self,
        name: str,
        transport: MCPTransport,
        endpoint: str = None,
        config: Dict = None,
    ):
        """
        Conecta a un servidor MCP.

        Args:
            name: Nombre del servidor
            transport: Tipo de transporte
            endpoint: URL o comando según transporte
            config: Configuración adicional
        """
        config = config or {}

        server = MCPServer(
            name=name,
            transport=transport,
            status="connecting",
            endpoint=endpoint,
            capabilities=config.get("capabilities", []),
            tools=config.get("tools", []),
        )

        self.servers[name] = server

        # Registrar herramientas del servidor
        for tool_def in server.tools:
            tool = MCPTool(
                name=tool_def.get("name", ""),
                description=tool_def.get("description", ""),
                input_schema=tool_def.get("inputSchema", {}),
                server_name=name,
            )
            self._tools[tool.name] = tool

        server.status = "connected"
        self._emit("server_connected", server)

    def disconnect(self, name: str):
        """Desconecta servidor MCP"""
        if name in self.servers:
            self.servers[name].status = "disconnected"
            self._emit("server_disconnected", self.servers[name])

            # Remover herramientas
            to_remove = [
                t for t, tool in self._tools.items() if tool.server_name == name
            ]
            for t in to_remove:
                del self._tools[t]

    def get_servers(self) -> List[MCPServer]:
        """Obtiene lista de servidores"""
        return list(self.servers.values())

    def get_tools(self) -> List[MCPTool]:
        """Obtiene lista de herramientas disponibles"""
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Obtiene herramienta por nombre"""
        return self._tools.get(name)

    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Llama a una herramienta MCP.

        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos de la llamada

        Returns:
            Resultado de la herramienta
        """
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Herramienta no encontrada: {tool_name}")

        server = self.servers.get(tool.server_name)
        if not server or server.status != "connected":
            raise RuntimeError(f"Servidor no disponible: {tool.server_name}")

        # Construir mensaje MCP
        message = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        # Enviar según transporte
        if server.transport == MCPTransport.STDIO:
            return await self._call_stdio(server, message)
        elif server.transport == MCPTransport.SSE:
            return await self._call_sse(server, message)
        elif server.transport == MCPTransport.WEBSOCKET:
            return await self._call_websocket(server, message)

    async def _call_stdio(self, server: MCPServer, message: Dict) -> Any:
        """Llama herramienta via stdio (simulado)"""
        # En producción, usar subprocess
        return {"result": f"[Simulación] Llamada stdio a {server.name}"}

    async def _call_sse(self, server: MCPServer, message: Dict) -> Any:
        """Llama herramienta via SSE (simulado)"""
        return {"result": f"[Simulación] Llamada SSE a {server.name}"}

    async def _call_websocket(self, server: MCPServer, message: Dict) -> Any:
        """Llama herramienta via WebSocket (simulado)"""
        return {"result": f"[Simulación] Llamada WS a {server.name}"}

    def add_message_handler(self, event: str, handler: Callable):
        """Agrega handler para mensajes"""
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)

    def _emit(self, event: str, data: Any):
        """Emite evento"""
        for handler in self._message_handlers.get(event, []):
            try:
                handler(data)
            except:
                pass

    def _generate_id(self) -> str:
        """Genera ID único para mensajes"""
        import uuid

        return str(uuid.uuid4())

    def get_stats(self) -> Dict:
        """Obtiene estadísticas"""
        return {
            "servers": len(self.servers),
            "connected": sum(
                1 for s in self.servers.values() if s.status == "connected"
            ),
            "tools": len(self._tools),
            "transports": {
                t.value: sum(1 for s in self.servers.values() if s.transport == t)
                for t in MCPTransport
            },
        }
