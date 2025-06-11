from typing import Dict, List, Optional
#!/usr/bin/env python3
"""Système de patchage guidé pour Smart Patch Processor"""

from dataclasses import dataclass
from pathlib import Path
from colors import Colors

@dataclass
class GuidedPatchingConfig:
    preview_enabled: bool = True
    interactive_mode: bool = True
    backup_directory: Optional[Path] = None
    modify_original: bool = True
    confirmation_required: bool = True
    auto_backup: bool = True

class GuidedPatchProcessor:
    def __init__(self, processor, config: GuidedPatchingConfig):
        self.processor = processor
        self.config = config
    
    def process_guided(self, patches: List[Path]) -> Dict:
        print(f"{Colors.CYAN}🎯 Mode patchage guidé activé{Colors.END}")
        print(f"📦 {len(patches)} patch(es) à traiter")
        
        if self.config.confirmation_required:
            response = input("Continuer ? (y/N): ").strip().lower()
            if response != 'y':
                return {'success': False, 'reason': 'user_cancelled'}
        
        results = []
        for patch in patches:
            result = self.processor.process_single_patch(patch)
            results.append(result)
        
        successful = len([r for r in results if r.success])
        return {
            'success': successful > 0,
            'total_patches': len(patches),
            'successful_patches': successful,
            'results': results
        }

class ConfigGenerator:
    def create_interactive_config(self, output_path: Path = None) -> Path:
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, "generate_config.py"])
        return Path("smart_patch_config.json")

# Variables de compatibilité
GUIDED_SYSTEM_AVAILABLE = True

class SmartPatchCLI:
    def run_guided_mode(self, args):
        return True

print("📦 Système de patchage guidé chargé")
