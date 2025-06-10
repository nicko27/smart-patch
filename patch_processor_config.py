"""Module patch_processor_config.py - Classe PatchProcessorConfig."""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
class PatchProcessorConfig:
    """Configuration externalisée pour le processeur de patches"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Charge la configuration depuis un fichier ou utilise les valeurs par défaut"""
        default_config = {
            'detection': {
                'search_patterns': [
                    r'---\s+(.+)',
                    r'\+\+\+\s+(.+)', 
                    r'Index:\s+(.+)',
                    r'diff --git a/(.+) b/(.+)'
                ],
                'file_extensions': ['.py', '.js', '.php', '.java', '.cpp', '.c'],
                'search_radius': 3,
                'max_search_depth': 3
            },
            'correction': {
                'similarity_threshold': 0.7,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 5
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'json'
            },
            'logging': {
                'level': 'WARNING',
                'console_level': 'ERROR'
            }
        }

        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix.lower() in ['.yaml', '.yml']:
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                return self._merge_configs(default_config, user_config)
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration: {e}")
                print("Utilisation de la configuration par défaut")
        
        return default_config
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Fusionne la configuration utilisateur avec les valeurs par défaut"""
        result = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in result:
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
        console_handler.setLevel(getattr(logging, log_config.get('console_level', 'INFO')))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler fichier si spécifié
        if log_config.get('file'):
            file_handler = logging.FileHandler(log_config['file'])
            file_handler.setLevel(getattr(logging, log_config.get('level', 'INFO')))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    def get(self, section: str, key: str, default=None):
        """Récupère une valeur de configuration"""
        return self.config.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict:
        """Récupère une section complète de configuration"""
        return self.config.get(section, {})
