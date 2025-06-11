"""Module patch_applicator.py - Version corrigée et sécurisée"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from patch_processor_config import PatchProcessorConfig

try:
    from validation import validate_patch_content, ValidationError
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    class ValidationError(Exception):
        pass

class PatchApplicator:
    """Responsable de l'application des patches avec logique complète et sécurisée"""
    
    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.applicator')
        
        # Configuration de sécurité
        security_config = config.get_section('security')
        self.max_file_size_mb = security_config.get('max_file_size_mb', 50)
        self.max_hunks_per_patch = security_config.get('max_hunks_per_patch', 100)
    
    def apply_patch(self, original_content: str, diff_content: str) -> str:
        """Applique le patch avec validation complète et gestion d'erreurs robuste"""
        
        # Validation d'entrée sécurisée
        if not self._validate_inputs(original_content, diff_content):
            self.logger.error("Validation d'entrée échouée")
            return original_content
        
        # Vérification de taille pour éviter les DoS
        if not self._check_size_limits(original_content, diff_content):
            self.logger.error("Limites de taille dépassées")
            return original_content
        
        try:
            self.logger.debug("Application du patch")
            
            # Parse le diff en hunks avec limite de sécurité
            hunks = self._parse_unified_diff_secure(diff_content)
            
            if not hunks:
                self.logger.warning("Aucun hunk valide trouvé")
                return original_content
            
            if len(hunks) > self.max_hunks_per_patch:
                self.logger.error(f"Trop de hunks: {len(hunks)} > {self.max_hunks_per_patch}")
                return original_content
            
            # Analyser la structure du fichier
            structure = self._analyze_file_structure(original_content)
            
            # Appliquer les hunks avec logique sécurisée
            result = self._apply_hunks_secure(original_content, hunks, structure)
            
            self.logger.debug(f"{len(hunks)} hunk(s) appliqué(s) avec succès")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur critique lors de l'application: {e}")
            return original_content
    
    def _validate_inputs(self, original_content: str, diff_content: str) -> bool:
        """Validation sécurisée des entrées"""
        try:
            # Vérification des types
            if not isinstance(original_content, str) or not isinstance(diff_content, str):
                return False
            
            # Utiliser le module de validation si disponible
            if VALIDATION_AVAILABLE:
                try:
                    validate_patch_content(original_content, diff_content)
                except ValidationError as e:
                    self.logger.error(f"Validation error: {e}")
                    return False
            else:
                # Validation de base
                if len(diff_content.strip()) == 0:
                    return False
                
                # Vérifier que c'est un diff valide
                if not any(line.startswith(('@@', '---', '+++', '+', '-')) 
                          for line in diff_content.split('\n')):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur validation: {e}")
            return False
    
    def _check_size_limits(self, original_content: str, diff_content: str) -> bool:
        """Vérifie les limites de taille pour éviter les attaques DoS"""
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        
        if len(original_content.encode('utf-8')) > max_size_bytes:
            self.logger.error(f"Fichier original trop volumineux")
            return False
        
        if len(diff_content.encode('utf-8')) > max_size_bytes:
            self.logger.error(f"Diff trop volumineux")
            return False
        
        return True
    
    def _parse_unified_diff_secure(self, diff_content: str) -> List[Dict]:
        """Parse le diff avec protections de sécurité"""
        lines = diff_content.split('\n')
        hunks = []
        i = 0
        
        while i < len(lines) and len(hunks) < self.max_hunks_per_patch:
            line = lines[i].strip()
            
            # Ignorer les métadonnées et lignes dangereuses
            if (line.startswith(('--- ', '+++ ', 'diff --git', 'index ', 'new file', 'deleted file')) or
                len(line) > 1000):  # Ligne suspecte trop longue
                i += 1
                continue
            
            # Chercher un header de hunk
            if line.startswith('@@'):
                hunk = self._parse_hunk_header_secure(line)
                if hunk:
                    # Extraire le contenu du hunk avec limite
                    i += 1
                    hunk_lines = []
                    
                    while (i < len(lines) and 
                           not lines[i].strip().startswith('@@') and 
                           len(hunk_lines) < 1000):  # Limite de sécurité
                        hunk_line = lines[i]
                        if hunk_line.startswith(('+', '-', ' ')) or not hunk_line.strip():
                            hunk_lines.append(hunk_line)
                        i += 1
                    
                    hunk['lines'] = hunk_lines
                    hunks.append(hunk)
                    continue
            
            i += 1
        
        return hunks
    
    def _parse_hunk_header_secure(self, header: str) -> Optional[Dict]:
        """Parse un header de hunk avec validation"""
        pattern = r'@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@'
        match = re.match(pattern, header)
        
        if not match:
            return None
        
        try:
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1
            
            # Validation des valeurs
            if (old_start < 0 or new_start < 0 or 
                old_count < 0 or new_count < 0 or
                old_count > 10000 or new_count > 10000):
                return None
            
            return {
                'old_start': old_start - 1,  # Convertir en index 0
                'old_count': old_count,
                'new_start': new_start - 1,
                'new_count': new_count,
                'lines': []
            }
        except (ValueError, TypeError):
            return None
    
    def _analyze_file_structure(self, content: str) -> Dict:
        """Analyse sécurisée de la structure du fichier"""
        lines = content.split('\n')
        
        # Limiter l'analyse pour éviter les DoS
        max_lines_to_analyze = min(len(lines), 10000)
        lines = lines[:max_lines_to_analyze]
        
        language = self._detect_language_safe(content[:5000])  # Limite de contenu
        
        structure = {
            'classes': [],
            'functions': [],
            'main_block': None,
            'lines': lines,
            'language': language,
            'line_count': len(lines)
        }
        
        # Analyse simplifiée et sécurisée
        for i, line in enumerate(lines):
            if i > 5000:  # Limite pour éviter les boucles infinies
                break
                
            stripped = line.strip()
            if len(stripped) > 500:  # Ignorer les lignes suspectes
                continue
            
            # Détection sécurisée des classes et fonctions
            if self._is_safe_class_line(stripped, language):
                class_name = self._extract_safe_name(stripped, 'class')
                if class_name and len(class_name) <= 100:
                    structure['classes'].append({
                        'name': class_name,
                        'line': i,
                        'language': language
                    })
            
            elif self._is_safe_function_line(stripped, language):
                func_name = self._extract_safe_name(stripped, 'function')
                if func_name and len(func_name) <= 100:
                    structure['functions'].append({
                        'name': func_name,
                        'line': i,
                        'language': language
                    })
        
        return structure
    
    def _detect_language_safe(self, content: str) -> str:
        """Détection sécurisée du langage"""
        # Recherche sécurisée avec expressions régulières non-catastrophiques
        if '<?php' in content[:100]:
            return 'php'
        elif ('class ' in content and 'function ' in content and '{' in content and
              'var ' not in content):
            return 'javascript'
        elif ('public class' in content or 'import java' in content):
            return 'java'
        elif ('def ' in content and 'class ' in content):
            return 'python'
        else:
            return 'unknown'
    
    def _is_safe_class_line(self, line: str, language: str) -> bool:
        """Détection sécurisée des lignes de classe"""
        if len(line) > 200:
            return False
        
        patterns = {
            'python': r'^class\s+\w+',
            'javascript': r'^class\s+\w+',
            'php': r'^class\s+\w+',
            'java': r'class\s+\w+'
        }
        
        pattern = patterns.get(language, r'^class\s+\w+')
        return bool(re.search(pattern, line))
    
    def _is_safe_function_line(self, line: str, language: str) -> bool:
        """Détection sécurisée des lignes de fonction"""
        if len(line) > 200:
            return False
        
        patterns = {
            'python': r'^def\s+\w+',
            'javascript': r'function\s+\w+',
            'php': r'function\s+\w+',
            'java': r'\w+\s*\([^)]*\)\s*{'
        }
        
        pattern = patterns.get(language, r'^def\s+\w+')
        return bool(re.search(pattern, line))
    
    def _extract_safe_name(self, line: str, type_name: str) -> Optional[str]:
        """Extraction sécurisée de noms"""
        patterns = {
            'class': r'class\s+(\w+)',
            'function': r'(?:def|function)\s+(\w+)'
        }
        
        pattern = patterns.get(type_name, r'\w+')
        match = re.search(pattern, line)
        
        if match and len(match.group(1)) <= 100:
            return match.group(1)
        return None
    
    def _apply_hunks_secure(self, content: str, hunks: List[Dict], structure: Dict) -> str:
        """Application sécurisée des hunks"""
        lines = content.split('\n')
        
        for hunk in hunks:
            try:
                lines = self._apply_single_hunk_secure(lines, hunk, structure)
            except Exception as e:
                self.logger.warning(f"Échec application hunk: {e}")
                continue  # Continuer avec les autres hunks
        
        return '\n'.join(lines)
    
    def _apply_single_hunk_secure(self, lines: List[str], hunk: Dict, structure: Dict) -> List[str]:
        """Application sécurisée d'un seul hunk"""
        
        # Correction sécurisée des numéros de ligne
        start_line = self._correct_line_number_secure(lines, hunk, structure)
        hunk_lines = hunk.get('lines', [])
        
        if not hunk_lines or start_line < 0:
            return lines
        
        # Sécurité: limiter les modifications
        if start_line >= len(lines):
            start_line = len(lines) - 1
        
        # Appliquer le hunk avec vérifications
        return self._apply_hunk_content_secure(lines, hunk_lines, start_line)
    
    def _correct_line_number_secure(self, lines: List[str], hunk: Dict, structure: Dict) -> int:
        """Correction sécurisée des numéros de ligne"""
        original_start = hunk.get('old_start', 0)
        
        # Validation de base
        if 0 <= original_start < len(lines):
            return original_start
        
        # Recherche de contexte sécurisée
        context_lines = []
        for hunk_line in hunk.get('lines', [])[:10]:  # Limiter la recherche
            if hunk_line.startswith(' ') or hunk_line.startswith('-'):
                ctx = hunk_line[1:].strip()
                if ctx and len(ctx) <= 200:  # Éviter les lignes suspectes
                    context_lines.append(ctx)
        
        if context_lines:
            # Recherche limitée et sécurisée
            for i, line in enumerate(lines[:min(len(lines), 5000)]):
                if line.strip() == context_lines[0]:
                    self.logger.debug(f"Contexte trouvé à la ligne {i + 1}")
                    return i
        
        # Dernier recours sécurisé
        return min(original_start, len(lines) - 1) if lines else 0
    
    def _apply_hunk_content_secure(self, lines: List[str], hunk_lines: List[str], start_line: int) -> List[str]:
        """Application sécurisée du contenu du hunk"""
        result = lines.copy()
        current_line = start_line
        
        for hunk_line in hunk_lines[:1000]:  # Limite de sécurité
            if not hunk_line:
                continue
            
            operation = hunk_line[0] if hunk_line else ' '
            content = hunk_line[1:] if len(hunk_line) > 1 else ''
            
            # Vérifier la sécurité du contenu
            if len(content) > 1000:  # Ligne suspecte
                continue
            
            if operation == ' ':
                # Ligne de contexte
                current_line += 1
            elif operation == '-':
                # Ligne à supprimer
                if current_line < len(result):
                    result.pop(current_line)
            elif operation == '+':
                # Ligne à ajouter
                if current_line <= len(result):
                    result.insert(current_line, content)
                    current_line += 1
        
        return result

    def get_security_report(self) -> Dict[str, Any]:
        """Génère un rapport de sécurité"""
        return {
            'max_file_size_mb': self.max_file_size_mb,
            'max_hunks_per_patch': self.max_hunks_per_patch,
            'validation_available': VALIDATION_AVAILABLE,
            'security_features': [
                'Input validation',
                'Size limits',
                'DoS protection',
                'Safe parsing',
                'Content filtering'
            ]
        }
