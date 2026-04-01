"""
UltraCode Core Package
=====================
Contiene los módulos fundamentales del sistema de programación IA.
"""

from .terminal import TerminalBuffer, TerminalLine
from .executor import StreamingToolExecutor, ToolCall, ToolResult
from .permissions import DualPermissionSystem, PermissionRule, PermissionAction
from .features import FeatureGates
from .agents import SubAgentSystem, AgentMode, SubAgent
from .query import QueryEngine, QueryInternal, QueryConfig
from .session import SessionManager, SessionState
from .cache import PromptCache, CacheEntry
from .deferred import DeferredLoadingSystem

__all__ = [
    "TerminalBuffer",
    "TerminalLine",
    "StreamingToolExecutor",
    "ToolCall",
    "ToolResult",
    "DualPermissionSystem",
    "PermissionRule",
    "PermissionAction",
    "FeatureGates",
    "SubAgentSystem",
    "AgentMode",
    "SubAgent",
    "QueryEngine",
    "QueryInternal",
    "QueryConfig",
    "SessionManager",
    "SessionState",
    "PromptCache",
    "CacheEntry",
    "DeferredLoadingSystem",
]
