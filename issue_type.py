"""Module issue_type.py - Classe IssueType."""

from enum import Enum
class IssueType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
