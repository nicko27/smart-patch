"""Module git_integration.py - Classe GitIntegration."""

import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from patch_processor_config import PatchProcessorConfig

class GitIntegration:
    """Intégration Git simplifiée"""
    
    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.git')
        
        git_config = config.get_section('git')
        self.enabled = git_config.get('enabled', False)
        self.auto_detect = git_config.get('auto_detect_repo', True)
        self.create_branch = git_config.get('create_branch', True)
        
        self.is_git_available = self._check_git_availability()
    
    def _check_git_availability(self) -> bool:
        """Vérifie la disponibilité de Git"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def is_enabled(self) -> bool:
        return self.enabled and self.is_git_available
    
    def detect_git_repo(self, path: Path) -> bool:
        """Détecte si le chemin est dans un dépôt Git"""
        if not self.is_enabled():
            return False
        
        try:
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  cwd=path, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_integration_summary(self) -> Dict:
        """Résumé de l'intégration Git"""
        return {
            'enabled': self.enabled,
            'git_available': self.is_git_available,
            'auto_detect': self.auto_detect
        }
