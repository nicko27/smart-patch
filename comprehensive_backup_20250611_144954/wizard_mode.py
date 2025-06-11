"""Module wizard_mode.py - Classe WizardMode."""

import sys
import glob
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union

from git_integration import GitIntegration
from patch_processor_config import PatchProcessorConfig
from patch_previewer import PatchPreviewer
from rollback_manager import RollbackManager
from interactive_cli import InteractiveCLI
from colors import Colors
from core import registry

class WizardMode:
    """Assistant pas-à-pas pour guider les utilisateurs débutants"""

    def __init__(self, processor, config: PatchProcessorConfig):
        """Initialise le wizard avec validation"""
        if processor is None:
            raise ValueError("Processor cannot be None")
        
        self.processor = processor
        self.processor = processor
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.wizard')

        wizard_config = config.get_section('wizard')
        self.enabled = wizard_config.get('enabled', False)
        self.auto_detect_beginners = wizard_config.get('auto_detect_beginners', True)
        self.explain_steps = wizard_config.get('explain_steps', True)
        self.show_examples = wizard_config.get('show_examples', True)
        self.safety_prompts = wizard_config.get('safety_prompts', True)
        self.learning_mode = wizard_config.get('learning_mode', True)

        # Session state pour le wizard
        self.session = {
            'step': 0,
            'total_steps': 7,
            'user_choices': {},
            'detected_context': {},
            'recommendations': [],
            'warnings': []
        }

    def is_enabled(self) -> bool:
        """Vérifie si le mode wizard est activé"""
        return self.enabled

    def should_activate_wizard(self, args) -> bool:
        """Détermine si le wizard devrait être activé automatiquement"""
        if not self.auto_detect_beginners:
            return False

        # Indicateurs de débutant
        beginner_indicators = [
            not hasattr(args, 'config') or not args.config,  # Pas de config personnalisée
            not hasattr(args, 'verbose') or not args.verbose,  # Mode simple
            len(sys.argv) <= 3,  # Commande simple
        ]

        # Si plusieurs indicateurs, proposer le wizard
        return sum(beginner_indicators) >= 2

    def run_wizard(self) -> Dict:
        """Lance l'assistant complet pas-à-pas"""
        try:
            self._show_wizard_welcome()

            # Étapes du wizard
            steps = [
                self._step_1_introduction,
                self._step_2_source_discovery,
                self._step_3_safety_configuration,
                self._step_4_advanced_features,
                self._step_5_execution_plan,
                self._step_6_final_confirmation,
                self._step_7_execution_and_guidance
            ]

            for i, step_func in enumerate(steps, 1):
                self.session['step'] = i
                self._show_step_header(i, len(steps))

                try:
                    result = step_func()
                    if not result.get('continue', True):
                        return {'completed': False, 'step': i, 'reason': result.get('reason', 'user_exit')}
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}🛑 Assistant interrompu par l'utilisateur{Colors.END}")
                    return {'completed': False, 'step': i, 'reason': 'interrupted'}

            return {
                'completed': True,
                'user_choices': self.session['user_choices'],
                'final_config': self._build_final_configuration()
            }

        except Exception as e:
            self.logger.error(f"Erreur dans le wizard: {e}")
            return {'completed': False, 'error': str(e)}

    def _show_wizard_welcome(self):
        """Affiche l'écran d'accueil du wizard"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                    🧙‍♂️ ASSISTANT SMART PATCH PROCESSOR            ║")
        print("║                                                                  ║")
        print("║      Bienvenue dans l'assistant pas-à-pas qui va vous guider     ║")
        print("║      pour appliquer vos patches en toute sécurité !              ║")
        print("║                                                                  ║")
        print("║  📚 Parfait pour les débutants                                   ║")
        print("║  🛡️ Sécurité maximale                                            ║")
        print("║  🎓 Mode apprentissage intégré                                   ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")

        if self.learning_mode:
            print(f"\n{Colors.BLUE}💡 Mode apprentissage activé:{Colors.END}")
            print("   • Explications détaillées à chaque étape")
            print("   • Exemples concrets")
            print("   • Recommandations personnalisées")
            print("   • Vérifications de sécurité renforcées")

        print(f"\n{Colors.GREEN}Cet assistant va vous guider en 7 étapes simples.{Colors.END}")

        if not self._get_yes_no("Prêt à commencer", default=True):
            raise KeyboardInterrupt

    def _show_step_header(self, current_step: int, total_steps: int):
        """Affiche l'en-tête d'une étape"""
        progress = "█" * current_step + "░" * (total_steps - current_step)
        percentage = int((current_step / total_steps) * 100)

        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print(f"┌─ ÉTAPE {current_step}/{total_steps} ─ {percentage}% ─────────────────────────────")
        print(f"│ Progress: [{progress}]")
        print(f"└─────────────────────────────────────────────────────")
        print(f"{Colors.END}")

    def _step_1_introduction(self) -> Dict:
        """Étape 1: Introduction et explication des concepts"""
        print(f"{Colors.BOLD}🎯 COMPRENDRE LES PATCHES{Colors.END}")

        if self.explain_steps:
            print(f"\n{Colors.BLUE}📚 Qu'est-ce qu'un patch ?{Colors.END}")
            print("Un patch est un fichier qui contient les différences entre deux versions")
            print("d'un fichier. Il permet d'appliquer des modifications de façon précise.")

            if self.show_examples:
                print(f"\n{Colors.YELLOW}📋 Exemple typique:{Colors.END}")
                print("```")
                print("--- ancien_fichier.py")
                print("+++ nouveau_fichier.py")
                print("@@ -1,3 +1,4 @@")
                print(" def hello():")
                print("    print('Bonjour!')")
                print("     pass")
                print("```")
                print("☝️ Ce patch ajoute une ligne 'print' dans la fonction hello()")

        # Détecter le contexte de l'utilisateur
        print(f"\n{Colors.BOLD}🔍 Analysons votre situation:{Colors.END}")

        # Questions pour comprendre le contexte
        context = {}
        context['experience_level'] = self._ask_experience_level()
        context['project_type'] = self._ask_project_type()
        context['patch_source'] = self._ask_patch_source()

        self.session['detected_context'] = context

        # Recommandations basées sur le contexte
        self._generate_contextual_recommendations(context)

        return {'continue': True}

    def _ask_experience_level(self) -> str:
        """Demande le niveau d'expérience"""
        print(f"\n{Colors.CYAN}❓ Quel est votre niveau d'expérience avec les patches ?{Colors.END}")
        print("1. 👶 Débutant complet (jamais utilisé de patches)")
        print("2. 🌱 Débutant (quelques fois, pas très sûr)")
        print("3. 🚀 Intermédiaire (à l'aise avec les concepts de base)")
        print("4. 🎯 Avancé (juste besoin d'un outil efficace)")

        choice = self._get_choice("Votre niveau", ['1', '2', '3', '4'], default='2')
        levels = {'1': 'beginner', '2': 'novice', '3': 'intermediate', '4': 'advanced'}
        return levels[choice]

    def _ask_project_type(self) -> str:
        """Demande le type de projet"""
        print(f"\n{Colors.CYAN}❓ Sur quel type de projet travaillez-vous ?{Colors.END}")
        print("1. 🐍 Python (Django, Flask, scripts, etc.)")
        print("2. 🌐 Web (JavaScript, HTML, CSS, React, etc.)")
        print("3. ☕ Java (Spring, Android, etc.)")
        print("4. 🔧 Autre langage de programmation")
        print("5. 📄 Documentation/configuration (Markdown, YAML, etc.)")
        print("6. 🤷 Je ne sais pas exactement")

        choice = self._get_choice("Type de projet", ['1', '2', '3', '4', '5', '6'], default='6')
        types = {'1': 'python', '2': 'web', '3': 'java', '4': 'other_code', '5': 'docs', '6': 'unknown'}
        return types[choice]

    def _ask_patch_source(self) -> str:
        """Demande la source des patches"""
        print(f"\n{Colors.CYAN}❓ D'où viennent vos patches ?{Colors.END}")
        print("1. 🐛 Corrections de bugs (GitHub, forums, équipe)")
        print("2. ✨ Nouvelles fonctionnalités")
        print("3. 🔄 Migration/mise à jour de code")
        print("4. 🤝 Collaboration d'équipe")
        print("5. 📦 Packages/bibliothèques tierces")
        print("6. 🎲 Autre/je ne sais pas")

        choice = self._get_choice("Source des patches", ['1', '2', '3', '4', '5', '6'], default='6')
        sources = {'1': 'bugfix', '2': 'feature', '3': 'migration', '4': 'team', '5': 'package', '6': 'other'}
        return sources[choice]

    def _generate_contextual_recommendations(self, context: Dict):
        """Génère des recommandations basées sur le contexte"""
        recommendations = []
        warnings = []

        # Recommandations par niveau d'expérience
        if context['experience_level'] in ['beginner', 'novice']:
            recommendations.extend([
                "🛡️ Activation de toutes les sécurités (rollback, preview, backup)",
                "🎓 Mode apprentissage pour comprendre chaque étape",
                "⚠️ Vérifications renforcées avant application"
            ])

        # Recommandations par type de projet
        if context['project_type'] == 'python':
            recommendations.append("🐍 Analyse syntaxique Python avancée activée")
        elif context['project_type'] == 'web':
            recommendations.append("🌐 Support JavaScript/TypeScript activé")
        elif context['project_type'] == 'java':
            recommendations.append("☕ Détection de patterns Java")

        # Avertissements par source
        if context['patch_source'] in ['package', 'other']:
            warnings.append("⚠️ Source inconnue - vérifications de sécurité renforcées recommandées")

        self.session['recommendations'] = recommendations
        self.session['warnings'] = warnings

        # Affichage
        if recommendations:
            print(f"\n{Colors.GREEN}✅ Recommandations pour vous:{Colors.END}")
            for rec in recommendations:
                print(f"   {rec}")

        if warnings:
            print(f"\n{Colors.YELLOW}⚠️ Points d'attention:{Colors.END}")
            for warn in warnings:
                print(f"   {warn}")

    def _step_2_source_discovery(self) -> Dict:
        """Étape 2: Découverte et analyse des sources"""
        print(f"{Colors.BOLD}📁 TROUVER VOS PATCHES{Colors.END}")

        if self.explain_steps:
            print(f"\n{Colors.BLUE}📚 Où chercher vos patches ?{Colors.END}")
            print("Les patches peuvent être dans:")
            print("• Des fichiers .patch ou .diff")
            print("• Téléchargés depuis GitHub, GitLab, etc.")
            print("• Générés par git diff ou autres outils")
            print("• Envoyés par email ou équipe")

        # Auto-détection
        print(f"\n{Colors.CYAN}🔍 Recherche automatique...{Colors.END}")

        current_dir = Path.cwd()
        patches_found = list(current_dir.glob('*.patch')) + list(current_dir.glob('*.diff'))

        # Recherche plus large
        for pattern in ['**/*.patch', '**/*.diff']:
            patches_found.extend(list(current_dir.glob(pattern)))

        # Supprimer les doublons et limiter la profondeur
        unique_patches = []
        seen = set()
        for patch in patches_found:
            if patch.resolve() not in seen:
                seen.add(patch.resolve())
                # Limiter à 3 niveaux de profondeur max
                if len(patch.relative_to(current_dir).parts) <= 3:
                    unique_patches.append(patch)

        patches_found = unique_patches[:20]  # Limiter à 20 patches max pour l'affichage

        if patches_found:
            print(f"{Colors.GREEN}✅ {len(patches_found)} patch(es) détecté(s):{Colors.END}")
            for i, patch in enumerate(patches_found[:10], 1):
                size_kb = patch.stat().st_size // 1024
                rel_path = patch.relative_to(current_dir)
                print(f"  {i:2d}. {rel_path} ({size_kb}KB)")

            if len(patches_found) > 10:
                print(f"     ... et {len(patches_found) - 10} autre(s)")

            # Choix du mode de sélection
            print(f"\n{Colors.BOLD}📋 Comment voulez-vous procéder ?{Colors.END}")
            print("1. ✅ Utiliser tous les patches détectés")
            print("2. 🎯 Sélectionner des patches spécifiques")
            print("3. 📁 Spécifier un autre dossier")
            print("4. 📄 Spécifier un fichier patch unique")

            choice = self._get_choice("Votre choix", ['1', '2', '3', '4'], default='1')

            if choice == '1':
                selected_patches = patches_found
            elif choice == '2':
                selected_patches = self._select_specific_patches(patches_found)
            elif choice == '3':
                custom_dir = self._get_directory_input("Dossier contenant les patches")
                selected_patches = list(custom_dir.glob('*.patch')) + list(custom_dir.glob('*.diff'))
            else:  # choice == '4'
                patch_file = self._get_file_input("Fichier patch")
                selected_patches = [patch_file]

        else:
            print(f"{Colors.YELLOW}⚠️ Aucun patch détecté automatiquement{Colors.END}")
            print(f"\n{Colors.BOLD}📁 Veuillez spécifier vos patches:{Colors.END}")
            print("1. 📁 Spécifier un dossier")
            print("2. 📄 Spécifier un fichier patch")

            choice = self._get_choice("Votre choix", ['1', '2'], default='1')

            if choice == '1':
                custom_dir = self._get_directory_input("Dossier contenant les patches")
                selected_patches = list(custom_dir.glob('*.patch')) + list(custom_dir.glob('*.diff'))
            else:
                patch_file = self._get_file_input("Fichier patch")
                selected_patches = [patch_file]

        if not selected_patches:
            print(f"{Colors.RED}❌ Aucun patch sélectionné{Colors.END}")
            return {'continue': False, 'reason': 'no_patches'}

        self.session['user_choices']['selected_patches'] = selected_patches

        # Analyse des patches sélectionnés
        self._analyze_selected_patches(selected_patches)

        return {'continue': True}

    def _select_specific_patches(self, patches: List[Path]) -> List[Path]:
        """Permet de sélectionner des patches spécifiques"""
        print(f"\n{Colors.CYAN}🎯 Sélection des patches:{Colors.END}")
        print("Tapez les numéros des patches à traiter (séparés par des espaces)")
        print("Exemple: 1 3 5 pour sélectionner les patches 1, 3 et 5")

        while True:
            selection = input("Numéros des patches: ").strip()

            try:
                indices = [int(x) - 1 for x in selection.split()]
                selected = []

                for idx in indices:
                    if 0 <= idx < len(patches):
                        selected.append(patches[idx])
                    else:
                        print(f"❌ Numéro {idx + 1} invalide (max: {len(patches)})")
                        raise ValueError

                if selected:
                    print(f"{Colors.GREEN}✅ {len(selected)} patch(es) sélectionné(s){Colors.END}")
                    return selected
                else:
                    print("❌ Aucun patch sélectionné")

            except ValueError:
                print("❌ Format invalide. Exemple: 1 3 5")

    def _analyze_selected_patches(self, patches: List[Path]):
        """Analyse les patches sélectionnés"""
        print(f"\n{Colors.CYAN}🔍 Analyse des patches sélectionnés...{Colors.END}")

        total_size = sum(p.stat().st_size for p in patches)
        complex_patches = []

        for patch in patches:
            try:
                with open(patch, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Détection de complexité
                chunk_count = content.count('@@')
                lines_count = len(content.split('\n'))

                if chunk_count > 10 or lines_count > 200:
                    complex_patches.append(patch.name)

            except Exception as e:
                self.logger.debug(f"Erreur lecture {patch}: {e}")

        # Rapport d'analyse
        print(f"   📊 {len(patches)} patch(es) - {total_size // 1024}KB total")

        if complex_patches:
            print(f"   ⚠️ Patches complexes détectés: {len(complex_patches)}")
            if self.safety_prompts:
                print(f"   💡 Recommandation: mode preview activé pour ces patches")

    def _step_3_safety_configuration(self) -> Dict:
        """Étape 3: Configuration de la sécurité"""
        print(f"{Colors.BOLD}🛡️ CONFIGURATION DE SÉCURITÉ{Colors.END}")

        if self.explain_steps:
            print(f"\n{Colors.BLUE}📚 Pourquoi la sécurité est importante ?{Colors.END}")
            print("L'application de patches peut modifier vos fichiers de façon irréversible.")
            print("Les options de sécurité vous protègent contre:")
            print("• Les erreurs d'application")
            print("• Les patches malveillants")
            print("• Les modifications non désirées")
            print("• La perte de données")

        safety_config = {}

        # Niveau de sécurité global
        print(f"\n{Colors.BOLD}🔒 Choisissez votre niveau de sécurité:{Colors.END}")
        print("1. 🛡️ Maximum (débutants recommandé)")
        print("   → Sauvegardes, rollback, preview, confirmations")
        print("2. ⚖️ Équilibré")
        print("   → Sauvegardes et rollback, preview optionnel")
        print("3. ⚡ Rapide")
        print("   → Sauvegardes uniquement")
        print("4. 🎯 Personnalisé")
        print("   → Je configure moi-même")

        level_choice = self._get_choice("Niveau de sécurité", ['1', '2', '3', '4'], default='1')

        if level_choice == '1':  # Maximum
            safety_config = {
                'rollback_enabled': True,
                'preview_enabled': True,
                'backup_enabled': True,
                'confirmation_required': True,
                'security_scan': True
            }
        elif level_choice == '2':  # Équilibré
            safety_config = {
                'rollback_enabled': True,
                'preview_enabled': self._get_yes_no("Activer les aperçus avant application", default=True),
                'backup_enabled': True,
                'confirmation_required': False,
                'security_scan': True
            }
        elif level_choice == '3':  # Rapide
            safety_config = {
                'rollback_enabled': self._get_yes_no("Système de rollback (recommandé)", default=True),
                'preview_enabled': False,
                'backup_enabled': True,
                'confirmation_required': False,
                'security_scan': self._get_yes_no("Scanner les problèmes de sécurité", default=True)
            }
        else:  # Personnalisé
            safety_config = self._configure_custom_safety()

        self.session['user_choices']['safety_config'] = safety_config

        # Résumé de la configuration
        print(f"\n{Colors.GREEN}✅ Configuration de sécurité:{Colors.END}")
        for option, enabled in safety_config.items():
            status = "✅" if enabled else "❌"
            option_name = option.replace('_', ' ').title()
            print(f"   {status} {option_name}")

        return {'continue': True}

    def _configure_custom_safety(self) -> Dict:
        """Configuration personnalisée de la sécurité"""
        print(f"\n{Colors.CYAN}⚙️ Configuration personnalisée:{Colors.END}")

        config = {}

        # Questions détaillées
        questions = [
            ("rollback_enabled", "Système de rollback", "Permet d'annuler les modifications", True),
            ("backup_enabled", "Sauvegardes automatiques", "Copie des fichiers avant modification", True),
            ("preview_enabled", "Aperçus avant application", "Voir les changements avant application", True),
            ("security_scan", "Scan de sécurité", "Détecte les patterns dangereux", True),
            ("confirmation_required", "Confirmations individuelles", "Confirmer chaque patch", False)
        ]

        for key, name, description, default in questions:
            print(f"\n❓ {name}")
            if self.explain_steps:
                print(f"   💡 {description}")
            config[key] = self._get_yes_no(f"Activer {name.lower()}", default=default)

        return config

    def _step_4_advanced_features(self) -> Dict:
        """Étape 4: Fonctionnalités avancées"""
        print(f"{Colors.BOLD}🚀 FONCTIONNALITÉS AVANCÉES{Colors.END}")

        if self.explain_steps:
            print(f"\n{Colors.BLUE}📚 Fonctionnalités optionnelles:{Colors.END}")
            print("Ces fonctionnalités peuvent améliorer votre expérience mais ne sont pas")
            print("nécessaires pour un usage basique.")

        advanced_config = {}

        # Git integration
        if self.processor.git_integration.is_git_available:
            print(f"\n{Colors.BOLD}🔗 Intégration Git{Colors.END}")
            if self.explain_steps:
                print("   Git permet de créer des branches dédiées et de tracker les changements")

            git_detected = self.processor.git_integration.detect_git_repo(Path.cwd())
            if git_detected:
                print(f"   ✅ Dépôt Git détecté")
                advanced_config['git_enabled'] = self._get_yes_no("Utiliser l'intégration Git", default=True)

                if advanced_config['git_enabled']:
                    advanced_config['git_create_branch'] = self._get_yes_no("Créer une branche dédiée", default=True)
                    advanced_config['git_auto_commit'] = self._get_yes_no("Commit automatique", default=False)
            else:
                print(f"   ⚠️ Aucun dépôt Git détecté")
                advanced_config['git_enabled'] = False
        else:
            advanced_config['git_enabled'] = False

        # AST Analysis
        print(f"\n{Colors.BOLD}🧠 Analyse syntaxique avancée (AST){Colors.END}")
        if self.explain_steps:
            print("   Améliore la précision pour Python, JavaScript, TypeScript, PHP")

        advanced_config['ast_enabled'] = self._get_yes_no("Activer l'analyse AST", default=True)

        # Interactive mode
        if not self.processor.interactive_cli.is_enabled():
            print(f"\n{Colors.BOLD}💬 Mode interactif{Colors.END}")
            if self.explain_steps:
                print("   Permet de superviser le traitement en temps réel")

            advanced_config['interactive_enabled'] = self._get_yes_no("Mode interactif", default=False)
        else:
            advanced_config['interactive_enabled'] = True

        # HTML Preview
        print(f"\n{Colors.BOLD}🌐 Rapports HTML{Colors.END}")
        if self.explain_steps:
            print("   Génère des rapports HTML avec syntaxe colorée pour documentation")

        advanced_config['html_preview'] = self._get_yes_no("Générer des rapports HTML", default=False)

        self.session['user_choices']['advanced_config'] = advanced_config

        return {'continue': True}

    def _step_5_execution_plan(self) -> Dict:
        """Étape 5: Plan d'exécution"""
        print(f"{Colors.BOLD}📋 PLAN D'EXÉCUTION{Colors.END}")

        # Générer le plan basé sur les choix
        plan = self._generate_execution_plan()

        print(f"\n{Colors.CYAN}🎯 Voici ce qui va se passer:{Colors.END}")

        for i, step in enumerate(plan['steps'], 1):
            icon = step.get('icon', '•')
            description = step.get('description', '')
            details = step.get('details', '')

            print(f"{i:2d}. {icon} {description}")
            if details and self.explain_steps:
                print(f"     💡 {details}")

        # Estimations
        print(f"\n{Colors.BOLD}📊 Estimations:{Colors.END}")
        print(f"   ⏱️ Temps estimé: {plan['estimated_time']}")
        print(f"   📁 Fichiers traités: {plan['files_count']}")
        print(f"   💾 Espace nécessaire: {plan['space_needed']}")

        # Avertissements si nécessaire
        if plan['warnings']:
            print(f"\n{Colors.YELLOW}⚠️ Points d'attention:{Colors.END}")
            for warning in plan['warnings']:
                print(f"   • {warning}")

        self.session['execution_plan'] = plan

        return {'continue': True}

    def _generate_execution_plan(self) -> Dict:
        """Génère le plan d'exécution basé sur les choix"""
        patches = self.session['user_choices']['selected_patches']
        safety = self.session['user_choices']['safety_config']
        advanced = self.session['user_choices']['advanced_config']

        steps = []
        warnings = []

        # Étapes de base
        steps.append({
            'icon': '🔍',
            'description': 'Analyse des patches et détection des fichiers cibles',
            'details': 'Identification automatique des fichiers à modifier'
        })

        if safety.get('security_scan', True):
            steps.append({
                'icon': '🔒',
                'description': 'Scan de sécurité',
                'details': 'Détection de patterns dangereux dans les patches'
            })

        if safety.get('backup_enabled', True):
            steps.append({
                'icon': '💾',
                'description': 'Création des sauvegardes',
                'details': 'Sauvegarde des fichiers avant modification'
            })

        if advanced.get('git_enabled', False) and advanced.get('git_create_branch', False):
            steps.append({
                'icon': '🌿',
                'description': 'Création de branche Git dédiée',
                'details': 'Isolation des changements sur une branche temporaire'
            })

        if safety.get('preview_enabled', True):
            steps.append({
                'icon': '👁️',
                'description': 'Génération des aperçus',
                'details': 'Prévisualisation des modifications avant application'
            })

        steps.append({
            'icon': '⚡',
            'description': 'Application des patches',
            'details': 'Modification effective des fichiers'
        })

        if advanced.get('git_enabled', False) and advanced.get('git_auto_commit', False):
            steps.append({
                'icon': '📝',
                'description': 'Commit automatique',
                'details': 'Enregistrement des changements dans Git'
            })

        if advanced.get('html_preview', False):
            steps.append({
                'icon': '📄',
                'description': 'Génération des rapports HTML',
                'details': 'Documentation des changements appliqués'
            })

        # Estimations
        patch_count = len(patches)
        base_time = patch_count * 2  # 2 secondes par patch de base

        if safety.get('preview_enabled', True):
            base_time += patch_count * 1
        if advanced.get('html_preview', False):
            base_time += patch_count * 0.5

        estimated_time = f"{base_time:.0f} secondes" if base_time < 60 else f"{base_time/60:.1f} minutes"

        # Calcul espace nécessaire
        total_size = sum(p.stat().st_size for p in patches)
        space_multiplier = 2  # Fichiers originaux + modifiés
        if safety.get('backup_enabled', True):
            space_multiplier += 1
        if safety.get('rollback_enabled', True):
            space_multiplier += 1

        space_needed = f"{(total_size * space_multiplier) // 1024}KB"

        # Avertissements
        if patch_count > 20:
            warnings.append("Beaucoup de patches - le traitement peut prendre du temps")
        if not safety.get('rollback_enabled', True):
            warnings.append("Rollback désactivé - les modifications seront difficiles à annuler")

        return {
            'steps': steps,
            'estimated_time': estimated_time,
            'files_count': patch_count,
            'space_needed': space_needed,
            'warnings': warnings
        }

    def _step_6_final_confirmation(self) -> Dict:
        """Étape 6: Confirmation finale"""
        print(f"{Colors.BOLD}✅ CONFIRMATION FINALE{Colors.END}")

        print(f"\n{Colors.BLUE}📋 Récapitulatif de votre configuration:{Colors.END}")

        # Résumé patches
        patches = self.session['user_choices']['selected_patches']
        print(f"   📦 Patches: {len(patches)} fichier(s)")

        # Résumé sécurité
        safety = self.session['user_choices']['safety_config']
        safety_features = [name.replace('_', ' ').title() for name, enabled in safety.items() if enabled]
        print(f"   🛡️ Sécurité: {', '.join(safety_features) if safety_features else 'Aucune'}")

        # Résumé fonctionnalités
        advanced = self.session['user_choices']['advanced_config']
        advanced_features = [name.replace('_', ' ').title() for name, enabled in advanced.items() if enabled]
        if advanced_features:
            print(f"   🚀 Avancé: {', '.join(advanced_features)}")

        plan = self.session['execution_plan']
        print(f"   ⏱️ Durée estimée: {plan['estimated_time']}")

        # Derniers avertissements de sécurité
        if self.safety_prompts:
            print(f"\n{Colors.YELLOW}⚠️ IMPORTANT:{Colors.END}")
            print("• Cette opération va modifier vos fichiers")
            print("• Assurez-vous d'avoir une sauvegarde de votre travail")
            print("• En cas de problème, vous pourrez utiliser le rollback")

        print(f"\n{Colors.RED}{Colors.BOLD}🚨 DERNIÈRE CHANCE D'ANNULER 🚨{Colors.END}")

        if not self._get_yes_no("Confirmer et lancer l'application des patches", default=False):
            return {'continue': False, 'reason': 'user_cancelled'}

        return {'continue': True}

    def _step_7_execution_and_guidance(self) -> Dict:
        """Étape 7: Exécution avec guidance - VERSION CORRIGÉE"""
        print(f"{Colors.BOLD}🚀 EXÉCUTION EN COURS{Colors.END}")

        if self.explain_steps:
            print(f"{Colors.BLUE}📚 Que se passe-t-il maintenant ?{Colors.END}")
            print("L'assistant va appliquer votre configuration et traiter les patches.")
            print("Suivez les messages pour comprendre chaque étape.")

        # Configuration du processeur avec les choix du wizard
        self._apply_wizard_configuration()

        print(f"{Colors.GREEN}✨ Configuration appliquée avec succès !{Colors.END}")
        print(f"{Colors.CYAN}Le traitement va maintenant commencer...{Colors.END}")

        # 🔥 CORRECTION: Lancer le traitement réel des patches
        try:
            patches = self.session['user_choices']['selected_patches']

            # Configurer les chemins pour le processeur
            if patches:
                # Si un seul patch, utiliser le mode fichier unique
                if len(patches) == 1:
                    self.processor.source_dir = patches[0]
                else:
                    # Utiliser le répertoire parent des patches
                    self.processor.source_dir = patches[0].parent

                # Créer un répertoire de sortie si pas défini
                if not hasattr(self.processor, 'output_dir') or not self.processor.output_dir:
                    output_dir = Path.cwd() / "smart_patch_output"
                    output_dir.mkdir(exist_ok=True)
                    self.processor.output_dir = output_dir

                print(f"{Colors.BLUE}📁 Dossier de sortie: {self.processor.output_dir}{Colors.END}")

                # 🎯 LANCER LE TRAITEMENT RÉEL
                print(f"{Colors.CYAN}⚡ Application des patches...{Colors.END}")
                summary = self.processor.process_all_patches()

                # Afficher les résultats avec gestion robuste
                try:
                    # Analyser le format du résumé de manière sécurisée
                    if isinstance(summary, dict):
                        # Essayer différents formats de résumé
                        success_count = summary.get('success', 0)
                        failed_count = summary.get('failed', 0)
                        total_count = summary.get('total', 0)
                        
                        # Format alternatif: compter depuis les résultats
                        if success_count == 0 and 'results' in summary:
                            results = summary.get('results', [])
                            success_count = sum(1 for r in results if getattr(r, 'success', False))
                            failed_count = len(results) - success_count
                            total_count = len(results)
                        
                        # Format alternatif: utiliser les clés disponibles
                        if success_count == 0 and total_count == 0:
                            if 'successful_patches' in summary:
                                success_count = summary.get('successful_patches', 0)
                            if 'failed_patches' in summary:
                                failed_count = summary.get('failed_patches', 0)
                            if 'total_patches' in summary:
                                total_count = summary.get('total_patches', 0)
                        
                        print(f"\n{Colors.CYAN}📊 Résultats du traitement:{Colors.END}")
                        print(f"   📦 Total: {total_count} patch(es)")
                        print(f"   ✅ Succès: {success_count}")
                        print(f"   ❌ Échecs: {failed_count}")
                        
                        if success_count > 0:
                            print(f"\n{Colors.GREEN}🎉 Traitement terminé avec succès !{Colors.END}")
                            print(f"   📁 Résultats dans: {self.processor.output_dir}")
                            
                            # Proposer de voir les résultats si disponibles
                            if 'results' in summary and self._get_yes_no("Voulez-vous voir le détail des résultats", default=True):
                                self._show_detailed_results(summary)
                        else:
                            print(f"\n{Colors.RED}❌ Aucun patch n'a pu être appliqué{Colors.END}")
                            print("Vérifiez les erreurs ci-dessus ou lancez avec --verbose pour plus de détails")
                    
                    else:
                        # Résumé dans un format inattendu
                        print(f"\n{Colors.YELLOW}⚠️ Format de résumé inattendu{Colors.END}")
                        print(f"   Type: {type(summary).__name__}")
                        print(f"   Valeur: {summary}")
                        
                        # Essayer de déterminer le succès
                        if summary:
                            print(f"\n{Colors.GREEN}✅ Le traitement semble avoir réussi{Colors.END}")
                        else:
                            print(f"\n{Colors.RED}❌ Le traitement a probablement échoué{Colors.END}")
                            
                except Exception as e:
                    print(f"\n{Colors.RED}❌ Erreur lors de l'analyse des résultats: {e}{Colors.END}")
                    print(f"   📊 Résumé brut: {summary}")

            else:
                print(f"{Colors.RED}❌ Aucun patch à traiter{Colors.END}")

        except Exception as e:
            print(f"{Colors.RED}❌ Erreur durant l'application: {e}{Colors.END}")
            if self.processor.verbose:
                import traceback
                traceback.print_exc()
            return {'continue': False, 'error': str(e)}

        return {'continue': True, 'processing_completed': True}

    def _apply_wizard_configuration(self):
        """Applique la configuration du wizard au processeur"""
        choices = self.session['user_choices']

        # Configuration sécurité
        safety = choices.get('safety_config', {})
        if safety.get('rollback_enabled'):
            self.processor.config.config.setdefault('rollback', {})['enabled'] = True
        if safety.get('preview_enabled'):
            self.processor.config.config.setdefault('preview', {})['enabled'] = True
        if safety.get('security_scan'):
            self.processor.config.config.setdefault('security', {})['scan_dangerous_patterns'] = True

        # Configuration avancée
        advanced = choices.get('advanced_config', {})
        if advanced.get('git_enabled'):
            self.processor.config.config.setdefault('git', {})['enabled'] = True
            if advanced.get('git_create_branch'):
                self.processor.config.config['git']['create_branch'] = True
            if advanced.get('git_auto_commit'):
                self.processor.config.config['git']['auto_commit'] = True

        if advanced.get('ast_enabled'):
            self.processor.config.config.setdefault('correction', {})['ast_analysis_enabled'] = True

        if advanced.get('interactive_enabled'):
            self.processor.config.config.setdefault('interactive', {})['enabled'] = True

        if advanced.get('html_preview'):
            self.processor.config.config.setdefault('preview', {})['generate_html_preview'] = True

        # Recréer les composants avec la nouvelle configuration
        self.processor.rollback_manager = RollbackManager(self.processor.config)
        self.processor.previewer = PatchPreviewer(self.processor.config)
        self.processor.git_integration = GitIntegration(self.processor.config)
        self.processor.interactive_cli = InteractiveCLI(self.processor.config, self.processor)

    def _build_final_configuration(self) -> Dict:
        """Construit la configuration finale pour le processeur"""
        return {
            'patches': self.session['user_choices']['selected_patches'],
            'safety': self.session['user_choices']['safety_config'],
            'advanced': self.session['user_choices']['advanced_config'],
            'execution_plan': self.session['execution_plan']
        }

    # Méthodes utilitaires
    def _get_yes_no(self, prompt: str, default: bool = None) -> bool:
        """Récupère une réponse oui/non"""
        choices = ['y', 'n']
        default_str = 'y' if default else 'n' if default is False else None

        choice = self._get_choice(prompt, choices, default_str)
        return choice == 'y'

    def _get_choice(self, prompt: str, choices: List[str], default: str = None) -> str:
        """Récupère un choix utilisateur"""
        while True:
            choice_str = f" [{'/'.join(choices)}]"
            if default:
                choice_str += f" (défaut: {default})"

            user_input = input(f"{prompt}{choice_str}: ").strip()

            if not user_input and default:
                return default
            elif user_input in choices:
                return user_input
            else:
                print(f"❌ Choix invalide. Options: {', '.join(choices)}")

    def _get_directory_input(self, prompt: str) -> Path:
        """Récupère un répertoire avec validation"""
        while True:
            dir_str = input(f"{prompt}: ").strip()

            if not dir_str:
                print("❌ Veuillez spécifier un répertoire")
                continue

            dir_path = Path(dir_str)

            if dir_path.exists() and dir_path.is_dir():
                return dir_path
            else:
                print(f"❌ Répertoire non trouvé: {dir_path}")
                retry = self._get_yes_no("Réessayer", default=True)
                if not retry:
                    raise KeyboardInterrupt

    def _get_file_input(self, prompt: str) -> Path:
        """Récupère un fichier avec validation"""
        while True:
            file_str = input(f"{prompt}: ").strip()

            if not file_str:
                print("❌ Veuillez spécifier un fichier")
                continue

            file_path = Path(file_str)

            if file_path.exists() and file_path.is_file():
                return file_path
            else:
                print(f"❌ Fichier non trouvé: {file_path}")
                retry = self._get_yes_no("Réessayer", default=True)
                if not retry:
                    raise KeyboardInterrupt

    def _show_detailed_results(self, summary: Dict):
        """Affiche les résultats détaillés avec validation robuste"""
        if not isinstance(summary, dict):
            print(f"   ⚠️ Format inattendu: {type(summary).__name__}")
            return
        
        results = summary.get('results', [])
        if not results:
            print("   ℹ️ Aucun résultat détaillé disponible")
            return
        """Affiche les résultats détaillés - VERSION ULTRA-SÉCURISÉE"""
        print(f"\n{Colors.CYAN}📊 RÉSULTATS DÉTAILLÉS:{Colors.END}")
        
        try:
            # Vérifier le format du résumé
            if not isinstance(summary, dict):
                print(f"   ⚠️ Format de résumé non standard: {type(summary).__name__}")
                return
            
            results = summary.get('results', [])
            
            if not results:
                print("   ℹ️ Aucun résultat détaillé disponible")
                print(f"   📋 Clés disponibles: {list(summary.keys())}")
                return
                
            for i, result in enumerate(results, 1):
                try:
                    # Extraction sécurisée des attributs
                    success = getattr(result, 'success', None)
                    if success is None:
                        success = hasattr(result, 'success') and result.success
                    
                    patch_file = getattr(result, 'patch_file', None) or 'patch inconnu'
                    target_file = getattr(result, 'target_file', None) or 'cible inconnue'
                    output_file = getattr(result, 'output_file', None) or 'sortie inconnue'
                    issues = getattr(result, 'issues', []) or []
                    errors = getattr(result, 'errors', []) or []
                    
                    if success:
                        print(f"\n{i:2d}. ✅ {Path(patch_file).name}")
                        if target_file != 'cible inconnue':
                            print(f"     🎯 Cible: {Path(target_file).name}")
                        if output_file != 'sortie inconnue':
                            print(f"     💾 Sortie: {Path(output_file).name}")
                        if issues:
                            print(f"     🔧 {len(issues)} problème(s) corrigé(s)")
                    else:
                        print(f"\n{i:2d}. ❌ {Path(patch_file).name}")
                        if errors:
                            for error in errors[:3]:  # Limiter à 3 erreurs
                                print(f"     ⚠️ {error}")
                            if len(errors) > 3:
                                print(f"     ... et {len(errors) - 3} autre(s) erreur(s)")
                        else:
                            print(f"     ⚠️ Échec sans détail d'erreur")
                            
                except Exception as e:
                    print(f"\n{i:2d}. ⚠️ Erreur d'affichage du résultat: {e}")
                    # Essayer d'afficher au moins quelque chose
                    try:
                        print(f"     📋 Données brutes: {result}")
                    except:
                        print(f"     📋 Résultat non affichable")
                    
        except Exception as e:
            print(f"   ❌ Erreur lors de l'affichage des résultats: {e}")
            print(f"   📊 Clés du résumé: {list(summary.keys()) if isinstance(summary, dict) else 'N/A'}")
    def _diagnose_processor_state(self):
        """Diagnostique l'état du processeur pour débugger"""
        print(f"\n{Colors.YELLOW}🔍 DIAGNOSTIC DU PROCESSEUR:{Colors.END}")
        
        try:
            print(f"   • Type: {type(self.processor).__name__}")
            print(f"   • Source dir: {getattr(self.processor, 'source_dir', 'UNDEFINED')}")
            print(f"   • Output dir: {getattr(self.processor, 'output_dir', 'UNDEFINED')}")
            print(f"   • Verbose: {getattr(self.processor, 'verbose', 'UNDEFINED')}")
            
            # Vérifier les composants
            components = ['detector', 'analyzer', 'corrector', 'applicator']
            for comp in components:
                has_comp = hasattr(self.processor, comp)
                print(f"   • {comp}: {'✅' if has_comp else '❌'}")
            
            # Vérifier les patches sélectionnés
            patches = self.session.get('user_choices', {}).get('selected_patches', [])
            print(f"   • Patches sélectionnés: {len(patches)}")
            
            for i, patch in enumerate(patches[:3], 1):
                if hasattr(patch, 'exists') and patch.exists():
                    size = patch.stat().st_size
                    print(f"     {i}. {patch.name} ({size} bytes) ✅")
                else:
                    print(f"     {i}. {patch} ❌ MISSING")
                    
            if len(patches) > 3:
                print(f"     ... et {len(patches) - 3} autre(s)")
                
        except Exception as e:
            print(f"   ❌ Erreur de diagnostic: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_process_execution(self) -> Dict:
        """Exécution sécurisée des patches avec gestion d'erreurs robuste"""
        try:
            if not self.processor:
                return {'success': False, 'error': 'Processeur non disponible'}
            
            patches = self.session.get('user_choices', {}).get('selected_patches', [])
            if not patches:
                return {'success': False, 'error': 'Aucun patch sélectionné'}
            
            # Configuration sécurisée
            self._apply_wizard_configuration()
            
            # Traitement avec timeout et validation
            summary = self.processor.process_all_patches()
            
            # Validation du résultat
            if isinstance(summary, dict):
                success_count = (summary.get('success', 0) or 
                               summary.get('successful_patches', 0) or
                               len([r for r in summary.get('results', []) 
                                   if getattr(r, 'success', False)]))
                
                return {
                    'success': success_count > 0,
                    'summary': summary,
                    'patches_processed': len(patches),
                    'successful_patches': success_count
                }
            
            return {'success': False, 'error': 'Format de résultat invalide'}
            
        except Exception as e:
            self.logger.error(f"Erreur traitement: {e}")
            return {'success': False, 'error': str(e)}
