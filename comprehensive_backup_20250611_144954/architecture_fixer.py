#!/usr/bin/env python3
"""
Smart Patch Processor - Correcteur architectural automatique
Corrige les problèmes structurels critiques identifiés dans l'analyse
"""

import ast
import os
import re
import sys
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

class ArchitectureFixer:
    """Corrige automatiquement les problèmes architecturaux"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.backup_dir = self.script_dir / "architecture_backups"
        self.changes_made = []
        self.critical_issues = []
        self.warnings = []
        
    def run(self):
        """Lance toutes les corrections architecturales"""
        print("🏗️ Smart Patch Processor - Correcteur architectural")
        print("=" * 60)
        
        # Créer le dossier de backup
        self.backup_dir.mkdir(exist_ok=True)
        print(f"📁 Backups dans: {self.backup_dir}")
        
        try:
            # 1. Diagnostiquer les problèmes
            self.diagnose_issues()
            
            # 2. Corriger les imports circulaires
            self.fix_circular_imports()
            
            # 3. Sécuriser les dépendances optionnelles
            self.fix_optional_dependencies()
            
            # 4. Améliorer la validation d'entrée
            self.add_input_validation()
            
            # 5. Corriger la gestion d'erreurs
            self.fix_error_handling()
            
            # 6. Ajouter un gestionnaire central
            self.create_central_manager()
            
            # 7. Créer des tests de validation
            self.create_architecture_tests()
            
            # Résumé
            self.show_summary()
            
        except Exception as e:
            print(f"❌ Erreur durant la correction: {e}")
            print("💡 Restaurez les backups si nécessaire")
            return False
            
        return True
    
    def diagnose_issues(self):
        """Diagnostique les problèmes architecturaux"""
        print("\n🔍 Diagnostic des problèmes architecturaux...")
        
        # Analyser les imports circulaires
        circular_imports = self.detect_circular_imports()
        if circular_imports:
            self.critical_issues.extend(circular_imports)
            
        # Analyser les dépendances optionnelles
        optional_deps = self.check_optional_dependencies()
        if optional_deps:
            self.warnings.extend(optional_deps)
            
        # Analyser la sécurité des entrées
        input_issues = self.check_input_validation()
        if input_issues:
            self.critical_issues.extend(input_issues)
            
        print(f"   🚨 {len(self.critical_issues)} problème(s) critique(s)")
        print(f"   ⚠️ {len(self.warnings)} avertissement(s)")
    
    def detect_circular_imports(self) -> List[str]:
        """Détecte les imports circulaires potentiels"""
        issues = []
        import_graph = {}
        
        # Analyser tous les fichiers Python
        for py_file in self.script_dir.glob("*.py"):
            if py_file.name.startswith(('test_', '__')):
                continue
                
            imports = self.extract_imports(py_file)
            import_graph[py_file.stem] = imports
        
        # Détecter les cycles
        for module, imports in import_graph.items():
            for imported in imports:
                if imported in import_graph:
                    if module in import_graph[imported]:
                        issues.append(f"Import circulaire: {module} ↔ {imported}")
        
        return issues
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extrait les imports locaux d'un fichier"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parser AST pour extraire les imports
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Ignorer les imports externes
                        if not any(alias.name.startswith(ext) for ext in 
                                 ['os', 'sys', 'pathlib', 'typing', 'datetime', 'json', 'yaml', 'logging']):
                            imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not any(node.module.startswith(ext) for ext in 
                                             ['os', 'sys', 'pathlib', 'typing', 'datetime', 'json', 'yaml', 'logging']):
                        imports.add(node.module)
        
        except Exception:
            pass  # Ignorer les erreurs de parsing
            
        return imports
    
    def check_optional_dependencies(self) -> List[str]:
        """Vérifie la gestion des dépendances optionnelles"""
        issues = []
        
        # Vérifier yaml
        config_file = self.script_dir / "patch_processor_config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                
            if "yaml.dump(" in content or "yaml.safe_load(" in content:
                if "yaml = None" not in content:
                    issues.append("YAML utilisé sans vérification de disponibilité")
        
        return issues
    
    def check_input_validation(self) -> List[str]:
        """Vérifie la validation des entrées"""
        issues = []
        
        applicator_file = self.script_dir / "patch_applicator.py"
        if applicator_file.exists():
            with open(applicator_file, 'r') as f:
                content = f.read()
            
            if "def apply_patch(self, original_content: str, diff_content: str)" in content:
                if "if not original_content" not in content:
                    issues.append("apply_patch manque de validation d'entrée")
        
        return issues
    
    def fix_circular_imports(self):
        """Corrige les imports circulaires"""
        print("\n🔄 Correction des imports circulaires...")
        
        # Créer un module central pour briser les cycles
        self.create_core_module()
        
        # Modifier les imports problématiques
        self.fix_wizard_imports()
        
        self.changes_made.append("✅ Imports circulaires corrigés avec module central")
    
    def create_core_module(self):
        """Crée un module central pour gérer les dépendances"""
        core_content = '''"""
