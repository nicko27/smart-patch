"""Module patch_previewer.py - Classe PatchPreviewer."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from patch_processor_config import PatchProcessorConfig
from colors import Colors

class PatchPreviewer:
    """Système de prévisualisation des modifications"""
    
    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.previewer')
        
        preview_config = config.get_section('preview')
        self.enabled = preview_config.get('enabled', True)
        self.max_lines = preview_config.get('max_preview_lines', 50)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def generate_preview(self, original_content: str, patch_content: str, 
                        target_file: Path = None) -> Dict:
        """Génère un aperçu des modifications"""
        if not self.enabled:
            return {'enabled': False}
        
        preview = {
            'enabled': True,
            'target_file': str(target_file) if target_file else None,
            'changes': [],
            'statistics': {},
            'warnings': []
        }
        
        # Calcul des statistiques de base
        orig_lines = len(original_content.split('\n'))
        
        # Simulation simple de l'application du patch
        try:
            preview['statistics'] = {
                'lines_before': orig_lines,
                'estimated_changes': patch_content.count('\n+') + patch_content.count('\n-')
            }
        except Exception as e:
            preview['error'] = str(e)
        
        return preview
    
    def display_console_preview(self, preview_data: Dict):
        """Affiche un aperçu dans la console"""
        if not preview_data.get('enabled'):
            return
        
        print(f"\n{Colors.CYAN}👁️ APERÇU DES MODIFICATIONS{Colors.END}")
        stats = preview_data.get('statistics', {})
        if stats:
            changes = stats.get('estimated_changes', 0)
            print(f"📊 ~{changes} modification(s) estimée(s)")
