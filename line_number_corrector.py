"""Module line_number_corrector.py - Classe LineNumberCorrector."""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
import difflib

from patch_processor_config import PatchProcessorConfig
from ast_analyzer import ASTAnalyzer

class LineNumberCorrector:
    """Responsable de la correction intelligente des numéros de ligne"""
    
    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.corrector')
        
        # Intégration de l'analyseur AST
        self.ast_analyzer = ASTAnalyzer(config)
        
        correction_config = config.get_section('correction')
        self.similarity_threshold = correction_config.get('similarity_threshold', 0.7)
        self.fuzzy_search_enabled = correction_config.get('fuzzy_search_enabled', True)
        self.context_window = correction_config.get('context_window', 5)
    
    def correct_diff_headers(self, diff_content: str, original_content: str) -> str:
        """Corrige les headers de diff avec les bons numéros de ligne"""
        self.logger.debug("Correction des numéros de ligne")
        
        # CORRECTION: Nettoyer les métadonnées avant traitement
        cleaned_diff = self._clean_diff_metadata(diff_content)
        
        original_lines = original_content.split('\n')
        diff_lines = cleaned_diff.split('\n')
        corrected_lines = []
        
        i = 0
        corrections_made = 0        
        while i < len(diff_lines):
            line = diff_lines[i]
            
            if line.startswith('@@'):
                corrected_header, context_found = self._fix_single_header(
                    line, diff_lines, original_lines, i
                )
                corrected_lines.append(corrected_header)
                
                if corrected_header != line:
                    corrections_made += 1
                    self.logger.debug(f"Correction: {line} → {corrected_header}")
            else:
                corrected_lines.append(line)
            
            i += 1  # Incrémentation cruciale
        
        if corrections_made > 0:
            self.logger.debug(f"{corrections_made} correction(s) de numéro de ligne effectuée(s)")
            
        return '\n'.join(corrected_lines)
        
            
        
    

    def _fix_single_header(self, header_line: str, diff_lines: List[str], 
                          original_lines: List[str], header_index: int) -> Tuple[str, bool]:
        """Corrige un seul header de diff"""
        
        # Extraire le contexte autour de ce header
        context = self._extract_context_from_diff(diff_lines, header_index)
        
        if not context:
            return header_line, False
        
        # Trouver la position réelle dans le fichier original
        real_line = self._find_context_position(context, original_lines)
        
        if real_line is not None:
            # Recalculer les comptes de lignes
            old_count, new_count = self._calculate_line_counts(diff_lines, header_index)
            corrected_header = self._rebuild_header(header_line, real_line, old_count, new_count)
            return corrected_header, True
        
        return header_line, False
    
    def _extract_context_from_diff(self, diff_lines: List[str], start_index: int) -> List[str]:
        """Extrait les lignes de contexte après un header de diff"""
        context = []
        i = start_index + 1
        
        while i < len(diff_lines) and not diff_lines[i].startswith('@@'):
            line = diff_lines[i]
            if line.startswith(' '):  # Ligne de contexte
                context.append(line[1:])
            elif line.startswith('-'):  # Ligne supprimée (utile pour le contexte)
                context.append(line[1:])
            i += 1
            
            # Limiter le contexte pour éviter les faux positifs
            if len(context) >= self.context_window:
                break
        
        return context
    
    def _find_context_position(self, context: List[str], file_lines: List[str]) -> Optional[int]:
        """Trouve la position du contexte dans le fichier original"""
        if not context:
            return None
        
        clean_context = [line.strip() for line in context if line.strip()]
        if not clean_context:
            return None
        
        # Recherche exacte d'abord
        exact_pos = self._exact_search(clean_context, file_lines)
        if exact_pos is not None:
            return exact_pos
        
        # Recherche floue si activée
        if self.fuzzy_search_enabled:
            return self._fuzzy_search(clean_context, file_lines)
        
        return None
    
    def _exact_search(self, context: List[str], file_lines: List[str]) -> Optional[int]:
        """Recherche exacte du contexte"""
        for i in range(len(file_lines) - len(context) + 1):
            matches = 0
            for j, context_line in enumerate(context):
                if i + j < len(file_lines):
                    file_line = file_lines[i + j].strip()
                    if file_line == context_line:
                        matches += 1
                    elif matches == 0:
                        break  # Pas de match au début
                    else:
                        break  # Match partiel trouvé
            
            # Si on a au moins 80% de correspondance et au moins 2 lignes
            if matches >= max(2, len(context) * 0.8):
                return i + 1  # +1 car les numéros de ligne commencent à 1
        
        return None
    
    def _fuzzy_search(self, context: List[str], file_lines: List[str]) -> Optional[int]:
        """Recherche floue utilisant difflib"""
        best_ratio = 0
        best_position = None
        
        for i in range(len(file_lines) - len(context) + 1):
            file_segment = [file_lines[i + j].strip() for j in range(len(context))]
            ratio = difflib.SequenceMatcher(None, context, file_segment).ratio()
            
            if ratio > best_ratio and ratio >= self.similarity_threshold:
                best_ratio = ratio
                best_position = i + 1
        
        if best_position:
            self.logger.debug(f"Correspondance floue trouvée avec {best_ratio:.2f} de similarité")
        
        return best_position
    
    def _calculate_line_counts(self, diff_lines: List[str], header_index: int) -> Tuple[int, int]:
        """Calcule le nombre de lignes old et new pour le header"""
        old_count = new_count = 0
        i = header_index + 1
        
        while i < len(diff_lines) and not diff_lines[i].startswith('@@'):
            line = diff_lines[i]
            if line.startswith((' ', '-')):
                old_count += 1
            if line.startswith((' ', '+')):
                new_count += 1
            i += 1
        
        return max(1, old_count), max(1, new_count)
    

    
    def _clean_diff_metadata(self, diff_content: str) -> str:
        """Nettoie les métadonnées du diff (---, +++, etc.)"""
        lines = diff_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Ignorer les métadonnées
            if line.startswith(('--- ', '+++ ', 'diff --git', 'index ', 'new file', 'deleted file')):
                self.logger.debug(f"Métadonnée ignorée: {line[:50]}...")
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    def _rebuild_header(self, original_header: str, new_line_number: int, 
                       old_count: int, new_count: int) -> str:
        """Reconstruit le header avec les nouveaux paramètres"""
        # Préserver le suffixe si présent (nom de fonction, etc.)
        match = re.match(r'@@\s*-\d+,?\d*\s*\+\d+,?\d*\s*@@(.*)$', original_header)
        suffix = match.group(1) if match else ''
        
        return f"@@ -{new_line_number},{old_count} +{new_line_number},{new_count} @@{suffix}"
