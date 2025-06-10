#!/usr/bin/env python3
"""
Smart Patch Processor v2.0 - Système d'aide détaillé et coloré
Module help_system.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Import du système de couleurs
try:
    from colors import Colors
except ImportError:
    class Colors:
        BOLD = '\033[1m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        PURPLE = '\033[35m'
        CYAN = '\033[36m'
        END = '\033[0m'

class SmartPatchHelp:
    """Système d'aide avancé pour Smart Patch Processor"""

    def __init__(self, version="2.0"):
        self.version = version
        self.examples_dir = Path.cwd() / "examples"

    def show_main_help(self):
        """Affiche l'aide principale complète"""
        self._print_header()
        self._print_synopsis()
        self._print_modes()
        self._print_common_options()
        self._print_examples()
        self._print_troubleshooting()
        self._print_footer()

    def show_guided_help(self):
        """Aide spécifique au mode guidé"""
        self._print_section_header("🎯 MODE GUIDÉ - AIDE DÉTAILLÉE")

        print(f"{Colors.BLUE}📚 Le mode guidé est recommandé pour tous les utilisateurs.{Colors.END}")
        print("Il vous accompagne étape par étape avec des vérifications de sécurité.")
        print()

        print(f"{Colors.CYAN}{Colors.BOLD}USAGE DU MODE GUIDÉ:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --guided [OPTIONS] SOURCE DESTINATION{Colors.END}")
        print()

        print(f"{Colors.YELLOW}OPTIONS SPÉCIFIQUES AU MODE GUIDÉ:{Colors.END}")
        options = [
            ("--backup-dir DIR", "Répertoire personnalisé pour les sauvegardes", "~/backups"),
            ("--modify-original", "Modifier directement les fichiers originaux", "Attention !"),
            ("--preview-only", "Aperçu uniquement, sans application", "Sécurisé"),
            ("--interactive", "Mode interactif avec confirmations", "Recommandé"),
            ("--batch-mode", "Traitement par lots sans interruption", "Avancé"),
        ]

        for option, desc, note in options:
            print(f"   {Colors.CYAN}{option:20}{Colors.END} {desc}")
            print(f"      {Colors.PURPLE}💡 {note}{Colors.END}")

        print(f"\n{Colors.BOLD}🔄 PROCESSUS ÉTAPE PAR ÉTAPE:{Colors.END}")
        steps = [
            "🔍 Analyse et détection des patches",
            "🎯 Identification des fichiers cibles",
            "🛡️ Vérifications de sécurité",
            "👁️ Aperçu des modifications (optionnel)",
            "💾 Création des sauvegardes",
            "⚡ Application des patches",
            "📊 Rapport de résultats"
        ]

        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}")

        print(f"\n{Colors.GREEN}✨ EXEMPLES PRATIQUES:{Colors.END}")
        examples = [
            ("Débutant complet", "smart-patch --guided patches/ output/", "Traitement sécurisé de base"),
            ("Avec backup personnalisé", "smart-patch --guided --backup-dir ~/mes_sauvegardes patches/ output/", "Sauvegardes dans un dossier spécifique"),
            ("Preview seulement", "smart-patch --guided --preview-only patches/ /tmp/", "Voir sans appliquer"),
            ("Modification directe", "smart-patch --guided --modify-original patches/ ./", "Modifie les originaux")
        ]

        for title, cmd, desc in examples:
            print(f"\n   {Colors.BOLD}{title}:{Colors.END}")
            print(f"   {Colors.GREEN}$ {cmd}{Colors.END}")
            print(f"   💡 {desc}")

    def show_wizard_help(self):
        """Aide pour le mode assistant"""
        self._print_section_header("🧙‍♂️ MODE ASSISTANT - AIDE DÉTAILLÉE")

        print(f"{Colors.BLUE}📚 L'assistant vous guide pas-à-pas si vous débutez avec les patches.{Colors.END}")
        print("Il analyse votre situation et recommande la meilleure configuration.")
        print()

        print(f"{Colors.CYAN}{Colors.BOLD}LANCEMENT DE L'ASSISTANT:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --wizard{Colors.END}")
        print()

        print(f"{Colors.YELLOW}🎯 QUE FAIT L'ASSISTANT ?{Colors.END}")
        features = [
            "🔍 Détecte automatiquement vos patches",
            "❓ Analyse votre niveau d'expérience",
            "🎯 Identifie le type de votre projet",
            "🛡️ Configure la sécurité adaptée",
            "⚙️ Propose des fonctionnalités avancées",
            "📋 Génère un plan d'exécution détaillé",
            "✅ Lance le traitement avec votre validation"
        ]

        for feature in features:
            print(f"   {feature}")

        print(f"\n{Colors.BOLD}📊 PROFILS UTILISATEUR SUPPORTÉS:{Colors.END}")
        profiles = [
            ("👶 Débutant complet", "Jamais utilisé de patches", "Sécurité maximum + explications"),
            ("🌱 Débutant", "Quelques expériences", "Mode guidé + vérifications"),
            ("🚀 Intermédiaire", "À l'aise avec les concepts", "Fonctionnalités avancées"),
            ("🎯 Expert", "Juste besoin d'un outil efficace", "Personnalisation complète")
        ]

        for level, exp, config in profiles:
            print(f"\n   {Colors.CYAN}{level}{Colors.END}")
            print(f"      Expérience: {exp}")
            print(f"      Configuration: {config}")

    def show_examples_help(self):
        """Exemples détaillés d'utilisation"""
        self._print_section_header("📚 EXEMPLES DÉTAILLÉS D'UTILISATION")

        print(f"{Colors.BLUE}Voici des exemples concrets pour différentes situations.{Colors.END}")
        print()

        scenarios = [
            {
                "title": "🔰 DÉBUTANT - Premier patch",
                "situation": "Vous avez téléchargé un patch depuis GitHub et ne savez pas comment l'appliquer",
                "commands": [
                    ("smart-patch --wizard", "Lance l'assistant pour vous guider"),
                    ("smart-patch --guided fix.patch output/", "Mode guidé sécurisé")
                ],
                "tips": ["Gardez une sauvegarde de vos fichiers", "Utilisez toujours --guided au début"]
            },
            {
                "title": "👨‍💻 DÉVELOPPEUR - Patch d'équipe",
                "situation": "Un collègue vous a envoyé un patch pour corriger un bug",
                "commands": [
                    ("smart-patch --guided --backup-dir ~/backups colleague.patch src/", "Avec backup personnalisé"),
                    ("smart-patch --guided --interactive colleague.patch src/", "Avec confirmations")
                ],
                "tips": ["Vérifiez le patch avant application", "Testez après application"]
            },
            {
                "title": "🏭 PRODUCTION - Mise à jour critique",
                "situation": "Application d'un patch de sécurité en production",
                "commands": [
                    ("smart-patch --guided --preview-only security.patch /tmp/", "Preview d'abord"),
                    ("smart-patch --config production.json security.patch prod/", "Avec config production"),
                    ("smart-patch --guided --modify-original security.patch ./", "Application finale")
                ],
                "tips": ["Toujours preview en premier", "Utilisez une config adaptée", "Testez immédiatement"]
            },
            {
                "title": "🔧 MAINTENANCE - Lot de patches",
                "situation": "Vous devez appliquer plusieurs patches d'un dossier",
                "commands": [
                    ("smart-patch --guided patches/ output/", "Traitement automatique du dossier"),
                    ("smart-patch --guided --batch-mode patches/ output/", "Mode lot sans interruption"),
                    ("smart-patch --config custom.json patches/ output/ --report", "Avec rapport détaillé")
                ],
                "tips": ["Groupement automatique par fichier cible", "Un seul backup par fichier"]
            },
            {
                "title": "🎯 EXPERT - Cas spécifique",
                "situation": "Patch spécifique sur un fichier avec contrôle total",
                "commands": [
                    ("smart-patch fix.patch output/ --target myfile.py", "Cible explicite"),
                    ("smart-patch --config expert.json --no-backup fix.patch ./", "Sans backup"),
                    ("python3 main.py fix.patch myfile.py --verbose", "Appel direct Python")
                ],
                "tips": ["Mode expert pour contrôle maximum", "Vérification manuelle recommandée"]
            }
        ]

        for scenario in scenarios:
            print(f"{Colors.BOLD}{scenario['title']}{Colors.END}")
            print(f"📝 Situation: {scenario['situation']}")
            print()

            print(f"{Colors.GREEN}Commandes recommandées:{Colors.END}")
            for cmd, desc in scenario['commands']:
                print(f"   {Colors.CYAN}$ {cmd}{Colors.END}")
                print(f"     💡 {desc}")

            print(f"\n{Colors.YELLOW}💡 Conseils:{Colors.END}")
            for tip in scenario['tips']:
                print(f"   • {tip}")
            print()

    def show_config_help(self):
        """Aide sur la configuration"""
        self._print_section_header("⚙️ SYSTÈME DE CONFIGURATION")

        print(f"{Colors.BLUE}Smart Patch Processor utilise un système de configuration flexible.{Colors.END}")
        print()

        print(f"{Colors.CYAN}{Colors.BOLD}CRÉATION D'UNE CONFIGURATION:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --create-config{Colors.END}")
        print("   💡 Lance un assistant pour créer une configuration personnalisée")
        print()

        print(f"{Colors.YELLOW}SECTIONS DE CONFIGURATION PRINCIPALES:{Colors.END}")

        sections = [
            {
                "name": "detection",
                "desc": "Configuration de la détection des fichiers cibles",
                "options": [
                    ("file_extensions", "Extensions supportées", "['.py', '.js', '.php']"),
                    ("search_radius", "Rayon de recherche", "3"),
                    ("max_search_depth", "Profondeur max", "3")
                ]
            },
            {
                "name": "security",
                "desc": "Paramètres de sécurité",
                "options": [
                    ("scan_dangerous_patterns", "Scan des patterns dangereux", "true"),
                    ("allow_system_calls", "Autoriser les appels système", "false"),
                    ("max_file_size_mb", "Taille max des fichiers", "10")
                ]
            },
            {
                "name": "guided_patching",
                "desc": "Configuration du mode guidé",
                "options": [
                    ("enabled", "Mode guidé activé", "true"),
                    ("preview_enabled", "Aperçus activés", "true"),
                    ("auto_backup", "Backup automatique", "true")
                ]
            }
        ]

        for section in sections:
            print(f"\n{Colors.BOLD}📁 {section['name'].upper()}{Colors.END}")
            print(f"   {section['desc']}")
            for option, desc, default in section['options']:
                print(f"   • {Colors.CYAN}{option}{Colors.END}: {desc} (défaut: {Colors.YELLOW}{default}{Colors.END})")

        print(f"\n{Colors.GREEN}PROFILS PRÉDÉFINIS:{Colors.END}")
        profiles = [
            ("🔰 Débutant", "Sécurité max + mode guidé + confirmations"),
            ("👨‍💻 Développeur", "Équilibre performance/sécurité + AST"),
            ("🏭 Production", "Robuste + logging + rollback")
        ]

        for profile, desc in profiles:
            print(f"   {profile}: {desc}")

        print(f"\n{Colors.CYAN}UTILISATION D'UNE CONFIGURATION:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --config ma_config.json patches/ output/{Colors.END}")

    def show_troubleshooting_help(self):
        """Guide de dépannage détaillé"""
        self._print_section_header("🔧 GUIDE DE DÉPANNAGE")

        print(f"{Colors.BLUE}Solutions aux problèmes les plus courants.{Colors.END}")
        print()

        problems = [
            {
                "title": "❌ 'Fichier cible non détecté'",
                "causes": [
                    "Le patch ne contient pas d'informations sur le fichier cible",
                    "Le nom du fichier dans le patch ne correspond pas",
                    "Le fichier cible n'existe pas dans les répertoires de recherche"
                ],
                "solutions": [
                    ("Spécifier explicitement", "smart-patch patch.diff output/ --target myfile.py"),
                    ("Vérifier le contenu", "head -20 patch.diff  # Voir les headers"),
                    ("Mode wizard", "smart-patch --wizard  # Assistant de diagnostic")
                ]
            },
            {
                "title": "❌ 'Numéros de ligne incorrects'",
                "causes": [
                    "Le fichier original a été modifié depuis la création du patch",
                    "Différences d'encodage ou de fins de ligne",
                    "Le patch a été créé sur une version différente"
                ],
                "solutions": [
                    ("Correction automatique", "smart-patch --guided patch.diff output/  # Active par défaut"),
                    ("Mode verbose", "smart-patch --verbose patch.diff output/  # Détails de correction"),
                    ("Preview d'abord", "smart-patch --guided --preview-only patch.diff /tmp/")
                ]
            },
            {
                "title": "❌ 'Permission denied'",
                "causes": [
                    "Fichiers en lecture seule",
                    "Répertoire de destination protégé",
                    "Permissions insuffisantes"
                ],
                "solutions": [
                    ("Backup directory", "smart-patch --guided --backup-dir ~/writable patches/ output/"),
                    ("Permissions", "chmod +w target_file.py"),
                    ("Répertoire alternatif", "smart-patch patches/ ~/safe_output/")
                ]
            },
            {
                "title": "⚠️ 'Patches partiellement appliqués'",
                "causes": [
                    "Conflits entre plusieurs patches",
                    "Chunks de patch incompatibles",
                    "Modifications manuelles interférentes"
                ],
                "solutions": [
                    ("Mode interactif", "smart-patch --guided --interactive patches/ output/"),
                    ("Un par un", "smart-patch --guided single.patch output/"),
                    ("Rollback", "Utiliser les backups créés automatiquement")
                ]
            },
            {
                "title": "🐌 'Traitement trop lent'",
                "causes": [
                    "Nombreux patches volumineux",
                    "Analyse AST activée sur gros fichiers",
                    "Scan de sécurité approfondi"
                ],
                "solutions": [
                    ("Mode batch", "smart-patch --guided --batch-mode patches/ output/"),
                    ("Config optimisée", "smart-patch --config fast.json patches/ output/"),
                    ("Désactiver AST", "Configuration: ast_analysis_enabled: false")
                ]
            }
        ]

        for problem in problems:
            print(f"{Colors.BOLD}{problem['title']}{Colors.END}")

            print(f"\n{Colors.YELLOW}Causes possibles:{Colors.END}")
            for cause in problem['causes']:
                print(f"   • {cause}")

            print(f"\n{Colors.GREEN}Solutions:{Colors.END}")
            for solution, cmd in problem['solutions']:
                print(f"   🔧 {solution}:")
                print(f"      {Colors.CYAN}{cmd}{Colors.END}")
            print()

        print(f"{Colors.PURPLE}🆘 AIDE SUPPLÉMENTAIRE:{Colors.END}")
        print("   • Tests: smart-patch --test")
        print("   • Diagnostic: smart-patch --wizard")
        print("   • Mode verbose: --verbose pour plus de détails")
        print("   • Logs: Fichiers de log générés automatiquement")

    def show_advanced_help(self):
        """Aide sur les fonctionnalités avancées"""
        self._print_section_header("🚀 FONCTIONNALITÉS AVANCÉES")

        print(f"{Colors.BLUE}Fonctionnalités pour utilisateurs expérimentés.{Colors.END}")
        print()

        features = [
            {
                "title": "🧠 Analyse AST (Abstract Syntax Tree)",
                "desc": "Analyse syntaxique avancée pour Python, JavaScript, TypeScript, PHP",
                "usage": "Activé par défaut, améliore la précision de détection",
                "config": "correction.ast_analysis_enabled: true"
            },
            {
                "title": "🔗 Intégration Git",
                "desc": "Création automatique de branches et commits",
                "usage": "smart-patch --config git_enabled.json patches/ output/",
                "config": "git.enabled: true, git.create_branch: true"
            },
            {
                "title": "🔄 Système de rollback",
                "desc": "Annulation complète des modifications",
                "usage": "Automatique avec --guided, manuel via config",
                "config": "rollback.enabled: true"
            },
            {
                "title": "📊 Rapports détaillés",
                "desc": "Génération de rapports HTML et JSON",
                "usage": "smart-patch --report patches/ output/",
                "config": "output.report_format: 'html'"
            },
            {
                "title": "🚀 Streaming de gros fichiers",
                "desc": "Traitement efficace de fichiers volumineux",
                "usage": "Automatique pour fichiers > 50MB",
                "config": "streaming.large_file_threshold_mb: 50"
            },
            {
                "title": "🎯 Mode batch optimisé",
                "desc": "Traitement par lots de nombreux patches",
                "usage": "smart-patch --guided --batch-mode patches/ output/",
                "config": "batch.max_concurrent_patches: 4"
            }
        ]

        for feature in features:
            print(f"{Colors.BOLD}{feature['title']}{Colors.END}")
            print(f"   📝 {feature['desc']}")
            print(f"   🔧 Usage: {Colors.CYAN}{feature['usage']}{Colors.END}")
            print(f"   ⚙️ Config: {Colors.YELLOW}{feature['config']}{Colors.END}")
            print()

        print(f"{Colors.PURPLE}💡 CONSEILS D'EXPERT:{Colors.END}")
        tips = [
            "Utilisez --verbose pour comprendre le traitement interne",
            "Créez des configs spécialisées par projet",
            "Combinez --preview-only avec --verbose pour débugger",
            "Utilisez le mode interactif pour les cas complexes",
            "Activez le rollback pour expérimenter en sécurité"
        ]

        for tip in tips:
            print(f"   💡 {tip}")

    def show_quick_reference(self):
        """Référence rapide"""
        self._print_section_header("⚡ RÉFÉRENCE RAPIDE")

        print(f"{Colors.CYAN}COMMANDES ESSENTIELLES:{Colors.END}")

        quick_commands = [
            ("smart-patch --wizard", "🧙‍♂️ Assistant débutant"),
            ("smart-patch --guided patches/ output/", "🎯 Mode guidé standard"),
            ("smart-patch --guided --preview-only patches/ /tmp/", "👁️ Aperçu seulement"),
            ("smart-patch --create-config", "⚙️ Créer configuration"),
            ("smart-patch --help", "❓ Cette aide"),
            ("smart-patch --test", "🧪 Tests système"),
            ("smart-patch --version", "ℹ️ Version du logiciel")
        ]

        for cmd, desc in quick_commands:
            print(f"   {Colors.GREEN}{cmd:50}{Colors.END} {desc}")

        print(f"\n{Colors.YELLOW}OPTIONS IMPORTANTES:{Colors.END}")

        important_options = [
            ("--guided", "Mode guidé recommandé"),
            ("--wizard", "Assistant pas-à-pas"),
            ("--interactive", "Confirmations manuelles"),
            ("--verbose", "Affichage détaillé"),
            ("--config FILE", "Fichier de configuration"),
            ("--backup-dir DIR", "Répertoire de sauvegarde"),
            ("--target FILE", "Fichier cible explicite"),
            ("--preview-only", "Aperçu sans application"),
            ("--modify-original", "Modifier fichiers originaux")
        ]

        for option, desc in important_options:
            print(f"   {Colors.CYAN}{option:20}{Colors.END} {desc}")

        print(f"\n{Colors.BLUE}WORKFLOW RECOMMANDÉ:{Colors.END}")
        workflow = [
            "1. 🧙‍♂️ smart-patch --wizard (première fois)",
            "2. ⚙️ smart-patch --create-config (configuration)",
            "3. 👁️ smart-patch --guided --preview-only (vérification)",
            "4. 🎯 smart-patch --guided patches/ output/ (application)",
            "5. 🧪 smart-patch --test (validation)"
        ]

        for step in workflow:
            print(f"   {step}")

    def _print_header(self):
        """En-tête principal"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    🚀 SMART PATCH PROCESSOR v2.0                            ║")
        print("║                  Processeur Intelligent de Patches                          ║")
        print("║                          📚 AIDE DÉTAILLÉE                                  ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")

    def _print_section_header(self, title: str):
        """En-tête de section"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print(f"╔═══ {title} ═══╗".ljust(80, "═"))
        print(f"╚{'═' * (len(title) + 8)}╝")
        print(f"{Colors.END}")

    def _print_synopsis(self):
        """Synopsis d'utilisation"""
        print(f"{Colors.BOLD}📋 SYNOPSIS:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch [OPTIONS] SOURCE DESTINATION{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --guided [OPTIONS] SOURCE DESTINATION{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --wizard{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch PATCH_FILE DESTINATION --target TARGET_FILE{Colors.END}")
        print()

        print(f"{Colors.BLUE}📝 DESCRIPTION:{Colors.END}")
        print("Smart Patch Processor applique intelligemment des patches avec détection")
        print("automatique des fichiers cibles, correction des numéros de ligne, et")
        print("fonctionnalités avancées de sécurité et rollback.")
        print()

    def _print_modes(self):
        """Modes d'utilisation"""
        print(f"{Colors.BOLD}🎯 MODES D'UTILISATION:{Colors.END}")

        modes = [
            ("🎯 Mode Guidé", "--guided", "Recommandé pour tous - Interface sécurisée pas-à-pas"),
            ("🧙‍♂️ Mode Assistant", "--wizard", "Parfait pour débuter - Guide interactif complet"),
            ("⚡ Mode Standard", "(défaut)", "Traitement direct - Pour utilisateurs expérimentés"),
            ("🔧 Mode Expert", "--config", "Contrôle total - Configuration personnalisée"),
        ]

        for mode, flag, desc in modes:
            print(f"\n   {Colors.CYAN}{mode}{Colors.END}")
            print(f"      Flag: {Colors.YELLOW}{flag}{Colors.END}")
            print(f"      📝 {desc}")

        print(f"\n   {Colors.PURPLE}💡 Conseil: Commencez toujours par --wizard si vous débutez !{Colors.END}")
        print()

    def _print_common_options(self):
        """Options communes"""
        print(f"{Colors.BOLD}⚙️ OPTIONS PRINCIPALES:{Colors.END}")
        print()

        option_groups = [
            {
                "title": "🎯 Options de Mode",
                "options": [
                    ("--guided", "Active le mode guidé avec interface sécurisée"),
                    ("--wizard", "Lance l'assistant interactif pour débutants"),
                    ("--interactive", "Mode interactif avec confirmations manuelles"),
                    ("--batch-mode", "Traitement par lots sans interruption")
                ]
            },
            {
                "title": "📁 Options de Fichiers",
                "options": [
                    ("--target FILE", "Spécifie explicitement le fichier cible"),
                    ("--config FILE", "Utilise un fichier de configuration personnalisé"),
                    ("--backup-dir DIR", "Répertoire personnalisé pour les sauvegardes"),
                    ("--output-format FMT", "Format de sortie (json, yaml, html)")
                ]
            },
            {
                "title": "🛡️ Options de Sécurité",
                "options": [
                    ("--preview-only", "Aperçu uniquement, sans application des patches"),
                    ("--modify-original", "Modifie directement les fichiers originaux"),
                    ("--no-backup", "Désactive la création automatique de sauvegardes"),
                    ("--rollback", "Active le système de rollback avancé")
                ]
            },
            {
                "title": "📊 Options d'Affichage",
                "options": [
                    ("--verbose, -v", "Affichage détaillé du traitement"),
                    ("--quiet, -q", "Mode silencieux, erreurs uniquement"),
                    ("--report", "Génère un rapport détaillé des opérations"),
                    ("--no-color", "Désactive les couleurs dans l'affichage")
                ]
            },
            {
                "title": "🔧 Options Système",
                "options": [
                    ("--test", "Exécute les tests unitaires du système"),
                    ("--create-config", "Lance l'assistant de création de configuration"),
                    ("--version", "Affiche la version du logiciel"),
                    ("--help", "Affiche cette aide détaillée")
                ]
            }
        ]

        for group in option_groups:
            print(f"{Colors.YELLOW}{group['title']}:{Colors.END}")
            for option, desc in group['options']:
                print(f"   {Colors.CYAN}{option:20}{Colors.END} {desc}")
            print()

    def _print_examples(self):
        """Exemples d'utilisation"""
        print(f"{Colors.BOLD}💡 EXEMPLES COURANTS:{Colors.END}")
        print()

        examples = [
            {
                "title": "🔰 Premier usage (recommandé)",
                "cmd": "smart-patch --wizard",
                "desc": "Lance l'assistant qui vous guide étape par étape"
            },
            {
                "title": "🎯 Mode guidé standard",
                "cmd": "smart-patch --guided patches/ output/",
                "desc": "Traite tous les patches d'un dossier de façon sécurisée"
            },
            {
                "title": "👁️ Aperçu avant application",
                "cmd": "smart-patch --guided --preview-only patches/ /tmp/",
                "desc": "Voir les changements sans les appliquer"
            },
            {
                "title": "🎯 Patch unique avec cible explicite",
                "cmd": "smart-patch --guided fix.patch output/ --target myfile.py",
                "desc": "Applique un patch spécifique sur un fichier donné"
            },
            {
                "title": "💾 Avec backup personnalisé",
                "cmd": "smart-patch --guided --backup-dir ~/backups patches/ output/",
                "desc": "Sauvegarde dans un répertoire spécifique"
            },
            {
                "title": "⚙️ Avec configuration personnalisée",
                "cmd": "smart-patch --config production.json patches/ output/",
                "desc": "Utilise une configuration spécialisée pour la production"
            },
            {
                "title": "📊 Avec rapport détaillé",
                "cmd": "smart-patch --guided --report --verbose patches/ output/",
                "desc": "Génère un rapport complet avec détails de traitement"
            },
            {
                "title": "🔧 Mode expert direct",
                "cmd": "python3 main.py --config expert.json patches/ output/",
                "desc": "Appel direct Python avec configuration experte"
            }
        ]

        for example in examples:
            print(f"{Colors.GREEN}{example['title']}:{Colors.END}")
            print(f"   {Colors.CYAN}$ {example['cmd']}{Colors.END}")
            print(f"   💡 {example['desc']}")
            print()

    def _print_troubleshooting(self):
        """Section dépannage rapide"""
        print(f"{Colors.BOLD}🔧 DÉPANNAGE RAPIDE:{Colors.END}")
        print()

        quick_fixes = [
            ("❌ 'Command not found'", "Exécutez: ./install_script.sh puis rechargez votre shell"),
            ("❌ 'Fichier cible non détecté'", "Utilisez: --target FICHIER ou --wizard pour diagnostic"),
            ("❌ 'Permission denied'", "Utilisez: --backup-dir ~/writable ou chmod +w fichier"),
            ("⚠️ 'Numéros de ligne incorrects'", "Normal ! La correction automatique est activée"),
            ("🐌 'Traitement lent'", "Utilisez: --config fast.json ou --batch-mode"),
        ]

        for problem, solution in quick_fixes:
            print(f"   {Colors.RED}{problem}{Colors.END}")
            print(f"   🔧 {solution}")
            print()

        print(f"{Colors.PURPLE}🆘 Pour aide détaillée: smart-patch --help troubleshooting{Colors.END}")
        print()

    def _print_footer(self):
        """Pied de page"""
        print(f"{Colors.BOLD}📚 AIDE SPÉCIALISÉE:{Colors.END}")

        specialized_help = [
            ("smart-patch --help guided", "🎯 Aide détaillée du mode guidé"),
            ("smart-patch --help wizard", "🧙‍♂️ Aide du mode assistant"),
            ("smart-patch --help examples", "📚 Exemples détaillés par situation"),
            ("smart-patch --help config", "⚙️ Guide de configuration avancée"),
            ("smart-patch --help troubleshooting", "🔧 Guide de dépannage complet"),
            ("smart-patch --help advanced", "🚀 Fonctionnalités avancées"),
            ("smart-patch --help quick", "⚡ Référence rapide"),
        ]

        for cmd, desc in specialized_help:
            print(f"   {Colors.CYAN}{cmd:35}{Colors.END} {desc}")

        print()
        print(f"{Colors.YELLOW}🌟 PREMIÈRE FOIS ? Commencez par:{Colors.END}")
        print(f"   {Colors.GREEN}smart-patch --wizard{Colors.END}")
        print()
        print(f"{Colors.BLUE}📧 Support: smart-patch-processor@example.com{Colors.END}")
        print(f"{Colors.BLUE}🌐 Documentation: https://smart-patch-processor.readthedocs.io/{Colors.END}")
        print(f"{Colors.BLUE}🐛 Bugs: https://github.com/smart-patch-processor/issues{Colors.END}")


