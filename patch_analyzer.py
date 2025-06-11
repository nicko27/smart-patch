from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module patch_analyzer.py - Classe PatchAnalyzer."""

import re
import logging

from patch_processor_config import PatchProcessorConfig
from core_types import IssueType
from core_types import PatchIssue

class PatchAnalyzer:
    """Analyse les patches et détecte les problèmes"""
    
    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.analyzer')
        
        security_config = config.get_section('security')
        self.scan_dangerous_patterns = security_config.get('scan_dangerous_patterns', True)
        self.allow_system_calls = security_config.get('allow_system_calls', False)
    
    def analyze_patch_quality(self, patch_content: str, original_content: str) -> List[PatchIssue]:
        """Analyse complète d'un patch"""
        self.logger.debug("Analyse de la qualité du patch")
        
        issues = []
        
        # Vérifications de format
        issues.extend(self._check_format_issues(patch_content))
        
        # Vérifications de cohérence
        issues.extend(self._check_consistency_issues(patch_content, original_content))
        if issues:
            self.logger.debug(f"{len(issues)} problème(s) détecté(s) dans le patch")
        
        # Vérifications de sécurité
        if self.scan_dangerous_patterns:
            issues.extend(self._check_security_issues(patch_content))
        
        if issues:
            self.logger.debug(f"{len(issues)} problème(s) détecté(s) dans le patch")
        return issues
    
    def _check_format_issues(self, patch_content: str) -> List[PatchIssue]:
        """Vérifie les problèmes de format"""
        issues = []
        lines = patch_content.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Headers de diff malformés
            if line.startswith('@@'):
                if not re.match(r'@@\s*-\d+,?\d*\s*\+\d+,?\d*\s*@@', line):
                    issues.append(PatchIssue(
                        type=IssueType.ERROR,
                        line_number=line_num,
                        message="Format de header de diff invalide",
                        suggestion="Correction automatique du format",
                        auto_fixable=True,
                        severity=3
                    ))
            
            # Lignes sans marqueurs appropriés
            elif line.strip() and not line.startswith(('---', '+++', '@@', '+', '-', ' ', '\\')):
                issues.append(PatchIssue(
                    type=IssueType.WARNING,
                    line_number=line_num,
                    message="Ligne sans marqueur de diff détectée",
                    suggestion="Ajout automatique du marqueur approprié",
                    auto_fixable=True,
                    severity=2
                ))
            
            # Espaces en fin de ligne (peuvent causer des problèmes)
            elif line.endswith(' ') and not line.startswith('---'):
                issues.append(PatchIssue(
                    type=IssueType.INFO,
                    line_number=line_num,
                    message="Espace en fin de ligne détecté",
                    suggestion="Suppression automatique des espaces",
                    auto_fixable=True,
                    severity=1
                ))
        
        return issues
    
    def _check_consistency_issues(self, patch_content: str, original_content: str) -> List[PatchIssue]:
        """Vérifie la cohérence avec le fichier original"""
        issues = []
        original_lines = original_content.split('\n')
        
        # Vérifier les numéros de ligne dans les headers
        for match in re.finditer(r'@@\s*-(\d+)', patch_content):
            line_number = int(match.group(1))
            if line_number > len(original_lines):
                issues.append(PatchIssue(
                    type=IssueType.WARNING,
                    line_number=0,  # Header line
                    message=f"Numéro de ligne {line_number} supérieur à la taille du fichier ({len(original_lines)} lignes)",
                    suggestion="Recalcul automatique basé sur le contenu",
                    auto_fixable=True,
                    severity=2
                ))
            elif line_number <= 0:
                issues.append(PatchIssue(
                    type=IssueType.ERROR,
                    line_number=0,
                    message=f"Numéro de ligne invalide: {line_number}",
                    suggestion="Correction automatique à partir de 1",
                    auto_fixable=True,
                    severity=3
                ))
        
        return issues
    
    def _check_security_issues(self, patch_content: str) -> List[PatchIssue]:
        """Vérifie les problèmes de sécurité potentiels"""
        issues = []
        
        # Patterns dangereux à détecter
        dangerous_patterns = [
            (r'\beval\s*\(', "Utilisation d'eval() détectée", 3),
            (r'\bexec\s*\(', "Utilisation d'exec() détectée", 3),
            (r'__import__\s*\(', "Importation dynamique détectée", 2),
            (r'\bsystem\s*\(', "Appel système détecté", 3),
            (r'\bshell=True\b', "Exécution shell détectée", 2),
            (r'\bpasswd\b|\bpassword\b', "Référence à un mot de passe détectée", 2),
            (r'\btoken\b.*=.*["\'][^"\']+["\']', "Token en dur détecté", 2),
            (r'subprocess\..*shell=True', "Subprocess avec shell=True", 3)
        ]
        
        for pattern, message, severity in dangerous_patterns:
            if re.search(pattern, patch_content, re.IGNORECASE):
                issues.append(PatchIssue(
                    type=IssueType.WARNING,
                    line_number=0,
                    message=message,
                    suggestion="Vérifier que ce code est sûr",
                    auto_fixable=False,
                    severity=severity
                ))
        
        # Vérifications spécifiques si les appels système ne sont pas autorisés
        if not self.allow_system_calls:
            system_patterns = [
                r'\bos\.system\(',
                r'\bsubprocess\.',
                r'\bpopen\(',
                r'\bexecv?\('
            ]
            
            for pattern in system_patterns:
                if re.search(pattern, patch_content, re.IGNORECASE):
                    issues.append(PatchIssue(
                        type=IssueType.ERROR,
                        line_number=0,
                        message="Appel système non autorisé détecté",
                        suggestion="Supprimer ou configurer l'autorisation",
                        auto_fixable=False,
                        severity=3
                    ))
        
        return issues
