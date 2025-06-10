"""Module cache_stats.py - Classe CacheStats."""

from dataclasses import dataclass

@dataclass
class CacheStats:
    """Statistiques de performance du cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total * 100) if total > 0 else 0.0
