"""Module dummy_cache.py - Classe DummyCache."""

from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
class DummyCache:
    def put(self, key: str, value: Any, **kwargs) -> bool: return False
    def get(self, key: str) -> None: return None
    def clear(self): pass
