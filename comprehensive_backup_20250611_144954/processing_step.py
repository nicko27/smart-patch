"""Module processing_step.py - Classe ProcessingStep."""

from abc import ABC, abstractmethod

from processing_context import ProcessingContext

class ProcessingStep(ABC):
    """Interface pour les étapes de traitement"""
    
    @abstractmethod
    def execute(self, context: ProcessingContext):
        pass
