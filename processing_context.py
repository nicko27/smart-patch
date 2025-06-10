"""Module processing_context.py - Classe ProcessingContext."""

from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
class ProcessingContext:
    """Contexte partagé entre les étapes du pipeline"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value):
        self._data[key] = value
    
    def get(self, key: str, default=None):
        return self._data.get(key, default)
    
    def update(self, data: Dict):
        self._data.update(data)
    
    def get_all(self) -> Dict:
        return self._data.copy()
