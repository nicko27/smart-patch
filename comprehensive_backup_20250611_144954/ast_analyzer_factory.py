"""Module ast_analyzer_factory.py - Classe ASTAnalyzerFactory."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from language_type import LanguageType

class ASTAnalyzerFactory:
    """Factory pour créer les analyseurs AST appropriés selon le langage"""
    
    def __init__(self):
        self._analyzers: Dict[LanguageType, Type] = {}
        self._instances_cache: Dict[LanguageType, Any] = {}
        self._extension_mapping: Dict[str, LanguageType] = {}
        self.logger = logging.getLogger('smart_patch_processor.ast_factory')
        self._register_default_analyzers()
    
    def _register_default_analyzers(self):
        """Enregistre les analyseurs par défaut"""
        # Pour l'instant, utiliser l'analyseur existant comme fallback
        # TODO: Implémenter les analyseurs spécialisés
        pass
    
    def detect_language_from_extension(self, file_path: Path) -> LanguageType:
        """Détecte le langage depuis l'extension du fichier"""
        extension = file_path.suffix.lower()
        mapping = {
            '.py': LanguageType.PYTHON,
            '.js': LanguageType.JAVASCRIPT,
            '.ts': LanguageType.TYPESCRIPT,
            '.php': LanguageType.PHP,
            '.java': LanguageType.JAVA
        }
        return mapping.get(extension, LanguageType.UNKNOWN)
    
    def get_supported_languages(self) -> List[str]:
        """Retourne la liste des langages supportés"""
        return [lang.value for lang in LanguageType if lang != LanguageType.UNKNOWN]
