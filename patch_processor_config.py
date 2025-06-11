from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module patch_processor_config.py - Configuration YAML améliorée."""

import json
try:
    import yaml
except ImportError:
    yaml = None
import logging
from pathlib import Path

class PatchProcessorConfig:
    """Configuration externalisée pour le processeur de patches avec support YAML amélioré"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Charge la configuration depuis un fichier ou utilise les valeurs par défaut"""
        default_config = self._get_default_config()
        
        # Ordre de priorité pour la recherche de configuration
        search_paths = []
        
        # 1. Fichier spécifié explicitement
        if config_path and config_path.exists():
            search_paths.append(config_path)
        
        # 2. Configuration utilisateur dans ~/.config/smart-patch/
        user_config_dir = Path.home() / ".config" / "smart-patch"
        for config_name in ["config.yaml", "config.yml", "smart-patch.yaml", "smart-patch.yml"]:
            user_config_file = user_config_dir / config_name
            if user_config_file.exists():
                search_paths.append(user_config_file)
                break
        
        # 3. Configuration locale dans le répertoire courant
        for config_name in ["smart_patch_config.yaml", "smart_patch_config.yml", 
                           "smart_patch_config.json", ".smart-patch.yaml"]:
            local_config = Path.cwd() / config_name
            if local_config.exists():
                search_paths.append(local_config)
                break
        
        # Charger le premier fichier trouvé
        for config_file in search_paths:
            try:
                user_config = self._load_config_file(config_file)
                if user_config:
                    print(f"📄 Configuration chargée depuis: {config_file}")
                    return self._merge_configs(default_config, user_config)
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement de {config_file}: {e}")
                continue
        
        print("📄 Utilisation de la configuration par défaut")
        return default_config
    
    def _load_config_file(self, config_path: Path) -> Optional[Dict]:
        """Version sécurisée"""
        return self._load_config_file_secure(config_path)
    
    def _load_config_file_secure(self, config_path: Path) -> Optional[Dict]:
        """Charge un fichier de configuration (YAML ou JSON) de manière sécurisée"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return None
                
                # Vérifier la taille pour éviter DoS
                if len(content.encode('utf-8')) > 10 * 1024 * 1024:  # 10MB max
                    raise ValueError("Config file too large")
                
                # Détecter le format et parser sécurisé
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    if yaml is None:
                        print(f"⚠️ PyYAML non disponible, tentative JSON pour {config_path}")
                        return json.loads(content)
                    
                    # Utiliser safe_load directement (pas de méthode séparée)
                    config = yaml.safe_load(content)
                    
                    # Validation de base
                    if not isinstance(config, dict):
                        raise ValueError("Config must be a dictionary")
                    
                    return config
                    
                elif config_path.suffix.lower() == '.json':
                    return json.loads(content)
                else:
                    # Essayer YAML d'abord, puis JSON
                    try:
                        if yaml:
                            return yaml.safe_load(content)
                        else:
                            return json.loads(content)
                    except Exception:
                        return json.loads(content)
                        
        except Exception as e:
            print(f"⚠️ Erreur chargement {config_path}: {e}")
            return None

    def _get_default_config(self) -> Dict:
        """Retourne la configuration par défaut"""
        return {
            'detection': {
                'search_patterns': [
                    r'---\s+(.+)',
                    r'\+\+\+\s+(.+)', 
                    r'Index:\s+(.+)',
                    r'diff --git a/(.+) b/(.+)'
                ],
                'file_extensions': ['.py', '.js', '.ts', '.php', '.java', '.cpp', '.c'],
                'search_radius': 3,
                'max_search_depth': 3,
                'enable_content_based_detection': True,
                'enable_filename_similarity': True
            },
            'correction': {
                'similarity_threshold': 0.7,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 5,
                'prefer_ast_detection': True,
                'auto_fix_line_numbers': True,
                'max_correction_attempts': 3
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 10,
                'require_confirmation_for_large_patches': True,
                'blocked_patterns': [
                    r"eval\s*\(",
                    r"exec\s*\(",
                    r"system\s*\(",
                    r"shell=True",
                    r"__import__\s*\(",
                    r"subprocess\."
                ],
                'validate_patch_integrity': True,
                'log_security_events': True
            },
            'guided_patching': {
                'enabled': True,
                'preview_enabled': True,
                'interactive_mode': True,
                'step_by_step': True,
                'detailed_preview': True,
                'confirmation_required': True,
                'auto_backup': True,
                'backup_compression': False,
                'modify_original': True,
                'show_diff_preview': True,
                'syntax_highlighting': True,
                'line_numbers': True,
                'context_lines': 3,
                'max_preview_lines': 50,
                'backup_retention_days': 30,
                'create_session_log': True
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'yaml',  # Changé de json à yaml
                'create_diff_reports': True,
                'include_statistics': True,
                'timestamp_files': True
            },
            'logging': {
                'level': 'INFO',  # Plus verbeux par défaut
                'console_level': 'WARNING',
                'file': None,
                'max_file_size_mb': 20,
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'performance': {
                'max_concurrent_patches': 2,
                'memory_limit_mb': 512,
                'enable_streaming': True,
                'streaming_threshold_mb': 50,
                'enable_cache': True,
                'cache_max_size': 500
            },
            'rollback': {
                'enabled': True,
                'auto_restore_on_failure': True,
                'max_rollback_history': 100
            },
            'git': {
                'enabled': False,  # Désactivé par défaut
                'auto_detect_repo': True,
                'create_branch': False
            },
            'wizard': {
                'enabled': True,
                'auto_detect_beginners': True,
                'explain_steps': True,
                'show_examples': True,
                'safety_prompts': True,
                'learning_mode': True
            },
            'advanced': {
                'enable_experimental_features': False,
                'debug_ast_analysis': False,
                'verbose_error_reporting': True,
                'enable_profiling': False
            }
        }
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Fusionne la configuration utilisateur avec les valeurs par défaut"""
        result = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _setup_logging(self):
        """Configure le système de logging"""
        log_config = self.config.get('logging', {})
        
        # Configuration du logger principal
        logger = logging.getLogger('smart_patch_processor')
        logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Supprimer les handlers existants
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        formatter = logging.Formatter(log_config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config.get('console_level', 'WARNING')))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler fichier si spécifié
        if log_config.get('file'):
            try:
                file_handler = logging.FileHandler(log_config['file'])
                file_handler.setLevel(getattr(logging, log_config.get('level', 'INFO')))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️ Impossible de créer le fichier de log {log_config['file']}: {e}")
    
    def get(self, section: str, key: str, default=None):
        """Récupère une valeur de configuration"""
        return self.config.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict:
        """Récupère une section complète de configuration"""
        return self.config.get(section, {})
    
    def save_to_file(self, output_path: Path, format: str = 'yaml') -> bool:
        """Sauvegarde la configuration dans un fichier"""
        try:
            # Créer le répertoire parent si nécessaire
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if format.lower() in ['yaml', 'yml']:
                    if yaml is None:
                        raise Exception("PyYAML requis pour le format YAML")
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False, indent=2)
                else:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde configuration: {e}")
            return False
    
    def get_config_file_locations(self) -> Dict[str, Path]:
        """Retourne les emplacements possibles pour les fichiers de configuration"""
        user_config_dir = Path.home() / ".config" / "smart-patch"
        
        return {
            'user_config_dir': user_config_dir,
            'user_config_file': user_config_dir / "config.yaml",
            'local_config_file': Path.cwd() / "smart_patch_config.yaml",
            'fallback_config_file': user_config_dir / "smart-patch.yaml"
        }
    
    def ensure_user_config_dir(self) -> Path:
        """S'assure que le répertoire de configuration utilisateur existe"""
        user_config_dir = Path.home() / ".config" / "smart-patch"
        user_config_dir.mkdir(parents=True, exist_ok=True)
        return user_config_dir
    
    def get_active_config_path(self) -> Optional[Path]:
        """Retourne le chemin du fichier de configuration actuellement utilisé"""
        # Cette méthode pourrait être améliorée pour tracker le fichier chargé
        locations = self.get_config_file_locations()
        
        for location in locations.values():
            if isinstance(location, Path) and location.exists():
                return location
        
        return None
    
    def validate_config(self) -> List[str]:
        """Valide la configuration et retourne une liste d'erreurs/avertissements"""
        warnings = []
        
        # Validation des seuils
        similarity = self.get('correction', 'similarity_threshold', 0.7)
        if not 0.0 <= similarity <= 1.0:
            warnings.append(f"similarity_threshold doit être entre 0.0 et 1.0 (actuel: {similarity})")
        
        # Validation des tailles de fichier
        max_size = self.get('security', 'max_file_size_mb', 10)
        if max_size <= 0:
            warnings.append(f"max_file_size_mb doit être positif (actuel: {max_size})")
        
        # Validation des extensions
        extensions = self.get('detection', 'file_extensions', [])
        if not extensions:
            warnings.append("Aucune extension de fichier configurée")
        
        # Validation des patterns de sécurité
        if self.get('security', 'scan_dangerous_patterns', True):
            patterns = self.get('security', 'blocked_patterns', [])
            if not patterns:
                warnings.append("Scan de sécurité activé mais aucun pattern configuré")
        
        return warnings
    def _load_yaml_secure(self, content: str) -> Optional[Dict]:
        """Chargement YAML sécurisé"""
        try:
            if not yaml:
                return None
            
            # Vérifier la taille pour éviter DoS
            if len(content.encode('utf-8')) > 10 * 1024 * 1024:  # 10MB max
                raise ValueError("Config file too large")
            
            # Utiliser safe_load pour éviter l'exécution de code
            config = yaml.safe_load(content)
            
            # Validation du format
            if not isinstance(config, dict):
                raise ValueError("Config must be a dictionary")
            
            # Vérifier contre les clés dangereuses
            dangerous_keys = ['__import__', 'eval', 'exec', '__builtins__']
            self._check_dangerous_keys(config, dangerous_keys)
            
            return config
            
        except Exception as e:
            print(f"⚠️ Erreur chargement YAML sécurisé: {e}")
            return None
    
    def _check_dangerous_keys(self, obj: Any, dangerous_keys: List[str], path: str = "") -> None:
        """Vérifie récursivement les clés dangereuses"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if str(key) in dangerous_keys:
                    raise ValueError(f"Dangerous key detected: {path}.{key}")
                self._check_dangerous_keys(value, dangerous_keys, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_dangerous_keys(item, dangerous_keys, f"{path}[{i}]")
        elif isinstance(obj, str):
            for dangerous in dangerous_keys:
                if dangerous in obj:
                    raise ValueError(f"Dangerous content in {path}: {dangerous}")
    
    def _merge_configs_secure(self, default: Dict, user: Dict, max_depth: int = 10) -> Dict:
        """Fusion sécurisée des configurations avec limite de profondeur"""
        if max_depth <= 0:
            return default  # Éviter récursion infinie
        
        if not isinstance(default, dict) or not isinstance(user, dict):
            return default
        
        result = default.copy()
        
        for key, value in user.items():
            # Validation de la clé
            if not isinstance(key, (str, int, float)):
                continue  # Ignorer les clés non standards
            
            if str(key).startswith('_'):
                continue  # Ignorer les clés privées
            
            if key in result and isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self._merge_configs_secure(result[key], value, max_depth - 1)
            else:
                # Validation de la valeur
                if self._is_safe_config_value(value):
                    result[key] = value
        
        return result
    
    def _is_safe_config_value(self, value: Any) -> bool:
        """Vérifie si une valeur de config est sûre"""
        # Types autorisés
        safe_types = (str, int, float, bool, list, dict, type(None))
        if not isinstance(value, safe_types):
            return False
        
        # Vérification récursive pour listes et dicts
        if isinstance(value, list):
            return all(self._is_safe_config_value(item) for item in value)
        elif isinstance(value, dict):
            return all(self._is_safe_config_value(v) for v in value.values())
        elif isinstance(value, str):
            # Vérifier contre patterns dangereux
            dangerous_patterns = ['__import__', 'eval(', 'exec(', 'subprocess', 'os.system']
            return not any(pattern in value for pattern in dangerous_patterns)
        
        return True