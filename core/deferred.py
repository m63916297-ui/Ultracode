"""
Deferred Loading Module - Resultados en Disco
============================================
Implementación del pilar 7 - Sistema de persistencia con carga diferida.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List


@dataclass
class DeferredResult:
    """Resultado guardado en disco"""

    reference_id: str
    tool_id: str
    file_path: str
    created_at: datetime
    size_bytes: int
    accessed: bool = False
    access_count: int = 0


class DeferredLoadingSystem:
    """
    Sistema de persistencia de resultados con carga diferida.

    Resuelve el problema del Memory Bloat al:
    1. Guardar resultados grandes en disco
    2. Almacenar solo referencias ligeras en memoria
    3. Cargar bajo demanda cuando se necesita
    """

    def __init__(self, temp_dir: str = "/tmp/ultracode"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.references: Dict[str, DeferredResult] = {}
        self._memory_limit = 50 * 1024 * 1024  # 50MB default

    def store(self, tool_id: str, data: Any, custom_key: str = None) -> str:
        """
        Almacena datos en disco y retorna referencia.

        Args:
            tool_id: ID de la herramienta que generó los datos
            data: Datos a almacenar
            custom_key: Clave personalizada (opcional)

        Returns:
            Reference ID para recuperar los datos
        """
        reference_id = custom_key or self._generate_reference(tool_id, data)
        file_path = os.path.join(self.temp_dir, f"{reference_id}.json")

        # Serializar datos
        serialized = {
            "reference_id": reference_id,
            "tool_id": tool_id,
            "created_at": datetime.now().isoformat(),
            "data": data,
        }

        # Escribir a disco
        with open(file_path, "w") as f:
            json.dump(serialized, f)

        # Registrar referencia
        size = os.path.getsize(file_path)
        self.references[reference_id] = DeferredResult(
            reference_id=reference_id,
            tool_id=tool_id,
            file_path=file_path,
            created_at=datetime.now(),
            size_bytes=size,
        )

        # Verificar límite de memoria
        self._check_memory_limit()

        return reference_id

    def load(self, reference_id: str) -> Optional[Any]:
        """
        Carga datos desde referencia.

        Args:
            reference_id: ID de referencia

        Returns:
            Datos cargados o None si no existen
        """
        result = self.references.get(reference_id)
        if not result:
            return None

        if not os.path.exists(result.file_path):
            del self.references[reference_id]
            return None

        # Cargar de disco
        with open(result.file_path, "r") as f:
            serialized = json.load(f)

        # Actualizar estadísticas de acceso
        result.accessed = True
        result.access_count += 1

        return serialized.get("data")

    def exists(self, reference_id: str) -> bool:
        """Verifica si existe una referencia"""
        return reference_id in self.references

    def delete(self, reference_id: str) -> bool:
        """Elimina una referencia y sus datos"""
        result = self.references.get(reference_id)
        if result and os.path.exists(result.file_path):
            os.remove(result.file_path)
        if reference_id in self.references:
            del self.references[reference_id]
            return True
        return False

    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        Limpia archivos temporales antiguos.

        Args:
            max_age_hours: Antigüedad máxima en horas

        Returns:
            Número de archivos eliminados
        """
        cutoff = time.time() - (max_age_hours * 3600)
        deleted = 0

        for reference_id in list(self.references.keys()):
            result = self.references[reference_id]
            if os.path.getmtime(result.file_path) < cutoff:
                self.delete(reference_id)
                deleted += 1

        return deleted

    def get_stats(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        total_size = sum(r.size_bytes for r in self.references.values())
        total_accesses = sum(r.access_count for r in self.references.values())

        return {
            "references": len(self.references),
            "total_size_bytes": total_size,
            "total_size_kb": f"{total_size / 1024:.1f}",
            "total_size_mb": f"{total_size / (1024 * 1024):.2f}",
            "total_accesses": total_accesses,
            "memory_limit_bytes": self._memory_limit,
            "memory_limit_mb": f"{self._memory_limit / (1024 * 1024):.0f}",
        }

    def get_references(self) -> List[Dict]:
        """Obtiene lista de referencias"""
        return [
            {
                "reference_id": r.reference_id,
                "tool_id": r.tool_id,
                "created_at": r.created_at.isoformat(),
                "size_bytes": r.size_bytes,
                "accessed": r.accessed,
                "access_count": r.access_count,
            }
            for r in self.references.values()
        ]

    def _generate_reference(self, tool_id: str, data: Any) -> str:
        """Genera referencia única"""
        content = f"{tool_id}:{str(data)[:1000]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _check_memory_limit(self):
        """Verifica y limpia si se excede el límite de memoria"""
        total_size = sum(r.size_bytes for r in self.references.values())

        if total_size > self._memory_limit:
            # Ordenar por tiempo de acceso y eliminar los menos usados
            sorted_refs = sorted(
                self.references.items(),
                key=lambda x: (x[1].access_count, x[1].created_at),
            )

            # Eliminar la mitad menos usada
            for reference_id, _ in sorted_refs[: len(sorted_refs) // 2]:
                self.delete(reference_id)
