"""Module apply_patch_step.py - Classe ApplyPatchStep."""

from processing_context import ProcessingContext
from processing_step import ProcessingStep
from step_result import StepResult

class ApplyPatchStep(ProcessingStep):
    def __init__(self, applicator):
        self.applicator = applicator
    
    def execute(self, context: ProcessingContext):
        original_content = context.get('original_content')
        corrected_patch = context.get('corrected_patch')
        try:
            final_content = self.applicator.apply_patch(original_content, corrected_patch)
            return StepResult(success=True, data={'final_content': final_content})
        except Exception as e:
            return StepResult(success=False, errors=[f"Erreur application: {e}"])