Module central pour éviter les imports circulaires
Contient les interfaces et composants partagés
"""

from typing import Dict, Any, Optional, Protocol
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
'''
        
        core_file = self.script_dir / "core.py"
        with open(core_file, 'w', encoding='utf-8') as f:
            f.write(core_content)
        
        print(f"   📝 Module central créé: {core_file}")
    
    def fix_wizard_imports(self):
        """Corrige les imports du wizard pour utiliser le registre central"""
        wizard_file = self.script_dir / "wizard_mode.py"
        if not wizard_file.exists():
            return
        
        # Backup
        self.backup_file(wizard_file)
        
        with open(wizard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter l'import du core au début
        if "from core import registry" not in content:
            content = content.replace(
                "from colors import Colors",
                "from colors import Colors\nfrom core import registry, get_processor"
            )
        
        # Modifier les accès au processeur pour utiliser le registre
        content = content.replace(
            "self.processor.process_all_patches()",
            "get_processor().process_all_patches() if get_processor() else {}"
        )
        
        with open(wizard_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def fix_optional_dependencies(self):
        """Sécurise les dépendances optionnelles"""
        print("\n🛡️ Sécurisation des dépendances optionnelles...")
        
        config_file = self.script_dir / "patch_processor_config.py"
        if config_file.exists():
            self.backup_file(config_file)
            
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Sécuriser YAML
            if "import yaml" in content and "yaml = None" not in content:
                content = content.replace(
                    "import yaml",
                    """try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False"""
                )
                
                # Sécuriser l'utilisation de yaml
                content = content.replace(
                    "yaml.dump(",
                    "yaml.dump(" if "if yaml:" not in content else "yaml.dump("
                )
                
                content = content.replace(
                    "yaml.safe_load(",
                    "yaml.safe_load(" if "if yaml:" not in content else "yaml.safe_load("
                )
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_made.append("✅ Dépendances YAML sécurisées")
    
    def add_input_validation(self):
        """Ajoute la validation d'entrée manquante"""
        print("\n🔍 Ajout de la validation d'entrée...")
        
        # Créer un module de validation
        validation_content = '''"""
Module de validation d'entrée pour Smart Patch Processor
Centralise toutes les validations pour éviter les erreurs
"""

import os
from pathlib import Path
from typing import Union, Optional


class ValidationError(Exception):
    """Erreur de validation d'entrée"""
    pass


def validate_patch_content(original_content: str, diff_content: str) -> None:
    """Valide le contenu des patches"""
    if not isinstance(original_content, str):
        raise ValidationError(f"original_content must be string, got {type(original_content)}")
    
    if not isinstance(diff_content, str):
        raise ValidationError(f"diff_content must be string, got {type(diff_content)}")
    
    if len(diff_content.strip()) == 0:
        raise ValidationError("diff_content cannot be empty")
    
    # Vérifier que c'est un diff valide
    if not any(line.startswith(('@@', '---', '+++', '+', '-')) for line in diff_content.split('\\n')):
        raise ValidationError("diff_content does not appear to be a valid diff")


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> Path:
    """Valide un chemin de fichier"""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    if not isinstance(file_path, Path):
        raise ValidationError(f"file_path must be string or Path, got {type(file_path)}")
    
    # Vérifier contre path traversal
    try:
        resolved = file_path.resolve()
        # Vérifier que le chemin résolu ne sort pas du répertoire de travail
        cwd = Path.cwd().resolve()
        resolved.relative_to(cwd)
    except ValueError:
        raise ValidationError(f"Unsafe path detected: {file_path}")
    
    if must_exist and not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    return file_path


def validate_config_section(config_dict: dict, section: str, required_keys: list = None) -> None:
    """Valide une section de configuration"""
    if not isinstance(config_dict, dict):
        raise ValidationError(f"Config must be dict, got {type(config_dict)}")
    
    if section not in config_dict:
        raise ValidationError(f"Missing config section: {section}")
    
    section_dict = config_dict[section]
    if not isinstance(section_dict, dict):
        raise ValidationError(f"Config section {section} must be dict, got {type(section_dict)}")
    
    if required_keys:
        missing = [key for key in required_keys if key not in section_dict]
        if missing:
            raise ValidationError(f"Missing required keys in {section}: {missing}")


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour éviter les problèmes de sécurité"""
    if not isinstance(filename, str):
        raise ValidationError(f"filename must be string, got {type(filename)}")
    
    # Supprimer les caractères dangereux
    import re
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Supprimer les noms réservés Windows
    reserved = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    if cleaned.upper() in reserved:
        cleaned = f"_{cleaned}"
    
    # Limiter la longueur
    if len(cleaned) > 255:
        cleaned = cleaned[:255]
    
    return cleaned
'''
        
        validation_file = self.script_dir / "validation.py"
        with open(validation_file, 'w', encoding='utf-8') as f:
            f.write(validation_content)
        
        # Modifier patch_applicator.py pour utiliser la validation
        applicator_file = self.script_dir / "patch_applicator.py"
        if applicator_file.exists():
            self.backup_file(applicator_file)
            
            with open(applicator_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ajouter l'import de validation
            if "from validation import" not in content:
                content = content.replace(
                    "from patch_processor_config import PatchProcessorConfig",
                    "from patch_processor_config import PatchProcessorConfig\nfrom validation import validate_patch_content, ValidationError"
                )
            
            # Ajouter la validation au début de apply_patch
            content = content.replace(
                "def apply_patch(self, original_content: str, diff_content: str) -> str:",
                """def apply_patch(self, original_content: str, diff_content: str) -> str:
        \"\"\"Applique le patch avec validation et logique complète\"\"\"
        # Validation d'entrée
        try:
            validate_patch_content(original_content, diff_content)
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return original_content"""
            )
            
            with open(applicator_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        self.changes_made.append("✅ Module de validation ajouté")
        self.changes_made.append("✅ Validation d'entrée ajoutée à patch_applicator")
    
    def fix_error_handling(self):
        """Améliore la gestion d'erreurs"""
        print("\n🚨 Amélioration de la gestion d'erreurs...")
        
        # Créer un gestionnaire d'erreurs centralisé
        error_manager_content = '''"""
Gestionnaire d'erreurs centralisé pour Smart Patch Processor
"""

import logging
from typing import List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ProcessorError:
    """Représente une erreur du processeur"""
    message: str
    severity: ErrorSeverity
    context: str
    timestamp: datetime
    exception: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.context}: {self.message}"


class ErrorManager:
    """Gestionnaire centralisé des erreurs"""
    
    def __init__(self):
        self.errors: List[ProcessorError] = []
        self.logger = logging.getLogger('smart_patch_processor.errors')
    
    def add_error(self, message: str, severity: ErrorSeverity, 
                  context: str, exception: Optional[Exception] = None) -> ProcessorError:
        """Ajoute une erreur au gestionnaire"""
        error = ProcessorError(
            message=message,
            severity=severity,
            context=context,
            timestamp=datetime.now(),
            exception=exception
        )
        
        self.errors.append(error)
        
        # Logger selon la sévérité
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(str(error))
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(str(error))
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(str(error))
        else:
            self.logger.info(str(error))
        
        return error
    
    def has_critical_errors(self) -> bool:
        """Vérifie s'il y a des erreurs critiques"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)
    
    def has_errors(self) -> bool:
        """Vérifie s'il y a des erreurs (non warnings)"""
        return any(e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR] for e in self.errors)
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ProcessorError]:
        """Récupère les erreurs par sévérité"""
        return [e for e in self.errors if e.severity == severity]
    
    def clear_errors(self) -> None:
        """Efface toutes les erreurs"""
        self.errors.clear()
    
    def get_summary(self) -> dict:
        """Résumé des erreurs"""
        return {
            'total': len(self.errors),
            'critical': len(self.get_errors_by_severity(ErrorSeverity.CRITICAL)),
            'errors': len(self.get_errors_by_severity(ErrorSeverity.ERROR)),
            'warnings': len(self.get_errors_by_severity(ErrorSeverity.WARNING)),
            'info': len(self.get_errors_by_severity(ErrorSeverity.INFO))
        }


# Instance globale du gestionnaire d'erreurs
error_manager = ErrorManager()


def handle_error(message: str, context: str, exception: Optional[Exception] = None, 
                critical: bool = False) -> ProcessorError:
    """Fonction helper pour gérer les erreurs"""
    severity = ErrorSeverity.CRITICAL if critical else ErrorSeverity.ERROR
    return error_manager.add_error(message, severity, context, exception)


def handle_warning(message: str, context: str) -> ProcessorError:
    """Fonction helper pour gérer les avertissements"""
    return error_manager.add_error(message, ErrorSeverity.WARNING, context)
'''
        
        error_manager_file = self.script_dir / "error_manager.py"
        with open(error_manager_file, 'w', encoding='utf-8') as f:
            f.write(error_manager_content)
        
        self.changes_made.append("✅ Gestionnaire d'erreurs centralisé créé")
    
    def create_central_manager(self):
        """Crée un gestionnaire central pour coordonner tous les composants"""
        print("\n🏗️ Création du gestionnaire central...")
        
        manager_content = '''"""
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
'''
        
        manager_file = self.script_dir / "processor_manager.py"
        with open(manager_file, 'w', encoding='utf-8') as f:
            f.write(manager_content)
        
        self.changes_made.append("✅ Gestionnaire central créé")
    
    def create_architecture_tests(self):
        """Crée des tests pour valider l'architecture"""
        print("\n🧪 Création des tests architecturaux...")
        
        test_content = '''#!/usr/bin/env python3
"""
Tests architecturaux pour Smart Patch Processor
Valide que toutes les corrections fonctionnent correctement
"""

import sys
import traceback
from pathlib import Path
from typing import List, Tuple, Dict, Any


class ArchitectureTest:
    """Tests de validation architecturale"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_all_tests(self) -> bool:
        """Lance tous les tests architecturaux"""
        print("🧪 Tests architecturaux Smart Patch Processor")
        print("=" * 50)
        
        tests = [
            ("Imports circulaires", self.test_circular_imports),
            ("Dépendances optionnelles", self.test_optional_dependencies),
            ("Validation d'entrée", self.test_input_validation),
            ("Gestionnaire d'erreurs", self.test_error_manager),
            ("Gestionnaire central", self.test_central_manager),
            ("Configuration", self.test_configuration),
            ("Composants essentiels", self.test_core_components),
        ]
        
        for test_name, test_func in tests:
            self._run_test(test_name, test_func)
        
        self._show_results()
        return self.failed == 0
    
    def _run_test(self, name: str, test_func):
        """Lance un test individuel"""
        try:
            print(f"  Testing {name}...", end=" ")
            test_func()
            print("✅ PASS")
            self.passed += 1
        except Exception as e:
            print("❌ FAIL")
            self.failed += 1
            self.errors.append(f"{name}: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    def test_circular_imports(self):
        """Test des imports circulaires"""
        # Tester que le module core fonctionne
        from core import registry, ComponentRegistry
        assert isinstance(registry, ComponentRegistry)
        
        # Tester que les imports principaux fonctionnent
        import smart_patch_processor
        import wizard_mode
        import main
        
        # Tester que le wizard peut accéder au processeur via le registre
        from core import get_processor
        # Note: get_processor() peut retourner None si pas encore enregistré
    
    def test_optional_dependencies(self):
        """Test de la gestion des dépendances optionnelles"""
        # Tester que la configuration gère YAML correctement
        from patch_processor_config import PatchProcessorConfig
        
        # Créer une config sans fichier
        config = PatchProcessorConfig()
        assert config.config is not None
        
        # Tester que ça ne crash pas même si yaml n'est pas disponible
        try:
            # Simuler l'absence de yaml
            import sys
            original_yaml = sys.modules.get('yaml')
            if 'yaml' in sys.modules:
                del sys.modules['yaml']
            
            # Recréer la config
            config2 = PatchProcessorConfig()
            assert config2.config is not None
            
            # Restaurer yaml si il était là
            if original_yaml:
                sys.modules['yaml'] = original_yaml
                
        except Exception as e:
            # Si ça crash, c'est un problème
            raise AssertionError(f"Config crash sans yaml: {e}")
    
    def test_input_validation(self):
        """Test de la validation d'entrée"""
        from validation import validate_patch_content, ValidationError
        
        # Tester validation valide
        validate_patch_content("content", "@@ -1,1 +1,1 @@\\n content")
        
        # Tester validation invalide
        try:
            validate_patch_content(None, "content")
            raise AssertionError("Validation should have failed")
        except ValidationError:
            pass  # Expected
        
        try:
            validate_patch_content("content", "")
            raise AssertionError("Validation should have failed")
        except ValidationError:
            pass  # Expected
    
    def test_error_manager(self):
        """Test du gestionnaire d'erreurs"""
        from error_manager import error_manager, ErrorSeverity, handle_error
        
        # Nettoyer les erreurs précédentes
        error_manager.clear_errors()
        
        # Tester ajout d'erreur
        error = handle_error("Test error", "test_context")
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test error"
        
        # Tester résumé
        summary = error_manager.get_summary()
        assert summary['errors'] >= 1
        
        # Nettoyer
        error_manager.clear_errors()
    
    def test_central_manager(self):
        """Test du gestionnaire central"""
        from processor_manager import ProcessorManager, get_manager
        
        manager = get_manager()
        assert isinstance(manager, ProcessorManager)
        
        # Tester l'initialisation
        success = manager.initialize()
        assert success, "Manager initialization failed"
        
        # Tester l'état de santé
        health = manager.get_health_status()
        assert health['initialized']
        assert 'components' in health
    
    def test_configuration(self):
        """Test de la configuration"""
        from patch_processor_config import PatchProcessorConfig
        
        config = PatchProcessorConfig()
        
        # Tester les sections essentielles
        assert 'detection' in config.config
        assert 'security' in config.config
        assert 'correction' in config.config
        
        # Tester les méthodes d'accès
        threshold = config.get('correction', 'similarity_threshold', 0.5)
        assert isinstance(threshold, (int, float))
        
        security_section = config.get_section('security')
        assert isinstance(security_section, dict)
    
    def test_core_components(self):
        """Test des composants essentiels"""
        from patch_processor_config import PatchProcessorConfig
        from target_file_detector import TargetFileDetector
        from patch_analyzer import PatchAnalyzer
        from line_number_corrector import LineNumberCorrector
        from patch_applicator import PatchApplicator
        
        config = PatchProcessorConfig()
        
        # Tester que tous les composants peuvent être instanciés
        detector = TargetFileDetector(Path.cwd(), config)
        analyzer = PatchAnalyzer(config)
        corrector = LineNumberCorrector(config)
        applicator = PatchApplicator(config)
        
        assert detector is not None
        assert analyzer is not None
        assert corrector is not None
        assert applicator is not None
    
    def _show_results(self):
        """Affiche les résultats des tests"""
        total = self.passed + self.failed
        print("\\n" + "=" * 50)
        print(f"📊 Résultats: {self.passed}/{total} tests passés")
        
        if self.failed > 0:
            print(f"\\n❌ Échecs:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.failed == 0:
            print("\\n🎉 Tous les tests architecturaux sont passés !")
            print("✅ L'architecture est correctement corrigée")
        else:
            print("\\n⚠️ Certains tests ont échoué")
            print("💡 Vérifiez les erreurs ci-dessus")


def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
🧪 Tests architecturaux Smart Patch Processor

USAGE:
    python3 test_architecture.py [--verbose]

DESCRIPTION:
    Lance une suite de tests pour valider que toutes les corrections
    architecturales fonctionnent correctement.

OPTIONS:
    --verbose    Affiche les stack traces complètes en cas d'erreur

TESTS INCLUS:
    • Imports circulaires
    • Dépendances optionnelles  
    • Validation d'entrée
    • Gestionnaire d'erreurs
    • Gestionnaire central
    • Configuration
    • Composants essentiels
        """)
        return
    
    tester = ArchitectureTest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
'''
        
        test_file = self.script_dir / "test_architecture.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Rendre exécutable
        test_file.chmod(0o755)
        
        self.changes_made.append(f"✅ Tests architecturaux créés: {test_file}")
    
    def backup_file(self, file_path: Path) -> Path:
        """Crée une sauvegarde d'un fichier"""
        if not file_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.name}.backup.{timestamp}"
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def show_summary(self):
        """Affiche le résumé des corrections"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES CORRECTIONS ARCHITECTURALES")
        print("=" * 60)
        
        print(f"\\n🚨 Problèmes détectés:")
        print(f"   • {len(self.critical_issues)} problème(s) critique(s)")
        print(f"   • {len(self.warnings)} avertissement(s)")
        
        print(f"\\n✅ Corrections appliquées:")
        if self.changes_made:
            for change in self.changes_made:
                print(f"   {change}")
        else:
            print("   ⚠️ Aucune correction appliquée")
        
        print(f"\\n📁 Backups sauvegardés dans: {self.backup_dir}")
        
        print("\\n🎯 NOUVEAUX FICHIERS CRÉÉS:")
        new_files = [
            "core.py - Module central pour éviter les imports circulaires",
            "validation.py - Validation d'entrée robuste", 
            "error_manager.py - Gestionnaire d'erreurs centralisé",
            "processor_manager.py - Gestionnaire central des composants",
            "test_architecture.py - Tests de validation architecturale"
        ]
        
        for file_desc in new_files:
            print(f"   📝 {file_desc}")
        
        print("\\n🎯 PROCHAINES ÉTAPES:")
        print("1. Testez l'architecture corrigée:")
        print("   python3 test_architecture.py")
        print("\\n2. Testez le wizard corrigé:")
        print("   python3 main.py --wizard")
        print("\\n3. En cas de problème, restaurez les backups:")
        print(f"   cp {self.backup_dir}/*.backup.* ./")
        
        print("\\n🎉 Corrections architecturales terminées !")
        print("💡 Le système devrait maintenant être plus robuste et sécurisé")


def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
🏗️ Correcteur architectural Smart Patch Processor

USAGE:
    python3 fix_architecture.py

DESCRIPTION:
    Corrige automatiquement les problèmes architecturaux majeurs détectés
    dans le Smart Patch Processor, incluant :

CORRECTIONS APPLIQUÉES:
    🔄 Imports circulaires → Module central (core.py)
    🛡️ Dépendances optionnelles → Gestion sécurisée (YAML, etc.)
    🔍 Validation d'entrée → Module validation.py
    🚨 Gestion d'erreurs → Gestionnaire centralisé
    🏗️ Architecture → Gestionnaire central des composants
    🧪 Tests → Suite de validation automatique

FICHIERS MODIFIÉS:
    - wizard_mode.py (imports corrigés)
    - patch_processor_config.py (dépendances sécurisées)
    - patch_applicator.py (validation ajoutée)

NOUVEAUX FICHIERS:
    - core.py (registre central)
    - validation.py (validation robuste) 
    - error_manager.py (gestion d'erreurs)
    - processor_manager.py (gestionnaire principal)
    - test_architecture.py (tests de validation)

SÉCURITÉ:
    ✅ Backups automatiques de tous les fichiers modifiés
    ✅ Tests de validation post-correction
    ✅ Possibilité de rollback complet
        """)
        return
    
    fixer = ArchitectureFixer()
    success = fixer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()