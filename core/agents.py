"""
Agent System Module
==================
Implementación del pilar 6 - Sistema de Sub-Agentes.
"""

import uuid
import asyncio
import threading
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


class AgentMode(Enum):
    """Modos de ejecución de sub-agentes"""

    IN_PROCESS = "in-process"  # Misma memoria, máxima velocidad
    GIT_WORKTREE = "git-worktree"  # Aislamiento con Git
    REMOTE = "remote"  # Servidor en la nube


class AgentStatus(Enum):
    """Estados de un agente"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    IDLE = "idle"
    WAITING = "waiting"
    TERMINATED = "terminated"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Mensaje entre agentes"""

    from_id: str
    to_id: str
    content: Any
    message_type: str  # task, result, error, status
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None


@dataclass
class SubAgent:
    """Representación de un sub-agente"""

    id: str
    mode: AgentMode
    parent_id: str
    status: AgentStatus = AgentStatus.INITIALIZING
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    tasks: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    message_queue: List[AgentMessage] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "mode": self.mode.value,
            "parent_id": self.parent_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_activity.isoformat()
            if hasattr(self, "last_activity")
            else self.last_active.isoformat(),
            "tasks": self.tasks,
            "task_count": len(self.tasks),
        }


class SubAgentSystem:
    """
    Sistema de generación y gestión de sub-agentes.

    Implementa tres modos de ejecución:
    - In-process: Máxima velocidad, riesgo de fallo en cascada
    - Git Worktree: Aislamiento total con overhead mínimo
    - Remote: Escalabilidad ilimitada, depende de red
    """

    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self.agents: Dict[str, SubAgent] = {}
        self.message_queues: Dict[str, List[AgentMessage]] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_agents)
        self._lock = threading.Lock()
        self._event_handlers: Dict[str, List[Callable]] = {}

    def spawn(
        self, mode: AgentMode, parent_id: str = "main", config: Dict = None
    ) -> SubAgent:
        """
        Crea un nuevo sub-agente.

        Args:
            mode: Modo de ejecución
            parent_id: ID del agente padre
            config: Configuración adicional

        Returns:
            SubAgent: El nuevo agente creado
        """
        with self._lock:
            if len(self.agents) >= self.max_agents:
                raise Exception(f"Máximo de {self.max_agents} sub-agentes alcanzado")

            agent_id = str(uuid.uuid4())[:8]
            agent = SubAgent(
                id=agent_id,
                mode=mode,
                parent_id=parent_id,
                status=AgentStatus.ACTIVE,
                config=config or {},
            )
            self.agents[agent_id] = agent
            self.message_queues[agent_id] = []

            self._emit_event("agent_spawned", agent)

            return agent

    def terminate(self, agent_id: str) -> bool:
        """Termina un sub-agente"""
        with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].status = AgentStatus.TERMINATED
                self._emit_event("agent_terminated", self.agents[agent_id])
                del self.agents[agent_id]
                del self.message_queues[agent_id]
                return True
            return False

    def send_message(
        self,
        from_id: str,
        to_id: str,
        content: Any,
        message_type: str = "task",
        correlation_id: str = None,
    ) -> AgentMessage:
        """Envía mensaje a otro agente"""
        message = AgentMessage(
            from_id=from_id,
            to_id=to_id,
            content=content,
            message_type=message_type,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )

        if to_id in self.message_queues:
            self.message_queues[to_id].append(message)
            self._emit_event("message_received", message)

        return message

    def broadcast(self, from_id: str, content: Any, message_type: str = "broadcast"):
        """Envía mensaje a todos los agentes"""
        for agent_id in self.agents:
            if agent_id != from_id:
                self.send_message(from_id, agent_id, content, message_type)

    def get_messages(self, agent_id: str) -> List[AgentMessage]:
        """Obtiene mensajes pendientes de un agente"""
        messages = self.message_queues.get(agent_id, [])
        self.message_queues[agent_id] = []
        return messages

    def get_active_agents(self) -> List[SubAgent]:
        """Obtiene lista de agentes activos"""
        return [a for a in self.agents.values() if a.status != AgentStatus.TERMINATED]

    def get_agent(self, agent_id: str) -> Optional[SubAgent]:
        """Obtiene un agente por ID"""
        return self.agents.get(agent_id)

    def update_status(self, agent_id: str, status: AgentStatus):
        """Actualiza el estado de un agente"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_active = datetime.now()
            self._emit_event("status_changed", self.agents[agent_id])

    def assign_task(self, agent_id: str, task: str):
        """Asigna una tarea a un agente"""
        if agent_id in self.agents:
            self.agents[agent_id].tasks.append(task)
            self.update_status(agent_id, AgentStatus.PROCESSING)

    def add_event_handler(self, event: str, handler: Callable):
        """Agrega un handler para eventos"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit_event(self, event: str, data: Any):
        """Emite un evento"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass

    def get_stats(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len(self.get_active_agents()),
            "max_agents": self.max_agents,
            "modes": {
                mode.value: len([a for a in self.agents.values() if a.mode == mode])
                for mode in AgentMode
            },
            "statuses": {
                status.value: len(
                    [a for a in self.agents.values() if a.status == status]
                )
                for status in AgentStatus
            },
        }

    async def execute_parallel(
        self, tasks: List[Dict], agent_mode: AgentMode = AgentMode.IN_PROCESS
    ) -> List[Any]:
        """
        Ejecuta tareas en paralelo usando sub-agentes.

        Args:
            tasks: Lista de tareas a ejecutar
            agent_mode: Modo de ejecución de los agentes

        Returns:
            Lista de resultados
        """
        agents = []
        for _ in tasks:
            agent = self.spawn(agent_mode)
            agents.append(agent)

        results = []
        for agent, task in zip(agents, tasks):
            try:
                # Simular ejecución de tarea
                result = {"agent_id": agent.id, "status": "completed", "task": task}
                results.append(result)
            except Exception as e:
                results.append(
                    {"agent_id": agent.id, "status": "error", "error": str(e)}
                )

        return results


# Import para ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
