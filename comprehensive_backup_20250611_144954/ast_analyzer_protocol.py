"""Module ast_analyzer_protocol.py - Classe ASTAnalyzerProtocol."""

from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from language_info import LanguageInfo

class ASTAnalyzerProtocol(Protocol):
    """Protocole pour tous les analyseurs AST"""
    
    def analyze_source(self, source_code: str) -> Dict[str, Any]:
        """Analyse le code source et retourne les informations structurelles"""
        ...
    
    def get_language_info(self) -> LanguageInfo:
        """Retourne les informations sur le langage supporté"""
        ...
