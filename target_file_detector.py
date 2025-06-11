"""
Correction du module target_file_detector.py pour Smart Patch Processor
Problème: Détection incorrecte des fichiers cibles causant la création de "error.py"
"""

import os
import re
import glob
import logging
from pathlib import Path
from typing import Optional, List

from patch_processor_config import PatchProcessorConfig

class TargetFileDetector:
    """Responsable de la détection intelligente des fichiers cibles - VERSION CORRIGÉE"""

    def __init__(self, base_dir: Path, config: PatchProcessorConfig):
        self.base_dir = base_dir
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.detector')

        detection_config = config.get_section('detection')
        # CORRECTION: Patterns améliorés pour détecter les vrais fichiers
        self.search_patterns = detection_config.get('search_patterns', [
            r'^\+\+\+\s+([^\t\r\n]+)',        # Nouveau fichier (priorité haute)
            r'^---\s+([^\t\r\n]+)',          # Ancien fichier
            r'^Index:\s+([^\r\n]+)',         # Index Git
            r'^diff\s+--git\s+a/([^\s]+)\s+b/([^\s]+)',  # Git diff
            r'^\*\*\*\s+([^\t\r\n]+)',       # Context diff ancien
            r'^\+\+\+\s+([^\t\r\n]+)',       # Context diff nouveau
        ])

        self.file_extensions = detection_config.get('file_extensions', [])
        self.max_search_depth = detection_config.get('max_search_depth', 3)

    def detect_target_file(self, patch_path: Path, patch_content: str) -> Optional[Path]:
        """Détecter intelligemment le fichier cible d'un patch - VERSION CORRIGÉE"""
        self.logger.debug(f"Détection du fichier cible pour {patch_path}")

        # CORRECTION 1: D'abord essayer de détecter PLUSIEURS fichiers depuis le contenu
        targets = self._detect_all_targets_from_patch_content(patch_content)
        if targets:
            # Prendre le premier fichier valide trouvé
            for target in targets:
                if target and target.exists():
                    self.logger.info(f"Fichier cible détecté depuis le contenu: {target}")
                    return target

        # CORRECTION 2: Essayer avec le nom du patch (sans erreurs de parsing)
        target = self._detect_from_patch_name_safe(patch_path)
        if target:
            self.logger.info(f"Fichier cible détecté depuis le nom: {target}")
            return target

        # CORRECTION 3: Recherche heuristique améliorée
        target = self._heuristic_search_improved(patch_content)
        if target:
            self.logger.info(f"Fichier cible détecté par heuristique: {target}")
            return target

        self.logger.warning(f"Aucun fichier cible détecté pour {patch_path}")
        return None

    def _detect_all_targets_from_patch_content(self, patch_content: str) -> List[Path]:
        """NOUVEAU: Détecte TOUS les fichiers cibles possibles dans le patch"""
        targets = []
        lines = patch_content.split('\n')

        # CORRECTION: Analyser TOUTES les lignes d'en-tête, pas seulement les 10 premières
        for line_num, line in enumerate(lines):
            # Arrêter à la première ligne de contenu de diff
            if line.startswith(('@@', ' ', '+', '-')) and not line.startswith(('+++', '---')):
                break

            line = line.strip()
            if not line:
                continue

            for pattern in self.search_patterns:
                try:
                    match = re.search(pattern, line)
                    if match:
                        # CORRECTION: Gestion des différents groupes de capture
                        if pattern.startswith(r'^diff\s+--git'):
                            # Pour git diff, prendre le fichier nouveau (groupe 2)
                            filename = match.group(2).strip()
                        else:
                            # Pour les autres, prendre le premier groupe
                            filename = match.group(1).strip()

                        # CORRECTION: Validation et nettoyage du nom de fichier
                        target = self._resolve_filename_safe(filename)
                        if target and target not in targets:
                            targets.append(target)
                            self.logger.debug(f"Fichier candidat trouvé: {target} (ligne {line_num + 1})")

                except Exception as e:
                    self.logger.debug(f"Erreur parsing ligne '{line}': {e}")
                    continue

        return targets

    def _resolve_filename_safe(self, filename: str) -> Optional[Path]:
        """CORRECTION: Résolution sécurisée et robuste des noms de fichiers"""
        if not filename or not isinstance(filename, str):
            return None

        # CORRECTION: Nettoyer les caractères parasites et timestamps
        filename = filename.strip()

        # Supprimer les timestamps et métadonnées communes
        # Exemple: "execution_screen.py	2024-01-01 12:00:01.000000000 +0100"
        filename = re.sub(r'\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.*$', '', filename)
        filename = re.sub(r'\s+[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+.*$', '', filename)  # Mon Jan 01...
        filename = filename.split('\t')[0]  # Supprimer tout après une tabulation
        filename = filename.strip()

        # CORRECTION: Ignorer les fichiers spéciaux et invalides
        invalid_names = ['/dev/null', '', '.', '..', 'a', 'b', 'error', 'new', 'old']
        clean_name = os.path.basename(filename)

        if (not clean_name or
            clean_name.lower() in invalid_names or
            len(clean_name) < 2 or
            clean_name.startswith('.')):
            return None

        # CORRECTION: Vérifier si c'est un nom de fichier valide
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]*\.[a-zA-Z0-9]+$', clean_name):
            self.logger.debug(f"Nom de fichier invalide ignoré: '{clean_name}'")
            return None

        return self._find_target_file_improved(clean_name)

    def _find_target_file_improved(self, base_name: str) -> Optional[Path]:
        """CORRECTION: Recherche améliorée des fichiers cibles"""
        # CORRECTION: Étendre la recherche à plus de répertoires
        search_dirs = [
            Path.cwd(),                    # Répertoire courant
            self.base_dir,                 # Répertoire de base
            self.base_dir.parent,          # Répertoire parent
            Path.cwd().parent,             # Parent du répertoire courant
        ]

        # Ajouter des sous-répertoires communs
        for base_dir in [Path.cwd(), self.base_dir]:
            for subdir in ['src', 'source', 'lib', 'app', 'ui', 'core']:
                subdir_path = base_dir / subdir
                if subdir_path.exists():
                    search_dirs.append(subdir_path)

        # Supprimer les doublons tout en gardant l'ordre
        seen = set()
        unique_dirs = []
        for d in search_dirs:
            if d.exists() and d not in seen:
                seen.add(d)
                unique_dirs.append(d)

        for search_dir in unique_dirs:
            self.logger.debug(f"Recherche dans: {search_dir}")

            # CORRECTION 1: Essayer le nom exact d'abord
            exact_match = search_dir / base_name
            if exact_match.exists() and exact_match.is_file():
                self.logger.debug(f"Fichier trouvé (exact): {exact_match}")
                return exact_match

            # CORRECTION 2: Recherche récursive limitée avec patterns
            for depth in range(1, min(self.max_search_depth + 1, 4)):
                pattern = "*/" * depth + base_name
                try:
                    for file_path in search_dir.glob(pattern):
                        if (file_path.is_file() and
                            not file_path.name.endswith(('.patch', '.diff', '.orig', '.backup'))):
                            self.logger.debug(f"Fichier trouvé (récursif): {file_path}")
                            return file_path
                except Exception as e:
                    self.logger.debug(f"Erreur recherche récursive: {e}")
                    continue

        self.logger.debug(f"Fichier non trouvé: {base_name}")
        return None

    def _detect_from_patch_name_safe(self, patch_path: Path) -> Optional[Path]:
        """CORRECTION: Détection sécurisée depuis le nom du patch"""
        try:
            patch_stem = patch_path.stem.lower()

            # CORRECTION: Ignorer les noms de patch génériques
            generic_names = ['error', 'patch', 'diff', 'fix', 'update', 'changes', 'new', 'old']
            if patch_stem in generic_names:
                return None

            # CORRECTION: Nettoyer le nom du patch
            # Supprimer les suffixes comme .patch, .diff
            potential_name = patch_stem
            for suffix in ['.patch', '.diff', '.fix']:
                if potential_name.endswith(suffix):
                    potential_name = potential_name[:-len(suffix)]

            # CORRECTION: Vérifier si le nom semble valide
            if len(potential_name) < 2:
                return None

            return self._find_target_file_improved(potential_name)

        except Exception as e:
            self.logger.debug(f"Erreur détection nom patch: {e}")
            return None

    def _heuristic_search_improved(self, patch_content: str) -> Optional[Path]:
        """CORRECTION: Recherche heuristique améliorée"""
        lines = patch_content.split('\n')
        keywords = set()

        # CORRECTION: Analyser le contenu pour trouver des indices
        for line in lines[:100]:  # Analyser plus de lignes
            if line.startswith(('+', '-')) and len(line) > 1:
                content = line[1:].strip()

                # CORRECTION: Recherche de patterns spécifiques améliorés
                # Classes Python
                class_match = re.search(r'class\s+([A-Z][a-zA-Z0-9_]+)', content)
                if class_match:
                    class_name = class_match.group(1)
                    keywords.add(class_name.lower())

                # Fonctions Python
                func_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]+)', content)
                if func_match:
                    func_name = func_match.group(1)
                    keywords.add(func_name)

                # Imports Python
                import_match = re.search(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]+)\s+import', content)
                if import_match:
                    module_name = import_match.group(1)
                    keywords.add(module_name.replace('.', '_'))

        # CORRECTION: Rechercher des fichiers basés sur ces mots-clés
        for keyword in keywords:
            if len(keyword) > 3:  # Ignorer les mots trop courts
                # Essayer avec extension Python
                target = self._find_target_file_improved(f"{keyword}.py")
                if target:
                    return target

                # Essayer le mot-clé dans le nom de fichier
                target = self._find_file_by_keyword(keyword)
                if target:
                    return target

        return None

    def _find_file_by_keyword(self, keyword: str) -> Optional[Path]:
        """CORRECTION: Trouve un fichier contenant un mot-clé"""
        search_dirs = [Path.cwd(), self.base_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # CORRECTION: Recherche par nom de fichier contenant le mot-clé
            for ext in self.file_extensions:
                pattern = f"*{keyword}*{ext}"
                try:
                    for file_path in search_dir.glob(pattern):
                        if file_path.is_file():
                            return file_path

                    # Recherche récursive limitée
                    for file_path in search_dir.glob(f"**/{pattern}"):
                        if (file_path.is_file() and
                            len(file_path.relative_to(search_dir).parts) <= 3):
                            return file_path

                except Exception as e:
                    self.logger.debug(f"Erreur recherche mot-clé: {e}")
                    continue

        return None

    def get_detection_summary(self) -> dict:
        """NOUVEAU: Résumé des capacités de détection pour debug"""
        return {
            'search_patterns': len(self.search_patterns),
            'file_extensions': self.file_extensions,
            'max_search_depth': self.max_search_depth,
            'base_dir': str(self.base_dir),
            'search_dirs_count': len([Path.cwd(), self.base_dir, self.base_dir.parent])
        }