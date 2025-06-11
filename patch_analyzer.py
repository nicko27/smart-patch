"""
Correction du module patch_analyzer.py pour Smart Patch Processor
Problème: Analyse incorrecte des patches multi-fichiers
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional

from patch_processor_config import PatchProcessorConfig
from core_types import IssueType, PatchIssue

class PatchAnalyzer:
    """Analyse les patches et détecte les problèmes - VERSION CORRIGÉE"""

    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.analyzer')

        security_config = config.get_section('security')
        self.scan_dangerous_patterns = security_config.get('scan_dangerous_patterns', True)
        self.allow_system_calls = security_config.get('allow_system_calls', False)

    def analyze_patch_quality(self, patch_content: str, original_content: str) -> List[PatchIssue]:
        """Analyse complète d'un patch - VERSION CORRIGÉE"""
        self.logger.debug("Analyse de la qualité du patch")

        issues = []

        # CORRECTION 1: Vérifier d'abord si c'est un patch multi-fichiers
        if self._is_multi_file_patch(patch_content):
            issues.extend(self._analyze_multi_file_patch(patch_content))
            return issues

        # CORRECTION 2: Vérifications de format améliorées
        issues.extend(self._check_format_issues_improved(patch_content))

        # CORRECTION 3: Vérifications de cohérence uniquement si on a un fichier original
        if original_content and original_content.strip():
            issues.extend(self._check_consistency_issues_improved(patch_content, original_content))

        # Vérifications de sécurité
        if self.scan_dangerous_patterns:
            issues.extend(self._check_security_issues(patch_content))

        if issues:
            self.logger.debug(f"{len(issues)} problème(s) détecté(s) dans le patch")
        return issues

    def _is_multi_file_patch(self, patch_content: str) -> bool:
        """NOUVEAU: Détecte si le patch contient plusieurs fichiers"""
        lines = patch_content.split('\n')
        file_headers = 0

        for line in lines:
            line = line.strip()
            # Compter les en-têtes de fichiers
            if (line.startswith('*** ') and line.endswith('.py') or
                line.startswith('--- ') and line.endswith('.py') or
                line.startswith('+++ ') and line.endswith('.py') or
                line.startswith('Index: ') or
                line.startswith('diff --git')):
                file_headers += 1

        # Si plus de 2 en-têtes, c'est probablement multi-fichiers
        return file_headers > 2

    def _analyze_multi_file_patch(self, patch_content: str) -> List[PatchIssue]:
        """NOUVEAU: Analyse spéciale pour patches multi-fichiers"""
        issues = []

        # Détecter les fichiers individuels dans le patch
        files_detected = self._extract_individual_files(patch_content)

        if len(files_detected) > 1:
            issues.append(PatchIssue(
                type=IssueType.WARNING,
                line_number=0,
                message=f"Patch multi-fichiers détecté ({len(files_detected)} fichiers)",
                suggestion="Considérer séparer en patches individuels",
                auto_fixable=False,
                severity=2
            ))

            for file_info in files_detected:
                issues.append(PatchIssue(
                    type=IssueType.INFO,
                    line_number=file_info['line'],
                    message=f"Fichier détecté: {file_info['name']}",
                    suggestion=None,
                    auto_fixable=False,
                    severity=1
                ))

        return issues

    def _extract_individual_files(self, patch_content: str) -> List[Dict]:
        """NOUVEAU: Extrait les informations sur les fichiers individuels"""
        lines = patch_content.split('\n')
        files = []

        for i, line in enumerate(lines):
            line = line.strip()

            # Détecter les en-têtes de fichiers
            if line.startswith('*** ') and '.py' in line:
                filename = self._extract_filename_from_header(line)
                if filename:
                    files.append({
                        'name': filename,
                        'line': i + 1,
                        'type': 'context_old'
                    })
            elif line.startswith('--- ') and '.py' in line:
                filename = self._extract_filename_from_header(line)
                if filename:
                    files.append({
                        'name': filename,
                        'line': i + 1,
                        'type': 'unified_old'
                    })
            elif line.startswith('+++ ') and '.py' in line:
                filename = self._extract_filename_from_header(line)
                if filename:
                    files.append({
                        'name': filename,
                        'line': i + 1,
                        'type': 'unified_new'
                    })

        return files

    def _extract_filename_from_header(self, line: str) -> Optional[str]:
        """NOUVEAU: Extrait proprement le nom de fichier d'un en-tête"""
        # Supprimer le préfixe (---, +++, ***)
        content = re.sub(r'^[\-\+\*]+\s+', '', line)

        # Supprimer les timestamps et métadonnées
        content = re.sub(r'\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.*$', '', content)
        content = re.sub(r'\s+[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+.*$', '', content)
        content = content.split('\t')[0].strip()

        # Extraire juste le nom de fichier
        filename = content.split('/')[-1] if '/' in content else content

        # Valider que c'est un nom de fichier Python valide
        if filename and filename.endswith('.py') and len(filename) > 3:
            return filename

        return None

    def _check_format_issues_improved(self, patch_content: str) -> List[PatchIssue]:
        """CORRECTION: Vérifications de format améliorées"""
        issues = []
        lines = patch_content.split('\n')

        # CORRECTION: Détecter le type de patch d'abord
        patch_type = self._detect_patch_type(patch_content)

        if patch_type == 'unknown':
            issues.append(PatchIssue(
                type=IssueType.ERROR,
                line_number=1,
                message="Format de patch non reconnu",
                suggestion="Vérifier que c'est un patch diff valide",
                auto_fixable=False,
                severity=3
            ))
            return issues

        header_count = 0
        hunk_count = 0

        for i, line in enumerate(lines):
            line_num = i + 1

            # CORRECTION: Validation des en-têtes selon le type
            if line.startswith('@@'):
                if not re.match(r'@@\s*-\d+(?:,\d+)?\s*\+\d+(?:,\d+)?\s*@@', line):
                    issues.append(PatchIssue(
                        type=IssueType.ERROR,
                        line_number=line_num,
                        message="Format de header de diff invalide",
                        suggestion="Correction automatique du format",
                        auto_fixable=True,
                        severity=3
                    ))
                else:
                    hunk_count += 1

            elif line.startswith(('--- ', '+++ ', '*** ')):
                header_count += 1

            # CORRECTION: Validation du contenu selon le type de patch
            elif line and not line.startswith(('diff ', 'Index: ', '====')):
                if patch_type == 'unified':
                    if not line.startswith((' ', '+', '-', '\\')):
                        issues.append(PatchIssue(
                            type=IssueType.WARNING,
                            line_number=line_num,
                            message="Ligne de contenu invalide pour patch unifié",
                            suggestion="Vérifier le format du patch",
                            auto_fixable=False,
                            severity=2
                        ))

        # CORRECTION: Vérifications structurelles
        if hunk_count == 0:
            issues.append(PatchIssue(
                type=IssueType.WARNING,
                line_number=0,
                message="Aucun hunk de modification trouvé",
                suggestion="Vérifier que le patch contient des modifications",
                auto_fixable=False,
                severity=2
            ))

        if header_count == 0:
            issues.append(PatchIssue(
                type=IssueType.WARNING,
                line_number=0,
                message="Aucun en-tête de fichier trouvé",
                suggestion="Ajouter des en-têtes --- et +++ appropriés",
                auto_fixable=True,
                severity=2
            ))

        return issues

    def _detect_patch_type(self, patch_content: str) -> str:
        """NOUVEAU: Détecte le type de patch"""
        lines = patch_content.split('\n')

        has_unified_headers = any(line.startswith(('--- ', '+++ ')) for line in lines)
        has_context_headers = any(line.startswith(('*** ', '--- ')) for line in lines)
        has_hunks = any(line.startswith('@@') for line in lines)
        has_ed_commands = any(re.match(r'^\d+[acd]\d+', line) for line in lines)

        if has_unified_headers and has_hunks:
            return 'unified'
        elif has_context_headers:
            return 'context'
        elif has_ed_commands:
            return 'ed'
        elif any(line.startswith(('diff ', 'Index: ')) for line in lines):
            return 'git'
        else:
            return 'unknown'

    def _check_consistency_issues_improved(self, patch_content: str, original_content: str) -> List[PatchIssue]:
        """CORRECTION: Vérifications de cohérence améliorées"""
        issues = []

        if not original_content or not original_content.strip():
            return issues

        original_lines = original_content.split('\n')

        # CORRECTION: Validation plus intelligente des numéros de ligne
        for match in re.finditer(r'@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@', patch_content):
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1

            # Vérifications de validité
            if old_start <= 0:
                issues.append(PatchIssue(
                    type=IssueType.ERROR,
                    line_number=0,
                    message=f"Numéro de ligne de départ invalide: {old_start}",
                    suggestion="Correction automatique à partir de 1",
                    auto_fixable=True,
                    severity=3
                ))

            if old_start + old_count - 1 > len(original_lines):
                issues.append(PatchIssue(
                    type=IssueType.WARNING,
                    line_number=0,
                    message=f"Numéro de ligne {old_start + old_count - 1} dépasse la taille du fichier ({len(original_lines)} lignes)",
                    suggestion="Recalcul automatique basé sur le contenu",
                    auto_fixable=True,
                    severity=2
                ))

            # CORRECTION: Vérifications de cohérence de compte
            if old_count < 0 or new_count < 0:
                issues.append(PatchIssue(
                    type=IssueType.ERROR,
                    line_number=0,
                    message=f"Compte de lignes négatif: old={old_count}, new={new_count}",
                    suggestion="Correction des comptes de lignes",
                    auto_fixable=True,
                    severity=3
                ))

        return issues

    def _check_security_issues(self, patch_content: str) -> List[PatchIssue]:
        """Vérifie les problèmes de sécurité potentiels - VERSION AMÉLIORÉE"""
        issues = []

        # CORRECTION: Patterns de sécurité plus spécifiques
        dangerous_patterns = [
            (r'eval\s*\(', "Utilisation d'eval() détectée", 3),
            (r'exec\s*\(', "Utilisation d'exec() détectée", 3),
            (r'__import__\s*\(', "Importation dynamique détectée", 2),
            (r'subprocess\..*shell\s*=\s*True', "Exécution shell détectée", 3),
            (r'os\.system\s*\(', "Appel système détecté", 3),
            (r'password\s*=\s*["\'][^"\']+["\']', "Mot de passe en dur détecté", 2),
            (r'secret_key\s*=\s*["\'][^"\']+["\']', "Clé secrète en dur détectée", 3),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Clé API en dur détectée", 2),
        ]

        lines = patch_content.split('\n')

        for i, line in enumerate(lines):
            # Analyser uniquement les lignes ajoutées
            if line.startswith('+') and len(line) > 1:
                content = line[1:]  # Supprimer le +

                for pattern, message, severity in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(PatchIssue(
                            type=IssueType.WARNING,
                            line_number=i + 1,
                            message=message,
                            suggestion="Vérifier que ce code est sûr",
                            auto_fixable=False,
                            severity=severity
                        ))

        # CORRECTION: Vérifications spécifiques si les appels système ne sont pas autorisés
        if not self.allow_system_calls:
            system_patterns = [
                r'os\.system\(',
                r'subprocess\.',
                r'popen\(',
                r'execv?\('
            ]

            for i, line in enumerate(lines):
                if line.startswith('+'):
                    content = line[1:]
                    for pattern in system_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append(PatchIssue(
                                type=IssueType.ERROR,
                                line_number=i + 1,
                                message="Appel système non autorisé détecté",
                                suggestion="Supprimer ou configurer l'autorisation",
                                auto_fixable=False,
                                severity=3
                            ))

        return issues

    def get_patch_statistics(self, patch_content: str) -> Dict:
        """NOUVEAU: Statistiques détaillées du patch pour debug"""
        lines = patch_content.split('\n')
        stats = {
            'total_lines': len(lines),
            'added_lines': 0,
            'removed_lines': 0,
            'context_lines': 0,
            'header_lines': 0,
            'hunk_count': 0,
            'files_detected': 0,
            'patch_type': self._detect_patch_type(patch_content)
        }

        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                stats['added_lines'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                stats['removed_lines'] += 1
            elif line.startswith(' '):
                stats['context_lines'] += 1
            elif line.startswith(('--- ', '+++ ', '*** ')):
                stats['header_lines'] += 1
            elif line.startswith('@@'):
                stats['hunk_count'] += 1

        # Compter les fichiers détectés
        files = self._extract_individual_files(patch_content)
        stats['files_detected'] = len(files)

        return stats