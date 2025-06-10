"""Module correct_patch_step.py - Classe CorrectPatchStep."""

from processing_context import ProcessingContext
from step_result import StepResult
from processing_step import ProcessingStep

class CorrectPatchStep(ProcessingStep):
    def __init__(self, corrector):
        self.corrector = corrector
    
    def execute(self, context: ProcessingContext):
        patch_content = context.get('patch_content')
        original_content = context.get('original_content')
        corrected_patch = self.corrector.correct_diff_headers(patch_content, original_content)
        return StepResult(success=True, data={'corrected_patch': corrected_patch})
