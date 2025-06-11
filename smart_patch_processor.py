from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module smart_patch_processor.py - Classe SmartPatchProcessor."""

import glob
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from datetime import datetime, timedelta
import stat
import re

from processing_result import ProcessingResult
from permission_config import PermissionConfig
from streaming_system import StreamingConfig
from patch_analyzer import PatchAnalyzer
from git_integration import GitIntegration
from patch_processor_config import PatchProcessorConfig
from target_file_detector import TargetFileDetector
from wizard_mode import WizardMode
from streaming_system import StreamingManager
from patch_applicator import PatchApplicator
from permission_manager import PermissionManager
from patch_previewer import PatchPreviewer
from processing_coordinator import ProcessingCoordinator
from rollback_manager import RollbackManager
from interactive_cli import InteractiveCLI
from core_types import PatchIssue
from colors import Colors
from line_number_corrector import LineNumberCorrector

class SmartPatchProcessor:
    """Processeur principal de patches avec architecture modulaire"""

    def __init__(self, source_dir: str, output_dir: str, verbose: bool = False, config_path: Optional[str] = None, target_file: Optional[str] = None):
        # Configuration
        self.config = PatchProcessorConfig(Path(config_path) if config_path else None)
        self.verbose = verbose

        # Chemins
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

        # Composants
        self.detector = TargetFileDetector(self.source_dir, self.config)
        self.analyzer = PatchAnalyzer(self.config)
        self.corrector = LineNumberCorrector(self.config)
        self.applicator = PatchApplicator(self.config)

        # Logging
        self.logger = logging.getLogger('smart_patch_processor.main')

        # Création du coordinateur
        self._create_coordinator()

        # Attributs manquants ajoutés par le correcteur
        self.target_file = Path(target_file) if target_file else None

        # État du processeur
        self.processed_patches = []
        self.processing_stats = {
            'total_patches': 0,
            'successful_patches': 0,
            'failed_patches': 0,
            'total_issues_fixed': 0,
            'processing_time': 0
        }

    def detect_patch_targets_improved(self, patch_content: str, patch_path: Path) -> list:
        """NOUVEAU: Détecte TOUS les fichiers cibles dans un patch (même multi-fichiers)"""
        targets = []

        # Analyser le patch pour identifier tous les fichiers
        lines = patch_content.split('\n')
        current_files = set()

        for line in lines:
            line = line.strip()

            # Détecter les en-têtes de fichiers
            filename = None
            if line.startswith('--- ') and not line.endswith('/dev/null'):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('+++ ') and not line.endswith('/dev/null'):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('*** '):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('Index: '):
                filename = self._extract_clean_filename(line[7:])

            if filename and filename not in current_files:
                # Résoudre le nom de fichier vers un chemin réel
                resolved_path = self._resolve_target_path(filename, patch_path)
                if resolved_path:
                    targets.append(resolved_path)
                    current_files.add(filename)
                    self.logger.debug(f"Fichier cible détecté: {filename} -> {resolved_path}")

        # Fallback vers la détection classique si rien trouvé
        if not targets:
            classic_target = self.detector.detect_target_file(patch_path, patch_content)
            if classic_target:
                targets.append(classic_target)

        return targets

    def _extract_clean_filename(self, raw_filename: str) -> str:
        """NOUVEAU: Extrait et nettoie un nom de fichier des métadonnées"""
        if not raw_filename:
            return None

        # Supprimer les timestamps et métadonnées
        filename = raw_filename.strip()
        filename = re.sub(r'\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.*$', '', filename)
        filename = re.sub(r'\s+[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+.*$', '', filename)
        filename = filename.split('\t')[0].strip()

        # Extraire juste le nom de fichier (pas le chemin complet)
        filename = filename.split('/')[-1] if '/' in filename else filename

        # Valider que c'est un nom de fichier valide
        if (filename and
            len(filename) > 2 and
            '.' in filename and
            not filename.startswith('.') and
            filename not in ['a', 'b', 'old', 'new', 'error']):
            return filename

        return None

    def _resolve_target_path(self, filename: str, patch_path: Path) -> Path:
        """NOUVEAU: Résout un nom de fichier vers un chemin réel"""
        if not filename:
            return None

        # Rechercher dans plusieurs répertoires
        search_dirs = [
            Path.cwd(),                           # Répertoire courant
            patch_path.parent,                    # Répertoire du patch
            self.source_dir if self.source_dir.is_dir() else self.source_dir.parent,
        ]

        # Ajouter des sous-répertoires courants si ils existent
        for base in [Path.cwd(), patch_path.parent]:
            for subdir in ['src', 'ui', 'lib', 'app', 'core']:
                subdir_path = base / subdir
                if subdir_path.exists():
                    search_dirs.append(subdir_path)

        # Rechercher le fichier
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Recherche exacte
            target_path = search_dir / filename
            if target_path.exists() and target_path.is_file():
                return target_path

            # Recherche récursive limitée
            for depth in range(1, 4):
                pattern = "*/" * depth + filename
                try:
                    for found_path in search_dir.glob(pattern):
                        if found_path.is_file():
                            return found_path
                except Exception:
                    continue

        return None

        # Composants optionnels
        try:
            self.rollback_manager = RollbackManager(self.config)
        except:
            self.rollback_manager = None

        try:
            self.previewer = PatchPreviewer(self.config)
        except:
            self.previewer = None

        try:
            self.git_integration = GitIntegration(self.config)
        except:
            self.git_integration = None

        try:
            self.interactive_cli = InteractiveCLI(self.config, self)
        except:
            self.interactive_cli = None

        try:
            permission_config = PermissionConfig()
            self.permission_manager = PermissionManager(permission_config)
        except:
            self.permission_manager = None

        try:
            streaming_config = StreamingConfig()
            self.streaming_manager = StreamingManager(streaming_config)
        except:
            self.streaming_manager = None

        try:
            self.wizard_mode = WizardMode(self, self.config)
        except:
            self.wizard_mode = None


    def _create_coordinator(self) -> None:
        """Crée un coordinateur avec les composants existants"""
        components = {
            'detector': self.detector,
            'analyzer': self.analyzer,
            'corrector': self.corrector,
            'applicator': self.applicator
        }
        self.coordinator = ProcessingCoordinator(self.config, components)

    def process_with_pipeline(self, patch_path: Path, target_file: Optional[Path] = None):
        """Utilise le nouveau pipeline pour traiter un patch"""
        return self.coordinator.coordinate_single_patch(patch_path, target_file)

    def user_message(self, message: str, level: str = "info"):
        """Affiche un message à l'utilisateur selon le niveau de verbosité"""
        if level == "error":
            print(f"{Colors.RED}❌ {message}{Colors.END}")
        elif level == "success":
            print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        elif level == "warning":
            print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
        elif level == "info" and self.verbose:
            print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
        elif level == "debug" and self.verbose:
            print(f"{Colors.PURPLE}🔍 {message}{Colors.END}")

    def print_banner(self):
        """Afficher la bannière"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║          🚀 SMART PATCH PROCESSOR v2.0                         ║")
        print("║      Traitement Intelligent de Dossiers de Patches             ║")
        print("║         Architecture Modulaire & Fonctionnalités Avancées      ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")


    def process_large_file_streaming(self, file_path: Path, processor_func: callable):
        """Traite un gros fichier en streaming"""
        if self.streaming_manager.should_use_streaming(file_path):
            self.user_message(f"Traitement streaming activé pour {file_path.name}", "debug")

            with self.streaming_manager.streaming_context(file_path) as reader:
                return processor_func(reader)
        else:
            # Traitement standard pour petits fichiers
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return processor_func(content)

    def find_patches(self) -> List[Path]:
        """Trouver tous les patches dans le dossier source"""
        patch_extensions = ['*.patch', '*.diff', '*.pch']
        patches = []

        if self.source_dir.is_file():
            patches = [self.source_dir]
        else:
            for pattern in patch_extensions:
                patches.extend(self.source_dir.glob(pattern))
                patches.extend(self.source_dir.glob(f"**/{pattern}"))

        self.logger.debug(f"{len(patches)} patch(es) trouvé(s)")
        return sorted(patches)

    def process_single_patch(self, patch_path: Path, explicit_target: Optional[Path] = None) -> ProcessingResult:
        """Traiter un seul patch"""
        result = ProcessingResult(
            patch_file=str(patch_path),
            processing_type="individual"
        )

        try:
            self.logger.debug(f"Traitement du patch: {patch_path.name}")

            # Vérifier la taille du fichier
            max_size = self.config.get('security', 'max_file_size_mb', 10) * 1024 * 1024
            if patch_path.stat().st_size > max_size:
                result.errors.append(f"Fichier trop volumineux (>{max_size} bytes)")
                return result

            # Lire le patch
            with open(patch_path, 'r', encoding='utf-8') as f:
                patch_content = f.read()

            # CORRECTION: Détection améliorée des fichiers cibles
            if explicit_target and explicit_target.exists():
                target_files = [explicit_target]
                self.logger.debug(f"Utilisation du fichier cible spécifié: {explicit_target}")
            elif hasattr(self, "target_file") and self.target_file and self.target_file.exists():
                target_files = [self.target_file]
                self.logger.debug(f"Utilisation du fichier cible de l\'instance: {self.target_file}")
            else:
                # NOUVEAU: Détecter tous les fichiers cibles possibles
                target_files = self.detect_patch_targets_improved(patch_content, patch_path)

                if not target_files:
                    result.errors.append("Aucun fichier cible détecté - le patch ne semble pas contenir de fichiers Python valides")
                    return result

                self.logger.debug(f"Fichiers cibles détectés: {[str(f) for f in target_files]}")

            # Traiter le premier fichier cible valide trouvé
            target_file = target_files[0]

            result.target_file = str(target_file)

            # Lire le fichier original
            with open(target_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Analyser le patch
            issues = self.analyzer.analyze_patch_quality(patch_content, original_content)
            result.issues = issues

            # Corriger les numéros de ligne
            corrected_patch = self.corrector.correct_diff_headers(patch_content, original_content)

            # Appliquer le patch
            corrected_content = self.applicator.apply_patch(original_content, corrected_patch)

            # Sauvegarder le résultat
            output_file = self._get_unique_output_path(target_file)

            # Optionnel: créer une sauvegarde
            if self.config.get('output', 'preserve_original', True):
                backup_file = output_file.with_suffix(output_file.suffix + '.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(corrected_content)

            result.output_file = str(output_file)
            result.success = True

            # Statistiques
            result.stats = self._calculate_stats(original_content, corrected_content, issues)

            self.logger.debug(f"Patch appliqué avec succès: {output_file}")

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {patch_path}: {e}")
            result.errors.append(str(e))

            # Restaurer les permissions en cas d'erreur si configuré
            if self.permission_manager.config.auto_restore_on_failure and target_file:
                try:
                    self.permission_manager.restore_file_permissions(target_file)
                    self.user_message(f"Permissions restaurées pour {target_file.name} après erreur", "info")
                except Exception as e:
                    self.logger.debug(f"Erreur non-critique ignorée: {e}")


        return result

    def process_cumulative_patches(self, target_file: Path, patches: List[Path]) -> ProcessingResult:
        """Appliquer plusieurs patches de manière cumulative sur un même fichier"""
        result = ProcessingResult(
            target_file=str(target_file),
            patches=[str(p) for p in patches],
            processing_type="cumulative"
        )

        try:
            self.user_message(f"Application cumulative de {len(patches)} patch(es) sur {target_file.name}", "debug")

            # Lire le fichier original
            with open(target_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            original_content = current_content

            all_issues = []
            total_modifications = 0

            # Appliquer chaque patch séquentiellement
            for i, patch_path in enumerate(patches, 1):
                self.logger.debug(f"Application du patch {i}/{len(patches)}: {patch_path.name}")

                # Lire le patch
                with open(patch_path, 'r', encoding='utf-8') as f:
                    patch_content = f.read()

                # Analyser le patch
                issues = self.analyzer.analyze_patch_quality(patch_content, current_content)
                all_issues.extend(issues)

                # Corriger et appliquer le patch
                corrected_patch = self.corrector.correct_diff_headers(patch_content, current_content)
                new_content = self.applicator.apply_patch(current_content, corrected_patch)

                # Compter les modifications
                lines_before = len(current_content.split('\n'))
                lines_after = len(new_content.split('\n'))
                total_modifications += abs(lines_after - lines_before)

                # Mettre à jour le contenu pour le prochain patch
                current_content = new_content

            # Sauvegarder le résultat final
            output_file = self._get_unique_output_path(target_file, suffix='_cumulative')

            # Sauvegarde optionnelle
            if self.config.get('output', 'preserve_original', True):
                backup_file = output_file.with_suffix(output_file.suffix + '.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(current_content)

            result.output_file = str(output_file)
            result.success = True
            result.issues = all_issues

            # Statistiques cumulatives
            result.stats = {
                'original_lines': len(original_content.split('\n')),
                'final_lines': len(current_content.split('\n')),
                'total_lines_diff': len(current_content.split('\n')) - len(original_content.split('\n')),
                'patches_applied': len(patches),
                'total_issues_fixed': len(all_issues),
                'total_modifications': total_modifications
            }

            self.user_message(f"Application cumulative réussie: {output_file}", "debug")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'application cumulative: {e}")
            result.errors.append(str(e))



        return result

    def group_patches_by_target(self, patches: List[Path]) -> Dict[str, List[Path]]:
        """Grouper les patches par fichier cible"""
        groups = {}

        for patch_path in patches:
            try:
                with open(patch_path, 'r', encoding='utf-8') as f:
                    patch_content = f.read()

                target_file = self.detector.detect_target_file(patch_path, patch_content)
                if target_file:
                    target_key = str(target_file)
                    if target_key not in groups:
                        groups[target_key] = []
                    groups[target_key].append(patch_path)
                else:
                    # Patches orphelins
                    orphan_key = f"orphan_{patch_path.name}"
                    groups[orphan_key] = [patch_path]
            except Exception as e:
                self.logger.warning(f"Erreur lecture {patch_path.name}: {e}")
                error_key = f"error_{patch_path.name}"
                groups[error_key] = [patch_path]

        return groups

    def process_explicit_patch(self, patch_file: Path, target_file: Path) -> ProcessingResult:
        """Traiter un patch spécifique sur un fichier cible spécifique"""
        if not patch_file.exists():
            result = ProcessingResult(patch_file=str(patch_file))
            result.errors.append(f"Fichier patch non trouvé: {patch_file}")
            return result

        if not target_file.exists():
            result = ProcessingResult(patch_file=str(patch_file), target_file=str(target_file))
            result.errors.append(f"Fichier cible non trouvé: {target_file}")
            return result

        self.user_message(f"Mode explicite: {patch_file.name} → {target_file.name}", "debug")
        return self.process_single_patch(patch_file, explicit_target=target_file)

    def process_all_patches(self) -> Dict:
        """Traiter tous les patches trouvés ou un patch spécifique"""
        start_time = datetime.now()

        # Mode patch explicite avec fichier cible
        if self.source_dir.is_file() and self.target_file:
            self.logger.info("Mode patch explicite avec fichier cible spécifié")
            result = self.process_explicit_patch(self.source_dir, self.target_file)

            processing_time = (datetime.now() - start_time).total_seconds()
            success_count = 1 if result.success else 0

            self._print_single_result(result)
            self._print_summary(1, 1, success_count, len(result.issues), processing_time)

            return {
                'total': 1,
                'groups': 1,
                'success': success_count,
                'failed': 1 - success_count,
                'results': [result],
                'processing_time': processing_time
            }

        patches = self.find_patches()
        if not patches:
            self.logger.error(f"Aucun patch trouvé dans {self.source_dir}")
            return {'total': 0, 'success': 0, 'failed': 0, 'results': []}

        # Grouper les patches par fichier cible
        groups = self.group_patches_by_target(patches)

        print(f"{Colors.BLUE}📦 Traitement de {len(patches)} patch(es) groupé(s) en {len(groups)} cible(s)...{Colors.END}\n")

        results = []
        success_count = 0
        total_issues_fixed = 0

        for i, (target_path, target_patches) in enumerate(groups.items(), 1):
            print(f"{Colors.CYAN}[{i}/{len(groups)}] 🎯 Cible: {Path(target_path).name if not target_path.startswith(('orphan_', 'error_')) else target_path}{Colors.END}")

            if len(target_patches) == 1:
                # Un seul patch pour cette cible
                result = self.process_single_patch(target_patches[0])
            else:
                # Plusieurs patches pour la même cible - application cumulative
                if not target_path.startswith(('orphan_', 'error_')):
                    target_file = Path(target_path)
                    result = self.process_cumulative_patches(target_file, target_patches)
                else:
                    # Patches orphelins - traiter individuellement
                    result = self.process_single_patch(target_patches[0])

            results.append(result)

            if result.success:
                success_count += 1
                issues_count = len(result.issues)
                total_issues_fixed += issues_count

                if result.processing_type == "cumulative":
                    patches_applied = result.stats.get('patches_applied', 1)
                    print(f"{Colors.GREEN}   ✅ Succès: {patches_applied} patch(es) appliqué(s) → {result.output_file}{Colors.END}")
                else:
                    print(f"{Colors.GREEN}   ✅ Succès: {result.output_file}{Colors.END}")

                if issues_count > 0:
                    print(f"{Colors.YELLOW}   🔧 {issues_count} problème(s) corrigé(s){Colors.END}")
            else:
                print(f"{Colors.RED}   ❌ Échec: {', '.join(result.errors)}{Colors.END}")

            print()

        # Calculer le temps de traitement
        processing_time = (datetime.now() - start_time).total_seconds()

        # Mettre à jour les statistiques
        self.processing_stats.update({
            'total_patches': len(patches),
            'successful_patches': success_count,
            'failed_patches': len(groups) - success_count,
            'total_issues_fixed': total_issues_fixed,
            'processing_time': processing_time
        })

        # Résumé final
        self._print_summary(len(patches), len(groups), success_count, total_issues_fixed, processing_time)

        return {
            'total': len(patches),
            'groups': len(groups),
            'success': success_count,
            'failed': len(groups) - success_count,
            'results': results,
            'processing_time': processing_time
        }

    def _get_unique_output_path(self, target_file: Path, suffix: str = '') -> Path:
        """Génère un chemin de sortie unique pour éviter les collisions"""
        base_name = target_file.stem + suffix
        extension = target_file.suffix
        output_file = self.output_dir / f"{base_name}{extension}"

        counter = 1
        while output_file.exists():
            output_file = self.output_dir / f"{base_name}_{counter}{extension}"
            counter += 1

        return output_file

    def _calculate_stats(self, original_content: str, final_content: str,
                        issues: List[PatchIssue]) -> Dict:
        """Calcule les statistiques pour un patch"""
        original_lines = len(original_content.split('\n'))
        final_lines = len(final_content.split('\n'))

        return {
            'original_lines': original_lines,
            'final_lines': final_lines,
            'lines_diff': final_lines - original_lines,
            'issues_fixed': len(issues),
            'auto_fixable_issues': len([i for i in issues if i.auto_fixable]),
            'severity_breakdown': {
                'high': len([i for i in issues if i.severity == 3]),
                'medium': len([i for i in issues if i.severity == 2]),
                'low': len([i for i in issues if i.severity == 1])
            }
        }

    def _print_single_result(self, result: ProcessingResult):
        """Affiche le résultat d'un traitement unique"""
        if result.success:
            print(f"{Colors.GREEN}✅ Patch appliqué avec succès:{Colors.END}")
            print(f"   📁 Fichier source: {result.patch_file}")
            print(f"   🎯 Fichier cible: {result.target_file}")
            print(f"   💾 Fichier généré: {result.output_file}")

            if result.issues:
                issues_count = len(result.issues)
                print(f"   🔧 {issues_count} problème(s) corrigé(s)")

                if self.verbose:
                    for issue in result.issues:
                        severity_icon = "🔴" if issue.severity == 3 else "🟡" if issue.severity == 2 else "🟢"
                        print(f"      {severity_icon} {issue.message}")

            if result.stats:
                stats = result.stats
                lines_diff = stats.get('lines_diff', 0)
                sign = '+' if lines_diff > 0 else ''
                print(f"   📊 {sign}{lines_diff} ligne(s) de différence")
        else:
            print(f"{Colors.RED}❌ Échec de l'application du patch:{Colors.END}")
            print(f"   📁 Fichier patch: {result.patch_file}")
            if result.target_file:
                print(f"   🎯 Fichier cible: {result.target_file}")
            for error in result.errors:
                print(f"   ⚠️ {error}")

    def _print_summary(self, total_patches: int, total_groups: int, success_count: int,
                      total_issues_fixed: int, processing_time: float):
        """Affiche le résumé final"""
        failed_count = total_groups - success_count

        print(f"{Colors.BOLD}📊 RÉSUMÉ DU TRAITEMENT:{Colors.END}")
        print(f"   • Total patches: {total_patches}")
        print(f"   • Fichiers cibles: {total_groups}")
        print(f"   • {Colors.GREEN}Succès: {success_count}{Colors.END}")
        print(f"   • {Colors.RED}Échecs: {failed_count}{Colors.END}")
        print(f"   • {Colors.YELLOW}Problèmes corrigés: {total_issues_fixed}{Colors.END}")
        print(f"   • ⏱️ Temps de traitement: {processing_time:.2f}s")

        if success_count > 0:
            print(f"   • {Colors.BLUE}Fichiers générés dans: {self.output_dir}{Colors.END}")


    def process_wizard_patches(self, selected_patches: List[Path]) -> Dict:
        """Traite spécifiquement les patches sélectionnés par le wizard"""
        start_time = datetime.now()

        print(f"{Colors.BLUE}📦 Traitement de {len(selected_patches)} patch(es) sélectionné(s)...{Colors.END}\n")

        results = []
        success_count = 0
        total_issues_fixed = 0

        for i, patch_path in enumerate(selected_patches, 1):
            print(f"{Colors.CYAN}[{i}/{len(selected_patches)}] 📄 {patch_path.name}{Colors.END}")

            try:
                result = self.process_single_patch(patch_path)
                results.append(result)

                if result.success:
                    success_count += 1
                    issues_count = len(result.issues)
                    total_issues_fixed += issues_count

                    print(f"{Colors.GREEN}   ✅ Succès: {result.output_file}{Colors.END}")
                    if issues_count > 0:
                        print(f"{Colors.YELLOW}   🔧 {issues_count} problème(s) corrigé(s){Colors.END}")
                else:
                    print(f"{Colors.RED}   ❌ Échec: {', '.join(result.errors)}{Colors.END}")

            except Exception as e:
                print(f"{Colors.RED}   ❌ Erreur: {e}{Colors.END}")

            print()

        # Calculer le temps de traitement
        processing_time = (datetime.now() - start_time).total_seconds()

        # Résumé final
        self._print_summary(len(selected_patches), len(selected_patches),
                           success_count, total_issues_fixed, processing_time)

        return {
            'total': len(selected_patches),
            'groups': len(selected_patches),
            'success': success_count,
            'failed': len(selected_patches) - success_count,
            'results': results,
            'processing_time': processing_time
        }

    def generate_report(self, summary: Dict) -> str:
        """Générer un rapport détaillé"""
        report_format = self.config.get('output', 'report_format', 'json')

        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0',
                'source_directory': str(self.source_dir),
                'output_directory': str(self.output_dir),
                'configuration': self.config.config
            },
            'summary': {
                'total_patches': summary['total'],
                'target_groups': summary['groups'],
                'successful_targets': summary['success'],
                'failed_targets': summary['failed'],
                'processing_time_seconds': summary.get('processing_time', 0)
            },
            'statistics': self.processing_stats,
            'detailed_results': []
        }

        # Traiter les résultats détaillés
        for result in summary['results']:
            report_entry = {
                'target_file': result.target_file,
                'output_file': result.output_file,
                'success': result.success,
                'processing_type': result.processing_type,
                'errors': result.errors
            }

            if result.processing_type == 'cumulative':
                report_entry['patches_applied'] = result.patches
                report_entry['cumulative_issues'] = [issue.to_dict() for issue in result.issues]
            else:
                report_entry['patch_file'] = result.patch_file
                report_entry['issues'] = [issue.to_dict() for issue in result.issues]

            if result.success and result.stats:
                report_entry['statistics'] = result.stats

            report_data['detailed_results'].append(report_entry)

        # Sauvegarder le rapport
        if report_format.lower() == 'yaml':
            report_file = self.output_dir / 'processing_report.yaml'
            with open(report_file, 'w', encoding='utf-8') as f:
                yaml.dump(report_data, f, default_flow_style=False, allow_unicode=True)
        else:
            report_file = self.output_dir / 'processing_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Rapport généré: {report_file}")
        return str(report_file)
