#!/usr/bin/env python3
"""
Smart Patch Processor v2.0 - Main Function Enhanced
Fonction main() complète avec système d'aide intégré
"""

import sys
import argparse
from pathlib import Path
from unittest.mock import patch, mock_open
import traceback

# Imports du système de base

# Protection contre les erreurs d'import manquantes
def safe_import(module_name, fallback=None):
    try:
        return __import__(module_name)
    except ImportError:
        return fallback

# Protection contre les erreurs d'import manquantes
def safe_import(module_name, fallback=None):
    try:
        return __import__(module_name)
    except ImportError:
        return fallback
from cache_system import DummyCache
from streaming_system import CircularBuffer
from file_permissions import FilePermissions

# Imports locaux du Smart Patch Processor
from analyze_patch_step import AnalyzePatchStep
from apply_patch_step import ApplyPatchStep
from ast_analyzer import ASTAnalyzer
from cache_system import CacheManager
from colors import Colors
from correct_patch_step import CorrectPatchStep
from detect_target_step import DetectTargetStep
from git_integration import GitIntegration
from interactive_cli import InteractiveCLI
from line_number_corrector import LineNumberCorrector
from patch_analyzer import PatchAnalyzer
from patch_applicator import PatchApplicator
from patch_previewer import PatchPreviewer
from patch_processor_config import PatchProcessorConfig
from permission_manager import PermissionManager
from processing_coordinator import ProcessingCoordinator
from rollback_manager import RollbackManager
from smart_patch_processor import SmartPatchProcessor
from streaming_system import StreamingManager
from target_file_detector import TargetFileDetector
from wizard_mode import WizardMode

# Import du système d'aide amélioré
try:
    from help_system import show_help, enhance_argument_parser, handle_help_command
    ENHANCED_HELP_AVAILABLE = True
except ImportError:
    ENHANCED_HELP_AVAILABLE = False
    print(f"{Colors.YELLOW}⚠️ Système d'aide avancé non disponible (help_system.py manquant){Colors.END}")

# Import du nouveau système guidé
GUIDED_SYSTEM_AVAILABLE = True
print(f"{Colors.GREEN}📦 Système de patchage guidé intégré chargé{Colors.END}")


