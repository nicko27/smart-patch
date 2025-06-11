from typing import Any, Dict, Optional, Protocol
"""
Module central pour éviter les imports circulaires
Contient les interfaces et composants partagés
"""

from pathlib import Path


class ComponentRegistry:
    """Registre central des composants pour éviter les imports circulaires"""
    
    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._config: Optional[Any] = None
    
    def register(self, name: str, component: Any) -> None:
        """Enregistre un composant"""
        self._components[name] = component
    
    def get(self, name: str) -> Any:
        """Récupère un composant"""
        return self._components.get(name)
    
    def set_config(self, config: Any) -> None:
        """Définit la configuration globale"""
        self._config = config
    
    def get_config(self) -> Any:
        """Récupère la configuration globale"""
        return self._config


# Instance globale du registre
registry = ComponentRegistry()


class ProcessorProtocol(Protocol):
    """Interface pour les processeurs"""
    
    def process_single_patch(self, patch_path: Path) -> Any:
        ...
    
    def process_all_patches(self) -> Dict:
        ...


class ConfigProtocol(Protocol):
    """Interface pour la configuration"""
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        ...
    
    def get_section(self, section: str) -> Dict:
        ...


def get_processor() -> Optional[ProcessorProtocol]:
    """Récupère le processeur principal"""
    return registry.get('processor')


def get_config() -> Optional[ConfigProtocol]:
    """Récupère la configuration"""
    return registry.get_config()


def safe_import(module_name: str, fallback=None):
    """Import sécurisé pour éviter les erreurs de dépendances"""
    try:
        return __import__(module_name)
    except ImportError:
        return fallback
