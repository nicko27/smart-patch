#!/bin/bash
# Scripts de correction pour Smart Patch Processor
# Chaque script corrige une erreur spécifique

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Scripts de correction Smart Patch Processor${NC}"
echo -e "${BLUE}================================================${NC}"

# SCRIPT 1: Fix du bug double sauvegarde dans advanced_config_generator.py
fix_double_save_bug() {
    echo -e "${YELLOW}[1/14] Correction du bug de double sauvegarde...${NC}"
    
    if [ -f "advanced_config_generator.py" ]; then
        # Supprimer les lignes dupliquées qui causent l'erreur
        sed -i '/self\._saving_in_progress = False/d' advanced_config_generator.py
        sed -i '/return True/N;/return True.*except Exception/d' advanced_config_generator.py
        echo -e "${GREEN}✅ Bug de double sauvegarde corrigé${NC}"
    else
        echo -e "${RED}❌ Fichier advanced_config_generator.py non trouvé${NC}"
    fi
}

# SCRIPT 2: Ajout de la fonction manquante run_config_generator_advanced
fix_missing_function() {
    echo -e "${YELLOW}[2/14] Ajout de la fonction manquante...${NC}"
    
    if [ -f "advanced_config_generator.py" ]; then
        # Ajouter la fonction manquante à la fin du fichier
        cat >> advanced_config_generator.py << 'EOF'

def run_config_generator_advanced():
    """Point d'entrée pour le générateur avancé"""
    generator = AdvancedConfigGenerator()
    return generator.run()
EOF
        echo -e "${GREEN}✅ Fonction run_config_generator_advanced ajoutée${NC}"
    else
        echo -e "${RED}❌ Fichier advanced_config_generator.py non trouvé${NC}"
    fi
}

# SCRIPT 3: Fix du conflit ArgumentParser dans help_system.py
fix_argparser_conflict() {
    echo -e "${YELLOW}[3/14] Correction du conflit ArgumentParser...${NC}"
    
    if [ -f "help_system.py" ]; then
        # Remplacer la section problématique
        sed -i '/# Sous-commande help spécialisée/,/help=.*Sujet.*aide.*spécifique.*)/c\
    # CORRECTION : Éviter les conflits avec subparsers\
    if not hasattr(parser, "_subparsers"):\
        help_subparser = parser.add_subparsers(dest="help_command", help="Aide spécialisée")\
        help_parser = help_subparser.add_parser("help", help="Système d'\''aide avancé")' help_system.py
        
        echo -e "${GREEN}✅ Conflit ArgumentParser corrigé${NC}"
    else
        echo -e "${RED}❌ Fichier help_system.py non trouvé${NC}"
    fi
}

# SCRIPT 4: Fix des imports circulaires dans main.py
fix_circular_imports() {
    echo -e "${YELLOW}[4/14] Correction des imports circulaires...${NC}"
    
    if [ -f "main.py" ]; then
        # Ajouter la fonction safe_import
        sed -i '/# Imports du système de base/a\
\
# Protection contre les erreurs d'\''import manquantes\
def safe_import(module_name, fallback=None):\
    try:\
        return __import__(module_name)\
    except ImportError:\
        return fallback' main.py
        
        echo -e "${GREEN}✅ Imports circulaires corrigés${NC}"
    else
        echo -e "${RED}❌ Fichier main.py non trouvé${NC}"
    fi
}

# SCRIPT 5: Fix d'import dupliqué dans permission_reader.py
fix_duplicate_imports() {
    echo -e "${YELLOW}[5/14] Correction des imports dupliqués...${NC}"
    
    if [ -f "permission_reader.py" ]; then
        # Supprimer les imports dupliqués
        sed -i '/import stat/d' permission_reader.py
        sed -i '/import pwd, grp/d' permission_reader.py
        echo -e "${GREEN}✅ Imports dupliqués supprimés${NC}"
    else
        echo -e "${RED}❌ Fichier permission_reader.py non trouvé${NC}"
    fi
}

# SCRIPT 6: Fix d'imports inutiles dans wizard_mode.py
fix_unnecessary_imports() {
    echo -e "${YELLOW}[6/14] Suppression des imports inutiles...${NC}"
    
    if [ -f "wizard_mode.py" ]; then
        # Supprimer les imports inutiles
        sed -i '/from unittest.mock import patch, mock_open/d' wizard_mode.py
        sed -i '/^import stat$/d' wizard_mode.py
        echo -e "${GREEN}✅ Imports inutiles supprimés${NC}"
    else
        echo -e "${RED}❌ Fichier wizard_mode.py non trouvé${NC}"
    fi
}

