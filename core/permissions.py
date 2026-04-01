"""
Permissions Module - Sistema Dual de Permisos
========================================
Implementación del pilar 3 del sistema de seguridad.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Any


class PermissionAction(Enum):
    """Acciones de permiso"""

    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


class PermissionRule:
    """Regla de permisos para Track 1"""

    def __init__(
        self,
        pattern: str,
        action: PermissionAction,
        reason: str,
        is_regex: bool = False,
        is_global: bool = False,
    ):
        self.pattern = pattern
        self.action = action
        self.reason = reason
        self.is_regex = is_regex
        self.is_global = is_global


class PermissionResult:
    """Resultado de evaluación de permisos"""

    def __init__(
        self,
        allowed: bool,
        track: int,
        reason: str,
        rule_match: Optional[str] = None,
        requires_confirmation: bool = False,
    ):
        self.allowed = allowed
        self.track = track
        self.reason = reason
        self.rule_match = rule_match
        self.requires_confirmation = requires_confirmation


class Track1PermissionEngine:
    """
    Motor de permisos rápido con Glob/Regex (Track 1)
    """

    def __init__(self):
        self.rules = self._get_default_rules()

    def _get_default_rules(self) -> List[PermissionRule]:
        """Reglas predeterminadas del sistema"""
        return [
            PermissionRule(
                "*.env", PermissionAction.DENY, "Archivo de variables de entorno"
            ),
            PermissionRule("*.pem", PermissionAction.DENY, "Certificado SSL/TLS"),
            PermissionRule("*.key", PermissionAction.DENY, "Clave privada"),
            PermissionRule(
                "~/.ssh/", PermissionAction.DENY, "Directorio SSH", is_global=True
            ),
            PermissionRule(
                "~/.aws/", PermissionAction.DENY, "Credenciales AWS", is_global=True
            ),
            PermissionRule("rm -rf /", PermissionAction.DENY, "Eliminación de raíz"),
            PermissionRule(
                "drop database",
                PermissionAction.DENY,
                "Eliminar base de datos",
                is_regex=True,
            ),
            PermissionRule("format", PermissionAction.DENY, "Formateo de disco"),
            PermissionRule("shutdown", PermissionAction.DENY, "Apagado del sistema"),
            PermissionRule(
                "chmod 777", PermissionAction.ASK, "Permisos inseguros", is_regex=True
            ),
        ]

    def evaluate(
        self, command: str, tool_name: Optional[str] = None
    ) -> PermissionResult:
        """Evalúa comando contra reglas deterministas"""
        command_lower = command.lower()

        for rule in self.rules:
            if rule.is_global and tool_name:
                continue

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
                    requires_confirmation=(rule.action == PermissionAction.ASK),
                )

        return PermissionResult(allowed=True, track=1, reason="Sin restricciones")

    def add_rule(self, rule: PermissionRule):
        """Agrega una nueva regla"""
        self.rules.append(rule)

    def get_rules(self) -> List[PermissionRule]:
        """Obtiene todas las reglas"""
        return self.rules.copy()


class Track2PermissionClassifier:
    """
    Clasificador ML para permisos contextuales (Track 2)
    """

    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.dangerous_patterns = [
            "eval(",
            "exec(",
            "os.system",
            "subprocess.",
            "shell=True",
            "nc -e",
            "/dev/tcp",
            "curl.*|.*sh",
            "wget.*|.*sh",
        ]
        self.suspicious_patterns = [
            "git reset --hard",
            "git clean -fd",
            "docker rm --force",
            "kill -9",
        ]

    async def evaluate(
        self, command: str, context: Optional[Dict] = None
    ) -> PermissionResult:
        """Evalúa comando con comprensión semántica"""
        context = context or {}

        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=False, track=2, reason=f"Patrón peligroso: {pattern}"
                )

        for pattern in self.suspicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason=f"Comando sospechoso: {pattern}",
                    requires_confirmation=True,
                )

        return PermissionResult(allowed=True, track=2, reason="Comando seguro")


class DualPermissionSystem:
    """
    Sistema dual de permisos (Track 1 + Track 2)
    """

    def __init__(self):
        self.track1 = Track1PermissionEngine()
        self.track2 = Track2PermissionClassifier()
        self.permission_history = []
        self.user_overrides = {}

    async def check(
        self,
        command: str,
        tool_name: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> PermissionResult:
        """Evalúa permisos en dos tracks"""
        result = self.track1.evaluate(command, tool_name)
        self.permission_history.append(result)

        if not result.allowed:
            return result

        for pattern, action in self.user_overrides.items():
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=(action == PermissionAction.ALLOW),
                    track=0,
                    reason=f"Override de usuario: {pattern}",
                )

        result = await self.track2.evaluate(command, context)
        self.permission_history.append(result)

        return result

    def add_rule(
        self,
        pattern: str,
        action: PermissionAction,
        reason: str,
        is_regex: bool = False,
    ):
        """Agrega regla personalizada al Track 1"""
        rule = PermissionRule(pattern, action, reason, is_regex=is_regex)
        self.track1.add_rule(rule)

    def set_override(self, pattern: str, action: PermissionAction):
        """Establece override del usuario"""
        self.user_overrides[pattern] = action

    def get_history(self) -> List[Dict]:
        """Obtiene historial de permisos"""
        return [
            {
                "allowed": h.allowed,
                "track": h.track,
                "reason": h.reason,
                "rule_match": h.rule_match,
            }
            for h in self.permission_history[-100:]
        ]

    def clear_history(self):
        """Limpia historial de permisos"""
        self.permission_history.clear()
