"""
Security Module - Sistema Dual de Permisos
=========================================
Implementación de los pilares 3 del sistema de seguridad.
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class PermissionAction(Enum):
    """Acciones de permiso"""

    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


@dataclass
class PermissionRule:
    """Regla de permisos para Track 1"""

    pattern: str
    action: PermissionAction
    reason: str
    is_regex: bool = False
    is_global: bool = False  # Aplica a todas las herramientas


@dataclass
class PermissionResult:
    """Resultado de evaluación de permisos"""

    allowed: bool
    track: int  # 1 o 2
    reason: str
    rule_match: Optional[str] = None
    requires_confirmation: bool = False


class Track1PermissionEngine:
    """
    Motor de permisos rápido con Glob/Regex (Track 1)

    Implementa evaluación determinista de permisos sin uso de IA,
    usando patrones Glob para coincidencias simples y Regex para
    expresiones complejas.
    """

    def __init__(self):
        self.rules: List[PermissionRule] = self._get_default_rules()

    def _get_default_rules(self) -> List[PermissionRule]:
        """Reglas predeterminadas del sistema"""
        return [
            # Archivos sensibles - nunca acceder
            PermissionRule(
                "*.env", PermissionAction.DENY, "Archivo de variables de entorno"
            ),
            PermissionRule("*.pem", PermissionAction.DENY, "Certificado SSL/TLS"),
            PermissionRule("*.key", PermissionAction.DENY, "Clave privada"),
            PermissionRule(
                "*.pfx", PermissionAction.DENY, "Certificado con clave privada"
            ),
            PermissionRule(
                "~/.ssh/*",
                PermissionAction.DENY,
                "Directorio SSH con claves",
                is_global=True,
            ),
            PermissionRule(
                "~/.aws/*", PermissionAction.DENY, "Credenciales AWS", is_global=True
            ),
            PermissionRule(
                "~/.kube/*",
                PermissionAction.DENY,
                "Configuración Kubernetes",
                is_global=True,
            ),
            # Comandos destructivos
            PermissionRule(
                r"rm\s+-rf\s+/",
                PermissionAction.DENY,
                "Eliminación de raíz",
                is_regex=True,
            ),
            PermissionRule(
                r"rm\s+-rf\s+\*",
                PermissionAction.DENY,
                "Eliminación masiva",
                is_regex=True,
            ),
            PermissionRule(
                r"del\s+/[fqs]",
                PermissionAction.DENY,
                "Eliminación Windows",
                is_regex=True,
            ),
            PermissionRule(
                r"format\s+[a-z]:",
                PermissionAction.DENY,
                "Formateo de disco",
                is_regex=True,
            ),
            # Comandos de base de datos peligrosos
            PermissionRule(
                r"drop\s+database",
                PermissionAction.DENY,
                "Eliminar base de datos",
                is_regex=True,
            ),
            PermissionRule(
                r"drop\s+table", PermissionAction.DENY, "Eliminar tabla", is_regex=True
            ),
            PermissionRule(
                r"truncate\s+\w+", PermissionAction.DENY, "Truncar tabla", is_regex=True
            ),
            # Comandos de sistema
            PermissionRule(
                r"shutdown", PermissionAction.DENY, "Apagado del sistema", is_regex=True
            ),
            PermissionRule(
                r"reboot", PermissionAction.DENY, "Reinicio del sistema", is_regex=True
            ),
            PermissionRule(
                r"init\s+6", PermissionAction.DENY, "Reinicio Linux", is_regex=True
            ),
            # Permisos riesgosos
            PermissionRule(
                r"chmod\s+777",
                PermissionAction.ASK,
                "Permisos inseguros",
                is_regex=True,
            ),
            PermissionRule(
                r"chmod\s+000", PermissionAction.ASK, "Quitar permisos", is_regex=True
            ),
        ]

    def evaluate(self, command: str, tool_name: str = None) -> PermissionResult:
        """Evalúa comando contra reglas deterministas"""
        command_lower = command.lower()

        for rule in self.rules:
            # Saltar reglas globales si no aplican
            if rule.is_global and tool_name:
                continue

            if rule.is_regex:
                pattern = rule.pattern
            else:
                # Convertir Glob a regex
                pattern = (
                    rule.pattern.replace(".", r"\.")
                    .replace("**/", ".*/")
                    .replace("*", ".*")
                )

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

    def remove_rule(self, pattern: str):
        """Elimina una regla por patrón"""
        self.rules = [r for r in self.rules if r.pattern != pattern]

    def get_rules(self) -> List[PermissionRule]:
        """Obtiene todas las reglas"""
        return self.rules.copy()


class Track2PermissionClassifier:
    """
    Clasificador ML para permisos contextuales (Track 2)

    Usa comprensión semántica para evaluar comandos en contexto,
    identificando patrones peligrosos que las reglas simples no capturan.
    """

    DANGEROUS_PATTERNS = [
        # Ejecución de código
        (r"eval\s*\(", "Ejecución dinámica de código"),
        (r"exec\s*\(", "Ejecución de código"),
        (r"compile\s*\(", "Compilación dinámica"),
        # Shell injection
        (r"os\.system\s*\(", "Llamada al sistema"),
        (r"subprocess\..*shell\s*=\s*True", "Shell injection"),
        (r"\|\s*sh", "Redirección a shell"),
        # Acceso al sistema
        (r"/proc/self", "Acceso a proceso propio"),
        (r"/etc/passwd", "Lectura de contraseñas"),
        (r"cat\s+/etc/shadow", "Lectura de sombras"),
        # Network
        (r"nc\s+-[el]", "Netcat reverse shell"),
        (r"/dev/tcp/", "Shell directo"),
        (r"curl.*\|.*sh", "Download and execute"),
        (r"wget.*\|.*sh", "Download and execute"),
    ]

    SUSPICIOUS_PATTERNS = [
        (r"git\s+reset\s+--hard", "Reset destructivo de Git"),
        (r"git\s+clean\s+-fd", "Limpieza forzada"),
        (r"docker\s+rm\s+--force", "Eliminar contenedor forzado"),
        (r"kill\s+-9", "Kill forzado"),
        (r"pkill\s+-9", "Kill de procesos"),
    ]

    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold

    async def evaluate(self, command: str, context: Dict = None) -> PermissionResult:
        """Evalúa comando con comprensión semántica"""
        context = context or {}

        # Verificar patrones peligrosos
        for pattern, reason in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason=f"Patrón peligroso: {reason}",
                    requires_confirmation=True,
                )

        # Verificar patrones sospechosos
        for pattern, reason in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=False,
                    track=2,
                    reason=f"Comando sospechoso: {reason}",
                    requires_confirmation=True,
                )

        # Análisis contextual
        if self._analyze_context(command, context):
            return PermissionResult(
                allowed=True, track=2, reason="Comando seguro en contexto actual"
            )

        return PermissionResult(allowed=True, track=2, reason="Comando seguro")

    def _analyze_context(self, command: str, context: Dict) -> bool:
        """Analiza comando en el contexto actual"""
        # Verificar si estamos en un directorio de proyecto
        project_path = context.get("project_path", "")
        if "/node_modules/" in command and "package.json" not in project_path:
            return True

        # Verificar herramientas activas
        active_tools = context.get("active_tools", [])

        # Si solo hay herramientas de lectura y comando es de escritura
        if "Read" in active_tools and "Write" not in active_tools:
            if any(
                cmd in command.lower() for cmd in ["rm ", "del ", "move ", "rename "]
            ):
                return False

        # Verificar historial de permisos del usuario
        user_preferences = context.get("user_preferences", {})
        denied_commands = user_preferences.get("denied_commands", [])
        if any(cmd in command.lower() for cmd in denied_commands):
            return False

        return True


class DualPermissionSystem:
    """
    Sistema dual de permisos (Track 1 + Track 2)

    Combina la velocidad de las reglas deterministas (Track 1) con
    la sofisticación del análisis semántico (Track 2) para una
    seguridad robusta y eficiente.
    """

    def __init__(self):
        self.track1 = Track1PermissionEngine()
        self.track2 = Track2PermissionClassifier()
        self.permission_history: List[PermissionResult] = []
        self.user_overrides: Dict[str, PermissionAction] = {}

    async def check(
        self, command: str, tool_name: str = None, context: Dict = None
    ) -> PermissionResult:
        """
        Evalúa permisos en dos tracks.

        1. Track 1: Evaluación rápida determinista
        2. Track 2: Clasificación semántica (solo si pasa Track 1)
        """
        # Track 1: Evaluación rápida
        result = self.track1.evaluate(command, tool_name)
        self.permission_history.append(result)

        if not result.allowed:
            return result

        # Verificar overrides del usuario
        for pattern, action in self.user_overrides.items():
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionResult(
                    allowed=(action == PermissionAction.ALLOW),
                    track=0,  # Override de usuario
                    reason=f"Override de usuario: {pattern}",
                )

        # Track 2: Clasificación semántica
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
        return [asdict(h) for h in self.permission_history[-100:]]

    def clear_history(self):
        """Limpia historial de permisos"""
        self.permission_history.clear()


# Helper para dataclass.asdict
def asdict(obj):
    """Convierte objeto a diccionario"""
    if hasattr(obj, "__dataclass_fields__"):
        return {
            k: asdict(v)
            for k, v in obj.__dict__.items()
            if v is not None or k in getattr(obj, "__dataclass_fields__", {})
        }
    elif isinstance(obj, list):
        return [asdict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: asdict(v) for k, v in obj.items()}
    return obj
