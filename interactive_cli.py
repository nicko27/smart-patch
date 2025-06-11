from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module interactive_cli.py - Classe InteractiveCLI."""

import logging
from pathlib import Path

from patch_processor_config import PatchProcessorConfig
from colors import Colors

class InteractiveCLI:
    """Interface CLI interactive pour guider l'utilisateur"""
    
    def __init__(self, config: PatchProcessorConfig, processor):
        self.config = config
        self.processor = processor
        self.interactive_config = config.get_section('interactive')
        self.enabled = self.interactive_config.get('enabled', False)
        self.level = self.interactive_config.get('level', 'standard')
        self.logger = logging.getLogger('smart_patch_processor.interactive')
    
    def is_enabled(self) -> bool:
        """Vérifie si l'interface interactive est activée"""
        return self.enabled
    
    def prompt_processing_start(self, patches: List[Path]) -> Dict:
        """Invite de démarrage du traitement"""
        if not self.enabled:
            return {'proceed': True, 'options': {}}
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 MODE INTERACTIF ACTIVÉ{Colors.END}")
        print(f"📦 {len(patches)} patch(es) détecté(s)")
        
        if self.level == 'minimal':
            choice = input("Continuer ? (y/N): ").lower()
            return {'proceed': choice == 'y', 'options': {}}
        
        print("\n1. 🚀 Traitement automatique")
        print("2. 🔍 Traitement avec confirmations")
        print("3. ❌ Annuler")
        
        choice = input("Votre choix (1-3): ").strip()
        
        if choice == '3':
            return {'proceed': False, 'options': {}}
        elif choice == '2':
            return {'proceed': True, 'options': {'confirm_each': True}}
        else:
            return {'proceed': True, 'options': {'auto_mode': True}}
    
    def confirm_patch_application(self, patch_path: Path, target_file: Path) -> Dict:
        """Demande confirmation pour l'application d'un patch"""
        if not self.enabled:
            return {'proceed': True, 'options': {}}
        
        print(f"\n📄 Appliquer {patch_path.name} → {target_file.name} ? (y/N): ", end="")
        choice = input().lower()
        return {'proceed': choice == 'y', 'options': {}}
