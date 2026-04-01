"""
Feature Gates Module
===================
Implementación del pilar 5 - Feature Gates con Dead-Code Elimination.
"""

from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class FeatureGateStatus(Enum):
    """Estado de un Feature Gate"""

    DISABLED = "disabled"
    ENABLED = "enabled"
    BETA = "beta"
    DEPRECATED = "deprecated"


@dataclass
class FeatureGate:
    """Definición de un Feature Gate"""

    name: str
    description: str
    status: FeatureGateStatus = FeatureGateStatus.DISABLED
    min_version: Optional[str] = None
    requires_config: Optional[str] = None
    experimental: bool = False

    def is_active(self) -> bool:
        """Verifica si el feature está activo"""
        return self.status in (FeatureGateStatus.ENABLED, FeatureGateStatus.BETA)


class FeatureGates:
    """
    Sistema de Feature Gates con Dead-Code Elimination.

    Permite activar/desactivar características experimentalmente
    con soporte para eliminación automática de código muerto durante
    la compilación.

    Feature Gates descubiertos en Claude Code:
    - KAIROS: Sistema de planificación temporal avanzada
    - COORDINATOR_MODE: Coordinación multi-agente centralizada
    - VOICE_MODE: Interacción por voz con la herramienta
    - PROACTIVE: Ejecución proactiva sin solicitud explícita
    """

    def __init__(self):
        self._gates: Dict[str, FeatureGate] = self._init_default_gates()
        self._listeners: Dict[str, list] = {}

    def _init_default_gates(self) -> Dict[str, FeatureGate]:
        """Inicializa los feature gates predeterminados"""
        return {
            "KAIROS": FeatureGate(
                name="KAIROS",
                description="Sistema de planificación temporal avanzada para coordinación de tareas",
                experimental=True,
            ),
            "COORDINATOR_MODE": FeatureGate(
                name="COORDINATOR_MODE",
                description="Coordinación multi-agente centralizada para tareas complejas",
                experimental=True,
            ),
            "VOICE_MODE": FeatureGate(
                name="VOICE_MODE",
                description="Interacción por voz con la herramienta de programación",
                experimental=True,
            ),
            "PROACTIVE": FeatureGate(
                name="PROACTIVE",
                description="Ejecución proactiva sin solicitud explícita del usuario",
                experimental=True,
            ),
            "STREAMING": FeatureGate(
                name="STREAMING",
                description="Streaming de respuestas en tiempo real",
                status=FeatureGateStatus.ENABLED,
            ),
            "PROMPT_CACHE": FeatureGate(
                name="PROMPT_CACHE",
                description="Cache de prompts para reducción de costos",
                status=FeatureGateStatus.ENABLED,
            ),
            "DEFERRED_LOADING": FeatureGate(
                name="DEFERRED_LOADING",
                description="Carga diferida de resultados de herramientas",
                status=FeatureGateStatus.ENABLED,
            ),
            "SESSION_RESTORE": FeatureGate(
                name="SESSION_RESTORE",
                description="Persistencia y reanudación de sesiones",
                status=FeatureGateStatus.ENABLED,
            ),
            "MCP_INTEGRATION": FeatureGate(
                name="MCP_INTEGRATION",
                description="Soporte para Model Context Protocol",
                status=FeatureGateStatus.ENABLED,
            ),
            "SUBAGENTS": FeatureGate(
                name="SUBAGENTS",
                description="Sistema de sub-agentes",
                status=FeatureGateStatus.ENABLED,
            ),
        }

    def is_enabled(self, gate_name: str) -> bool:
        """Verifica si un feature gate está habilitado"""
        gate = self._gates.get(gate_name)
        return gate.is_active() if gate else False

    def enable(self, gate_name: str) -> bool:
        """Habilita un feature gate"""
        gate = self._gates.get(gate_name)
        if gate:
            old_status = gate.status
            gate.status = FeatureGateStatus.ENABLED
            self._notify_listeners(gate_name, old_status, gate.status)
            return True
        return False

    def disable(self, gate_name: str) -> bool:
        """Deshabilita un feature gate"""
        gate = self._gates.get(gate_name)
        if gate:
            old_status = gate.status
            gate.status = FeatureGateStatus.DISABLED
            self._notify_listeners(gate_name, old_status, gate.status)
            return True
        return False

    def toggle(self, gate_name: str) -> bool:
        """Alterna el estado de un feature gate"""
        if self.is_enabled(gate_name):
            self.disable(gate_name)
            return False
        else:
            self.enable(gate_name)
            return True

    def register(self, gate: FeatureGate):
        """Registra un nuevo feature gate"""
        self._gates[gate.name] = gate

    def unregister(self, gate_name: str) -> bool:
        """Elimina un feature gate"""
        if gate_name in self._gates:
            del self._gates[gate_name]
            return True
        return False

    def get_status(self) -> Dict[str, str]:
        """Obtiene el estado de todos los feature gates"""
        return {name: gate.status.value for name, gate in self._gates.items()}

    def get_info(self, gate_name: str) -> Optional[Dict]:
        """Obtiene información detallada de un feature gate"""
        gate = self._gates.get(gate_name)
        if gate:
            return {
                "name": gate.name,
                "description": gate.description,
                "status": gate.status.value,
                "is_active": gate.is_active(),
                "experimental": gate.experimental,
                "min_version": gate.min_version,
                "requires_config": gate.requires_config,
            }
        return None

    def add_listener(self, gate_name: str, callback):
        """Agrega un listener para cambios en un feature gate"""
        if gate_name not in self._listeners:
            self._listeners[gate_name] = []
        self._listeners[gate_name].append(callback)

    def _notify_listeners(self, gate_name: str, old_status, new_status):
        """Notifica a los listeners de un cambio"""
        callbacks = self._listeners.get(gate_name, [])
        for callback in callbacks:
            try:
                callback(gate_name, old_status, new_status)
            except Exception:
                pass

    def get_enabled_features(self) -> Set[str]:
        """Obtiene el conjunto de features habilitados"""
        return {name for name, gate in self._gates.items() if gate.is_active()}

    def get_experimental_features(self) -> Dict[str, str]:
        """Obtiene features experimentales disponibles"""
        return {
            name: gate.description
            for name, gate in self._gates.items()
            if gate.experimental and gate.status != FeatureGateStatus.DEPRECATED
        }

    def conditional_code(self, gate_name: str, enabled_code, disabled_code=None):
        """
        Ejecución condicional basada en feature gate.
        Simula Dead-Code Elimination en tiempo de ejecución.
        """
        if self.is_enabled(gate_name):
            return enabled_code if callable(enabled_code) else enabled_code
        else:
            return disabled_code() if callable(disabled_code) else disabled_code

    def generate_compilation_config(self) -> Dict:
        """
        Genera configuración para eliminación de código muerto.
        Útil para build tools que soporten tree-shaking.
        """
        return {
            "enabled_features": list(self.get_enabled_features()),
            "disabled_features": [
                name for name, gate in self._gates.items() if not gate.is_active()
            ],
            "feature_flags": {
                name: gate.is_active() for name, gate in self._gates.items()
            },
        }
