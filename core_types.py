from typing import Dict, List, Optional
"""
Types de base consolidés pour Smart Patch Processor
Regroupe: IssueType, LanguageType, LanguageInfo, PatchIssue
"""

from enum import Enum
from dataclasses import dataclass, field

# ============================================================================
# ENUMS DE BASE
# ============================================================================

class IssueType(Enum):
    """Types d'issues détectées"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class LanguageType(Enum):
    """Types de langages supportés"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript" 
    PHP = "php"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    RUBY = "ruby"
    CSHARP = "csharp"
    UNKNOWN = "unknown"

# ============================================================================
# CLASSES DE DONNÉES
# ============================================================================

@dataclass
class LanguageInfo:
    """Informations sur un langage"""
    name: str
    type: LanguageType
    extensions: List[str]
    analyzer_class: str
    features: List[str]
    complexity: int

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

# ============================================================================
# UTILITAIRES
# ============================================================================

def get_language_from_extension(extension: str) -> LanguageType:
    """Détecte le langage depuis l'extension de fichier"""
    mapping = {
        '.py': LanguageType.PYTHON,
        '.js': LanguageType.JAVASCRIPT,
        '.jsx': LanguageType.JAVASCRIPT,
        '.ts': LanguageType.TYPESCRIPT,
        '.tsx': LanguageType.TYPESCRIPT,
        '.php': LanguageType.PHP,
        '.java': LanguageType.JAVA,
        '.cpp': LanguageType.CPP,
        '.cxx': LanguageType.CPP,
        '.cc': LanguageType.CPP,
        '.c': LanguageType.C,
        '.h': LanguageType.C,
        '.go': LanguageType.GO,
        '.rs': LanguageType.RUST,
        '.kt': LanguageType.KOTLIN,
        '.swift': LanguageType.SWIFT,
        '.rb': LanguageType.RUBY,
        '.cs': LanguageType.CSHARP,
    }
    return mapping.get(extension.lower(), LanguageType.UNKNOWN)

def get_supported_extensions() -> Dict[LanguageType, List[str]]:
    """Retourne les extensions supportées par langage"""
    return {
        LanguageType.PYTHON: ['.py', '.pyi', '.pyw'],
        LanguageType.JAVASCRIPT: ['.js', '.jsx', '.mjs'],
        LanguageType.TYPESCRIPT: ['.ts', '.tsx', '.d.ts'],
        LanguageType.PHP: ['.php', '.php5', '.phtml'],
        LanguageType.JAVA: ['.java'],
        LanguageType.CPP: ['.cpp', '.cxx', '.cc', '.hpp', '.hxx'],
        LanguageType.C: ['.c', '.h'],
        LanguageType.GO: ['.go'],
        LanguageType.RUST: ['.rs'],
        LanguageType.KOTLIN: ['.kt', '.kts'],
        LanguageType.SWIFT: ['.swift'],
        LanguageType.RUBY: ['.rb', '.rbw'],
        LanguageType.CSHARP: ['.cs'],
    }