def show_help(help_type: str = "main"):
    """Point d'entrée principal pour l'aide"""
    help_system = SmartPatchHelp()

    help_types = {
        "main": help_system.show_main_help,
        "guided": help_system.show_guided_help,
        "wizard": help_system.show_wizard_help,
        "examples": help_system.show_examples_help,
        "config": help_system.show_config_help,
        "troubleshooting": help_system.show_troubleshooting_help,
        "advanced": help_system.show_advanced_help,
        "quick": help_system.show_quick_reference,
    }

    if help_type in help_types:
        help_types[help_type]()
    else:
        print(f"{Colors.RED}❌ Type d'aide inconnu: {help_type}{Colors.END}")
        print(f"{Colors.YELLOW}Types disponibles: {', '.join(help_types.keys())}{Colors.END}")
        help_system.show_main_help()


# Intégration dans main.py - Ajoutez ceci à votre main.py existant
def enhance_argument_parser(parser):
    """Améliore l'argument parser avec le nouveau système d'aide"""

    # Sous-commande help spécialisée
    help_subparser = parser.add_subparsers(dest='help_command', help='Aide spécialisée')

    help_parser = help_subparser.add_parser('help', help="Système d'aide avancé")
    help_parser.add_argument('topic', nargs='?', default='main',
                           choices=['main', 'guided', 'wizard', 'examples', 'config',
                                   'troubleshooting', 'advanced', 'quick'],
                           help='Sujet d\'aide spécifique')

    # Override de --help pour plus de détails
    parser.add_argument('--help-topic', choices=['guided', 'wizard', 'examples', 'config',
                                                'troubleshooting', 'advanced', 'quick'],
                       help='Affiche l\'aide sur un sujet spécifique')

    return parser