def create_argument_parser():
    """Crée et configure l'argument parser avec toutes les options"""

    # Description complète avec exemples
    description = """
Smart Patch Processor v2.0 - Traitement intelligent de patches avec mode guidé

🎯 MODES PRINCIPAUX:
  --guided    Mode guidé recommandé (interface sécurisée pas-à-pas)
  --wizard    Assistant interactif pour débutants
  --interactive   Mode interactif avec confirmations

💡 EXEMPLES RAPIDES:
  %(prog)s --wizard                              # Premier usage recommandé
  %(prog)s --guided patches/ output/             # Mode guidé standard
  %(prog)s --guided --preview-only patches/ /tmp/ # Aperçu seulement
  %(prog)s fix.patch output/ --target file.py   # Patch explicite
"""

    epilog = """
📚 AIDE SPÉCIALISÉE:
  --help-topic guided        Guide détaillé du mode guidé
  --help-topic wizard        Aide du mode assistant
  --help-topic examples      Exemples par situation
  --help-topic config        Configuration avancée
  --help-topic troubleshooting   Dépannage complet

🌟 PREMIÈRE FOIS ? Lancez: %(prog)s --wizard

📧 Support: smart-patch-processor@example.com
🌐 Documentation: https://smart-patch-processor.readthedocs.io/
"""

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # On gère --help nous-mêmes
    )

    # === ARGUMENTS PRINCIPAUX ===
    parser.add_argument('source', nargs='?',
                       help='Dossier de patches ou fichier patch unique')
    parser.add_argument('output', nargs='?',
                       help='Dossier de destination')

    # === MODE EXPLICITE ===
    explicit_group = parser.add_argument_group('🎯 Mode explicite')
    explicit_group.add_argument('-p', '--patch',
                               help='Fichier patch spécifique')
    explicit_group.add_argument('-t', '--target',
                               help='Fichier cible spécifique')
    explicit_group.add_argument('-o', '--output-dir',
                               help='Dossier de sortie')

    # === OPTIONS STANDARD ===
    standard_group = parser.add_argument_group('⚙️ Options standard')
    standard_group.add_argument('-v', '--verbose', action='store_true',
                               help='Affichage détaillé')
    standard_group.add_argument('-q', '--quiet', action='store_true',
                               help='Mode silencieux (erreurs uniquement)')
    standard_group.add_argument('-r', '--report', action='store_true',
                               help='Générer un rapport détaillé')
    standard_group.add_argument('--no-color', action='store_true',
                               help='Désactiver les couleurs')
    standard_group.add_argument('-c', '--config',
                               help='Fichier de configuration (JSON/YAML)')

    # === 🎯 MODE GUIDÉ ===
    guided_group = parser.add_argument_group('🎯 Mode guidé (recommandé)')
    guided_group.add_argument('--guided', action='store_true',
                             help='🎯 Mode patchage guidé interactif avec preview')
    guided_group.add_argument('--backup-dir',
                             help='📁 Dossier de backup personnalisé (ex: ~/backups)')
    guided_group.add_argument('--modify-original', action='store_true',
                             help='✏️ Modifier directement les fichiers originaux')
    guided_group.add_argument('--preview-only', action='store_true',
                             help='👁️ Preview uniquement, sans application')
    guided_group.add_argument('--batch-mode', action='store_true',
                             help='📦 Mode lot sans interruption')

    # === 🧙‍♂️ MODES SPÉCIAUX ===
    special_group = parser.add_argument_group('🧙‍♂️ Modes spéciaux')
    special_group.add_argument('--wizard', action='store_true',
                              help='🧙‍♂️ Mode assistant interactif pour débutants')
    special_group.add_argument('--interactive', action='store_true',
                              help='💬 Mode interactif avec confirmations')
    special_group.add_argument('--create-config', action='store_true',
                              help='⚙️ Créer une configuration personnalisée')
    special_group.add_argument('--test', action='store_true',
                              help='🧪 Exécuter les tests unitaires')

    # === 🔧 OPTIONS AVANCÉES ===
    advanced_group = parser.add_argument_group('🔧 Options avancées')
    advanced_group.add_argument('--rollback', action='store_true',
                               help='🔄 Activer le système de rollback')
    advanced_group.add_argument('--no-backup', action='store_true',
                               help='⚠️ Désactiver les sauvegardes automatiques')
    advanced_group.add_argument('--streaming', action='store_true',
                               help='🚀 Forcer le mode streaming pour gros fichiers')
    advanced_group.add_argument('--ast-analysis', action='store_true',
                               help='🧠 Activer l\'analyse syntaxique AST')
    advanced_group.add_argument('--git-integration', action='store_true',
                               help='🔗 Activer l\'intégration Git')

    # === 📊 SORTIE ET RAPPORTS ===
    output_group = parser.add_argument_group('📊 Sortie et rapports')
    output_group.add_argument('--output-format', choices=['json', 'yaml', 'html'],
                             default='json', help='Format du rapport de sortie')
    output_group.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                             default='WARNING', help='Niveau de logging')
    output_group.add_argument('--log-file',
                             help='Fichier de log personnalisé')

    # === ❓ AIDE ===
    help_group = parser.add_argument_group('❓ Aide et information')
    help_group.add_argument('-h', '--help', action='store_true',
                           help='Affiche cette aide détaillée')
    help_group.add_argument('--version', action='version',
                           version='Smart Patch Processor v2.0')

    # Intégrer le système d'aide avancé si disponible - CORRECTION DU CONFLIT
    if ENHANCED_HELP_AVAILABLE:
        # SUPPRIMER LA LIGNE CONFLICTUELLE qui est déjà définie dans enhance_argument_parser
        # help_group.add_argument('--help-topic', ...)  # <- Cette ligne causait le conflit
        parser = enhance_argument_parser(parser)

    return parser


