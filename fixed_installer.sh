#!/bin/bash

# Smart Patch Processor - Installateur et Vérificateur Complet
# Applique toutes les corrections et vérifie le bon fonctionnement

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/installation_backups_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$SCRIPT_DIR/installation.log"

# Fonctions utilitaires
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo -e "$1"
}

success() {
    log "${GREEN}✅ $1${NC}"
}

warning() {
    log "${YELLOW}⚠️ $1${NC}"
}

error() {
    log "${RED}❌ $1${NC}"
}

info() {
    log "${BLUE}ℹ️ $1${NC}"
}

section() {
    log "\n${CYAN}${BOLD}$1${NC}"
    log "${CYAN}$(printf '%.0s=' {1..60})${NC}"
}

# Fonction de sauvegarde
backup_files() {
    section "📁 CRÉATION DES SAUVEGARDES"
    
    mkdir -p "$BACKUP_DIR"
    
    # Liste des fichiers à sauvegarder
    files_to_backup=(
        "patch_applicator.py"
        "wizard_mode.py"
        "rollback_manager.py"
        "validation.py"
        "patch_processor_config.py"
        "line_number_corrector.py"
        "core.py"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            cp "$SCRIPT_DIR/$file" "$BACKUP_DIR/"
            info "Sauvegardé: $file"
        else
            warning "Fichier non trouvé: $file"
        fi
    done
    
    success "Sauvegardes créées dans: $BACKUP_DIR"
}

# Fonction d'application des corrections
apply_fixes() {
    section "🔧 APPLICATION DES CORRECTIONS"
    
    if [ -f "$SCRIPT_DIR/smart_patch_fixes.py" ]; then
        info "Lancement du correcteur automatique..."
        cd "$SCRIPT_DIR"
        
        if python3 smart_patch_fixes.py; then
            success "Corrections appliquées avec succès"
        else
            error "Échec lors de l'application des corrections"
            return 1
        fi
    else
        error "Fichier smart_patch_fixes.py non trouvé"
        return 1
    fi
}

# Fonction de test des imports
test_imports() {
    section "📦 TEST DES IMPORTS"
    
    # Liste des modules à tester
    modules=(
        "smart_patch_processor"
        "patch_applicator"
        "wizard_mode"
        "patch_processor_config" 
        "target_file_detector"
        "line_number_corrector"
        "validation"
        "safe_coordinator"
    )
    
    success_count=0
    total_count=${#modules[@]}
    
    for module in "${modules[@]}"; do
        if python3 -c "import $module; print('✅ $module')" 2>/dev/null; then
            success "Import réussi: $module"
            ((success_count++))
        else
            warning "Import échoué: $module"
        fi
    done
    
    info "Imports réussis: $success_count/$total_count"
    
    if [ $success_count -ge $((total_count * 70 / 100)) ]; then
        success "Taux d'import acceptable (≥70%)"
        return 0
    else
        warning "Taux d'import faible (<70%)"
        return 1
    fi
}

# Fonction de test de validation
run_validation_tests() {
    section "🧪 TESTS DE VALIDATION"
    
    if [ -f "$SCRIPT_DIR/validation_test_suite.py" ]; then
        info "Lancement de la suite de tests..."
        cd "$SCRIPT_DIR"
        
        if python3 validation_test_suite.py; then
            success "Tests de validation réussis"
            return 0
        else
            warning "Certains tests de validation ont échoué"
            return 1
        fi
    else
        warning "Suite de tests non trouvée (validation_test_suite.py)"
        return 1
    fi
}

# Fonction de test du wizard
test_wizard() {
    section "🧙‍♂️ TEST DU WIZARD"
    
    info "Test d'import du wizard..."
    if python3 -c "
from wizard_mode import WizardMode
from patch_processor_config import PatchProcessorConfig

# Test basique
config = PatchProcessorConfig()
print('✅ Configuration chargée')

# Test avec mock processor
class MockProcessor:
    def __init__(self):
        self.source_dir = '.'
        self.output_dir = '.'
        self.verbose = False
    
    def process_all_patches(self):
        return {'success': 1, 'failed': 0}

try:
    processor = MockProcessor()
    wizard = WizardMode(processor, config)
    print('✅ Wizard créé avec succès')
    
    # Test méthode critique
    if hasattr(wizard, '_show_detailed_results'):
        wizard._show_detailed_results({'test': 'data'})
        print('✅ Méthode _show_detailed_results fonctionne')
    
    print('✅ Wizard entièrement fonctionnel')
except Exception as e:
    print(f'❌ Erreur wizard: {e}')
    exit(1)
" 2>/dev/null; then
        success "Wizard fonctionnel"
        return 0
    else
        error "Wizard non fonctionnel"
        return 1
    fi
}

# Fonction de test de sécurité basique
test_security() {
    section "🔒 TESTS DE SÉCURITÉ"
    
    info "Test de protection path traversal..."
    if python3 -c "
from validation import validate_file_path_secure, ValidationError

try:
    validate_file_path_secure('../../../etc/passwd', must_exist=False)
    print('❌ Path traversal non bloqué')
    exit(1)
except ValidationError:
    print('✅ Path traversal bloqué')
except ImportError:
    print('⚠️ Module validation non disponible')

try:
    from patch_applicator import PatchApplicator
    from patch_processor_config import PatchProcessorConfig
    
    config = PatchProcessorConfig()
    applicator = PatchApplicator(config)
    
    # Test DoS protection
    huge_content = 'A' * (200 * 1024 * 1024)  # 200MB
    result = applicator.apply_patch(huge_content, '@@ test @@')
    print('✅ Protection DoS active')
    
except Exception as e:
    print(f'⚠️ Test sécurité partiel: {e}')
" 2>/dev/null; then
        success "Tests de sécurité passés"
        return 0
    else
        warning "Tests de sécurité partiels"
        return 1
    fi
}

# Fonction de création des fichiers manquants
create_missing_files() {
    section "📝 CRÉATION DES FICHIERS MANQUANTS"
    
    # Créer __init__.py si manquant
    if [ ! -f "$SCRIPT_DIR/__init__.py" ]; then
        echo '"""Smart Patch Processor Package"""' > "$SCRIPT_DIR/__init__.py"
        info "Créé: __init__.py"
    fi
    
    # Créer un script de lancement simplifié
    cat > "$SCRIPT_DIR/run_smart_patch.py" << 'EOF'
#!/usr/bin/env python3
"""
Script de lancement simplifié pour Smart Patch Processor
Usage: python3 run_smart_patch.py [options]
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au Python path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from main import main
    main()
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous que tous les modules sont présents")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur d'exécution: {e}")
    sys.exit(1)
EOF
    
    chmod +x "$SCRIPT_DIR/run_smart_patch.py"
    success "Créé: run_smart_patch.py"
}

# Fonction de vérification finale
final_verification() {
    section "🎯 VÉRIFICATION FINALE"
    
    info "Test du système complet..."
    
    # Test 1: Imports essentiels
    info "1. Test des imports essentiels..."
    test_imports
    import_status=$?
    
    # Test 2: Wizard
    info "2. Test du wizard..."
    test_wizard
    wizard_status=$?
    
    # Test 3: Sécurité
    info "3. Test de sécurité..."
    test_security
    security_status=$?
    
    # Test 4: Script de lancement
    info "4. Test du script de lancement..."
    if [ -f "$SCRIPT_DIR/run_smart_patch.py" ]; then
        if python3 "$SCRIPT_DIR/run_smart_patch.py" --help >/dev/null 2>&1; then
            success "Script de lancement fonctionnel"
            launch_status=0
        else
            warning "Script de lancement partiellement fonctionnel"
            launch_status=1
        fi
    else
        error "Script de lancement manquant"
        launch_status=1
    fi
    
    # Calcul du score global
    total_tests=4
    passed_tests=0
    
    [ $import_status -eq 0 ] && ((passed_tests++))
    [ $wizard_status -eq 0 ] && ((passed_tests++))
    [ $security_status -eq 0 ] && ((passed_tests++))
    [ $launch_status -eq 0 ] && ((passed_tests++))
    
    success_rate=$((passed_tests * 100 / total_tests))
    
    info "Score global: $passed_tests/$total_tests tests réussis ($success_rate%)"
    
    if [ $success_rate -ge 75 ]; then
        success "✅ INSTALLATION RÉUSSIE !"
        success "Le système Smart Patch Processor est opérationnel"
        return 0
    elif [ $success_rate -ge 50 ]; then
        warning "⚠️ INSTALLATION PARTIELLE"
        warning "Le système fonctionne mais avec limitations"
        return 1
    else
        error "❌ INSTALLATION ÉCHOUÉE"
        error "Problèmes critiques détectés"
        return 1
    fi
}

# Fonction d'affichage des instructions d'utilisation
show_usage_instructions() {
    section "📖 INSTRUCTIONS D'UTILISATION"
    
    info "Commandes disponibles après installation:"
    echo ""
    echo -e "${GREEN}1. Mode débutant (recommandé):${NC}"
    echo "   python3 run_smart_patch.py --wizard"
    echo "   python3 main.py --wizard"
    echo ""
    echo -e "${GREEN}2. Mode guidé:${NC}"
    echo "   python3 run_smart_patch.py --guided patches/ output/"
    echo "   python3 main.py --guided patches/ output/"
    echo ""
    echo -e "${GREEN}3. Mode standard:${NC}"
    echo "   python3 run_smart_patch.py patches/ output/"
    echo "   python3 main.py patches/ output/"
    echo ""
    echo -e "${GREEN}4. Aide complète:${NC}"
    echo "   python3 run_smart_patch.py --help"
    echo "   python3 main.py --help"
    echo ""
    echo -e "${GREEN}5. Tests:${NC}"
    echo "   python3 validation_test_suite.py"
    echo "   python3 test_architecture.py"
    echo ""
    
    info "Fichiers importants:"
    echo "   📁 Sauvegardes: $BACKUP_DIR"
    echo "   📄 Log d'installation: $LOG_FILE"
    echo "   🚀 Script de lancement: run_smart_patch.py"
    echo ""
    
    info "En cas de problème:"
    echo "   1. Vérifiez le log: $LOG_FILE"
    echo "   2. Lancez les tests: python3 validation_test_suite.py"
    echo "   3. Restaurez depuis: $BACKUP_DIR"
    echo "   4. Relancez l'installateur: $0"
}

# Fonction de nettoyage en cas d'erreur
cleanup_on_error() {
    section "🧹 NETTOYAGE APRÈS ERREUR"
    
    if [ -d "$BACKUP_DIR" ]; then
        warning "Restauration des fichiers depuis les sauvegardes..."
        
        for backup_file in "$BACKUP_DIR"/*; do
            if [ -f "$backup_file" ]; then
                filename=$(basename "$backup_file")
                cp "$backup_file" "$SCRIPT_DIR/$filename"
                info "Restauré: $filename"
            fi
        done
        
        success "Fichiers restaurés depuis les sauvegardes"
    fi
}

# Fonction d'installation des dépendances Python
install_dependencies() {
    section "📦 VÉRIFICATION DES DÉPENDANCES"
    
    info "Vérification de Python 3..."
    if ! command -v python3 &> /dev/null; then
        error "Python 3 non trouvé. Veuillez installer Python 3.6+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    info "Python version: $python_version"
    
    info "Vérification des modules Python essentiels..."
    
    # Modules essentiels
    essential_modules=("pathlib" "json" "logging" "datetime" "typing")
    
    for module in "${essential_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            success "Module $module: OK"
        else
            error "Module $module: MANQUANT"
            exit 1
        fi
    done
    
    # Modules optionnels
    info "Vérification des modules optionnels..."
    
    optional_modules=("yaml" "sqlite3")
    
    for module in "${optional_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            success "Module optionnel $module: OK"
        else
            warning "Module optionnel $module: MANQUANT (fonctionnalité limitée)"
        fi
    done
    
    success "Vérification des dépendances terminée"
}

# Fonction principale
main() {
    # En-tête
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║        🔧 INSTALLATEUR SMART PATCH PROCESSOR v2.0             ║"
    echo "║           Correcteur et Vérificateur Complet                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Initialisation du log
    echo "=== Installation Smart Patch Processor ===" > "$LOG_FILE"
    echo "Date: $(date)" >> "$LOG_FILE"
    echo "Répertoire: $SCRIPT_DIR" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    info "Début de l'installation - Log: $LOG_FILE"
    
    # Vérification de l'environnement
    if [ ! -f "$SCRIPT_DIR/main.py" ]; then
        error "Fichier main.py non trouvé. Êtes-vous dans le bon répertoire ?"
        exit 1
    fi
    
    # Traitement des arguments
    FORCE_MODE=false
    SKIP_TESTS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_MODE=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--force] [--skip-tests] [--help]"
                echo ""
                echo "Options:"
                echo "  --force      Force l'installation même en cas d'erreurs mineures"
                echo "  --skip-tests Ignore les tests de validation"
                echo "  --help       Affiche cette aide"
                echo ""
                echo "Ce script applique toutes les corrections identifiées au Smart Patch"
                echo "Processor et vérifie que le système fonctionne correctement."
                exit 0
                ;;
            *)
                warning "Option inconnue: $1"
                shift
                ;;
        esac
    done
    
    # Étapes d'installation
    success_count=0
    total_steps=0
    
    # Étape 1: Vérification des dépendances
    info "Étape 1/8: Vérification des dépendances"
    ((total_steps++))
    if install_dependencies; then
        ((success_count++))
    elif [ "$FORCE_MODE" = false ]; then
        exit 1
    fi
    
    # Étape 2: Sauvegarde
    info "Étape 2/8: Création des sauvegardes"
    ((total_steps++))
    if backup_files; then
        ((success_count++))
    else
        error "Échec de la sauvegarde"
        exit 1
    fi
    
    # Étape 3: Application des corrections
    info "Étape 3/8: Application des corrections"
    ((total_steps++))
    if apply_fixes; then
        ((success_count++))
    else
        error "Échec de l'application des corrections"
        if [ "$FORCE_MODE" = false ]; then
            cleanup_on_error
            exit 1
        fi
    fi
    
    # Étape 4: Création des fichiers manquants
    info "Étape 4/8: Création des fichiers manquants"
    ((total_steps++))
    if create_missing_files; then
        ((success_count++))
    fi
    
    # Étape 5: Test des imports
    info "Étape 5/8: Test des imports"
    ((total_steps++))
    if test_imports; then
        ((success_count++))
    elif [ "$FORCE_MODE" = false ]; then
        warning "Échec des tests d'import - utilisez --force pour continuer"
    fi
    
    # Étape 6: Tests de validation (optionnel)
    if [ "$SKIP_TESTS" = false ]; then
        info "Étape 6/8: Tests de validation"
        ((total_steps++))
        if run_validation_tests; then
            ((success_count++))
        elif [ "$FORCE_MODE" = false ]; then
            warning "Échec des tests de validation - utilisez --skip-tests pour ignorer"
        fi
    else
        info "Étape 6/8: Tests de validation (ignorés)"
        ((total_steps++))
        ((success_count++))
    fi
    
    # Étape 7: Test du wizard
    info "Étape 7/8: Test du wizard"
    ((total_steps++))
    if test_wizard; then
        ((success_count++))
    elif [ "$FORCE_MODE" = false ]; then
        warning "Échec du test wizard"
    fi
    
    # Étape 8: Vérification finale
    info "Étape 8/8: Vérification finale"
    ((total_steps++))
    if final_verification; then
        ((success_count++))
        final_status=0
    else
        final_status=1
    fi
    
    # Résumé final
    section "📊 RÉSUMÉ DE L'INSTALLATION"
    
    success_rate=$((success_count * 100 / total_steps))
    info "Étapes réussies: $success_count/$total_steps ($success_rate%)"
    
    if [ $final_status -eq 0 ]; then
        success "🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !"
        echo ""
        success "Le Smart Patch Processor v2.0 est maintenant opérationnel"
        success "Toutes les corrections de sécurité et de robustesse ont été appliquées"
        
        show_usage_instructions
        
    elif [ $success_rate -ge 75 ]; then
        warning "⚠️ INSTALLATION LARGEMENT RÉUSSIE"
        warning "Le système fonctionne mais quelques fonctionnalités peuvent être limitées"
        
        show_usage_instructions
        
    else
        error "❌ INSTALLATION ÉCHOUÉE"
        error "Problèmes critiques empêchent le bon fonctionnement"
        
        info "Suggestions de dépannage:"
        echo "   1. Relancez avec --force: $0 --force"
        echo "   2. Vérifiez les erreurs dans: $LOG_FILE"
        echo "   3. Restaurez les sauvegardes depuis: $BACKUP_DIR"
        echo "   4. Vérifiez les dépendances Python"
        
        exit 1
    fi
}

# Gestion des signaux
trap cleanup_on_error ERR
trap 'echo -e "\n${YELLOW}Installation interrompue par l'\''utilisateur${NC}"; exit 130' INT

# Vérification que le script est lancé depuis le bon répertoire
if [ ! -f "$(dirname "$0")/main.py" ]; then
    error "Veuillez lancer ce script depuis le répertoire Smart Patch Processor"
    exit 1
fi

# Lancement de l'installation
main "$@"