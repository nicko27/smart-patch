from typing import Dict, List
"""Module step_result.py - Classe StepResult."""

from dataclasses import dataclass, field

@dataclass
class StepResult:
    """Résultat d'une étape de traitement"""
    success: bool
    data: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
