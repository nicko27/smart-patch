"""Module cache_entry.py - Classe CacheEntry."""

from typing import List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    file_mtime: Optional[float] = None
    size_bytes: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        self.last_accessed = datetime.now()
        self.access_count += 1