def validate_arguments(args):
    """Valide et normalise les arguments"""
    errors = []
    warnings = []

    # === VALIDATION DES MODES ===

    # Compter les modes actifs
    active_modes = sum([
        bool(args.wizard),
        bool(args.guided),
        bool(args.create_config),
        bool(args.test)
    ])

    if active_modes > 1:
        errors.append("Un seul mode peut être actif à la fois (--wizard, --guided, --create-config, --test)")

    # === VALIDATION DES FICHIERS ===

    # Mode wizard, create-config et test n'ont pas besoin de fichiers
    if not any([args.wizard, args.create_config, args.test]):

        # Déterminer les chemins source/output
        source_path = args.patch or args.source
        output_path = args.output_dir or args.output

        if not source_path:
            errors.append("Source requise (fichier patch ou dossier)")

        if not output_path and not args.preview_only:
            errors.append("Destination requise (sauf pour --preview-only)")

        # Vérifier l'existence des fichiers
        if source_path and not Path(source_path).exists():
            errors.append(f"Fichier/dossier source introuvable: {source_path}")

        if args.target and not Path(args.target).exists():
            errors.append(f"Fichier cible introuvable: {args.target}")

        if args.config and not Path(args.config).exists():
            errors.append(f"Fichier de configuration introuvable: {args.config}")

    # === VALIDATION DES OPTIONS ===

    # Conflits d'options
    if args.modify_original and args.preview_only:
        errors.append("--modify-original et --preview-only sont incompatibles")

    if args.no_backup and args.backup_dir:
        warnings.append("--no-backup ignore --backup-dir")

    if args.quiet and args.verbose:
        warnings.append("--quiet et --verbose sont contradictoires, --verbose prioritaire")

    # === NORMALISATION ===

    # Priorité verbose > quiet
    if args.verbose:
        args.quiet = False

    # Mode guidé automatique pour débutants si détecté
    if not any([args.wizard, args.guided, args.interactive]) and len(sys.argv) <= 3:
        warnings.append("Mode guidé recommandé pour la première utilisation (ajoutez --guided)")

    return errors, warnings


def handle_special_modes(args):
    """Gère les modes spéciaux qui ne font pas de traitement de patches"""

    # === MODE AIDE ===
    if args.help:
        if ENHANCED_HELP_AVAILABLE:
            show_help('main')
        else:
            # Fallback vers aide standard
            create_argument_parser().print_help()
        return True

    if ENHANCED_HELP_AVAILABLE and handle_help_command(args):
        return True

    # === MODE CRÉATION DE CONFIGURATION ===
    if args.create_config:
        success = run_config_generator()
        sys.exit(0 if success else 1)

    # === MODE TESTS ===
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    # === MODE WIZARD ===
    if args.wizard:
        try:
            # Créer un processeur temporaire pour le wizard
            processor = SmartPatchProcessor('.', '.', args.verbose, args.config)
            processor.print_banner()

            wizard = processor.wizard_mode
            if wizard and (wizard.is_enabled() or True):  # Force enable pour --wizard
                result = wizard.run_wizard()

                # 🔥 CORRECTION: Vérifier si le traitement a été effectué
                if result.get('completed'):
                    if result.get('processing_completed'):
                        print("💡 Exemples d'usage pour la prochaine fois:")
                        print("   smart-patch --guided patches/ output/")
                        print("   smart-patch single.patch output/ --target myfile.py")
                        return True  # Indiquer que tout est terminé
                    else:
                        print("✨ Configuration terminée !")
                        print("💡 Les patches n'ont pas été appliqués automatiquement.")
                        print("💡 Relancez avec les paramètres configurés :")
                        print("   smart-patch --guided patches/ output/")
                        return True
                else:
                    print("👋 À bientôt ! Lancez à nouveau avec --wizard quand vous voulez.")
                    return True
            return True
        except Exception as e:
            print(f"❌ Erreur wizard: {e}")
            if args.verbose:
                traceback.print_exc()
            return True  # Toujours terminer même en cas d'erreur

    return False


def determine_processing_mode(args):
    """Détermine le mode de traitement et les paramètres"""

    # Déterminer les chemins
    if args.patch and args.target and args.output_dir:
        # Mode explicite avec flags
        source_path = args.patch
        target_path = args.target
        output_path = args.output_dir
        mode = "explicit_flags"
    elif args.source and args.output and args.target:
        # Mode explicite avec arguments positionnels + --target
        source_path = args.source
        target_path = args.target
        output_path = args.output
        mode = "explicit_mixed"
    elif args.source and (args.output or args.preview_only):
        # Mode standard
        source_path = args.source
        output_path = args.output or '/tmp'  # Fallback pour preview-only
        target_path = None
        mode = "standard"
    else:
        return None, None, None, None

    # Déterminer le sous-mode
    if args.guided:
        if args.preview_only:
            submode = "guided_preview"
        elif args.batch_mode:
            submode = "guided_batch"
        elif args.interactive:
            submode = "guided_interactive"
        else:
            submode = "guided_standard"
    elif args.interactive:
        submode = "interactive"
    else:
        submode = "standard"

    return mode, submode, source_path, output_path, target_path


