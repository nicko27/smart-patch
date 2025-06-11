"""Module language_type.py - Classe LanguageType."""

from enum import Enum
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
