"""Module patch_issue.py - Classe PatchIssue."""

from typing import Dict, Optional
from dataclasses import dataclass
from issue_type import IssueType

@dataclass
class PatchIssue:
    """Représente un problème détecté dans un patch"""
    type: IssueType
    line_number: int
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    severity: int = 1  # 1=low, 2=medium, 3=high

    def to_dict(self) -> Dict:
        """Convertir en dictionnaire pour sérialisation"""
        return {
            'type': self.type.value,
            'line_number': self.line_number,
            'message': self.message,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable,
            'severity': self.severity
        }