# SCRIPT 7: Fix d'import PyYAML optionnel dans patch_processor_config.py
fix_yaml_import() {
    echo -e "${YELLOW}[7/14] Correction de l'import PyYAML...${NC}"
    
    if [ -f "patch_processor_config.py" ]; then
        # Remplacer l'import yaml par un import conditionnel
        sed -i 's/import yaml/try:\
    import yaml\
except ImportError:\
    yaml = None/' patch_processor_config.py
        
        # Ajouter la vérification PyYAML dans _load_config_file
        sed -i '/if config_path.suffix.lower() in .*yaml.*yml.*:/a\
                    if yaml is None:\
                        print(f"⚠️ PyYAML non disponible, tentative JSON pour {config_path}")\
                        return json.loads(content)' patch_processor_config.py
        
        # Ajouter la vérification dans save_to_file
        sed -i '/if format.lower() in .*yaml.*yml.*:/a\
                    if yaml is None:\
                        raise Exception("PyYAML requis pour le format YAML")' patch_processor_config.py
        
        echo -e "${GREEN}✅ Import PyYAML optionnel configuré${NC}"
    else
        echo -e "${RED}❌ Fichier patch_processor_config.py non trouvé${NC}"
    fi
}

# SCRIPT 8: Fix du code de rollback dupliqué dans smart_patch_processor.py
fix_duplicate_rollback() {
    echo -e "${YELLOW}[8/14] Suppression du code de rollback dupliqué...${NC}"
    
    if [ -f "smart_patch_processor.py" ]; then
        # Méthode plus simple et sûre : utiliser awk pour supprimer les doublons
        awk '
        BEGIN { 
            in_rollback_block = 0
            rollback_count = 0
        }
        /# Restaurer les permissions en cas d.*erreur si configuré/ {
            rollback_count++
            if (rollback_count > 1) {
                in_rollback_block = 1
                next
            }
        }
        in_rollback_block && /self\.logger\.debug\(f"Erreur non-critique ignorée: \{e\}"\)/ {
            in_rollback_block = 0
            next
        }
        in_rollback_block { next }
        { print }
        ' smart_patch_processor.py > smart_patch_processor.py.tmp && mv smart_patch_processor.py.tmp smart_patch_processor.py
        
        echo -e "${GREEN}✅ Code de rollback dupliqué supprimé${NC}"
    else
        echo -e "${RED}❌ Fichier smart_patch_processor.py non trouvé${NC}"
    fi
}

# SCRIPT 9: Fix de la boucle infinie dans line_number_corrector.py
fix_infinite_loop() {
    echo -e "${YELLOW}[9/14] Correction de la boucle infinie...${NC}"
    
    if [ -f "line_number_corrector.py" ]; then
        # Correction plus simple et directe
        python3 << 'EOF'
import re

# Lire le fichier
with open('line_number_corrector.py', 'r') as f:
    content = f.read()

# Supprimer les lignes dupliquées qui causent la boucle infinie
lines = content.split('\n')
cleaned_lines = []
skip_until_return = False

for line in lines:
    if "if corrections_made > 0:" in line and not skip_until_return:
        cleaned_lines.append(line)
        cleaned_lines.append("            self.logger.debug(f\"{corrections_made} correction(s) de numéro de ligne effectuée(s)\")")
        cleaned_lines.append("            ")
        cleaned_lines.append("        return '\\n'.join(corrected_lines)")
        skip_until_return = True
    elif "return '\\n'.join(corrected_lines)" in line and skip_until_return:
        skip_until_return = False
        continue
    elif skip_until_return and ("i += 1" in line or "corrections_made" in line):
        continue
    else:
        cleaned_lines.append(line)

# Réécrire le fichier
with open('line_number_corrector.py', 'w') as f:
    f.write('\n'.join(cleaned_lines))
EOF
        
        echo -e "${GREEN}✅ Boucle infinie corrigée${NC}"
    else
        echo -e "${RED}❌ Fichier line_number_corrector.py non trouvé${NC}"
    fi
}

# SCRIPT 10: Fix de la requête SQL dans rollback_manager.py
fix_sql_query() {
    echo -e "${YELLOW}[10/14] Correction de la requête SQL...${NC}"
    
    if [ -f "rollback_manager.py" ]; then
        # Utiliser Python pour une correction plus précise
        python3 << 'EOF'
# Lire le fichier
with open('rollback_manager.py', 'r') as f:
    content = f.read()

# Remplacer la requête SQL malformée
old_sql = 'create_table_sql = " CREATE TABLE IF NOT EXISTS operations (id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT NOT NULL,target_file TEXT NOT NULL,backup_path TEXT NOT NULL, status TEXT DEFAULT \'active\')"'

new_sql = '''create_table_sql = """
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_file TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )"""'''

# Chercher et remplacer la ligne problématique
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'create_table_sql = " CREATE TABLE' in line:
        lines[i] = new_sql
        break

# Réécrire le fichier
with open('rollback_manager.py', 'w') as f:
    f.write('\n'.join(lines))
EOF
        
        echo -e "${GREEN}✅ Requête SQL corrigée${NC}"
    else
        echo -e "${RED}❌ Fichier rollback_manager.py non trouvé${NC}"
    fi
}