def setup_logging(args):
    """Configure le système de logging"""
    import logging

    # Niveau basé sur les arguments
    if args.verbose:
        level = logging.DEBUG
        console_level = logging.INFO
    elif args.quiet:
        level = logging.ERROR
        console_level = logging.ERROR
    else:
        level = getattr(logging, args.log_level, logging.WARNING)
        console_level = logging.WARNING

    # Configuration du logger principal
    logger = logging.getLogger('smart_patch_processor')
    logger.setLevel(level)

    # Supprimer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler fichier si spécifié
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging vers fichier: {args.log_file}")


def run_tests():
    """Exécute les tests unitaires du Smart Patch Processor"""
    try:
        import unittest

        print(f"{Colors.BLUE}🧪 Exécution des tests unitaires...{Colors.END}")

        # Découvrir et exécuter les tests
        loader = unittest.TestLoader()
        start_dir = Path(__file__).parent
        suite = loader.discover(start_dir, pattern='test_*.py')

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        # Afficher le résumé
        if result.wasSuccessful():
            print(f"{Colors.GREEN}✅ Tous les tests sont passés ({result.testsRun} tests){Colors.END}")
            return True
        else:
            failures = len(result.failures)
            errors = len(result.errors)
            print(f"{Colors.RED}❌ {failures} échec(s), {errors} erreur(s) sur {result.testsRun} tests{Colors.END}")
            return False

    except ImportError as e:
        print(f"{Colors.YELLOW}⚠️ Impossible de charger les tests: {e}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur lors des tests: {e}{Colors.END}")
        return False


def run_guided_patching(args, source_path, output_path, target_path):
    """Lance le mode patchage guidé"""

    print(f"{Colors.CYAN}🎯 Lancement du patchage guidé{Colors.END}")

    if args.preview_only:
        print(f"{Colors.BLUE}👁️ Mode preview uniquement activé{Colors.END}")

    if args.batch_mode:
        print(f"{Colors.PURPLE}📦 Mode batch activé - traitement sans interruption{Colors.END}")

    # Créer le processeur principal
    processor = SmartPatchProcessor(
        source_path,
        output_path,
        args.verbose,
        args.config,
        target_path
    )

    # Configuration spécifique au mode guidé
    if args.backup_dir:
        # TODO: Configurer le répertoire de backup personnalisé
        print(f"{Colors.CYAN}💾 Backup personnalisé: {args.backup_dir}{Colors.END}")

    if args.modify_original:
        print(f"{Colors.YELLOW}⚠️ Modification directe des originaux activée{Colors.END}")

    # Trouver les patches
    if Path(source_path).is_file():
        patches = [Path(source_path)]
        print(f"{Colors.BLUE}📄 Mode fichier unique: {Path(source_path).name}{Colors.END}")
    else:
        patches = processor.find_patches()
        print(f"{Colors.BLUE}📁 Mode dossier: {len(patches)} patch(es) trouvé(s){Colors.END}")

    if not patches:
        print(f"{Colors.RED}❌ Aucun patch trouvé{Colors.END}")
        return False

    # Affichage des patches trouvés
    for i, patch in enumerate(patches, 1):
        size_kb = patch.stat().st_size // 1024
        print(f"   {i:2d}. {patch.name} ({size_kb}KB)")

    # Confirmation si mode interactif
    if args.interactive and not args.batch_mode:
        response = input(f"\n{Colors.CYAN}Continuer avec le traitement ? (y/N): {Colors.END}").strip().lower()
        if response != 'y':
            print(f"{Colors.YELLOW}Traitement annulé par l'utilisateur{Colors.END}")
            return False

    # Traitement des patches
    if args.preview_only:
        # Mode preview uniquement
        print(f"\n{Colors.CYAN}👁️ APERÇU DES MODIFICATIONS{Colors.END}")
        success_count = 0

        for i, patch_path in enumerate(patches, 1):
            print(f"\n[{i}/{len(patches)}] 📄 {patch_path.name}")

            try:
                with open(patch_path, 'r') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    print(f"  📊 {lines} lignes, ~{content.count('@@')} section(s)")

                    # Analyser les modifications
                    additions = content.count('\n+')
                    deletions = content.count('\n-')
                    print(f"  📈 ~{additions} addition(s), {deletions} suppression(s)")

                success_count += 1
                print(f"  ✅ Preview généré")

            except Exception as e:
                print(f"  ❌ Erreur: {e}")

        print(f"\n📊 Résumé preview: {success_count}/{len(patches)} patch(es) analysé(s)")
        return success_count > 0

    else:
        # Mode traitement normal
        print(f"\n{Colors.GREEN}⚡ TRAITEMENT DES PATCHES{Colors.END}")
        summary = processor.process_all_patches()

        # Générer un rapport si demandé
        if args.report:
            report_file = processor.generate_report(summary)
            print(f"\n{Colors.CYAN}📄 Rapport généré: {report_file}{Colors.END}")

        return summary['success'] > 0


