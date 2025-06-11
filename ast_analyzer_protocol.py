from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module ast_analyzer_protocol.py - Classe ASTAnalyzerProtocol."""


from core_types import LanguageInfo

class ASTAnalyzerProtocol(Protocol):
    """Protocole pour tous les analyseurs AST"""
    
    def analyze_source(self, source_code: str) -> Dict[str, Any]:
        """Analyse le code source et retourne les informations structurelles"""
        ...
    
    def get_language_info(self) -> LanguageInfo:
        """Retourne les informations sur le langage supporté"""
        ...
