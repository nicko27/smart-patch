"""Module language_info.py - Classe LanguageInfo."""

from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
from dataclasses import dataclass, field

from language_type import LanguageType

@dataclass
class LanguageInfo:
    """Informations sur un langage"""
    name: str
    type: LanguageType
    extensions: List[str]
    analyzer_class: str
    features: List[str]
    complexity: int
