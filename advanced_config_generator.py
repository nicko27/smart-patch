#!/usr/bin/env python3
"""
Générateur de Configuration Avancé pour Smart Patch Processor v2.0
Version intégrée dans main.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from colors import Colors

class AdvancedConfigGenerator:
    """Générateur de configuration avancé simplifié pour intégration"""
    
    def __init__(self):
        self.config = {}
        self.expert_mode = False
        
    def run(self) -> bool:
        """Lance le générateur"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║            🔧 GÉNÉRATEUR DE CONFIGURATION AVANCÉ                ║")
        print("║              Smart Patch Processor v2.0                         ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        return self._interactive_setup()
    
    def _interactive_setup(self) -> bool:
        """Configuration interactive complète"""
        print(f"\n{Colors.BLUE}🎯 Configuration Smart Patch Processor{Colors.END}")
        print()
        
        # Sélection du niveau de configuration
        print("Choisissez votre niveau de configuration :")
        print("1. 🔰 Rapide - Configuration prédéfinie (recommandé)")
        print("2. 🔧 Personnalisée - Options détaillées")
        print("3. 🎯 Expert - Toutes les options avancées")
        
        choice = self._get_choice("Niveau", ['1', '2', '3'], '1')
        
        if choice == '1':
            return self._quick_config()
        elif choice == '2':
            return self._detailed_config()
        else:
            return self._expert_config()
    
    def _quick_config(self) -> bool:
        """Configuration rapide avec profils"""
        print(f"\n{Colors.CYAN}🚀 CONFIGURATION RAPIDE{Colors.END}")
        print()
        print("Profils disponibles :")
        print("1. 🔰 Débutant - Sécurité max, mode guidé")
        print("2. 👨‍💻 Développeur - Équilibre performance/sécurité")
        print("3. 🏭 Production - Robuste et sécurisé")
        
        profile_choice = self._get_choice("Profil", ['1', '2', '3'], '1')
        
        if profile_choice == '1':
            config = self._get_beginner_config()
        elif profile_choice == '2':
            config = self._get_developer_config()
        else:
            config = self._get_production_config()
        
        return self._save_config(config)
    
    def _detailed_config(self) -> bool:
        """Configuration détaillée section par section"""
        print(f"\n{Colors.CYAN}🔧 CONFIGURATION DÉTAILLÉE{Colors.END}")
        print()
        
        config = {}
        
        # Configuration de base
        print(f"{Colors.BOLD}🔍 Configuration de la détection:{Colors.END}")
        config['detection'] = self._configure_detection()
        
        print(f"\n{Colors.BOLD}🛡️ Configuration de la sécurité:{Colors.END}")
        config['security'] = self._configure_security()
        
        print(f"\n{Colors.BOLD}🎯 Configuration du patchage guidé:{Colors.END}")
        config['guided_patching'] = self._configure_guided_patching()
        
        print(f"\n{Colors.BOLD}📝 Configuration du logging:{Colors.END}")
        config['logging'] = self._configure_logging()
        
        # Autres sections avec valeurs par défaut
        config['correction'] = {
            'similarity_threshold': 0.7,
            'ast_analysis_enabled': True,
            'fuzzy_search_enabled': True,
            'context_window': 5
        }
        
        config['output'] = {
            'preserve_original': True,
            'generate_backup': True,
            'report_format': 'json'
        }
        
        return self._save_config(config)
    
    def _expert_config(self) -> bool:
        """Configuration expert avec toutes les options"""
        print(f"\n{Colors.PURPLE}🎯 CONFIGURATION EXPERT{Colors.END}")
        print("⚠️  Mode avancé avec toutes les options disponibles")
        print()
        
        if not self._get_yes_no("Confirmer le mode expert", False):
            return self._detailed_config()
        
        # Configuration complète
        config = self._get_expert_config()
        return self._save_config(config)
    
    def _configure_detection(self) -> Dict[str, Any]:
        """Configure la détection"""
        config = {}
        
        print("Extensions de fichiers :")
        print("1. Python (.py)")
        print("2. Web (.js, .ts, .html, .css)")
        print("3. Système (.php, .java, .cpp)")
        print("4. Personnalisé")
        
        ext_choice = self._get_choice("Extensions", ['1', '2', '3', '4'], '1')
        
        if ext_choice == '1':
            config['file_extensions'] = ['.py', '.pyi']
        elif ext_choice == '2':
            config['file_extensions'] = ['.js', '.ts', '.jsx', '.tsx', '.html', '.css']
        elif ext_choice == '3':
            config['file_extensions'] = ['.php', '.java', '.cpp', '.c', '.h']
        else:
            exts = input("Extensions (séparées par virgules): ").strip()
            config['file_extensions'] = [e.strip() for e in exts.split(',')]
        
        config['search_radius'] = self._get_number("Rayon de recherche", 1, 10, 3)
        config['max_search_depth'] = self._get_number("Profondeur max", 1, 10, 3)
        
        return config
    
    def _configure_security(self) -> Dict[str, Any]:
        """Configure la sécurité"""
        config = {}
        
        print("Niveau de sécurité :")
        print("1. 🔓 Minimal")
        print("2. ⚖️  Équilibré")
        print("3. 🔒 Élevé")
        
        security_level = self._get_choice("Sécurité", ['1', '2', '3'], '2')
        
        if security_level == '1':
            config.update({
                'scan_dangerous_patterns': False,
                'allow_system_calls': True,
                'max_file_size_mb': 100
            })
        elif security_level == '2':
            config.update({
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 10,
                'require_confirmation_for_large_patches': True
            })
        else:
            config.update({
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 5,
                'require_confirmation_for_large_patches': True,
                'require_signature_verification': True
            })
        
        return config
    
    def _configure_guided_patching(self) -> Dict[str, Any]:
        """Configure le patchage guidé"""
        config = {}
        
        config['enabled'] = self._get_yes_no("Activer le mode guidé par défaut", True)
        
        if config['enabled']:
            config['preview_enabled'] = self._get_yes_no("Activer les previews", True)
            config['interactive_mode'] = self._get_yes_no("Mode interactif", True)
            config['confirmation_required'] = self._get_yes_no("Confirmations requises", True)
            config['auto_backup'] = self._get_yes_no("Backup automatique", True)
            
            if config['auto_backup']:
                backup_dir = input("Dossier de backup (vide pour défaut): ").strip()
                if backup_dir:
                    config['backup_directory'] = backup_dir
            
            config['modify_original'] = self._get_yes_no("Modifier les originaux", True)
            config['show_diff_preview'] = self._get_yes_no("Afficher les diffs", True)
            config['context_lines'] = self._get_number("Lignes de contexte", 1, 20, 3)
        
        return config
    
    def _configure_logging(self) -> Dict[str, Any]:
        """Configure le logging"""
        config = {}
        
        print("Niveau de logging :")
        print("1. DEBUG (très détaillé)")
        print("2. INFO (informatif)")
        print("3. WARNING (avertissements)")
        print("4. ERROR (erreurs seulement)")
        
        level_choice = self._get_choice("Niveau", ['1', '2', '3', '4'], '3')
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        config['level'] = levels[int(level_choice) - 1]
        config['console_level'] = 'ERROR'
        
        log_file = self._get_yes_no("Enregistrer dans un fichier", False)
        if log_file:
            filename = input("Nom du fichier (smart_patch.log): ").strip()
            config['file'] = filename or 'smart_patch.log'
        
        return config
    
    def _get_beginner_config(self) -> Dict[str, Any]:
        """Configuration débutant"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.php', '.java'],
                'search_radius': 3,
                'max_search_depth': 2
            },
            'correction': {
                'similarity_threshold': 0.8,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 7
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 5,
                'require_confirmation_for_large_patches': True
            },
            'guided_patching': {
                'enabled': True,
                'preview_enabled': True,
                'interactive_mode': True,
                'step_by_step': True,
                'detailed_preview': True,
                'confirmation_required': True,
                'auto_backup': True,
                'modify_original': True,
                'show_diff_preview': True,
                'context_lines': 5,
                'backup_retention_days': 30
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'json'
            },
            'logging': {
                'level': 'INFO',
                'console_level': 'WARNING'
            }
        }
    
    def _get_developer_config(self) -> Dict[str, Any]:
        """Configuration développeur"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.java', '.cpp'],
                'search_radius': 3,
                'max_search_depth': 3
            },
            'correction': {
                'similarity_threshold': 0.7,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 5,
                'prefer_ast_detection': True
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': True,
                'max_file_size_mb': 20,
                'require_confirmation_for_large_patches': False
            },
            'guided_patching': {
                'enabled': True,
                'preview_enabled': True,
                'interactive_mode': False,
                'confirmation_required': False,
                'auto_backup': True,
                'modify_original': True,
                'show_diff_preview': True,
                'context_lines': 3
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'yaml'
            },
            'logging': {
                'level': 'WARNING',
                'console_level': 'ERROR'
            },
            'performance': {
                'max_concurrent_patches': 3,
                'enable_cache': True
            },
            'git': {
                'enabled': True,
                'auto_detect_repo': True
            }
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Configuration production"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.php', '.java'],
                'search_radius': 2,
                'max_search_depth': 2
            },
            'correction': {
                'similarity_threshold': 0.85,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 10,
                'prefer_ast_detection': True
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 50,
                'require_confirmation_for_large_patches': True,
                'require_signature_verification': True
            },
            'guided_patching': {
                'enabled': False,
                'auto_backup': True,
                'backup_compression': True,
                'backup_retention_days': 90
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'json',
                'create_diff_reports': True,
                'timestamp_files': True
            },
            'logging': {
                'level': 'INFO',
                'console_level': 'WARNING',
                'file': 'smart_patch_production.log',
                'max_file_size_mb': 50
            },
            'performance': {
                'max_concurrent_patches': 4,
                'memory_limit_mb': 1024,
                'enable_streaming': True,
                'enable_cache': True
            },
            'rollback': {
                'enabled': True,
                'auto_restore_on_failure': True
            }
        }
    
    def _get_expert_config(self) -> Dict[str, Any]:
        """Configuration expert complète"""
        print("🎯 Configuration expert - toutes les options disponibles")
        
        config = {
            'detection': {
                'search_patterns': [
                    r"---\\s+(.+)",
                    r"\\+\\+\\+\\s+(.+)",
                    r"Index:\\s+(.+)",
                    r"diff --git a/(.+) b/(.+)"
                ],
                'file_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.java', '.cpp', '.c', '.go', '.rs'],
                'search_radius': 3,
                'max_search_depth': 5,
                'enable_content_based_detection': True,
                'enable_filename_similarity': True
            },
            'correction': {
                'similarity_threshold': 0.7,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 5,
                'prefer_ast_detection': True,
                'auto_fix_line_numbers': True,
                'max_correction_attempts': 3
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 10,
                'require_confirmation_for_large_patches': True,
                'blocked_patterns': [
                    "eval\\s*\\(",
                    "exec\\s*\\(",
                    "system\\s*\\(",
                    "shell=True",
                    "__import__\\s*\\(",
                    "subprocess\\."
                ],
                'validate_patch_integrity': True,
                'log_security_events': True
            },
            'guided_patching': {
                'enabled': True,
                'preview_enabled': True,
                'interactive_mode': True,
                'step_by_step': True,
                'detailed_preview': True,
                'confirmation_required': True,
                'auto_backup': True,
                'backup_compression': False,
                'modify_original': True,
                'show_diff_preview': True,
                'syntax_highlighting': True,
                'line_numbers': True,
                'context_lines': 3,
                'max_preview_lines': 50,
                'backup_retention_days': 30,
                'create_session_log': True
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'json',
                'create_diff_reports': True,
                'include_statistics': True,
                'timestamp_files': True
            },
            'logging': {
                'level': 'DEBUG',
                'console_level': 'INFO',
                'file': 'smart_patch_expert.log',
                'max_file_size_mb': 20,
                'backup_count': 5,
                'enable_debug_mode': True
            },
            'performance': {
                'max_concurrent_patches': 2,
                'memory_limit_mb': 512,
                'enable_streaming': True,
                'streaming_threshold_mb': 50,
                'enable_cache': True,
                'cache_max_size': 500
            },
            'rollback': {
                'enabled': True,
                'auto_restore_on_failure': True,
                'max_rollback_history': 100
            },
            'git': {
                'enabled': True,
                'auto_detect_repo': True,
                'create_branch': True
            },
            'advanced': {
                'enable_experimental_features': False,
                'debug_ast_analysis': False,
                'verbose_error_reporting': True,
                'enable_profiling': False
            }
        }
        
        # Personnalisation supplémentaire
        if self._get_yes_no("Personnaliser davantage", False):
            config = self._detailed_config()
        
        return config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Sauvegarde la configuration"""
        try:
            # Ajouter métadonnées
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"smart_patch_config_{timestamp}.json")
            
            full_config = {
                "_metadata": {
                    "generated_by": "Smart Patch Processor Advanced Config Generator",
                    "version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "platform": sys.platform
                },
                "_description": "Configuration générée automatiquement",
                "_usage": {
                    "command_line": f"smart-patch --config {output_path.name}",
                    "guided_mode": f"smart-patch --guided --config {output_path.name}"
                },
                **config
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            print(f"\n{Colors.GREEN}✅ Configuration sauvegardée: {output_path}{Colors.END}")
            print()
            print(f"{Colors.BOLD}🚀 Utilisation:{Colors.END}")
            print(f"   smart-patch --config {output_path.name} patches/ output/")
            print(f"   smart-patch --guided --config {output_path.name} patches/ output/")
            print()
            print(f"{Colors.BOLD}🔧 Test:{Colors.END}")
            print(f"   smart-patch --help")
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur sauvegarde: {e}{Colors.END}")
            return False
    
    def _get_choice(self, prompt: str, choices: List[str], default: str = None) -> str:
        """Récupère un choix avec validation"""
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
                print(f"{Colors.RED}❌ Choix invalide. Options: {', '.join(choices)}{Colors.END}")
    
    def _get_yes_no(self, prompt: str, default: bool = None) -> bool:
        """Récupère oui/non"""
        default_str = " (y/N)" if default is False else " (Y/n)" if default is True else " (y/n)"
        
        while True:
            response = input(f"{prompt}{default_str}: ").strip().lower()
            
            if not response and default is not None:
                return default
            elif response in ['y', 'yes', 'o', 'oui']:
                return True
            elif response in ['n', 'no', 'non']:
                return False
            else:
                print(f"{Colors.RED}❌ Réponse invalide{Colors.END}")
    
    def _get_number(self, prompt: str, min_val: int, max_val: int, default: int = None) -> int:
        """Récupère un nombre avec validation"""
        while True:
            default_str = f" (défaut: {default})" if default is not None else ""
            range_str = f" [{min_val}-{max_val}]"
            
            user_input = input(f"{prompt}{range_str}{default_str}: ").strip()
            
            if not user_input and default is not None:
                return default
            
            try:
                value = int(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"{Colors.RED}❌ Valeur hors limite: {min_val}-{max_val}{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}❌ Nombre invalide{Colors.END}")

def run_config_generator_advanced():
    """Point d'entrée pour le générateur avancé"""
    generator = AdvancedConfigGenerator()
    return generator.run()