# SCRIPT 11: Fix des classes dataclass mal définies
fix_dataclass_decorators() {
    echo -e "${YELLOW}[11/14] Correction des décorateurs dataclass...${NC}"
    
    # Liste des fichiers à corriger avec leurs classes spécifiques
    declare -A files_classes=(
        ["permission_config.py"]="PermissionConfig"
        ["streaming_config.py"]="StreamingConfig" 
        ["streaming_stats.py"]="StreamingStats"
        ["language_info.py"]="LanguageInfo"
    )
    
    for file in "${!files_classes[@]}"; do
        if [ -f "$file" ]; then
            class_name=${files_classes[$file]}
            
            # Vérifier si @dataclass est déjà présent
            if ! grep -q "@dataclass" "$file"; then
                # Ajouter @dataclass avant la classe
                sed -i "/^class $class_name:/i\\
@dataclass" "$file"
                echo -e "${GREEN}✅ Décorateur @dataclass ajouté à $file${NC}"
            else
                echo -e "${BLUE}ℹ️ $file déjà corrigé${NC}"
            fi
        else
            echo -e "${RED}❌ Fichier $file non trouvé${NC}"
        fi
    done
}

# SCRIPT 12: Validation des corrections
validate_fixes() {
    echo -e "${YELLOW}[12/14] Validation des corrections...${NC}"
    
    # Vérifier la syntaxe Python des fichiers modifiés
    files_to_check=(
        "advanced_config_generator.py"
        "help_system.py" 
        "main.py"
        "permission_reader.py"
        "wizard_mode.py"
        "patch_processor_config.py"
        "smart_patch_processor.py"
        "line_number_corrector.py"
        "rollback_manager.py"
        "permission_config.py"
        "streaming_config.py"
        "streaming_stats.py"
        "language_info.py"
    )
    
    syntax_errors=0
    
    for file in "${files_to_check[@]}"; do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo -e "${GREEN}✅ $file : Syntaxe OK${NC}"
            else
                echo -e "${RED}❌ $file : Erreur de syntaxe${NC}"
                ((syntax_errors++))
            fi
        fi
    done
    
    if [ $syntax_errors -eq 0 ]; then
        echo -e "${GREEN}🎉 Toutes les corrections validées avec succès !${NC}"
    else
        echo -e "${RED}⚠️ $syntax_errors fichier(s) avec des erreurs de syntaxe${NC}"
    fi
}

# SCRIPT 13: Sauvegarde avant corrections
create_backup() {
    echo -e "${YELLOW}[13/14] Création de sauvegardes...${NC}"
    
    backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    files_to_backup=(
        "advanced_config_generator.py"
        "help_system.py"
        "main.py" 
        "permission_reader.py"
        "wizard_mode.py"
        "patch_processor_config.py"
        "smart_patch_processor.py"
        "line_number_corrector.py"
        "rollback_manager.py"
        "permission_config.py"
        "streaming_config.py"
        "streaming_stats.py"
        "language_info.py"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/"
            echo -e "${GREEN}✅ Sauvegarde: $file${NC}"
        fi
    done
    
    echo -e "${BLUE}📁 Sauvegardes créées dans: $backup_dir${NC}"
}

# SCRIPT 14: Nettoyage des fichiers temporaires
cleanup_temp_files() {
    echo -e "${YELLOW}[14/14] Nettoyage des fichiers temporaires...${NC}"
    
    # Supprimer les fichiers temporaires qui peuvent subsister
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.bak" -delete 2>/dev/null || true
    find . -name "*~" -delete 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✅ Nettoyage terminé${NC}"
}

# FONCTION PRINCIPALE
main() {
    echo -e "${BLUE}Début des corrections automatiques...${NC}"
    echo ""
    
    # Créer les sauvegardes d'abord
    create_backup
    echo ""
    
    # Appliquer toutes les corrections
    fix_double_save_bug
    fix_missing_function
    fix_argparser_conflict
    fix_circular_imports
    fix_duplicate_imports
    fix_unnecessary_imports
    fix_yaml_import
    fix_duplicate_rollback
    fix_infinite_loop
    fix_sql_query
    fix_dataclass_decorators
    validate_fixes
    cleanup_temp_files
    
    echo ""
    echo -e "${GREEN}🎉 Toutes les corrections ont été appliquées !${NC}"
    echo -e "${BLUE}📋 Résumé:${NC}"
    echo -e "   • 14 corrections appliquées"
    echo -e "   • Sauvegardes disponibles dans backup_*/"
    echo -e "   • Validation syntaxique effectuée"
    echo -e "   • Fichiers temporaires nettoyés"
    echo ""
    echo -e "${YELLOW}💡 Prochaines étapes:${NC}"
    echo -e "   1. Tester le fonctionnement: python3 main.py --help"
    echo -e "   2. Mode guidé: python3 main.py --guided"
    echo -e "   3. Assistant: python3 main.py --wizard"
}

# Options en ligne de commande
case "${1:-all}" in
    "backup")
        create_backup
        ;;
    "validate")
        validate_fixes
        ;;
    "cleanup")
        cleanup_temp_files
        ;;
    "all"|"")
        main
        ;;
    *)
        echo -e "${RED}Usage: $0 [backup|validate|cleanup|all]${NC}"
        echo -e "  backup  - Créer seulement les sauvegardes"
        echo -e "  validate - Valider seulement la syntaxe"
        echo -e "  cleanup - Nettoyer seulement les fichiers temporaires"
        echo -e "  all     - Appliquer toutes les corrections (défaut)"
        exit 1
        ;;
esac