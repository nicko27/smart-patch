"""Module target_file_detector.py - Classe TargetFileDetector."""

import os
import re
import glob
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from patch_processor_config import PatchProcessorConfig

class TargetFileDetector:
    """Responsable de la détection intelligente des fichiers cibles"""
    
    def __init__(self, base_dir: Path, config: PatchProcessorConfig):
        self.base_dir = base_dir
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.detector')
        
        detection_config = config.get_section('detection')
        self.search_patterns = detection_config.get('search_patterns', [])
        self.file_extensions = detection_config.get('file_extensions', [])
        self.max_search_depth = detection_config.get('max_search_depth', 3)
    
    def detect_target_file(self, patch_path: Path, patch_content: str) -> Optional[Path]:
        """Détecter intelligemment le fichier cible d'un patch"""
        self.logger.debug(f"Détection du fichier cible pour {patch_path}")
        
        # 1. Essayer d'extraire depuis le contenu du patch
        target = self._detect_from_patch_content(patch_content)
        if target:
            self.logger.info(f"Fichier cible détecté depuis le contenu: {target}")
            return target
        
        # 2. Déduire depuis le nom du patch
        target = self._detect_from_patch_name(patch_path)
        if target:
            self.logger.info(f"Fichier cible détecté depuis le nom: {target}")
            return target
        
        # 3. Recherche heuristique basée sur le contenu
        target = self._heuristic_search(patch_content)
        if target:
            self.logger.info(f"Fichier cible détecté par heuristique: {target}")
            return target
        
        self.logger.warning(f"Aucun fichier cible détecté pour {patch_path}")
        return None
    
    def _detect_from_patch_content(self, patch_content: str) -> Optional[Path]:
        """Détecte le fichier cible depuis le contenu du patch"""
        lines = patch_content.split('\n')
        
        for line in lines[:10]:  # Regarder les 10 premières lignes
            for pattern in self.search_patterns:
                match = re.search(pattern, line)
                if match:
                    # Prendre le premier groupe de capture
                    filename = match.group(1).strip()
                    target = self._resolve_filename(filename)
                    if target:
                        return target
        
        return None
    
    def _detect_from_patch_name(self, patch_path: Path) -> Optional[Path]:
        """Détecte le fichier cible depuis le nom du patch"""
        patch_stem = patch_path.stem
        
        # Enlever les suffixes comme .patch, .diff
        if patch_stem.endswith(('.patch', '.diff')):
            potential_name = patch_stem.rsplit('.', 1)[0]
        else:
            potential_name = patch_stem
        
        return self._find_target_file(potential_name)
    
    def _heuristic_search(self, patch_content: str) -> Optional[Path]:
        """Recherche heuristique basée sur l'analyse du contenu"""
        # Analyser les imports, noms de classes/fonctions pour deviner le fichier
        lines = patch_content.split('\n')
        
        # Chercher des indices dans les lignes ajoutées/supprimées
        for line in lines:
            if line.startswith(('+', '-')) and len(line) > 1:
                content = line[1:].strip()
                
                # Recherche de patterns spécifiques au langage
                if content.startswith(('import ', 'from ', 'class ', 'def ', 'function ')):
                    # Extraire des mots-clés pour la recherche
                    words = re.findall(r'\b\w+\b', content)
                    for word in words:
                        if len(word) > 3:  # Ignorer les mots très courts
                            target = self._find_file_by_content_search(word)
                            if target:
                                return target
        
        return None
    
    def _resolve_filename(self, filename: str) -> Optional[Path]:
        """Résout un nom de fichier extrait du patch"""
        # Nettoyer le chemin
        clean_name = os.path.basename(filename.strip())
        
        if not clean_name or clean_name == '/dev/null':
            return None
        
        return self._find_target_file(clean_name)
    
    def _find_target_file(self, base_name: str) -> Optional[Path]:
        """Trouve un fichier cible basé sur un nom de base"""
        search_dirs = [
            self.base_dir.parent,
            self.base_dir,
            Path.cwd()
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            # Essayer le nom exact
            exact_match = search_dir / base_name
            if exact_match.exists() and exact_match.is_file():
                return exact_match
            
            # Essayer avec différentes extensions
            for ext in self.file_extensions:
                potential_file = search_dir / f"{base_name}{ext}"
                if potential_file.exists() and potential_file.is_file():
                    return potential_file
            
            # Recherche récursive limitée
            for depth in range(1, self.max_search_depth + 1):
                pattern = "*/" * depth + f"{base_name}.*"
                for file_path in search_dir.glob(pattern):
                    if (file_path.is_file() and 
                        not file_path.name.endswith(('.patch', '.diff')) and
                        file_path.suffix in self.file_extensions):
                        return file_path
        
        return None
    
    def _find_file_by_content_search(self, keyword: str) -> Optional[Path]:
        """Trouve un fichier en cherchant un mot-clé dans le contenu"""
        search_dirs = [self.base_dir.parent, self.base_dir]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for ext in self.file_extensions:
                for file_path in search_dir.glob(f"**/*{ext}"):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if keyword in content:
                                    return file_path
                        except Exception:
                            continue  # Ignorer les erreurs de lecture
        
        return None
