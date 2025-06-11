"""
Gestionnaire central du Smart Patch Processor
Coordonne tous les composants et évite les couplages forts
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from core import registry, ComponentRegistry
from error_manager import error_manager, ErrorSeverity
from validation import validate_file_path, ValidationError


class ProcessorManager:
    """Gestionnaire principal du Smart Patch Processor"""
    
    def __init__(self):
        self.logger = logging.getLogger('smart_patch_processor.manager')
        self._initialized = False
        self._components = {}
        
    def initialize(self, config_path: Optional[Path] = None) -> bool:
        """Initialise tous les composants de manière sécurisée"""
        try:
            self.logger.info("Initialisation du ProcessorManager...")
            
            # 1. Charger la configuration
            config = self._load_config(config_path)
            registry.set_config(config)
            
            # 2. Initialiser les composants de base
            self._init_core_components(config)
            
            # 3. Initialiser les composants optionnels
            self._init_optional_components(config)
            
            # 4. Valider l'initialisation
            self._validate_initialization()
            
            self._initialized = True
            self.logger.info("ProcessorManager initialisé avec succès")
            return True
            
        except Exception as e:
            error_manager.add_error(
                f"Échec d'initialisation: {e}",
                ErrorSeverity.CRITICAL,
                "ProcessorManager.initialize",
                e
            )
            return False
    
    def _load_config(self, config_path: Optional[Path] = None):
        """Charge la configuration de manière sécurisée"""
        try:
            from patch_processor_config import PatchProcessorConfig
            
            if config_path:
                validate_file_path(config_path, must_exist=True)
            
            config = PatchProcessorConfig(config_path)
            return config
            
        except ValidationError as e:
            raise ValueError(f"Configuration invalide: {e}")
        except ImportError as e:
            raise ValueError(f"Module de configuration non disponible: {e}")
    
    def _init_core_components(self, config):
        """Initialise les composants essentiels"""
        components_to_init = [
            ('detector', 'target_file_detector', 'TargetFileDetector'),
            ('analyzer', 'patch_analyzer', 'PatchAnalyzer'),
            ('corrector', 'line_number_corrector', 'LineNumberCorrector'),
            ('applicator', 'patch_applicator', 'PatchApplicator'),
        ]
        
        for name, module_name, class_name in components_to_init:
            try:
                module = __import__(module_name)
                component_class = getattr(module, class_name)
                
                if name == 'detector':
                    # TargetFileDetector needs base_dir
                    component = component_class(Path.cwd(), config)
                else:
                    component = component_class(config)
                
                registry.register(name, component)
                self._components[name] = component
                
            except Exception as e:
                error_manager.add_error(
                    f"Échec d'initialisation du composant {name}: {e}",
                    ErrorSeverity.ERROR,
                    "ProcessorManager._init_core_components",
                    e
                )
    
    def _init_optional_components(self, config):
        """Initialise les composants optionnels"""
        optional_components = [
            ('rollback_manager', 'rollback_manager', 'RollbackManager'),
            ('previewer', 'patch_previewer', 'PatchPreviewer'),
            ('git_integration', 'git_integration', 'GitIntegration'),
            ('streaming_manager', 'streaming_manager', 'StreamingManager'),
        ]
        
        for name, module_name, class_name in optional_components:
            try:
                module = __import__(module_name)
                component_class = getattr(module, class_name)
                
                if name == 'streaming_manager':
                    from streaming_config import StreamingConfig
                    component = component_class(StreamingConfig())
                else:
                    component = component_class(config)
                
                registry.register(name, component)
                self._components[name] = component
                
            except Exception as e:
                error_manager.add_error(
                    f"Composant optionnel {name} non disponible: {e}",
                    ErrorSeverity.WARNING,
                    "ProcessorManager._init_optional_components",
                    e
                )
    
    def _validate_initialization(self):
        """Valide que l'initialisation s'est bien passée"""
        required_components = ['detector', 'analyzer', 'corrector', 'applicator']
        
        for component in required_components:
            if registry.get(component) is None:
                raise ValueError(f"Composant requis manquant: {component}")
        
        if error_manager.has_critical_errors():
            raise ValueError("Erreurs critiques détectées durant l'initialisation")
    
    def get_component(self, name: str) -> Any:
        """Récupère un composant de manière sécurisée"""
        if not self._initialized:
            raise RuntimeError("ProcessorManager not initialized")
        
        component = registry.get(name)
        if component is None:
            error_manager.add_error(
                f"Composant non trouvé: {name}",
                ErrorSeverity.WARNING,
                "ProcessorManager.get_component"
            )
        
        return component
    
    def is_initialized(self) -> bool:
        """Vérifie si le manager est initialisé"""
        return self._initialized
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retourne l'état de santé du système"""
        return {
            'initialized': self._initialized,
            'components': list(self._components.keys()),
            'errors': error_manager.get_summary(),
            'config_loaded': registry.get_config() is not None
        }


# Instance globale du gestionnaire
manager = ProcessorManager()


def get_manager() -> ProcessorManager:
    """Récupère l'instance du gestionnaire"""
    return manager


def ensure_initialized() -> bool:
    """S'assure que le système est initialisé"""
    if not manager.is_initialized():
        return manager.initialize()
    return True
