"""
Module de coordination sécurisé pour éviter les imports circulaires
"""

import logging
from typing import Dict, Any, Optional, Protocol
from pathlib import Path


class ProcessorProtocol(Protocol):
    """Interface sécurisée pour les processeurs"""
    
    def process_all_patches(self) -> Dict[str, Any]:
        """Traite tous les patches et retourne un résumé"""
        ...
    
    def process_single_patch(self, patch_path: Path) -> Any:
        """Traite un patch unique"""
        ...


class SafeCoordinator:
    """Coordinateur sécurisé pour éviter les références circulaires"""
    
    def __init__(self):
        self._processor: Optional[ProcessorProtocol] = None
        self._config: Optional[Any] = None
        self.logger = logging.getLogger('smart_patch_processor.coordinator')
    
    def set_processor(self, processor: ProcessorProtocol) -> None:
        """Enregistre le processeur de manière sécurisée"""
        if processor is None:
            raise ValueError("Processor cannot be None")
        self._processor = processor
        self.logger.debug("Processeur enregistré")
    
    def get_processor(self) -> Optional[ProcessorProtocol]:
        """Récupère le processeur avec validation"""
        if self._processor is None:
            self.logger.warning("Aucun processeur enregistré")
        return self._processor
    
    def set_config(self, config: Any) -> None:
        """Enregistre la configuration"""
        self._config = config
    
    def get_config(self) -> Any:
        """Récupère la configuration"""
        return self._config
    
    def is_ready(self) -> bool:
        """Vérifie si le coordinateur est prêt"""
        return self._processor is not None and self._config is not None
    
    def safe_execute(self, operation: str, *args, **kwargs) -> Dict[str, Any]:
        """Exécute une opération de manière sécurisée"""
        try:
            if not self.is_ready():
                return {
                    'success': False,
                    'error': 'Coordinateur non initialisé',
                    'ready': False
                }
            
            if operation == 'process_all_patches':
                result = self._processor.process_all_patches()
                return {
                    'success': True,
                    'result': result,
                    'operation': operation
                }
            
            elif operation == 'process_single_patch' and args:
                result = self._processor.process_single_patch(args[0])
                return {
                    'success': True,
                    'result': result,
                    'operation': operation
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Opération non supportée: {operation}'
                }
                
        except Exception as e:
            self.logger.error(f"Erreur exécution {operation}: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': operation
            }


# Instance globale sécurisée
safe_coordinator = SafeCoordinator()


def get_safe_processor() -> Optional[ProcessorProtocol]:
    """Récupère le processeur de manière sécurisée"""
    return safe_coordinator.get_processor()


def register_processor_safe(processor: ProcessorProtocol) -> bool:
    """Enregistre un processeur de manière sécurisée"""
    try:
        safe_coordinator.set_processor(processor)
        return True
    except Exception as e:
        logging.getLogger('smart_patch_processor').error(f"Erreur enregistrement: {e}")
        return False
