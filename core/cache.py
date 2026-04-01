"""
Cache Module - Prompt Caching
=============================
Implementación del pilar 11 - Sistema de cache de prompts.
"""

import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class CacheEntry:
    """Entrada de cache"""

    content: str
    hash: str
    created_at: datetime
    ttl_seconds: int = 300  # 5 minutos por defecto
    hit_count: int = 0
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds


class PromptCache:
    """
    Sistema de cache de prompts para reducción de costos.

    Implementa el Prompt Caching de Anthropic con:
    - Cache de 5 minutos en servidores
    - Tracking de hit rate
    - Detección automática de contenido reutilizable
    """

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.total_requests = 0

    def mark(self, content: str, ttl: int = None) -> str:
        """
        Marca contenido para cache.

        Returns:
            Hash único para identificar el contenido cacheado
        """
        hash_key = self._generate_hash(content)

        entry = CacheEntry(
            content=content,
            hash=hash_key,
            created_at=datetime.now(),
            ttl_seconds=ttl or self.default_ttl,
            size_bytes=len(content.encode()),
        )

        self.cache[hash_key] = entry
        return hash_key

    def get(self, hash_key: str) -> Optional[str]:
        """
        Obtiene contenido desde cache.

        Returns:
            Contenido cacheado o None si no existe/expiró
        """
        self.total_requests += 1
        entry = self.cache.get(hash_key)

        if not entry:
            self.miss_count += 1
            return None

        if entry.is_expired():
            del self.cache[hash_key]
            self.miss_count += 1
            return None

        entry.hit_count += 1
        self.hit_count += 1
        return entry.content

    def invalidate(self, hash_key: str) -> bool:
        """Invalida entrada de cache"""
        if hash_key in self.cache:
            del self.cache[hash_key]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Limpia entradas expiradas"""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)

    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        total_hits = sum(e.hit_count for e in self.cache.values())
        hit_rate = (self.hit_count / max(self.total_requests, 1)) * 100
        total_size = sum(e.size_bytes for e in self.cache.values())

        return {
            "entries": len(self.cache),
            "total_hits": self.hit_count,
            "total_misses": self.miss_count,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_size_bytes": total_size,
            "total_size_kb": f"{total_size / 1024:.1f}",
            "total_requests": self.total_requests,
        }

    def get_all_entries(self) -> List[Dict]:
        """Obtiene todas las entradas del cache"""
        return [
            {
                "hash": entry.hash,
                "size": entry.size_bytes,
                "created": entry.created_at.isoformat(),
                "ttl": entry.ttl_seconds,
                "hits": entry.hit_count,
                "expired": entry.is_expired(),
            }
            for entry in self.cache.values()
        ]

    def clear(self):
        """Limpia todo el cache"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        self.total_requests = 0

    def _generate_hash(self, content: str) -> str:
        """Genera hash único para contenido"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def mark_for_large_content(
        self, content: str, threshold: int = 1000
    ) -> Optional[str]:
        """
        Marca contenido grande para cache (heurística para archivos).

        Detecta automáticamente archivos grandes con alta probabilidad
        de ser reutilizados.
        """
        if len(content) >= threshold:
            return self.mark(content, ttl=300)
        return None


class MCPCache:
    """Cache específico para herramientas MCP"""

    def __init__(self):
        self.resources: Dict[str, Dict] = {}

    def cache_resource(self, uri: str, content: Any, metadata: Dict = None):
        """Cachea recurso MCP"""
        self.resources[uri] = {
            "content": content,
            "metadata": metadata or {},
            "cached_at": datetime.now().isoformat(),
        }

    def get_resource(self, uri: str) -> Optional[Any]:
        """Obtiene recurso cacheado"""
        resource = self.resources.get(uri)
        if resource:
            return resource["content"]
        return None
