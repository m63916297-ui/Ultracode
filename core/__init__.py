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
from .query import QueryEngine, QueryInternal, QueryConfig, BudgetTracker
from .session import SessionManager, SessionState
from .cache import PromptCache
from .deferred import DeferredLoadingSystem
from .mcp import MCPClient, MCPTransport

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
    "BudgetTracker",
    "SessionManager",
    "SessionState",
    "PromptCache",
    "DeferredLoadingSystem",
    "MCPClient",
    "MCPTransport",
]