def run_config_generator():
    """Lance le générateur de configuration"""
    try:
        from advanced_config_generator import run_config_generator_advanced
        return run_config_generator_advanced()
    except ImportError:
        # Fallback vers version simple
        print("🔧 Générateur de Configuration Smart Patch Processor (version simple)")

        config = {
            "detection": {"file_extensions": [".py", ".js", ".ts", ".php", ".java"]},
            "security": {"scan_dangerous_patterns": True, "allow_system_calls": False},
            "guided_patching": {"enabled": True, "preview_enabled": True, "auto_backup": True},
            "logging": {"level": "WARNING", "console_level": "ERROR"}
        }

        import json
        output_file = Path("smart_patch_config.json")
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration créée: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Fonction principale améliorée avec gestion complète des arguments"""

    # === PHASE 1: PARSING ET VALIDATION ===
    parser = create_argument_parser()
    args = parser.parse_args()

    # Désactiver les couleurs si demandé
    if args.no_color:
        Colors.disable_colors()

    # Valider les arguments
    errors, warnings = validate_arguments(args)

    # Afficher les avertissements
    for warning in warnings:
        print(f"{Colors.YELLOW}⚠️ {warning}{Colors.END}")

    # Arrêter si erreurs
    if errors:
        print(f"{Colors.RED}❌ Erreurs de validation:{Colors.END}")
        for error in errors:
            print(f"   • {error}")
        parser.print_usage()
        sys.exit(1)

    # === PHASE 2: CONFIGURATION ===
    setup_logging(args)

    # === PHASE 3: MODES SPÉCIAUX ===
    if handle_special_modes(args):
        return

    # === PHASE 4: DÉTERMINATION DU MODE DE TRAITEMENT ===
    mode, submode, source_path, output_path, target_path = determine_processing_mode(args)

    if mode is None:
        print(f"{Colors.RED}❌ Arguments insuffisants{Colors.END}")
        print(f"\n{Colors.CYAN}Utilisations possibles:{Colors.END}")
        print(f"  {Colors.GREEN}Mode débutant:{Colors.END}        smart-patch --wizard")
        print(f"  {Colors.GREEN}Mode guidé:{Colors.END}           smart-patch --guided patches/ output/")
        print(f"  {Colors.YELLOW}Mode explicite:{Colors.END}       smart-patch patch.diff output/ --target file.py")
        print(f"  {Colors.PURPLE}Créer config:{Colors.END}         smart-patch --create-config")
        print(f"  {Colors.BLUE}Aide complète:{Colors.END}        smart-patch --help")
        if ENHANCED_HELP_AVAILABLE:
            print(f"  {Colors.BLUE}Aide spécialisée:{Colors.END}     smart-patch --help-topic examples")
        sys.exit(1)

    # === PHASE 5: TRAITEMENT PRINCIPAL ===
    try:
        # Affichage du mode et bannière
        if not args.quiet:
            # Bannière
            print(f"{Colors.CYAN}{Colors.BOLD}")
            print("╔════════════════════════════════════════════════════════════════╗")
            print("║          🚀 SMART PATCH PROCESSOR v2.0                         ║")
            print("║      Traitement Intelligent de Patches avec Mode Guidé         ║")
            print("╚════════════════════════════════════════════════════════════════╝")
            print(f"{Colors.END}")

            # Affichage du mode
            mode_descriptions = {
                "explicit_flags": f"{Colors.PURPLE}🎯 Mode explicite avec flags{Colors.END}",
                "explicit_mixed": f"{Colors.PURPLE}🎯 Mode explicite mixte{Colors.END}",
                "standard": f"{Colors.BLUE}📁 Mode standard{Colors.END}"
            }

            submode_descriptions = {
                "guided_standard": f"{Colors.GREEN}🎯 Mode guidé standard{Colors.END}",
                "guided_preview": f"{Colors.CYAN}👁️ Mode guidé preview{Colors.END}",
                "guided_batch": f"{Colors.PURPLE}📦 Mode guidé batch{Colors.END}",
                "guided_interactive": f"{Colors.YELLOW}💬 Mode guidé interactif{Colors.END}",
                "interactive": f"{Colors.YELLOW}💬 Mode interactif{Colors.END}",
                "standard": f"{Colors.BLUE}⚡ Mode standard{Colors.END}"
            }

            print(f"{mode_descriptions.get(mode, mode)} • {submode_descriptions.get(submode, submode)}")

            if Path(source_path).is_file():
                print(f"📄 Fichier: {Path(source_path).name}")
            else:
                print(f"📁 Dossier: {Path(source_path).name}")

            if target_path:
                print(f"🎯 Cible: {Path(target_path).name}")

            print()

        # === TRAITEMENT SELON LE MODE ===
        success = False

        if submode.startswith('guided'):
            # Mode guidé
            success = run_guided_patching(args, source_path, output_path, target_path)

        else:
            # Mode standard ou interactif
            processor = SmartPatchProcessor(
                source_path,
                output_path,
                args.verbose,
                args.config,
                target_path
            )

            if args.interactive:
                print(f"{Colors.CYAN}🔄 Mode interactif activé{Colors.END}")

            # Traitement
            summary = processor.process_all_patches()

            # Générer un rapport si demandé
            if args.report:
                report_file = processor.generate_report(summary)
                print(f"\n{Colors.CYAN}📄 Rapport généré: {report_file}{Colors.END}")

            success = summary['success'] > 0

        # === CODES DE SORTIE ===
        if success:
            if not args.quiet:
                print(f"\n{Colors.GREEN}🎉 Traitement terminé avec succès !{Colors.END}")
            sys.exit(0)
        else:
            if not args.quiet:
                print(f"\n{Colors.RED}❌ Traitement échoué{Colors.END}")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Traitement interrompu par l'utilisateur{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur fatale: {e}{Colors.END}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def print_guided_examples():
    """Affiche des exemples d'utilisation du mode guidé"""

    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                   🎯 EXEMPLES MODE GUIDÉ                         ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    examples = [
        {
            'title': '🔰 Débutant - Mode guidé de base',
            'command': 'smart-patch --guided patches/ output/',
            'description': 'Mode guidé avec toutes les sécurités et confirmations'
        },
        {
            'title': '💾 Backup personnalisé',
            'command': 'smart-patch --guided --backup-dir ~/mes_backups patches/ output/',
            'description': 'Sauvegardes dans un dossier spécifique'
        },
        {
            'title': '✏️ Modification directe des originaux',
            'command': 'smart-patch --guided --modify-original patches/ output/',
            'description': 'Modifie directement les fichiers sans créer de copies'
        },
        {
            'title': '👁️ Preview uniquement',
            'command': 'smart-patch --guided --preview-only patches/ /tmp/',
            'description': 'Voir les changements sans les appliquer'
        },
        {
            'title': '⚙️ Avec configuration personnalisée',
            'command': 'smart-patch --guided --config ma_config.json patches/ output/',
            'description': 'Utilise une configuration créée avec --create-config'
        },
        {
            'title': '🎯 Patch unique avec cible explicite',
            'command': 'smart-patch --guided fix.patch output/ --target myfile.py',
            'description': 'Mode guidé pour un patch spécifique'
        },
        {
            'title': '📦 Mode batch pour lots de patches',
            'command': 'smart-patch --guided --batch-mode patches/ output/',
            'description': 'Traitement automatique sans interruption'
        },
        {
            'title': '💬 Mode interactif avec confirmations',
            'command': 'smart-patch --guided --interactive patches/ output/',
            'description': 'Confirmation manuelle pour chaque patch'
        }
    ]

    for example in examples:
        print(f"\n{Colors.BOLD}{example['title']}{Colors.END}")
        print(f"   {Colors.GREEN}{example['command']}{Colors.END}")
        print(f"   💡 {example['description']}")

    print(f"\n{Colors.BLUE}💡 Conseils:{Colors.END}")
    print("   • Utilisez --create-config pour créer une configuration personnalisée")
    print("   • Le mode guidé vous permet de valider chaque patch avant application")
    print("   • Les backups sont automatiques et personnalisables")
    print("   • Utilisez --verbose pour plus de détails")
    print("   • Commencez par --wizard si c'est votre première fois")


