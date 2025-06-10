"""Module cache_strategy.py - Classe CacheStrategy."""

from enum import Enum
class CacheStrategy(Enum):
    """Stratégies de cache disponibles"""
    LRU = "lru"
    LFU = "lfu" 
    TTL = "ttl"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
