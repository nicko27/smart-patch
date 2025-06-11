"""Module detect_target_step.py - Classe DetectTargetStep."""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from processing_step import ProcessingStep
from processing_context import ProcessingContext
from step_result import StepResult

class DetectTargetStep(ProcessingStep):
    def __init__(self, detector, explicit_target: Optional[Path] = None):
        self.detector = detector
        self.explicit_target = explicit_target
    
    def execute(self, context: ProcessingContext):
        patch_content = context.get('patch_content')
        patch_path = context.get('patch_path')
        
        if self.explicit_target and self.explicit_target.exists():
            target_file = self.explicit_target
        else:
            target_file = self.detector.detect_target_file(patch_path, patch_content)
        
        if not target_file:
            return StepResult(success=False, errors=["Fichier cible non détecté"])
        
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            return StepResult(success=True, data={'target_file': target_file, 'original_content': original_content})
        except Exception as e:
            return StepResult(success=False, errors=[f"Erreur lecture cible: {e}"])
