from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module processing_pipeline.py - Classe ProcessingPipeline."""


from processing_context import ProcessingContext
from processing_result import ProcessingResult

class ProcessingPipeline:
    """Pipeline de traitement modulaire pour les patches"""
    
    def __init__(self):
        self.steps: List['ProcessingStep'] = []
        self.context = ProcessingContext()
    
    def add_step(self, step: 'ProcessingStep'):
        self.steps.append(step)
    
    def execute(self):
        try:
            for step in self.steps:
                result = step.execute(self.context)
                if not result.success:
                    return ProcessingResult(success=False, errors=result.errors)
                self.context.update(result.data)
            return ProcessingResult(success=True, data=self.context.get_all())
        except Exception as e:
            return ProcessingResult(success=False, errors=[str(e)])
