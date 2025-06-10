"""Module processing_result.py - Classe ProcessingResult."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from patch_issue import PatchIssue

@dataclass
class ProcessingResult:
    """Résultat du traitement d'un patch"""
    patch_file: Optional[str] = None
    patches: Optional[List[str]] = None
    target_file: Optional[str] = None
    output_file: Optional[str] = None
    success: bool = False
    issues: List[PatchIssue] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    processing_type: str = "individual"
