"""
Session Module - Persistencia y Reanudación
===========================================
Implementación del pilar 10 - Checkpoint/Restore System.
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SessionState:
    """Estado completo de sesión"""

    session_id: str
    created_at: datetime
    last_updated: datetime
    tool_states: Dict[str, Any] = field(default_factory=dict)
    permissions_granted: List[str] = field(default_factory=list)
    permissions_denied: List[str] = field(default_factory=list)
    budget_spent: float = 0.0
    agent_states: Dict[str, Any] = field(default_factory=dict)
    tool_history: List[Dict] = field(default_factory=list)
    chat_history: List[Dict] = field(default_factory=list)
    active_tools: List[str] = field(default_factory=list)
    mcp_connections: List[Dict] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "tool_states": self.tool_states,
            "permissions_granted": self.permissions_granted,
            "permissions_denied": self.permissions_denied,
            "budget_spent": self.budget_spent,
            "agent_states": self.agent_states,
            "tool_history": self.tool_history,
            "chat_history": self.chat_history,
            "active_tools": self.active_tools,
            "mcp_connections": self.mcp_connections,
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionState":
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class SessionManager:
    """
    Gestor de sesiones con checkpoint/restore.

    Permite:
    - Crear nuevas sesiones
    - Guardar checkpoints
    - Restaurar sesiones anteriores
    - Listar sesiones guardadas
    """

    def __init__(self, storage_dir: str = ".ultracode/sessions"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.current_session: Optional[SessionState] = None
        self._listeners: Dict[str, list] = {}

    def create_session(self) -> SessionState:
        """Crea nueva sesión"""
        session = SessionState(
            session_id=str(uuid.uuid4())[:12],
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )
        self.current_session = session
        self._emit("session_created", session)
        return session

    def checkpoint(self) -> Optional[str]:
        """Guarda checkpoint de sesión actual"""
        if not self.current_session:
            return None

        self.current_session.last_updated = datetime.now()
        file_path = os.path.join(
            self.storage_dir, f"session_{self.current_session.session_id}.json"
        )

        with open(file_path, "w") as f:
            json.dump(self.current_session.to_dict(), f, indent=2, default=str)

        self._emit("checkpoint_saved", self.current_session)
        return file_path

    def restore(self, session_id: str) -> Optional[SessionState]:
        """Restaura sesión desde checkpoint"""
        file_path = os.path.join(self.storage_dir, f"session_{session_id}.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

            session = SessionState.from_dict(data)
            self.current_session = session
            self._emit("session_restored", session)
            return session

        return None

    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión guardada"""
        file_path = os.path.join(self.storage_dir, f"session_{session_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        """Lista sesiones guardadas"""
        sessions = []

        for file in os.listdir(self.storage_dir):
            if file.endswith(".json"):
                file_path = os.path.join(self.storage_dir, file)
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        sessions.append(
                            {
                                "id": data.get("session_id"),
                                "created": data.get("created_at"),
                                "last_updated": data.get("last_updated"),
                                "budget": data.get("budget_spent", 0),
                                "tools_used": len(data.get("tool_history", [])),
                                "chat_messages": len(data.get("chat_history", [])),
                            }
                        )
                except:
                    pass

        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)

    def get_current_session(self) -> Optional[SessionState]:
        """Obtiene sesión actual"""
        return self.current_session

    def update_current_session(self, **kwargs):
        """Actualiza datos de la sesión actual"""
        if self.current_session:
            for key, value in kwargs.items():
                if hasattr(self.current_session, key):
                    setattr(self.current_session, key, value)
            self.current_session.last_updated = datetime.now()

    def add_listener(self, event: str, callback):
        """Agrega listener para eventos"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def _emit(self, event: str, data: Any):
        """Emite evento"""
        for callback in self._listeners.get(event, []):
            try:
                callback(data)
            except:
                pass

    def export_session(self, session_id: str = None) -> Optional[str]:
        """Exporta sesión a JSON"""
        if session_id:
            file_path = os.path.join(self.storage_dir, f"session_{session_id}.json")
        elif self.current_session:
            file_path = os.path.join(
                self.storage_dir, f"session_{self.current_session.session_id}.json"
            )
        else:
            return None

        if os.path.exists(file_path):
            export_path = file_path.replace(".json", "_export.json")
            shutil.copy(file_path, export_path)
            return export_path

        return None

    def import_session(self, file_path: str) -> Optional[SessionState]:
        """Importa sesión desde JSON"""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
            session = SessionState.from_dict(data)
            # Guardar con nuevo ID
            session.session_id = str(uuid.uuid4())[:12]
            file_new = os.path.join(
                self.storage_dir, f"session_{session.session_id}.json"
            )
            with open(file_new, "w") as f:
                json.dump(session.to_dict(), f, indent=2, default=str)
            return session
        return None