def handle_help_command(args):
    """Gère les commandes d'aide"""
    if hasattr(args, 'help_command') and args.help_command == 'help':
        show_help(args.topic)
        return True
    elif hasattr(args, 'help_topic') and args.help_topic:
        show_help(args.help_topic)
        return True
    return False


# Exemple d'intégration dans votre main() existant
def main_with_enhanced_help():
    """Version améliorée de main() avec système d'aide avancé"""

    parser = argparse.ArgumentParser(
        description="Smart Patch Processor v2.0 - Traitement intelligent de patches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # On gère --help nous-mêmes
    )

    # Améliorer le parser
    parser = enhance_argument_parser(parser)

    # Ajouter --help personnalisé
    parser.add_argument('-h', '--help', action='store_true',
                       help='Affiche cette aide détaillée')

    # Vos arguments existants...
    parser.add_argument('source', nargs='?', help='Dossier de patches ou fichier patch unique')
    parser.add_argument('output', nargs='?', help='Dossier de destination')
    # ... autres arguments

    args = parser.parse_args()

    # Gérer les commandes d'aide en premier
    if args.help:
        show_help('main')
        sys.exit(0)

    if handle_help_command(args):
        sys.exit(0)

    # Votre logique main() existante...
    # ... reste de votre code


if __name__ == "__main__":
    # Test du système d'aide
    import argparse

    if len(sys.argv) > 1:
        help_type = sys.argv[1]
        show_help(help_type)
    else:
        show_help('main')
