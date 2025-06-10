#!/usr/bin/env python3
"""
Générateur de Configuration Avancé pour Smart Patch Processor v2.0
Version YAML améliorée avec support ~/.config/smart-patch/
VERSION CORRIGÉE - Fix du bug NoneType
"""

import os
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from colors import Colors

class AdvancedConfigGenerator:
    """Générateur de configuration avancé avec support YAML et configuration utilisateur"""
    
    def __init__(self):
        self.config = {}
        self.expert_mode = False
        self.user_config_dir = Path.home() / ".config" / "smart-patch"
        
    def run(self) -> bool:
        """Lance le générateur"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║            🔧 GÉNÉRATEUR DE CONFIGURATION AVANCÉ                ║")
        print("║              Smart Patch Processor v2.0                         ║")
        print("║                     Format YAML                                 ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        return self._interactive_setup()
    
    def _interactive_setup(self) -> bool:
        """Configuration interactive complète"""
        print(f"\n{Colors.BLUE}🎯 Configuration Smart Patch Processor{Colors.END}")
        print()
        
        # Afficher l'état actuel de la configuration
        self._show_current_config_status()
        
        # Sélection du niveau de configuration
        print("\nChoisissez votre niveau de configuration :")
        print("1. 🔰 Rapide - Configuration prédéfinie (recommandé)")
        print("2. 🔧 Personnalisée - Options détaillées")
        print("3. 🎯 Expert - Toutes les options avancées")
        print("4. 📝 Modifier configuration existante")
        
        choice = self._get_choice("Niveau", ['1', '2', '3', '4'], '1')
        
        if choice == '1':
            return self._quick_config()
        elif choice == '2':
            return self._detailed_config()
        elif choice == '3':
            return self._expert_config()
        else:
            return self._modify_existing_config()
    
    def _show_current_config_status(self):
        """Affiche l'état actuel de la configuration"""
        print(f"{Colors.CYAN}📁 État actuel de la configuration:{Colors.END}")
        
        # Vérifier les emplacements de configuration
        config_locations = [
            (self.user_config_dir / "config.yaml", "Configuration utilisateur principale"),
            (self.user_config_dir / "smart-patch.yaml", "Configuration utilisateur alternative"),
            (Path.cwd() / "smart_patch_config.yaml", "Configuration locale (YAML)"),
            (Path.cwd() / "smart_patch_config.json", "Configuration locale (JSON)")
        ]
        
        found_configs = []
        for config_path, description in config_locations:
            if config_path.exists():
                size_kb = config_path.stat().st_size // 1024
                mtime = datetime.fromtimestamp(config_path.stat().st_mtime)
                found_configs.append((config_path, description, size_kb, mtime))
                print(f"   ✅ {description}")
                print(f"      📄 {config_path}")
                print(f"      📊 {size_kb}KB - Modifiée: {mtime.strftime('%Y-%m-%d %H:%M')}")
        
        if not found_configs:
            print(f"   ⚠️ Aucune configuration personnalisée trouvée")
            print(f"   💡 Configuration par défaut sera utilisée")
        
        print(f"\n   📁 Répertoire utilisateur: {self.user_config_dir}")
        if not self.user_config_dir.exists():
            print(f"   ℹ️ Le répertoire sera créé automatiquement")
        
    def _quick_config(self) -> bool:
        """Configuration rapide avec profils"""
        print(f"\n{Colors.CYAN}🚀 CONFIGURATION RAPIDE{Colors.END}")
        print()
        print("Profils disponibles :")
        print("1. 🔰 Débutant - Sécurité max, mode guidé")
        print("2. 👨‍💻 Développeur - Équilibre performance/sécurité")
        print("3. 🏭 Production - Robuste et sécurisé")
        print("4. 🎯 Minimaliste - Configuration légère")
        
        profile_choice = self._get_choice("Profil", ['1', '2', '3', '4'], '1')
        
        if profile_choice == '1':
            config = self._get_beginner_config()
        elif profile_choice == '2':
            config = self._get_developer_config()
        elif profile_choice == '3':
            config = self._get_production_config()
        else:
            config = self._get_minimal_config()
        
        return self._save_config(config, profile_choice)
    
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
        
        print(f"\n{Colors.BOLD}⚡ Configuration des performances:{Colors.END}")
        config['performance'] = self._configure_performance()
        
        # Autres sections avec valeurs par défaut
        config['correction'] = {
            'similarity_threshold': 0.7,
            'ast_analysis_enabled': True,
            'fuzzy_search_enabled': True,
            'context_window': 5,
            'prefer_ast_detection': True
        }
        
        config['output'] = {
            'preserve_original': True,
            'generate_backup': True,
            'report_format': 'yaml'
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
    
    def _modify_existing_config(self) -> bool:
        """Modifie une configuration existante"""
        print(f"\n{Colors.YELLOW}📝 MODIFICATION DE CONFIGURATION EXISTANTE{Colors.END}")
        
        # Trouver les configurations existantes
        existing_configs = []
        for config_path in [
            self.user_config_dir / "config.yaml",
            self.user_config_dir / "smart-patch.yaml",
            Path.cwd() / "smart_patch_config.yaml"
        ]:
            if config_path.exists():
                existing_configs.append(config_path)
        
        if not existing_configs:
            print("❌ Aucune configuration existante trouvée")
            return self._detailed_config()
        
        # Sélection du fichier à modifier
        if len(existing_configs) == 1:
            selected_config = existing_configs[0]
            print(f"📄 Configuration sélectionnée: {selected_config}")
        else:
            print("Configurations disponibles :")
            for i, config_path in enumerate(existing_configs, 1):
                print(f"{i}. {config_path}")
            
            choice = self._get_choice("Configuration à modifier", 
                                    [str(i) for i in range(1, len(existing_configs) + 1)], '1')
            selected_config = existing_configs[int(choice) - 1]
        
        # Charger la configuration existante
        try:
            with open(selected_config, 'r', encoding='utf-8') as f:
                current_config = yaml.safe_load(f)
            
            print(f"✅ Configuration chargée: {selected_config}")
            
            # Modifications interactives
            modified_config = self._interactive_modify_config(current_config)
            
            # Sauvegarder
            return self._save_config(modified_config, 
                                   output_path=selected_config,
                                   backup_original=True)
            
        except Exception as e:
            print(f"❌ Erreur chargement configuration: {e}")
            return False
    
    def _interactive_modify_config(self, config: Dict) -> Dict:
        """Modification interactive d'une configuration"""
        print(f"\n{Colors.CYAN}🔧 Sections modifiables:{Colors.END}")
        
        sections = list(config.keys())
        for i, section in enumerate(sections, 1):
            print(f"{i:2d}. {section}")
        
        while True:
            choice = input(f"\nSection à modifier (1-{len(sections)}, 'done' pour terminer): ").strip()
            
            if choice.lower() in ['done', 'fini', 'q', 'quit']:
                break
            
            try:
                section_idx = int(choice) - 1
                if 0 <= section_idx < len(sections):
                    section_name = sections[section_idx]
                    print(f"\n📝 Modification de la section '{section_name}':")
                    config[section_name] = self._modify_section(section_name, config[section_name])
                else:
                    print("❌ Numéro invalide")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
        
        return config
    
    def _modify_section(self, section_name: str, section_config: Dict) -> Dict:
        """Modifie une section spécifique"""
        print(f"Configuration actuelle de '{section_name}':")
        self._print_config_section(section_config, indent=2)
        
        if section_name == 'detection':
            return self._configure_detection(current=section_config)
        elif section_name == 'security':
            return self._configure_security(current=section_config)
        elif section_name == 'guided_patching':
            return self._configure_guided_patching(current=section_config)
        elif section_name == 'logging':
            return self._configure_logging(current=section_config)
        elif section_name == 'performance':
            return self._configure_performance(current=section_config)
        else:
            # Section générique
            return self._configure_generic_section(section_config)
    
    def _print_config_section(self, config: Dict, indent: int = 0):
        """Affiche une section de configuration"""
        for key, value in config.items():
            spaces = "  " * indent
            if isinstance(value, dict):
                print(f"{spaces}{key}:")
                self._print_config_section(value, indent + 1)
            elif isinstance(value, list):
                print(f"{spaces}{key}: [{', '.join(map(str, value))}]")
            else:
                print(f"{spaces}{key}: {value}")
    
    def _configure_detection(self, current: Dict = None) -> Dict:
        """Configure la détection - VERSION CORRIGÉE"""
        # FIX: S'assurer que current est un dict valide
        if current is None:
            current = {}
        
        config = current.copy() if current else {}
        
        print("Extensions de fichiers :")
        print("1. Python (.py)")
        print("2. Web (.js, .ts, .html, .css)")
        print("3. Système (.php, .java, .cpp)")
        print("4. Personnalisé")
        print("5. Garder actuel" if current else "5. Tous les langages")
        
        ext_choice = self._get_choice("Extensions", ['1', '2', '3', '4', '5'], '5' if current else '1')
        
        if ext_choice == '1':
            config['file_extensions'] = ['.py', '.pyi']
        elif ext_choice == '2':
            config['file_extensions'] = ['.js', '.ts', '.jsx', '.tsx', '.html', '.css']
        elif ext_choice == '3':
            config['file_extensions'] = ['.php', '.java', '.cpp', '.c', '.h']
        elif ext_choice == '4':
            exts = input("Extensions (séparées par virgules): ").strip()
            config['file_extensions'] = [e.strip() for e in exts.split(',') if e.strip()]
        elif ext_choice == '5' and not current:
            config['file_extensions'] = ['.py', '.js', '.ts', '.php', '.java', '.cpp', '.c', '.go', '.rs']
        
        if ext_choice != '5' or not current:
            config['search_radius'] = self._get_number("Rayon de recherche", 1, 10, 
                                                     current.get('search_radius', 3) if current else 3)
            config['max_search_depth'] = self._get_number("Profondeur max", 1, 10, 
                                                        current.get('max_search_depth', 3) if current else 3)
            config['enable_content_based_detection'] = self._get_yes_no("Détection basée sur le contenu", 
                                                                       current.get('enable_content_based_detection', True) if current else True)
        
        return config
    
    def _configure_security(self, current: Dict = None) -> Dict:
        """Configure la sécurité - VERSION CORRIGÉE"""
        # FIX: S'assurer que current est un dict valide
        if current is None:
            current = {}
            
        config = current.copy() if current else {}
        
        print("Niveau de sécurité :")
        print("1. 🔓 Minimal")
        print("2. ⚖️  Équilibré")
        print("3. 🔒 Élevé")
        print("4. 🎯 Personnalisé")
        print("5. Garder actuel" if current else "")
        
        choices = ['1', '2', '3', '4'] + (['5'] if current else [])
        security_level = self._get_choice("Sécurité", choices, '5' if current else '2')
        
        if security_level == '1':
            config.update({
                'scan_dangerous_patterns': False,
                'allow_system_calls': True,
                'max_file_size_mb': 100,
                'require_confirmation_for_large_patches': False
            })
        elif security_level == '2':
            config.update({
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 10,
                'require_confirmation_for_large_patches': True
            })
        elif security_level == '3':
            config.update({
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 5,
                'require_confirmation_for_large_patches': True,
                'validate_patch_integrity': True,
                'log_security_events': True
            })
        elif security_level == '4':
            config['scan_dangerous_patterns'] = self._get_yes_no("Scanner les patterns dangereux", 
                                                              current.get('scan_dangerous_patterns', True) if current else True)
            config['allow_system_calls'] = self._get_yes_no("Autoriser les appels système", 
                                                          current.get('allow_system_calls', False) if current else False)
            config['max_file_size_mb'] = self._get_number("Taille max fichier (MB)", 1, 1000, 
                                                        current.get('max_file_size_mb', 10) if current else 10)
        
        return config
    
    def _configure_guided_patching(self, current: Dict = None) -> Dict:
        """Configure le patchage guidé - VERSION CORRIGÉE"""
        # FIX: S'assurer que current est un dict valide
        if current is None:
            current = {}
            
        config = current.copy() if current else {}
        
        config['enabled'] = self._get_yes_no("Activer le mode guidé par défaut", 
                                           current.get('enabled', True) if current else True)
        
        if config['enabled']:
            config['preview_enabled'] = self._get_yes_no("Activer les previews", 
                                                       current.get('preview_enabled', True) if current else True)
            config['interactive_mode'] = self._get_yes_no("Mode interactif", 
                                                        current.get('interactive_mode', True) if current else True)
            config['confirmation_required'] = self._get_yes_no("Confirmations requises", 
                                                             current.get('confirmation_required', True) if current else True)
            config['auto_backup'] = self._get_yes_no("Backup automatique", 
                                                   current.get('auto_backup', True) if current else True)
            
            if config['auto_backup']:
                backup_dir = input("Dossier de backup (vide pour défaut): ").strip()
                if backup_dir:
                    config['backup_directory'] = backup_dir
            
            config['modify_original'] = self._get_yes_no("Modifier les originaux", 
                                                       current.get('modify_original', True) if current else True)
            config['show_diff_preview'] = self._get_yes_no("Afficher les diffs", 
                                                         current.get('show_diff_preview', True) if current else True)
            config['context_lines'] = self._get_number("Lignes de contexte", 1, 20, 
                                                     current.get('context_lines', 3) if current else 3)
        
        return config
    
    def _configure_logging(self, current: Dict = None) -> Dict:
        """Configure le logging - VERSION CORRIGÉE"""
        # FIX: S'assurer que current est un dict valide
        if current is None:
            current = {}
            
        config = current.copy() if current else {}
        
        print("Niveau de logging :")
        print("1. DEBUG (très détaillé)")
        print("2. INFO (informatif)")
        print("3. WARNING (avertissements)")
        print("4. ERROR (erreurs seulement)")
        
        level_choice = self._get_choice("Niveau", ['1', '2', '3', '4'], 
                                      '2' if not current else str(['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(current.get('level', 'INFO')) + 1))
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        config['level'] = levels[int(level_choice) - 1]
        config['console_level'] = self._get_choice("Niveau console", ['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                                                 current.get('console_level', 'WARNING') if current else 'WARNING')
        
        log_file = self._get_yes_no("Enregistrer dans un fichier", 
                                   bool(current.get('file')) if current else False)
        if log_file:
            filename = input(f"Nom du fichier ({current.get('file', 'smart_patch.log')}): ").strip()
            config['file'] = filename or current.get('file', 'smart_patch.log')
        else:
            config['file'] = None
        
        return config
    
    def _configure_performance(self, current: Dict = None) -> Dict:
        """Configure les performances - VERSION CORRIGÉE"""
        # FIX: S'assurer que current est un dict valide
        if current is None:
            current = {}
            
        config = current.copy() if current else {}
        
        config['max_concurrent_patches'] = self._get_number("Patches simultanés", 1, 10, 
                                                          current.get('max_concurrent_patches', 2) if current else 2)
        config['enable_cache'] = self._get_yes_no("Activer le cache", 
                                                current.get('enable_cache', True) if current else True)
        config['enable_streaming'] = self._get_yes_no("Activer le streaming", 
                                                    current.get('enable_streaming', True) if current else True)
        
        if config['enable_streaming']:
            config['streaming_threshold_mb'] = self._get_number("Seuil streaming (MB)", 1, 1000, 
                                                              current.get('streaming_threshold_mb', 50) if current else 50)
        
        return config
    
    def _configure_generic_section(self, section_config: Dict) -> Dict:
        """Configuration générique pour sections inconnues"""
        print("Modification générique de section:")
        print("1. Garder tel quel")
        print("2. Réinitialiser aux valeurs par défaut")
        
        choice = self._get_choice("Action", ['1', '2'], '1')
        
        if choice == '2':
            return {}
        
        return section_config
    
    def _get_beginner_config(self) -> Dict:
        """Configuration débutant"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.php', '.java'],
                'search_radius': 3,
                'max_search_depth': 2,
                'enable_content_based_detection': True,
                'enable_filename_similarity': True
            },
            'correction': {
                'similarity_threshold': 0.8,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 7,
                'prefer_ast_detection': True,
                'auto_fix_line_numbers': True
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 5,
                'require_confirmation_for_large_patches': True,
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
                'modify_original': True,
                'show_diff_preview': True,
                'context_lines': 5,
                'backup_retention_days': 30
            },
            'output': {
                'preserve_original': True,
                'generate_backup': True,
                'report_format': 'yaml',
                'create_diff_reports': True,
                'include_statistics': True
            },
            'logging': {
                'level': 'INFO',
                'console_level': 'WARNING',
                'file': None
            },
            'performance': {
                'max_concurrent_patches': 1,
                'enable_cache': True,
                'enable_streaming': True,
                'streaming_threshold_mb': 25
            },
            'rollback': {
                'enabled': True,
                'auto_restore_on_failure': True
            },
            'wizard': {
                'enabled': True,
                'explain_steps': True,
                'show_examples': True,
                'safety_prompts': True,
                'learning_mode': True
            }
        }
    
    def _get_developer_config(self) -> Dict:
        """Configuration développeur"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.java', '.cpp', '.go', '.rs'],
                'search_radius': 3,
                'max_search_depth': 3,
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
                'allow_system_calls': True,
                'max_file_size_mb': 20,
                'require_confirmation_for_large_patches': False,
                'validate_patch_integrity': True
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
                'report_format': 'yaml',
                'create_diff_reports': True,
                'include_statistics': True
            },
            'logging': {
                'level': 'WARNING',
                'console_level': 'ERROR',
                'file': None
            },
            'performance': {
                'max_concurrent_patches': 3,
                'enable_cache': True,
                'enable_streaming': True,
                'streaming_threshold_mb': 50
            },
            'git': {
                'enabled': True,
                'auto_detect_repo': True,
                'create_branch': False
            }
        }
    
    def _get_production_config(self) -> Dict:
        """Configuration production"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.ts', '.php', '.java'],
                'search_radius': 2,
                'max_search_depth': 2,
                'enable_content_based_detection': True,
                'enable_filename_similarity': False
            },
            'correction': {
                'similarity_threshold': 0.85,
                'ast_analysis_enabled': True,
                'fuzzy_search_enabled': True,
                'context_window': 10,
                'prefer_ast_detection': True,
                'auto_fix_line_numbers': True,
                'max_correction_attempts': 2
            },
            'security': {
                'scan_dangerous_patterns': True,
                'allow_system_calls': False,
                'max_file_size_mb': 50,
                'require_confirmation_for_large_patches': True,
                'validate_patch_integrity': True,
                'log_security_events': True
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
                'report_format': 'yaml',
                'create_diff_reports': True,
                'timestamp_files': True,
                'include_statistics': True
            },
            'logging': {
                'level': 'INFO',
                'console_level': 'WARNING',
                'file': 'smart_patch_production.log',
                'max_file_size_mb': 50,
                'backup_count': 10
            },
            'performance': {
                'max_concurrent_patches': 4,
                'memory_limit_mb': 1024,
                'enable_streaming': True,
                'enable_cache': True,
                'streaming_threshold_mb': 100
            },
            'rollback': {
                'enabled': True,
                'auto_restore_on_failure': True,
                'max_rollback_history': 200
            }
        }
    
    def _get_minimal_config(self) -> Dict:
        """Configuration minimaliste"""
        return {
            'detection': {
                'file_extensions': ['.py', '.js', '.php'],
                'search_radius': 2,
                'max_search_depth': 2
            },
            'correction': {
                'similarity_threshold': 0.7,
                'ast_analysis_enabled': False,
                'fuzzy_search_enabled': True,
                'context_window': 3
            },
            'security': {
                'scan_dangerous_patterns': False,
                'allow_system_calls': True,
                'max_file_size_mb': 50
            },
            'guided_patching': {
                'enabled': False,
                'auto_backup': False
            },
            'output': {
                'preserve_original': False,
                'generate_backup': False,
                'report_format': 'yaml'
            },
            'logging': {
                'level': 'WARNING',
                'console_level': 'ERROR'
            },
            'performance': {
                'max_concurrent_patches': 1,
                'enable_cache': False,
                'enable_streaming': False
            }
        }
    
    def _get_expert_config(self) -> Dict:
        """Configuration expert complète"""
        print("🎯 Configuration expert - toutes les options disponibles")
        
        config = {
            'detection': {
                'search_patterns': [
                    r"---\s+(.+)",
                    r"\+\+\+\s+(.+)",
                    r"Index:\s+(.+)",
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
                'report_format': 'yaml',
                'create_diff_reports': True,
                'include_statistics': True,
                'timestamp_files': True
            },
            'logging': {
                'level': 'DEBUG',
                'console_level': 'INFO',
                'file': 'smart_patch_expert.log',
                'max_file_size_mb': 20,
                'backup_count': 5
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
                'create_branch': True,
                'auto_commit': False
            },
            'wizard': {
                'enabled': True,
                'auto_detect_beginners': True,
                'explain_steps': True,
                'show_examples': True,
                'safety_prompts': True,
                'learning_mode': True
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
    
    def _save_config(self, config: Dict, profile_name: str = None, 
                    output_path: Path = None, backup_original: bool = False) -> bool:
        """Sauvegarde la configuration"""
        try:
            # Déterminer le chemin de sortie
            if output_path:
                config_path = output_path
            else:
                config_path = self._get_output_path(profile_name)
            
            # Créer une sauvegarde si demandé
            if backup_original and config_path.exists():
                backup_path = config_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
                config_path.rename(backup_path)
                print(f"💾 Sauvegarde créée: {backup_path}")
            
            # Ajouter métadonnées
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_config = {
                '_metadata': {
                    'generated_by': 'Smart Patch Processor Advanced Config Generator',
                    'version': '2.0',
                    'created_at': timestamp,
                    'profile': profile_name or 'custom',
                    'format': 'yaml',
                    'platform': sys.platform
                },
                '_description': 'Configuration générée automatiquement pour Smart Patch Processor v2.0',
                '_usage': {
                    'command_line': f'smart-patch --config {config_path.name}',
                    'guided_mode': f'smart-patch --guided --config {config_path.name}',
                    'wizard_mode': 'smart-patch --wizard'
                }
            }
            full_config.update(config)
            
            # S'assurer que le répertoire existe
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder en YAML
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(full_config, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False, indent=2)
            
            print(f"\n{Colors.GREEN}✅ Configuration sauvegardée: {config_path}{Colors.END}")
            
            # Affichage des informations d'utilisation
            self._show_usage_info(config_path, profile_name)
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur sauvegarde: {e}{Colors.END}")
            return False
    
    def _get_output_path(self, profile_name: str = None) -> Path:
        """Détermine le chemin de sortie pour la configuration"""
        print(f"\n{Colors.CYAN}📁 Choix de l'emplacement:{Colors.END}")
        print("1. 🏠 Configuration utilisateur (~/.config/smart-patch/config.yaml)")
        print("2. 📁 Répertoire courant (smart_patch_config.yaml)")
        print("3. 🎯 Chemin personnalisé")
        
        location_choice = self._get_choice("Emplacement", ['1', '2', '3'], '1')
        
        if location_choice == '1':
            # S'assurer que le répertoire existe
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            return self.user_config_dir / "config.yaml"
        elif location_choice == '2':
            profile_suffix = f"_{profile_name}" if profile_name and profile_name != 'custom' else ""
            return Path.cwd() / f"smart_patch_config{profile_suffix}.yaml"
        else:
            while True:
                custom_path = input("Chemin du fichier de configuration: ").strip()
                if custom_path:
                    path = Path(custom_path)
                    if not path.suffix:
                        path = path.with_suffix('.yaml')
                    return path
                print("❌ Veuillez spécifier un chemin valide")
    
    def _show_usage_info(self, config_path: Path, profile_name: str = None):
        """Affiche les informations d'utilisation"""
        print()
        print(f"{Colors.BOLD}🚀 Utilisation:{Colors.END}")
        print(f"   smart-patch --config {config_path}")
        print(f"   smart-patch --guided --config {config_path}")
        
        if config_path.parent == self.user_config_dir:
            print(f"\n{Colors.GREEN}💡 Configuration utilisateur installée !{Colors.END}")
            print("   Cette configuration sera utilisée automatiquement")
            print("   Commandes simplifiées:")
            print("   • smart-patch --guided patches/ output/")
            print("   • smart-patch --wizard")
        
        print(f"\n{Colors.BOLD}🔧 Test de la configuration:{Colors.END}")
        print(f"   smart-patch --config {config_path} --help")
        
        if profile_name:
            profile_descriptions = {
                '1': 'débutant (sécurité maximale)',
                '2': 'développeur (équilibré)',
                '3': 'production (robuste)',
                '4': 'minimaliste (léger)'
            }
            desc = profile_descriptions.get(profile_name, 'personnalisé')
            print(f"\n{Colors.BLUE}📋 Profil: {desc}{Colors.END}")
    
    # Méthodes utilitaires
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
def run_config_generator_advanced():
    """Point d'entrée pour le générateur avancé"""
    generator = AdvancedConfigGenerator()
    return generator.run()

def run_config_generator_advanced():
    """Point d'entrée pour le générateur avancé"""
    generator = AdvancedConfigGenerator()
    return generator.run()
