"""
Query Engine Module - Motor de Consultas de Dos Capas
=====================================================
Implementación del pilar 8 - Query Engine con separación de responsabilidades.
"""

import os
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator


@dataclass
class QueryConfig:
    """Configuración de query"""

    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = ""
    context_window: int = 200000
    api_key: str = ""


@dataclass
class QueryRequest:
    """Request de query"""

    prompt: str
    config: QueryConfig
    tools: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class QueryResponse:
    """Response de query"""

    content: str
    model: str
    usage: Dict
    tool_calls: List[Dict] = field(default_factory=list)
    stop_reason: str = "end_turn"
    cached: bool = False


class QueryInternal:
    """
    Capa Interna - Obrero Especializado (query.ts)

    Responsabilidades:
    - Formato JSON API
    - Conexión de red
    - Datos crudos
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.base_url = "https://api.anthropic.com/v1"
        self.streaming = True

    async def format_request(self, request: QueryRequest) -> Dict:
        """Formatea request para API de Anthropic"""
        return {
            "model": request.config.model,
            "max_tokens": request.config.max_tokens,
            "temperature": request.config.temperature,
            "system": request.config.system_prompt
            or "You are Claude Code, an AI assistant.",
            "messages": [{"role": "user", "content": request.prompt}],
            "tools": request.tools if request.tools else None,
            "stream": self.streaming,
        }

    async def send_request(self, request_data: Dict) -> QueryResponse:
        """Envía request a API (simulado sin API key real)"""
        if not self.api_key:
            return QueryResponse(
                content=f"[Simulación] Query preparado para modelo: {request_data.get('model')}\n[Requiere ANTHROPIC_API_KEY para ejecución real]",
                model=request_data.get("model"),
                usage={"input_tokens": 0, "output_tokens": 0, "cache_hits": 0},
                cached=False,
            )

        # En producción real, aquí se haría el request HTTP
        # usando aiohttp o similar
        return QueryResponse(
            content="[Respuesta simulada]",
            model=request_data.get("model"),
            usage={"input_tokens": 0, "output_tokens": 0, "cache_hits": 0},
        )

    async def stream_response(self, request_data: Dict) -> AsyncIterator[str]:
        """Genera respuesta en streaming (simulado)"""
        if not self.api_key:
            # Simular streaming
            words = ["[Simulación]", "Respuesta", "en", "streaming..."]
            for word in words:
                yield word + " "
                await asyncio.sleep(0.1)
        else:
            # Streaming real con API
            # Implementar con aiohttp
            pass


class QueryEngine:
    """
    Capa Externa - Director de Orquestación (QueryEngine.ts)

    Responsabilidades:
    - Lógica de negocio
    - Presupuesto
    - Permisos
    - Reintentos
    """

    def __init__(self, tool_executor=None, permission_system=None, budget_tracker=None):
        self.internal = QueryInternal()
        self.tool_executor = tool_executor
        self.permission_system = permission_system
        self.budget_tracker = budget_tracker
        self.config = QueryConfig()
        self.retry_count = 3
        self.retry_delay = 1.0

    async def execute(
        self, prompt: str, tools: List[Dict] = None, context: Dict = None
    ) -> QueryResponse:
        """
        Ejecuta query con todas las verificaciones.

        Pipeline:
        1. Verificar presupuesto
        2. Verificar permisos de herramientas
        3. Formatear request
        4. Enviar a API
        5. Ejecutar herramientas si las hay
        """
        context = context or {}

        # 1. Verificar presupuesto
        if self.budget_tracker and self.budget_tracker.is_exhausted():
            return QueryResponse(
                content="[Error] Presupuesto agotado", model=self.config.model, usage={}
            )

        # 2. Verificar permisos de herramientas
        if tools and self.permission_system:
            for tool in tools:
                tool_name = tool.get("name", "")
                perm_result = await self.permission_system.check(
                    tool_name, tool_name, context
                )
                if not perm_result.allowed:
                    return QueryResponse(
                        content=f"[Error] Permiso denegado para {tool_name}: {perm_result.reason}",
                        model=self.config.model,
                        usage={},
                    )

        # 3. Formatear request
        request = QueryRequest(
            prompt=prompt, config=self.config, tools=tools or [], metadata=context
        )
        request_data = await self.internal.format_request(request)

        # 4. Enviar request con reintentos
        for attempt in range(self.retry_count):
            try:
                response = await self.internal.send_request(request_data)

                # Actualizar presupuesto
                if self.budget_tracker and response.usage:
                    self.budget_tracker.track(
                        response.usage.get("input_tokens", 0),
                        response.usage.get("output_tokens", 0),
                        response.usage.get("cache_hits", 0),
                    )

                # 5. Ejecutar herramientas si las hay
                if response.tool_calls and self.tool_executor:
                    tool_results = []
                    for tool_call in response.tool_calls:
                        result = await self.tool_executor.execute(tool_call)
                        tool_results.append(result)
                    response.tool_results = tool_results

                return response

            except Exception as e:
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    return QueryResponse(
                        content=f"[Error] Fallo después de {self.retry_count} intentos: {str(e)}",
                        model=self.config.model,
                        usage={},
                    )

    async def stream(
        self, prompt: str, tools: List[Dict] = None, context: Dict = None
    ) -> AsyncIterator[str]:
        """Ejecuta query con streaming de respuesta"""
        context = context or {}

        if self.budget_tracker and self.budget_tracker.is_exhausted():
            yield "[Error] Presupuesto agotado"
            return

        request = QueryRequest(
            prompt=prompt, config=self.config, tools=tools or [], metadata=context
        )
        request_data = await self.internal.format_request(request)

        async for chunk in self.internal.stream_response(request_data):
            yield chunk


class BudgetTracker:
    """Sistema de Budget Tracking en tiempo real"""

    def __init__(self, limit: float = 5.00):
        self.limit = limit
        self.spent = 0.0
        self.rates = {
            "input": 0.003,  # $0.003 por 1K tokens
            "output": 0.015,  # $0.015 por 1K tokens
            "cache_hit": 0.001,  # $0.001 por 1K tokens
        }
        self.history = []

    def track(self, input_tokens: int, output_tokens: int, cache_hits: int = 0):
        """Registra uso de tokens"""
        cost = (
            (input_tokens * self.rates["input"]) / 1000
            + (output_tokens * self.rates["output"]) / 1000
            - (cache_hits * self.rates["cache_hit"]) / 1000
        )
        self.spent = min(self.spent + cost, self.limit)
        self.history.append(
            {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_hits": cache_hits,
                "cost": cost,
                "total": self.spent,
            }
        )

    def is_exhausted(self) -> bool:
        """Verifica si el presupuesto está agotado"""
        return self.spent >= self.limit

    def get_remaining(self) -> float:
        """Obtiene presupuesto restante"""
        return max(0, self.limit - self.spent)

    def get_stats(self) -> Dict:
        """Obtiene estadísticas de uso"""
        return {
            "limit": self.limit,
            "spent": self.spent,
            "remaining": self.get_remaining(),
            "percent_used": (self.spent / self.limit) * 100,
            "requests": len(self.history),
        }


# Import asyncio
import asyncio
