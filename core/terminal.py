"""
Terminal Buffer Module
======================
Implementación del buffer de terminal con soporte para streaming.
"""

import threading
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class TerminalLine:
    """Representación de una línea en la terminal"""

    content: str
    type: str = "response"  # response, command, success, error, warning, info
    timestamp: datetime = field(default_factory=datetime.now)
    prefix: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "prefix": self.prefix,
        }


class TerminalBuffer:
    """
    Buffer de terminal con soporte para streaming.

    Implementa el sistema de buffer similar al motor Ink/ de Claude Code,
    con soporte para múltiples tipos de líneas y streaming en tiempo real.
    """

    def __init__(self, max_lines: int = 500):
        self.lines: List[TerminalLine] = []
        self.max_lines = max_lines
        self._lock = threading.Lock()
        self._callbacks: List[callable] = []

    def add_line(
        self, content: str, line_type: str = "response", prefix: str = None
    ) -> TerminalLine:
        """Agrega una nueva línea al buffer"""
        with self._lock:
            line = TerminalLine(content=content, type=line_type, prefix=prefix)
            self.lines.append(line)

            # Notificar callbacks
            for callback in self._callbacks:
                try:
                    callback(line)
                except:
                    pass

            # Mantener límite de líneas
            if len(self.lines) > self.max_lines:
                self.lines.pop(0)

            return line

    def add_lines(self, lines: List[str], line_type: str = "response"):
        """Agrega múltiples líneas"""
        for line in lines:
            self.add_line(line, line_type)

    def get_lines(self) -> List[TerminalLine]:
        """Obtiene todas las líneas"""
        with self._lock:
            return self.lines.copy()

    def get_last_lines(self, count: int) -> List[TerminalLine]:
        """Obtiene las últimas N líneas"""
        with self._lock:
            return self.lines[-count:] if count < len(self.lines) else self.lines.copy()

    def clear(self):
        """Limpia el buffer"""
        with self._lock:
            self.lines.clear()

    def register_callback(self, callback: callable):
        """Registra un callback para nuevas líneas"""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: callable):
        """Elimina un callback"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def to_json(self) -> str:
        """Convierte el buffer a JSON"""
        import json

        with self._lock:
            return json.dumps([line.to_dict() for line in self.lines])

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)
