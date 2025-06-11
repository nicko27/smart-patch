"""Module analyze_patch_step.py - Classe AnalyzePatchStep."""

from processing_context import ProcessingContext
from step_result import StepResult
from processing_step import ProcessingStep

class AnalyzePatchStep(ProcessingStep):
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def execute(self, context: ProcessingContext):
        patch_content = context.get('patch_content')
        original_content = context.get('original_content')
        issues = self.analyzer.analyze_patch_quality(patch_content, original_content)
        return StepResult(success=True, data={'issues': issues})
