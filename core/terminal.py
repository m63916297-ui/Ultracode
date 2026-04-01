"""
Terminal Buffer Module
=====================
Implementación del buffer de terminal con soporte para streaming.
Compatible con Streamlit Cloud (sin threading).
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable


class TerminalLine:
    """Representación de una línea en la terminal"""

    def __init__(
        self, content: str, line_type: str = "response", prefix: Optional[str] = None
    ):
        self.content = content
        self.type = line_type
        self.timestamp = datetime.now()
        self.prefix = prefix

    def to_dict(self) -> Dict[str, Any]:
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
    Compatible con Streamlit Cloud usando asyncio en lugar de threading.
    """

    def __init__(self, max_lines: int = 500):
        self.lines: List[TerminalLine] = []
        self.max_lines = max_lines
        self._callbacks: List[Callable] = []
        self._is_async = False
        try:
            loop = asyncio.get_event_loop()
            self._is_async = loop.is_running()
        except RuntimeError:
            pass

    def add_line(
        self, content: str, line_type: str = "response", prefix: Optional[str] = None
    ) -> TerminalLine:
        """Agrega una nueva línea al buffer"""
        line = TerminalLine(content=content, line_type=line_type, prefix=prefix)
        self.lines.append(line)

        for callback in self._callbacks:
            try:
                callback(line)
            except Exception:
                pass

        if len(self.lines) > self.max_lines:
            self.lines.pop(0)

        return line

    def add_lines(self, lines: List[str], line_type: str = "response"):
        """Agrega múltiples líneas"""
        for line in lines:
            self.add_line(line, line_type)

    def get_lines(self) -> List[TerminalLine]:
        """Obtiene todas las líneas"""
        return list(self.lines)

    def get_last_lines(self, count: int) -> List[TerminalLine]:
        """Obtiene las últimas N líneas"""
        if count < len(self.lines):
            return self.lines[-count:]
        return list(self.lines)

    def clear(self):
        """Limpia el buffer"""
        self.lines.clear()

    def register_callback(self, callback: Callable):
        """Registra un callback para nuevas líneas"""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        """Elimina un callback"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def to_json(self) -> str:
        """Convierte el buffer a JSON"""
        import json

        return json.dumps([line.to_dict() for line in self.lines])

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)
