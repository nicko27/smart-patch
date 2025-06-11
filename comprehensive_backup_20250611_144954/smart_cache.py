"""Module smart_cache.py - Classe SmartCache."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
from datetime import datetime
import threading
from collections import OrderedDict
from datetime import datetime, timedelta
import stat

from cache_entry import CacheEntry
from cache_stats import CacheStats

class SmartCache:
    """Cache intelligent intégré pour Smart Patch Processor"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()
        self.logger = logging.getLogger('smart_patch_processor.cache')
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None, file_path: Optional[Path] = None) -> bool:
        with self._lock:
            effective_ttl = ttl or self.default_ttl
            file_mtime = file_path.stat().st_mtime if file_path and file_path.exists() else None
            
            entry = CacheEntry(
                key=key, value=value, created_at=datetime.now(),
                last_accessed=datetime.now(), access_count=1,
                ttl_seconds=effective_ttl, file_mtime=file_mtime
            )
            
            self._cache[key] = entry
            self._enforce_size_limits()
            return True
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.stats.misses += 1
                return None
            
            if entry.is_expired:
                self._cache.pop(key)
                self.stats.misses += 1
                return None
            
            entry.touch()
            self._cache.move_to_end(key)
            self.stats.hits += 1
            self.stats.update_hit_rate()
            return entry.value
    
    def _enforce_size_limits(self):
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
            self.stats.evictions += 1
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self.stats = CacheStats()
