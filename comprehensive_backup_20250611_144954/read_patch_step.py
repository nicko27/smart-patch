"""Module read_patch_step.py - Classe ReadPatchStep."""

from pathlib import Path

from processing_context import ProcessingContext
from step_result import StepResult
from processing_step import ProcessingStep

class ReadPatchStep(ProcessingStep):
    def __init__(self, patch_path: Path):
        self.patch_path = patch_path
    
    def execute(self, context: ProcessingContext):
        try:
            with open(self.patch_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return StepResult(success=True, data={'patch_path': self.patch_path, 'patch_content': content})
        except Exception as e:
            return StepResult(success=False, errors=[f"Erreur lecture patch: {e}"])