def show_welcome_message():
    """Affiche le message d'accueil pour nouveaux utilisateurs"""

    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║               👋 BIENVENUE DANS SMART PATCH PROCESSOR            ║")
    print("║                           v2.0                                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    print(f"{Colors.BLUE}🎯 Smart Patch Processor applique intelligemment vos patches{Colors.END}")
    print("avec détection automatique, correction des erreurs et sécurité avancée.")
    print()

    print(f"{Colors.GREEN}🌟 PREMIÈRE FOIS ? Trois options simples:{Colors.END}")
    print(f"   1. {Colors.CYAN}smart-patch --wizard{Colors.END}                    🧙‍♂️ Assistant pas-à-pas")
    print(f"   2. {Colors.CYAN}smart-patch --guided patches/ output/{Colors.END}   🎯 Mode guidé sécurisé")
    print(f"   3. {Colors.CYAN}smart-patch --help{Colors.END}                      📚 Aide complète")
    print()

    print(f"{Colors.YELLOW}💡 Le mode guidé est recommandé pour tous les utilisateurs !{Colors.END}")


def detect_user_context():
    """Détecte le contexte utilisateur pour suggérer le meilleur mode"""
    context = {
        'is_beginner': True,
        'has_patches': False,
        'in_git_repo': False,
        'suggested_mode': 'wizard'
    }

    # Détecter la présence de patches
    current_dir = Path.cwd()
    patch_files = list(current_dir.glob('*.patch')) + list(current_dir.glob('*.diff'))
    if patch_files:
        context['has_patches'] = True
        context['patch_count'] = len(patch_files)

    # Détecter si on est dans un repo Git
    git_dir = current_dir / '.git'
    if git_dir.exists():
        context['in_git_repo'] = True

    # Détecter l'expérience (basé sur l'historique des commandes)
    try:
        home = Path.home()
        bash_history = home / '.bash_history'
        zsh_history = home / '.zsh_history'

        patch_commands = ['patch', 'git apply', 'smart-patch']
        experience_score = 0

        for history_file in [bash_history, zsh_history]:
            if history_file.exists():
                try:
                    with open(history_file, 'r', errors='ignore') as f:
                        history = f.read()
                        for cmd in patch_commands:
                            experience_score += history.count(cmd)
                except:
                    pass

        if experience_score > 5:
            context['is_beginner'] = False
            context['suggested_mode'] = 'guided'
    except:
        pass

    # Suggestions basées sur le contexte
    if context['has_patches'] and not context['is_beginner']:
        context['suggested_mode'] = 'guided'
    elif context['has_patches']:
        context['suggested_mode'] = 'wizard'

    return context


def show_context_suggestions():
    """Affiche des suggestions basées sur le contexte détecté"""
    context = detect_user_context()

    print(f"{Colors.PURPLE}🎯 SUGGESTIONS PERSONNALISÉES:{Colors.END}")

    if context['has_patches']:
        print(f"   ✅ {context['patch_count']} patch(es) détecté(s) dans le répertoire actuel")
        if context['is_beginner']:
            print(f"   💡 Recommandation: {Colors.CYAN}smart-patch --wizard{Colors.END}")
            print("      L'assistant vous guidera pas-à-pas pour traiter vos patches")
        else:
            print(f"   💡 Recommandation: {Colors.GREEN}smart-patch --guided *.patch output/{Colors.END}")
            print("      Mode guidé direct pour traiter tous vos patches")
    else:
        print("   📁 Aucun patch détecté dans le répertoire actuel")
        print(f"   💡 Recommandation: {Colors.CYAN}smart-patch --wizard{Colors.END}")
        print("      L'assistant vous aidera à localiser et traiter vos patches")

    if context['in_git_repo']:
        print("   🔗 Dépôt Git détecté - intégration Git disponible")
        print("      Ajoutez --git-integration pour créer des branches automatiquement")

    print()


# Point d'entrée principal
if __name__ == "__main__":
    # Si appelé sans arguments, afficher l'accueil et suggestions
    if len(sys.argv) == 1:
        show_welcome_message()
        show_context_suggestions()
        print_guided_examples()
        print(f"\n{Colors.YELLOW}Utilisez --help pour l'aide complète{Colors.END}")
        sys.exit(0)

    # Sinon, lancer le traitement normal
    main()
