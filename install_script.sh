show_post_install_info() {
    echo ""
    echo -e "${GREEN}${BOLD}🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !${NC}"
    echo ""

    case $1 in
        "local")
            echo -e "${CYAN}📁 Installation locale:${NC}"
            echo "   • Exécutable: $SCRIPT_DIR/smart-patch"
            echo "   • Modules Python: $SCRIPT_DIR/"
            ;;
        "global_complete")
            echo -e "${CYAN}📁 Installation globale complète:${NC}"
            echo "   • Exécutable: $INSTALL_DIR/smart-patch"
            echo "   • Modules Python: $LIB_DIR/"
            ;;
        "user")
            echo -e "${CYAN}📁 Installation utilisateur:${NC}"
            echo "   • Exécutable: $HOME/.local/bin/smart-patch"
            echo "   • Modules Python: $HOME/.local/lib/smart-patch-processor/"
            ;;
        "pip")
            echo -e "${CYAN}📁 Installation pip:${NC}"
            echo "   • Package installé via pip3"
            echo "   • Commandes disponibles: smart-patch, smart-patch-processor"
            ;;
        "wheel")
            echo -e "${CYAN}📁 Package wheel créé:${NC}"
            echo "   • Fichier: dist/smart_patch_processor-$VERSION-py3-none-any.whl"
            echo "   • Installation: pip3 install dist/smart_patch_processor-*.whl"
            ;;
        "alias")
            echo -e "${CYAN}📁 Alias configurés:${NC}"
            echo "   • smart-patch, smart-guided, smart-wizard"
            ;;
        "distribution")
            echo -e "${CYAN}📁 Package de distribution créé:${NC}"
            echo "   • Répertoire: $DIST_DIR/smart-patch-processor-v$VERSION/"
            echo "   • Archives: distribution/*.tar.gz et *.zip"
            echo "   • Prêt pour partage et déploiement"
            ;;
    esac

    # Afficher les informations sur le package de distribution si créé
    if [[ -d "$DIST_DIR" ]] && [[ "$1" != "distribution" ]]; then
        local pkg_count=$(find "$DIST_DIR" -name "smart-patch-processor-v*" -type d 2>/dev/null | wc -l)
        if [[ $pkg_count -gt 0 ]]; then
            echo ""
            echo -e "${PURPLE}📦 Package de distribution également disponible:${NC}"
            echo "   • Répertoire: $DIST_DIR/"
            echo "   • Utilisez l'option 8 pour créer un package complet"
        fi
    fi

    echo ""
    echo -e "${CYAN}📁 Configuration:${NC}"
    echo "   • Répertoire: $CONFIG_DIR/"
    echo "   • Configuration rapide: $CONFIG_DIR/quick-config.sh"
    echo ""
    echo -e "${CYAN}🚀 Prochaines étapes:${NC}"
    echo "   1. Testez: smart-patch --help"
    echo "   2. Mode débutant: smart-patch --wizard"
    echo "   3. Mode guidé: smart-patch --guided patches/ output/"
    echo "   4. Configuration: smart-patch --create-config"
    echo ""
    echo -e "${YELLOW}💡 Aide et documentation:${NC}"
    echo "   • Mode guidé: smart-patch --guided --help"
    echo "   • Assistant: smart-patch --wizard"
    echo "   • Tests: smart-patch --test"
    echo "   • Toutes les options: smart-patch --help"

    # Informations spécifiques au partage si package de distribution
    if [[ "$1" == "distribution" ]] || [[ -d "$DIST_DIR" ]]; then
        echo ""
        echo -e "${PURPLE}${BOLD}📤 PARTAGE ET DÉPLOIEMENT:${NC}"
        echo ""
        echo -e "${GREEN}Pour partager avec d'autres:${NC}"
        echo "   • Partagez l'archive .tar.gz ou .zip"
        echo "   • Upload sur GitHub: git add distribution/ && git commit -m 'Package v$VERSION'"
        echo "   • Serveur web, email, etc."
        echo ""
        echo -e "${GREEN}Installation sur nouvelle machine:${NC}"
        echo "   tar -xzf smart-patch-processor-v$VERSION-complete.tar.gz"
        echo "   cd smart-patch-processor-v$VERSION/"
        echo "   bash install.sh    # Installation rapide"
        echo "   # OU"
        echo "   pip3 install --user *.whl    # Si package wheel inclus"
    fi
}

main() {
    # Vérifier les arguments de debug
    if [[ "$1" == "--debug" ]] || [[ "$2" == "--debug" ]]; then
        DEBUG_MODE=true
    fi

    # Trap pour gérer les erreurs
    trap cleanup_on_error ERR

    print_header "$@"
    check_requirements
    create_executable

    # Afficher les informations de debug si activé
    show_debug_info

    install_method_selection

    # Effectuer l'installation selon le choix
    case $choice in
        1) perform_installation "local" ;;
        2) perform_installation "global_complete" ;;
        3) perform_installation "user" ;;
        4) perform_installation "pip" ;;
        5) perform_installation "pip" ;;
        6) perform_installation "wheel" ;;
        7) perform_installation "alias" ;;
        8) create_complete_distribution ;;
    esac

    # Message de fin avec informations de nettoyage
    echo ""
    echo -e "${GREEN}${BOLD}✨ Installation Smart Patch Processor v$VERSION terminée !${NC}"

    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo -e "${YELLOW}🐛 Mode debug actif - fichiers temporaires conservés pour diagnostic${NC}"
        echo -e "${CYAN}Pour nettoyer manuellement: rm -rf build/ *.egg-info/ setup.py pyproject.toml MANIFEST.in${NC}"
    else
        echo -e "${GREEN}🧹 Fichiers temporaires nettoyés automatiquement${NC}"
        if [[ -d "$DIST_DIR" ]]; then
            echo -e "${PURPLE}📦 Package de distribution conservé dans: $DIST_DIR/${NC}"
        fi
    fi

    echo -e "${CYAN}Prêt à traiter vos patches intelligemment ! 🚀${NC}"
}

show_usage() {
    """Affiche l'usage du script d'installation"""
    echo "Usage: $0 [--debug]"
    echo ""
    echo "Options:"
    echo "  --debug    Active le mode debug (conserve les fichiers temporaires)"
    echo ""
    echo "Modes d'installation:"
    echo "  1. 🏠 Local        Installation dans le dossier actuel"
    echo "  2. 🌍 Global       Installation système complète"
    echo "  3. 👤 User         Installation utilisateur (~/.local/)"
    echo "  4. 📦 Pip Local    Installation pip utilisateur"
    echo "  5. 🌐 Pip Global   Installation pip système"
    echo "  6. 🔧 Wheel        Création package wheel (.whl)"
    echo "  7. 🔗 Alias        Configuration alias shell"
    echo "  8. 📦 Distribution Package complet pour partage"
    echo ""
    echo "Exemples:"
    echo "  $0                # Installation interactive normale"
    echo "  $0 --debug       # Installation en mode debug (fichiers conservés)"
    echo ""
    echo "Le mode debug est utile pour:"
    echo "  • Diagnostiquer les problèmes d'installation"
    echo "  • Examiner les fichiers de configuration générés"
    echo "  • Développer et tester des modifications"
    echo ""
    echo "Le mode distribution (option 8) crée un package complet avec:"
    echo "  • Tous les modules Python"
    echo "  • Script d'installation"
    echo "  • Exécutable portable"
    echo "  • Package pip (si possible)"
    echo "  • Archives .tar.gz et .zip pour partage"
}

# Ajouter l'option --help
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${CYAN}${BOLD}Smart Patch Processor v2.0 - Script d'Installation${NC}"
    echo ""
    show_usage
    exit 0
fi

# Vérifier si le script est exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fimain() {
    # Vérifier les arguments de debug
    if [[ "$1" == "--debug" ]] || [[ "$2" == "--debug" ]]; then
        DEBUG_MODE=true
    fi

    # Trap pour gérer les erreurs
    trap cleanup_on_error ERR

    print_header "$@"
    check_requirements
    create_executable

    # Afficher les informations de debug si activé
    show_debug_info

    install_method_selection

    # Effectuer l'installation selon le choix
    case $choice in
        1) perform_installation "local" ;;
        2) perform_installation "global_complete" ;;
        3) perform_installation "user" ;;
        4) perform_installation "pip" ;;
        5) perform_installation "pip" ;;
        6) perform_installation "wheel" ;;
        7) perform_installation "alias" ;;
    esac

    # Message de fin avec informations de nettoyage
    echo ""
    echo -e "${GREEN}${BOLD}✨ Installation Smart Patch Processor v2.0 terminée !${NC}"

    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo -e "${YELLOW}🐛 Mode debug actif - fichiers temporaires conservés pour diagnostic${NC}"
        echo -e "${CYAN}Pour nettoyer manuellement: rm -rf build/ dist/ *.egg-info/ setup.py pyproject.toml MANIFEST.in${NC}"
    else
        echo -e "${GREEN}🧹 Fichiers temporaires nettoyés automatiquement${NC}"
    fi

    echo -e "${CYAN}Prêt à traiter vos patches intelligemment ! 🚀${NC}"
}

show_usage() {
    """Affiche l'usage du script d'installation"""
    echo "Usage: $0 [--debug]"
    echo ""
    echo "Options:"
    echo "  --debug    Active le mode debug (conserve les fichiers temporaires)"
    echo ""
    echo "Exemples:"
    echo "  $0                # Installation normale avec nettoyage automatique"
    echo "  $0 --debug       # Installation en mode debug (fichiers conservés)"
    echo ""
    echo "Le mode debug est utile pour:"
    echo "  • Diagnostiquer les problèmes d'installation"
    echo "  • Examiner les fichiers de configuration générés"
    echo "  • Développer et tester des modifications"
    echo ""
}

# Ajouter l'option --help
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${CYAN}${BOLD}Smart Patch Processor v2.0 - Script d'Installation${NC}"
    echo ""
    show_usage
    exit 0
fi

# Vérifier si le script est exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi#!/bin/bash
# Script d'installation automatique pour Smart Patch Processor v2.0
# Version améliorée avec support pip wheel et installation complète

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"
LIB_DIR="/usr/local/lib/smart-patch-processor"
CONFIG_DIR="$HOME/.config/smart-patch-processor"
DIST_DIR="$SCRIPT_DIR/distribution"  # Nouveau: répertoire de distribution
PACKAGE_NAME="smart-patch-processor"
VERSION="2.0.0"

# Mode debug pour conserver les fichiers temporaires
DEBUG_MODE=false

# Détection des outils disponibles
HAS_PYTHON3=$(command -v python3 >/dev/null 2>&1 && echo "true" || echo "false")
HAS_PIP=$(command -v pip3 >/dev/null 2>&1 && echo "true" || echo "false")
HAS_SETUPTOOLS=$([[ "$HAS_PYTHON3" == "true" ]] && python3 -c "import setuptools" >/dev/null 2>&1 && echo "true" || echo "false")
HAS_WHEEL=$([[ "$HAS_PYTHON3" == "true" ]] && python3 -c "import wheel" >/dev/null 2>&1 && echo "true" || echo "false")

# Liste des fichiers/dossiers temporaires à nettoyer (exclut distribution/)
TEMP_FILES=(
    "build/"
    "*.egg-info/"
    "setup.py"
    "pyproject.toml"
    "MANIFEST.in"
    "smart-patch"
    ".pytest_cache/"
    "__pycache__/"
    "*.pyc"
    "*.pyo"
    ".coverage"
    ".tox/"
)

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🚀 INSTALLATION SMART PATCH PROCESSOR              ║"
    echo "║                           v2.0                                  ║"
    echo "║                      🔧 Version Améliorée                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Vérifier le mode debug
    if [[ "$1" == "--debug" ]]; then
        DEBUG_MODE=true
        echo -e "${YELLOW}🐛 MODE DEBUG ACTIVÉ - Les fichiers temporaires seront conservés${NC}"
        echo ""
    fi
}

create_distribution_package() {
    """Crée un package de distribution complet avec tous les fichiers nécessaires"""
    echo -e "${BLUE}📦 Création du package de distribution...${NC}"

    # Créer le répertoire de distribution
    mkdir -p "$DIST_DIR"

    # Nettoyer le répertoire de distribution précédent
    rm -rf "$DIST_DIR"/*

    echo "   📁 Création de la structure de distribution..."

    # Structure du package de distribution
    mkdir -p "$DIST_DIR/smart-patch-processor-v$VERSION"
    local pkg_dir="$DIST_DIR/smart-patch-processor-v$VERSION"

    # Copier tous les fichiers Python
    echo "   📄 Copie des modules Python..."
    for file in "$SCRIPT_DIR"/*.py; do
        if [[ -f "$file" ]]; then
            cp "$file" "$pkg_dir/"
        fi
    done

    # Copier les fichiers de configuration
    [[ -f "$SCRIPT_DIR/smart_patch_config.json" ]] && cp "$SCRIPT_DIR/smart_patch_config.json" "$pkg_dir/"
    [[ -f "$SCRIPT_DIR/requirements.txt" ]] && cp "$SCRIPT_DIR/requirements.txt" "$pkg_dir/"

    # Copier le script d'installation
    cp "$SCRIPT_DIR/install_script.sh" "$pkg_dir/"
    chmod +x "$pkg_dir/install_script.sh"

    # Créer le script exécutable dans le package
    cat > "$pkg_dir/smart-patch" << 'EOF'
#!/usr/bin/env python3
"""Smart Patch Processor v2.0 - Script Exécutable Portable"""

import sys
import os
from pathlib import Path

def main():
    # Le script cherche d'abord dans son propre répertoire
    script_dir = Path(__file__).parent.absolute()

    # Ajouter au Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    main_file = script_dir / "main.py"
    if not main_file.exists():
        print(f"❌ Erreur: main.py non trouvé dans {script_dir}")
        sys.exit(1)

    try:
        from main import main as smart_patch_main
        smart_patch_main()
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
    chmod +x "$pkg_dir/smart-patch"

    # Créer un README pour le package de distribution
    cat > "$pkg_dir/README.md" << EOF
# Smart Patch Processor v$VERSION - Package de Distribution

## 📦 Contenu du package

Ce package contient tout le nécessaire pour installer et utiliser Smart Patch Processor :

- **Modules Python** : Tous les fichiers .py requis
- **Script d'installation** : \`install_script.sh\` pour installation automatique
- **Exécutable portable** : \`smart-patch\` prêt à l'emploi
- **Configuration** : Fichiers de configuration par défaut
- **Package pip** : Fichier .whl pour installation pip (si généré)

## 🚀 Installation rapide

### Option 1 : Script d'installation automatique
\`\`\`bash
cd smart-patch-processor-v$VERSION/
bash install_script.sh
\`\`\`

### Option 2 : Installation pip (si .whl présent)
\`\`\`bash
pip3 install --user smart_patch_processor-$VERSION-py3-none-any.whl
\`\`\`

### Option 3 : Utilisation portable
\`\`\`bash
cd smart-patch-processor-v$VERSION/
./smart-patch --wizard
\`\`\`

## 💡 Premiers pas

1. **Débutants** : \`./smart-patch --wizard\`
2. **Mode guidé** : \`./smart-patch --guided patches/ output/\`
3. **Aide complète** : \`./smart-patch --help\`

## 📋 Modes d'installation disponibles

Le script d'installation propose plusieurs options :
- Installation locale (portable)
- Installation globale système
- Installation utilisateur (~/.local/)
- Installation pip (locale ou globale)
- Création de package wheel
- Configuration d'alias shell

## 🔧 Configuration

Créez une configuration personnalisée avec :
\`\`\`bash
./smart-patch --create-config
\`\`\`

## 📚 Documentation

- Aide générale : \`./smart-patch --help\`
- Mode guidé : \`./smart-patch --help-topic guided\`
- Exemples : \`./smart-patch --help-topic examples\`
- Dépannage : \`./smart-patch --help-topic troubleshooting\`

## 🌟 Fonctionnalités principales

- 🎯 Mode guidé pas-à-pas
- 🧙‍♂️ Assistant pour débutants
- 🔍 Détection automatique des fichiers cibles
- 🔧 Correction intelligente des numéros de ligne
- 🛡️ Sécurité et rollback
- 📊 Rapports détaillés

---
Smart Patch Processor v$VERSION - Traitement intelligent de patches
EOF

    # Créer un script d'installation simplifié pour le package
    cat > "$pkg_dir/install.sh" << 'EOF'
#!/bin/bash
# Installation rapide Smart Patch Processor

echo "🚀 Installation rapide Smart Patch Processor"
echo ""
echo "Choisissez une option :"
echo "1. 🏠 Utilisation portable (recommandé)"
echo "2. 👤 Installation utilisateur"
echo "3. 🔧 Installation complète (script avancé)"

read -p "Votre choix (1-3): " choice

case $choice in
    1)
        echo "✅ Prêt ! Utilisez : ./smart-patch --wizard"
        ;;
    2)
        if command -v pip3 >/dev/null 2>&1 && [[ -f "smart_patch_processor-*.whl" ]]; then
            pip3 install --user smart_patch_processor-*.whl
            echo "✅ Installé ! Utilisez : smart-patch --wizard"
        else
            echo "❌ pip3 ou fichier .whl manquant"
            echo "💡 Utilisez : bash install_script.sh"
        fi
        ;;
    3)
        bash install_script.sh
        ;;
    *)
        echo "❌ Choix invalide"
        ;;
esac
EOF
    chmod +x "$pkg_dir/install.sh"

    echo -e "${GREEN}✅ Package de distribution créé: $pkg_dir${NC}"
    return 0
}

copy_pip_package_to_distribution() {
    """Copie le package pip dans le répertoire de distribution"""
    local pkg_dir="$DIST_DIR/smart-patch-processor-v$VERSION"

    if [[ -d "dist" ]] && [[ -n "$(ls dist/*.whl 2>/dev/null)" ]]; then
        echo "   📦 Copie des packages pip..."
        cp dist/*.whl "$pkg_dir/" 2>/dev/null || true
        cp dist/*.tar.gz "$pkg_dir/" 2>/dev/null || true

        # Créer un script d'installation pip spécifique
        cat > "$pkg_dir/install-pip.sh" << EOF
#!/bin/bash
# Installation via pip

echo "📦 Installation Smart Patch Processor via pip"

if [[ -f smart_patch_processor-$VERSION-py3-none-any.whl ]]; then
    echo "1. Installation locale (utilisateur)"
    echo "2. Installation globale (système - nécessite sudo)"
    read -p "Choix (1-2): " choice

    case \$choice in
        1)
            pip3 install --user smart_patch_processor-$VERSION-py3-none-any.whl
            echo "✅ Installation terminée ! Utilisez: smart-patch --wizard"
            ;;
        2)
            sudo pip3 install smart_patch_processor-$VERSION-py3-none-any.whl
            echo "✅ Installation globale terminée ! Utilisez: smart-patch --wizard"
            ;;
        *)
            echo "❌ Choix invalide"
            ;;
    esac
else
    echo "❌ Fichier wheel non trouvé"
    echo "💡 Utilisez: bash install_script.sh puis choisissez l'option 6"
fi
EOF
        chmod +x "$pkg_dir/install-pip.sh"

        echo -e "${GREEN}   ✅ Packages pip copiés dans la distribution${NC}"
    else
        echo -e "${YELLOW}   ⚠️ Aucun package pip trouvé (sera créé si nécessaire)${NC}"
    fi
}

create_archive_distribution() {
    """Crée une archive complète du package de distribution"""
    echo -e "${BLUE}📦 Création d'archive de distribution...${NC}"

    local pkg_dir="$DIST_DIR/smart-patch-processor-v$VERSION"
    local archive_name="smart-patch-processor-v$VERSION-complete"

    cd "$DIST_DIR"

    # Créer plusieurs formats d'archive
    echo "   📁 Création archive tar.gz..."
    tar -czf "$archive_name.tar.gz" "smart-patch-processor-v$VERSION/"

    echo "   📁 Création archive zip..."
    zip -r "$archive_name.zip" "smart-patch-processor-v$VERSION/" >/dev/null 2>&1

    cd "$SCRIPT_DIR"

    # Calculer les tailles
    local tar_size=$(du -h "$DIST_DIR/$archive_name.tar.gz" 2>/dev/null | cut -f1 || echo "?")
    local zip_size=$(du -h "$DIST_DIR/$archive_name.zip" 2>/dev/null | cut -f1 || echo "?")

    echo -e "${GREEN}✅ Archives créées:${NC}"
    echo "   📦 $archive_name.tar.gz ($tar_size)"
    echo "   📦 $archive_name.zip ($zip_size)"

    return 0
}
cleanup_temp_files() {
    """Nettoie les fichiers temporaires après installation"""
    local install_type="$1"

    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo -e "${YELLOW}🐛 Mode debug: fichiers temporaires conservés${NC}"
        echo -e "${CYAN}📁 Fichiers conservés pour diagnostic:${NC}"
        for pattern in "${TEMP_FILES[@]}"; do
            if ls $pattern 2>/dev/null | head -1 >/dev/null 2>&1; then
                echo "   • $pattern"
            fi
        done
        return
    fi

    echo -e "${BLUE}🧹 Nettoyage des fichiers temporaires...${NC}"

    local cleaned_count=0
    local total_size=0

    # Calculer la taille avant nettoyage
    for pattern in "${TEMP_FILES[@]}"; do
        if [[ -e "$pattern" ]] || ls $pattern 2>/dev/null | head -1 >/dev/null 2>&1; then
            if [[ -d "$pattern" ]]; then
                local dir_size=$(du -sb "$pattern" 2>/dev/null | cut -f1 || echo "0")
                total_size=$((total_size + dir_size))
            elif [[ -f "$pattern" ]]; then
                local file_size=$(stat -f%z "$pattern" 2>/dev/null || stat -c%s "$pattern" 2>/dev/null || echo "0")
                total_size=$((total_size + file_size))
            fi
        fi
    done

    # Nettoyer les fichiers temporaires (MAIS PAS dist/ qui va dans distribution/)
    for pattern in "${TEMP_FILES[@]}"; do
        if [[ -d "$pattern" ]]; then
            rm -rf "$pattern" 2>/dev/null && {
                echo "   🗑️ Dossier supprimé: $pattern"
                cleaned_count=$((cleaned_count + 1))
            }
        elif [[ -f "$pattern" ]]; then
            rm -f "$pattern" 2>/dev/null && {
                echo "   🗑️ Fichier supprimé: $pattern"
                cleaned_count=$((cleaned_count + 1))
            }
        else
            # Pattern avec wildcards
            for file in $pattern; do
                if [[ -e "$file" ]]; then
                    if [[ -d "$file" ]]; then
                        rm -rf "$file" 2>/dev/null && cleaned_count=$((cleaned_count + 1))
                    else
                        rm -f "$file" 2>/dev/null && cleaned_count=$((cleaned_count + 1))
                    fi
                fi
            done
        fi
    done

    if [[ $cleaned_count -gt 0 ]]; then
        local size_mb=$((total_size / 1024 / 1024))
        echo -e "${GREEN}✅ Nettoyage terminé: $cleaned_count élément(s) supprimé(s) (~${size_mb}MB libérés)${NC}"
    else
        echo -e "${CYAN}✨ Aucun fichier temporaire à nettoyer${NC}"
    fi

    # Conserver dist/ mais le déplacer vers distribution/
    if [[ -d "dist" ]] && [[ "$install_type" == "wheel" || "$install_type" == "pip" ]]; then
        echo -e "${CYAN}📦 Conservation des packages pip dans distribution/${NC}"
        copy_pip_package_to_distribution
    fi

    # Nettoyage spécifique selon le type d'installation
    case "$install_type" in
        "pip"|"wheel")
            # Nettoyer le cache pip utilisateur
            if command -v pip3 >/dev/null 2>&1; then
                echo "   🧹 Nettoyage du cache pip..."
                pip3 cache purge >/dev/null 2>&1 || true
            fi
            ;;
        "global_complete"|"user")
            # Nettoyer les fichiers de backup temporaires
            find . -name "*.backup" -type f -mtime +0 -delete 2>/dev/null || true
            ;;
    esac
}

analyze_dependencies() {
    echo -e "${BLUE}🔍 Analyse des dépendances...${NC}"

    local required_deps=()
    local optional_deps=()
    local missing_optional=()

    # Analyser les imports dans le code
    echo "   📝 Analyse des imports..."

    # Chercher les imports optionnels
    if grep -r "import yaml\|import PyYAML" "$SCRIPT_DIR"/*.py >/dev/null 2>&1; then
        optional_deps+=("PyYAML>=5.1")
        if ! python3 -c "import yaml" >/dev/null 2>&1; then
            missing_optional+=("PyYAML (pour support YAML)")
        fi
    fi

    if grep -r "import libcst" "$SCRIPT_DIR"/*.py >/dev/null 2>&1; then
        optional_deps+=("libcst>=0.4.0")
        if ! python3 -c "import libcst" >/dev/null 2>&1; then
            missing_optional+=("libcst (pour analyse AST avancée)")
        fi
    fi

    echo -e "${GREEN}   ✅ Dépendances obligatoires: Aucune ! (stdlib uniquement)${NC}"

    if [[ ${#optional_deps[@]} -gt 0 ]]; then
        echo -e "${CYAN}   📦 Dépendances optionnelles détectées:${NC}"
        printf '      • %s\n' "${optional_deps[@]}"
    fi

    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        echo -e "${YELLOW}   ⚠️ Dépendances optionnelles manquantes:${NC}"
        printf '      • %s\n' "${missing_optional[@]}"
        echo ""
        read -p "Voulez-vous installer les dépendances optionnelles ? (y/N): " install_opt
        if [[ $install_opt =~ ^[Yy]$ ]]; then
            for dep in "${optional_deps[@]}"; do
                echo "Installation de $dep..."
                pip3 install --user "$dep" || echo "⚠️ Échec installation $dep (non critique)"
            done
        fi
    else
        echo -e "${GREEN}   ✅ Toutes les dépendances optionnelles sont disponibles${NC}"
    fi
}

check_requirements() {

check_requirements() {
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"

    # Vérifier Python 3
    if [[ "$HAS_PYTHON3" != "true" ]]; then
        echo -e "${RED}❌ Python 3 requis mais non trouvé${NC}"
        echo -e "${YELLOW}💡 Installation recommandée: sudo apt install python3 python3-pip${NC}"
        exit 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}✅ Python $python_version trouvé${NC}"

    # Vérifier pip
    if [[ "$HAS_PIP" == "true" ]]; then
        echo -e "${GREEN}✅ pip3 disponible${NC}"
    else
        echo -e "${YELLOW}⚠️ pip3 non trouvé (optionnel pour certains modes)${NC}"
    fi

    # Vérifier setuptools et wheel
    if [[ "$HAS_SETUPTOOLS" == "true" ]]; then
        echo -e "${GREEN}✅ setuptools disponible${NC}"
    else
        echo -e "${YELLOW}⚠️ setuptools manquant (requis pour pip wheel)${NC}"
    fi

    if [[ "$HAS_WHEEL" == "true" ]]; then
        echo -e "${GREEN}✅ wheel disponible${NC}"
    else
        echo -e "${YELLOW}⚠️ wheel manquant (requis pour pip wheel)${NC}"
    fi

    # Vérifier les fichiers requis
    required_files=("main.py" "smart_patch_processor.py" "colors.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
            echo -e "${RED}❌ Fichier requis manquant: $file${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}✅ Fichiers requis présents${NC}"

    # Analyser les dépendances
    analyze_dependencies
}
}

create_executable() {
    echo -e "${BLUE}📝 Création du script exécutable...${NC}"

    cat > "$SCRIPT_DIR/smart-patch" << 'EOF'
#!/usr/bin/env python3
"""Smart Patch Processor v2.0 - Script Exécutable"""

import sys
import os
from pathlib import Path

def main():
    # Chemins possibles pour les modules
    possible_paths = [
        # 1. Installation locale (développement)
        Path(__file__).parent.absolute(),
        # 2. Installation globale système
        Path("/usr/local/lib/smart-patch-processor"),
        # 3. Installation pip utilisateur
        Path.home() / ".local/lib/python3.*/site-packages/smart-patch-processor",
        # 4. Installation pip système
        Path("/usr/local/lib/python3.*/site-packages/smart-patch-processor"),
    ]

    # Rechercher le répertoire contenant main.py
    script_dir = None
    for path in possible_paths:
        # Gérer les wildcards pour les versions Python
        if "*" in str(path):
            import glob
            for expanded_path in glob.glob(str(path)):
                expanded_path = Path(expanded_path)
                if (expanded_path / "main.py").exists():
                    script_dir = expanded_path
                    break
        else:
            if (path / "main.py").exists():
                script_dir = path
                break

        if script_dir:
            break

    if not script_dir:
        print("❌ Erreur: Impossible de localiser les modules Smart Patch Processor")
        print("Chemins vérifiés:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\n💡 Solutions possibles:")
        print("  1. Réinstaller avec: ./install_script.sh")
        print("  2. Installer via pip: pip3 install ./")
        print("  3. Exécuter depuis le répertoire source: python3 main.py")
        sys.exit(1)

    # Ajouter au Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    try:
        from main import main as smart_patch_main
        smart_patch_main()
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print(f"Répertoire utilisé: {script_dir}")
        print("Fichiers disponibles:")
        for file in script_dir.glob("*.py"):
            print(f"  - {file.name}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur d'exécution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x "$SCRIPT_DIR/smart-patch"
    echo -e "${GREEN}✅ Script exécutable créé: $SCRIPT_DIR/smart-patch${NC}"
}

create_pip_package_files() {
    echo -e "${BLUE}📦 Création des fichiers pour package pip...${NC}"

    # Lister tous les modules Python présents
    local py_modules=()
    for file in "$SCRIPT_DIR"/*.py; do
        if [[ -f "$file" ]]; then
            local basename=$(basename "$file" .py)
            if [[ "$basename" != "__init__" ]]; then
                py_modules+=("\"$basename\"")
            fi
        fi
    done

    # Joindre les modules avec des virgules
    local py_modules_str=$(IFS=','; echo "${py_modules[*]}")

    # Créer setup.py
    cat > "$SCRIPT_DIR/setup.py" << EOF
#!/usr/bin/env python3
"""Setup script pour Smart Patch Processor"""

from setuptools import setup
from pathlib import Path
import glob

# Lire le README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Lire les dépendances
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

# Découvrir automatiquement tous les modules Python
py_modules = []
for py_file in glob.glob("*.py"):
    module_name = py_file[:-3]  # Enlever .py
    if module_name not in ['setup', '__init__']:
        py_modules.append(module_name)

setup(
    name="smart-patch-processor",
    version="$VERSION",
    author="Smart Patch Processor Team",
    author_email="contact@smart-patch-processor.dev",
    description="Processeur intelligent de patches avec détection automatique et correction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smart-patch-processor/smart-patch-processor",
    py_modules=py_modules,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "ast": ["libcst"],
        "yaml": ["PyYAML"],
    },
    entry_points={
        "console_scripts": [
            "smart-patch=main:main",
            "smart-patch-processor=main:main",
            "smart-guided=main:main",
        ],
    },
    include_package_data=True,
    data_files=[
        ('smart-patch-processor', ['smart_patch_config.json'] if Path('smart_patch_config.json').exists() else []),
    ],
    project_urls={
        "Bug Reports": "https://github.com/smart-patch-processor/smart-patch-processor/issues",
        "Source": "https://github.com/smart-patch-processor/smart-patch-processor",
        "Documentation": "https://smart-patch-processor.readthedocs.io/",
    },
    keywords="patch diff git development automation smart intelligent",
    zip_safe=False,
)
EOF

    # Créer pyproject.toml (moderne)
    cat > "$SCRIPT_DIR/pyproject.toml" << EOF
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "smart-patch-processor"
version = "$VERSION"
description = "Processeur intelligent de patches avec détection automatique et correction"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Smart Patch Processor Team", email = "contact@smart-patch-processor.dev"}
]
keywords = ["patch", "diff", "git", "development", "automation", "smart", "intelligent"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Version Control",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "black", "flake8", "mypy"]
ast = ["libcst"]
yaml = ["PyYAML"]

[project.scripts]
smart-patch = "main:main"
smart-patch-processor = "main:main"
smart-guided = "main:main"

[project.urls]
Homepage = "https://github.com/smart-patch-processor/smart-patch-processor"
"Bug Reports" = "https://github.com/smart-patch-processor/smart-patch-processor/issues"
"Source Code" = "https://github.com/smart-patch-processor/smart-patch-processor"
Documentation = "https://smart-patch-processor.readthedocs.io/"

[tool.setuptools]
py-modules = [$py_modules_str]

[tool.setuptools.package-data]
"*" = ["*.json", "*.yaml", "*.yml", "*.md", "*.txt"]
EOF

    # Créer MANIFEST.in
    cat > "$SCRIPT_DIR/MANIFEST.in" << EOF
include README.md
include LICENSE
include requirements.txt
include smart_patch_config.json
include *.py
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
recursive-exclude * *.so
recursive-exclude * .DS_Store
EOF

    # Créer requirements.txt avec les vraies dépendances
    if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
        cat > "$SCRIPT_DIR/requirements.txt" << EOF
# Smart Patch Processor v2.0 - Dépendances

# === DÉPENDANCES OPTIONNELLES ===
# Décommentez selon vos besoins

# Support configuration YAML (optionnel)
# PyYAML>=5.1

# Analyse syntaxique Python avancée (optionnel)
# libcst>=0.4.0

# === DÉPENDANCES DE DÉVELOPPEMENT ===
# Pour les développeurs uniquement

# Tests
# pytest>=6.0
# pytest-cov

# Formatage de code
# black>=22.0
# flake8>=4.0

# Vérification de types
# mypy>=0.950

# === NOTES ===
# Smart Patch Processor fonctionne sans aucune dépendance externe !
# Toutes les dépendances sont optionnelles pour des fonctionnalités avancées.
EOF
    else
        echo -e "${CYAN}💡 requirements.txt existant conservé${NC}"
    fi

    # Créer README.md s'il n'existe pas
    if [[ ! -f "$SCRIPT_DIR/README.md" ]]; then
        cat > "$SCRIPT_DIR/README.md" << EOF
# Smart Patch Processor v2.0

Processeur intelligent de patches avec détection automatique, correction et fonctionnalités avancées.

## Installation

\`\`\`bash
# Installation via pip (recommandé)
pip3 install ./

# Installation manuelle
./install_script.sh
\`\`\`

## Usage

\`\`\`bash
# Mode guidé (recommandé pour débuter)
smart-patch --guided patches/ output/

# Mode standard
smart-patch patches/ output/

# Mode assistant interactif
smart-patch --wizard
\`\`\`

## Fonctionnalités

- 🎯 Mode guidé pas-à-pas
- 🔍 Détection automatique des fichiers cibles
- 🔧 Correction intelligente des numéros de ligne
- 🛡️ Sécurité et rollback
- 🧠 Analyse syntaxique avancée (AST)
- 📊 Rapports détaillés
- 🔗 Intégration Git
- 🧙‍♂️ Assistant pour débutants

## Documentation

Voir \`smart-patch --help\` pour plus d'informations.
EOF
    fi

    echo -e "${GREEN}✅ Fichiers package pip créés${NC}"
}

install_method_selection() {
    echo -e "${YELLOW}📋 Choisissez une méthode d'installation:${NC}"
    echo "1. 🏠 Installation locale (dans le dossier actuel)"
    echo "2. 🌍 Installation globale complète (dans $LIB_DIR)"
    echo "3. 👤 Installation utilisateur (dans ~/.local/)"
    echo "4. 📦 Installation pip locale (pip install ./)"
    echo "5. 🌐 Installation pip globale (sudo pip install ./)"
    echo "6. 🔧 Créer package wheel (.whl)"
    echo "7. 🔗 Créer seulement l'alias bash/zsh"
    echo "8. 📦 Créer package de distribution complet"
    echo "9. ❌ Annuler"

    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}🐛 Mode debug actif - les fichiers temporaires seront conservés${NC}"
    fi

    read -p "Votre choix (1-9): " choice

    case $choice in
        1) install_local ;;
        2) install_global_complete ;;
        3) install_user ;;
        4) install_pip_local ;;
        5) install_pip_global ;;
        6) create_wheel_package ;;
        7) create_alias ;;
        8) create_complete_distribution ;;
        9) echo "Installation annulée"; cleanup_temp_files "cancelled"; exit 0 ;;
        *) echo -e "${RED}❌ Choix invalide${NC}"; cleanup_temp_files "error"; exit 1 ;;
    esac
}

create_complete_distribution() {
    """Crée un package de distribution complet avec tout inclus"""
    echo -e "${BLUE}📦 Création du package de distribution complet...${NC}"

    # Créer le package de distribution de base
    create_distribution_package

    # Créer également le package wheel si possible
    if [[ "$HAS_SETUPTOOLS" == "true" ]] && [[ "$HAS_WHEEL" == "true" ]]; then
        echo -e "${CYAN}🔧 Ajout du package wheel au package de distribution...${NC}"

        # Créer les fichiers de package
        create_pip_package_files

        # Nettoyer les builds précédents
        rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

        # Créer le wheel
        python3 setup.py sdist bdist_wheel >/dev/null 2>&1

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}   ✅ Package wheel créé et ajouté${NC}"
            # Copier vers la distribution
            copy_pip_package_to_distribution
        else
            echo -e "${YELLOW}   ⚠️ Échec création wheel (non critique)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ setuptools/wheel manquant - wheel non inclus${NC}"
    fi

    # Créer les archives
    create_archive_distribution

    # Afficher le résumé
    local pkg_dir="$DIST_DIR/smart-patch-processor-v$VERSION"
    local file_count=$(find "$pkg_dir" -type f | wc -l)
    local dir_size=$(du -sh "$pkg_dir" 2>/dev/null | cut -f1 || echo "?")

    echo ""
    echo -e "${GREEN}${BOLD}✅ PACKAGE DE DISTRIBUTION COMPLET CRÉÉ !${NC}"
    echo ""
    echo -e "${CYAN}📦 Contenu du package:${NC}"
    echo "   📁 Répertoire: $pkg_dir"
    echo "   📄 Fichiers: $file_count"
    echo "   💾 Taille: $dir_size"
    echo ""
    echo -e "${CYAN}📦 Archives créées:${NC}"
    if [[ -f "$DIST_DIR/smart-patch-processor-v$VERSION-complete.tar.gz" ]]; then
        local tar_size=$(du -h "$DIST_DIR/smart-patch-processor-v$VERSION-complete.tar.gz" | cut -f1)
        echo "   📦 smart-patch-processor-v$VERSION-complete.tar.gz ($tar_size)"
    fi
    if [[ -f "$DIST_DIR/smart-patch-processor-v$VERSION-complete.zip" ]]; then
        local zip_size=$(du -h "$DIST_DIR/smart-patch-processor-v$VERSION-complete.zip" | cut -f1)
        echo "   📦 smart-patch-processor-v$VERSION-complete.zip ($zip_size)"
    fi
    echo ""
    echo -e "${YELLOW}💡 UTILISATION DU PACKAGE:${NC}"
    echo ""
    echo -e "${GREEN}📤 Pour partager:${NC}"
    echo "   • Envoyez l'archive .tar.gz ou .zip à d'autres utilisateurs"
    echo "   • Uploadez sur GitHub, serveur web, etc."
    echo ""
    echo -e "${GREEN}📥 Pour installer ailleurs:${NC}"
    echo "   1. Extraire l'archive"
    echo "   2. cd smart-patch-processor-v$VERSION/"
    echo "   3. bash install.sh (installation rapide)"
    echo "   4. OU bash install_script.sh (installation complète)"
    echo ""
    echo -e "${GREEN}🚀 Installation rapide sur nouvelle machine:${NC}"
    echo "   tar -xzf smart-patch-processor-v$VERSION-complete.tar.gz"
    echo "   cd smart-patch-processor-v$VERSION/"
    echo "   bash install.sh"
    echo ""

    # Nettoyer après succès
    cleanup_temp_files "distribution"
}

install_local() {
    echo -e "${BLUE}🏠 Installation locale...${NC}"

    echo -e "${GREEN}✅ Installation locale terminée${NC}"
    echo -e "${CYAN}💡 Usage:${NC}"
    echo "   cd $SCRIPT_DIR"
    echo "   ./smart-patch --guided patches/ output/"

    # Proposer d'ajouter au PATH
    echo ""
    read -p "Voulez-vous ajouter ce dossier au PATH ? (y/N): " add_path
    if [[ $add_path =~ ^[Yy]$ ]]; then
        add_to_path "$SCRIPT_DIR"
    fi
}

install_global_complete() {
    echo -e "${BLUE}🌍 Installation globale complète...${NC}"

    # Créer le répertoire lib
    if [[ $EUID -eq 0 ]]; then
        mkdir -p "$LIB_DIR"
        cp "$SCRIPT_DIR"/*.py "$LIB_DIR/"
        [[ -f "$SCRIPT_DIR/smart_patch_config.json" ]] && cp "$SCRIPT_DIR/smart_patch_config.json" "$LIB_DIR/"
        cp "$SCRIPT_DIR/smart-patch" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/smart-patch"
    else
        echo "Installation globale nécessite les privilèges administrateur"
        sudo mkdir -p "$LIB_DIR"
        sudo cp "$SCRIPT_DIR"/*.py "$LIB_DIR/"
        [[ -f "$SCRIPT_DIR/smart_patch_config.json" ]] && sudo cp "$SCRIPT_DIR/smart_patch_config.json" "$LIB_DIR/"
        sudo cp "$SCRIPT_DIR/smart-patch" "$INSTALL_DIR/"
        sudo chmod +x "$INSTALL_DIR/smart-patch"
    fi

    echo -e "${GREEN}✅ Installation globale complète terminée${NC}"
    echo -e "${CYAN}💡 Fichiers installés:${NC}"
    echo "   • Modules Python: $LIB_DIR/"
    echo "   • Exécutable: $INSTALL_DIR/smart-patch"
    echo ""
    echo -e "${CYAN}💡 Usage depuis n'importe où:${NC}"
    echo "   smart-patch --guided patches/ output/"
}

install_user() {
    echo -e "${BLUE}👤 Installation utilisateur...${NC}"

    local user_bin="$HOME/.local/bin"
    local user_lib="$HOME/.local/lib/smart-patch-processor"

    mkdir -p "$user_bin"
    mkdir -p "$user_lib"

    cp "$SCRIPT_DIR"/*.py "$user_lib/"
    [[ -f "$SCRIPT_DIR/smart_patch_config.json" ]] && cp "$SCRIPT_DIR/smart_patch_config.json" "$user_lib/"
    cp "$SCRIPT_DIR/smart-patch" "$user_bin/"
    chmod +x "$user_bin/smart-patch"

    echo -e "${GREEN}✅ Installation utilisateur terminée${NC}"
    echo -e "${CYAN}💡 Fichiers installés:${NC}"
    echo "   • Modules Python: $user_lib/"
    echo "   • Exécutable: $user_bin/smart-patch"
    echo ""
    echo -e "${CYAN}💡 Usage:${NC}"
    echo "   smart-patch --guided patches/ output/"

    # Vérifier si ~/.local/bin est dans le PATH
    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
        echo -e "${YELLOW}⚠️ $user_bin n'est pas dans votre PATH${NC}"
        read -p "Voulez-vous l'ajouter ? (y/N): " add_path
        if [[ $add_path =~ ^[Yy]$ ]]; then
            add_to_path "$user_bin"
        fi
    fi
}

install_pip_local() {
    echo -e "${BLUE}📦 Installation pip locale...${NC}"

    if [[ "$HAS_PIP" != "true" ]]; then
        echo -e "${RED}❌ pip3 requis mais non disponible${NC}"
        echo -e "${YELLOW}💡 Installation: sudo apt install python3-pip${NC}"
        cleanup_temp_files "error"
        exit 1
    fi

    # Créer les fichiers de package si nécessaire
    create_pip_package_files

    echo "Installation avec pip en mode utilisateur..."
    pip3 install --user --editable .

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Installation pip locale réussie${NC}"
        echo -e "${CYAN}💡 Usage:${NC}"
        echo "   smart-patch --guided patches/ output/"
        echo "   smart-patch-processor --help"

        # Vérifier si ~/.local/bin est dans le PATH
        local user_bin="$HOME/.local/bin"
        if [[ ":$PATH:" != *":$user_bin:"* ]]; then
            echo -e "${YELLOW}⚠️ $user_bin n'est pas dans votre PATH${NC}"
            read -p "Voulez-vous l'ajouter ? (y/N): " add_path
            if [[ $add_path =~ ^[Yy]$ ]]; then
                add_to_path "$user_bin"
            fi
        fi

        # Nettoyer après succès
        cleanup_temp_files "pip"
    else
        echo -e "${RED}❌ Échec de l'installation pip${NC}"
        cleanup_temp_files "error"
        exit 1
    fi
}

install_pip_global() {
    echo -e "${BLUE}🌐 Installation pip globale...${NC}"

    if [[ "$HAS_PIP" != "true" ]]; then
        echo -e "${RED}❌ pip3 requis mais non disponible${NC}"
        cleanup_temp_files "error"
        exit 1
    fi

    # Créer les fichiers de package
    create_pip_package_files

    echo "Installation globale avec pip (nécessite sudo)..."
    if [[ $EUID -eq 0 ]]; then
        pip3 install .
    else
        sudo pip3 install .
    fi

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Installation pip globale réussie${NC}"
        echo -e "${CYAN}💡 Usage depuis n'importe où:${NC}"
        echo "   smart-patch --guided patches/ output/"
        echo "   smart-patch-processor --help"

        # Nettoyer après succès
        cleanup_temp_files "pip"
    else
        echo -e "${RED}❌ Échec de l'installation pip globale${NC}"
        cleanup_temp_files "error"
        exit 1
    fi
}

create_wheel_package() {
    echo -e "${BLUE}🔧 Création du package wheel...${NC}"

    if [[ "$HAS_SETUPTOOLS" != "true" ]] || [[ "$HAS_WHEEL" != "true" ]]; then
        echo -e "${RED}❌ setuptools et wheel requis${NC}"
        echo -e "${YELLOW}💡 Installation: pip3 install setuptools wheel${NC}"

        read -p "Voulez-vous installer setuptools et wheel maintenant ? (y/N): " install_deps
        if [[ $install_deps =~ ^[Yy]$ ]]; then
            pip3 install --user setuptools wheel
            if [[ $? -ne 0 ]]; then
                echo -e "${RED}❌ Échec de l'installation des dépendances${NC}"
                cleanup_temp_files "error"
                exit 1
            fi
        else
            cleanup_temp_files "cancelled"
            exit 1
        fi
    fi

    # Créer les fichiers de package
    create_pip_package_files

    # Nettoyer les builds précédents
    echo "🧹 Nettoyage des builds précédents..."
    rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

    echo "Création du package wheel..."
    python3 setup.py sdist bdist_wheel

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Package wheel créé avec succès${NC}"
        echo -e "${CYAN}📦 Fichiers générés:${NC}"
        ls -la dist/

        echo ""
        echo -e "${CYAN}💡 Installation du wheel:${NC}"
        echo "   # Installation locale:"
        echo "   pip3 install --user dist/smart_patch_processor-$VERSION-py3-none-any.whl"
        echo ""
        echo "   # Installation globale:"
        echo "   sudo pip3 install dist/smart_patch_processor-$VERSION-py3-none-any.whl"
        echo ""
        echo -e "${CYAN}💡 Publication PyPI (optionnel):${NC}"
        echo "   pip3 install twine"
        echo "   twine upload dist/*"

        # Proposer l'installation directe
        echo ""
        read -p "Voulez-vous installer le wheel maintenant ? (y/N): " install_wheel
        if [[ $install_wheel =~ ^[Yy]$ ]]; then
            echo "1. Installation locale (utilisateur)"
            echo "2. Installation globale (système)"
            read -p "Choix (1-2): " wheel_install_choice

            if [[ $wheel_install_choice == "1" ]]; then
                pip3 install --user "dist/smart_patch_processor-$VERSION-py3-none-any.whl"
                if [[ $? -eq 0 ]]; then
                    echo -e "${GREEN}✅ Wheel installé avec succès${NC}"
                    cleanup_temp_files "wheel"
                else
                    echo -e "${RED}❌ Échec installation wheel${NC}"
                    cleanup_temp_files "error"
                fi
            elif [[ $wheel_install_choice == "2" ]]; then
                sudo pip3 install "dist/smart_patch_processor-$VERSION-py3-none-any.whl"
                if [[ $? -eq 0 ]]; then
                    echo -e "${GREEN}✅ Wheel installé globalement${NC}"
                    cleanup_temp_files "wheel"
                else
                    echo -e "${RED}❌ Échec installation globale wheel${NC}"
                    cleanup_temp_files "error"
                fi
            fi
        else
            # Conserver le wheel mais nettoyer le reste
            if [[ "$DEBUG_MODE" != "true" ]]; then
                echo -e "${CYAN}💾 Conservation du package wheel, nettoyage des autres fichiers temporaires...${NC}"
                rm -rf build/ *.egg-info/ setup.py pyproject.toml MANIFEST.in smart-patch 2>/dev/null || true
                echo -e "${GREEN}✅ Nettoyage partiel terminé (wheel conservé)${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Échec de la création du wheel${NC}"
        cleanup_temp_files "error"
        exit 1
    fi
}

create_alias() {
    echo -e "${BLUE}🔗 Création des alias...${NC}"

    local shell_rc=""
    if [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        shell_rc="$HOME/.bashrc"
    else
        echo "Shell détecté: $SHELL"
        read -p "Fichier de configuration shell (~/.bashrc): " shell_rc
        shell_rc="${shell_rc:-$HOME/.bashrc}"
    fi

    # Ajouter les alias
    cat >> "$shell_rc" << EOF

# Smart Patch Processor v2.0 - Alias
alias smart-patch='python3 $SCRIPT_DIR/main.py'
alias smart-guided='python3 $SCRIPT_DIR/main.py --guided'
alias smart-config='python3 $SCRIPT_DIR/main.py --create-config'
alias smart-wizard='python3 $SCRIPT_DIR/main.py --wizard'

# Fonction Smart Patch avec vérifications et détection automatique
smart-patch() {
    # Chemins possibles pour les modules
    local script_paths=(
        "$SCRIPT_DIR/main.py"
        "/usr/local/lib/smart-patch-processor/main.py"
        "$HOME/.local/lib/smart-patch-processor/main.py"
    )

    local script_path=""
    for path in "\${script_paths[@]}"; do
        if [[ -f "\$path" ]]; then
            script_path="\$path"
            break
        fi
    done

    if [[ -z "\$script_path" ]]; then
        echo "❌ Smart Patch Processor non trouvé"
        echo "💡 Chemins vérifiés:"
        printf '   %s\n' "\${script_paths[@]}"
        echo "💡 Réinstallez avec: ./install_script.sh"
        return 1
    fi

    python3 "\$script_path" "\$@"
}
EOF

    echo -e "${GREEN}✅ Alias ajoutés à $shell_rc${NC}"
    echo -e "${CYAN}💡 Rechargez votre shell ou tapez:${NC}"
    echo "   source $shell_rc"
    echo ""
    echo -e "${CYAN}💡 Usage:${NC}"
    echo "   smart-patch --guided patches/ output/"
    echo "   smart-guided patches/ output/"
    echo "   smart-wizard"
}

add_to_path() {
    local dir_to_add="$1"

    # Déterminer le fichier de configuration shell
    local shell_rc=""
    if [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        shell_rc="$HOME/.bashrc"
    else
        read -p "Fichier de configuration shell (~/.bashrc): " shell_rc
        shell_rc="${shell_rc:-$HOME/.bashrc}"
    fi

    # Vérifier si déjà dans le PATH
    if [[ ":$PATH:" == *":$dir_to_add:"* ]]; then
        echo -e "${YELLOW}⚠️ $dir_to_add déjà dans le PATH${NC}"
        return
    fi

    # Ajouter au PATH
    echo "" >> "$shell_rc"
    echo "# Smart Patch Processor v2.0 - PATH" >> "$shell_rc"
    echo "export PATH=\"$dir_to_add:\$PATH\"" >> "$shell_rc"

    echo -e "${GREEN}✅ $dir_to_add ajouté au PATH dans $shell_rc${NC}"
    echo -e "${CYAN}💡 Rechargez votre shell:${NC} source $shell_rc"
}

setup_config() {
    echo -e "${BLUE}⚙️ Configuration initiale...${NC}"

    # Créer le répertoire de configuration
    mkdir -p "$CONFIG_DIR"

    # Copier la configuration par défaut si elle existe
    if [[ -f "$SCRIPT_DIR/smart_patch_config.json" ]]; then
        cp "$SCRIPT_DIR/smart_patch_config.json" "$CONFIG_DIR/default.json"
        echo -e "${GREEN}✅ Configuration par défaut copiée${NC}"
    fi

    # Créer un script de configuration rapide
    cat > "$CONFIG_DIR/quick-config.sh" << 'EOF'
#!/bin/bash
# Configuration rapide Smart Patch Processor
echo "🔧 Configuration rapide Smart Patch Processor"

# Chercher le générateur de config
config_generators=(
    "/usr/local/lib/smart-patch-processor/advanced_config_generator.py"
    "$HOME/.local/lib/smart-patch-processor/advanced_config_generator.py"
    "$(dirname "$0")/../advanced_config_generator.py"
)

generator_found=""
for gen in "${config_generators[@]}"; do
    if [[ -f "$gen" ]]; then
        generator_found="$gen"
        break
    fi
done

if [[ -n "$generator_found" ]]; then
    python3 "$generator_found"
else
    echo "❌ Générateur de configuration non trouvé"
    echo "💡 Utilisez: smart-patch --create-config"
fi
EOF
    chmod +x "$CONFIG_DIR/quick-config.sh"

    echo -e "${CYAN}💡 Configuration sauvée dans: $CONFIG_DIR${NC}"
}

test_installation() {
    echo -e "${BLUE}🧪 Test de l'installation...${NC}"

    case $1 in
        "local")
            cd "$SCRIPT_DIR"
            if ./smart-patch --version >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Test local réussi${NC}"
            else
                echo -e "${RED}❌ Test local échoué${NC}"
                return 1
            fi
            ;;
        "global"|"global_complete"|"user")
            if command -v smart-patch >/dev/null 2>&1; then
                if smart-patch --version >/dev/null 2>&1; then
                    echo -e "${GREEN}✅ Test global réussi${NC}"
                else
                    echo -e "${YELLOW}⚠️ Commande trouvée mais erreur d'exécution${NC}"
                    echo "Diagnostic:"
                    smart-patch --version 2>&1 | head -5
                    return 1
                fi
            else
                echo -e "${RED}❌ Commande smart-patch non trouvée${NC}"
                echo -e "${YELLOW}Vous devrez peut-être recharger votre shell${NC}"
                return 1
            fi
            ;;
        "pip")
            # Test avec Python
            if python3 -c "import main; print('Smart Patch Processor importé avec succès')" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Test pip réussi (import Python)${NC}"
            else
                echo -e "${YELLOW}⚠️ Import Python échoué${NC}"
            fi

            # Test commande
            if command -v smart-patch >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Commande smart-patch disponible${NC}"
            else
                echo -e "${YELLOW}⚠️ Commande smart-patch non dans PATH${NC}"
            fi
            ;;
        "wheel")
            echo -e "${CYAN}💡 Testez l'installation du wheel avec:${NC}"
            echo "   pip3 install --user dist/smart_patch_processor-$VERSION-py3-none-any.whl"
            echo "   smart-patch --version"
            ;;
        "alias")
            echo -e "${YELLOW}⚠️ Rechargez votre shell pour tester les alias${NC}"
            echo "   source ~/.bashrc  # ou ~/.zshrc"
            echo "   smart-patch --version"
            ;;
    esac
}

show_usage_examples() {
    echo -e "${CYAN}${BOLD}📚 EXEMPLES D'USAGE${NC}"
    echo ""
    echo -e "${BOLD}🎯 Mode guidé (recommandé pour débuter):${NC}"
    echo "   smart-patch --guided patches/ output/"
    echo ""
    echo -e "${BOLD}🧙‍♂️ Assistant interactif pour débutants:${NC}"
    echo "   smart-patch --wizard"
    echo ""
    echo -e "${BOLD}💾 Avec backup personnalisé:${NC}"
    echo "   smart-patch --guided --backup-dir ~/mes_backups patches/ output/"
    echo ""
    echo -e "${BOLD}✏️ Modification directe des originaux:${NC}"
    echo "   smart-patch --guided --modify-original patches/ output/"
    echo ""
    echo -e "${BOLD}👁️ Preview uniquement:${NC}"
    echo "   smart-patch --guided --preview-only patches/ output/"
    echo ""
    echo -e "${BOLD}🎯 Patch spécifique avec cible explicite:${NC}"
    echo "   smart-patch fix.patch output/ --target myfile.py"
    echo ""
    echo -e "${BOLD}⚙️ Créer une configuration personnalisée:${NC}"
    echo "   smart-patch --create-config"
    echo ""
    echo -e "${BOLD}📖 Aide complète:${NC}"
    echo "   smart-patch --help"
    echo ""
    echo -e "${BOLD}🧪 Tests unitaires:${NC}"
    echo "   smart-patch --test"
}

create_desktop_entry() {
    echo -e "${BLUE}🖥️ Création d'une entrée bureau (optionnel)...${NC}"

    read -p "Créer une entrée de menu bureau ? (y/N): " create_desktop
    if [[ ! $create_desktop =~ ^[Yy]$ ]]; then
        return
    fi

    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"

    # Déterminer le chemin de l'exécutable
    local exec_path="smart-patch"
    if command -v smart-patch >/dev/null 2>&1; then
        exec_path=$(command -v smart-patch)
    fi

    cat > "$desktop_dir/smart-patch-processor.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Smart Patch Processor
Comment=Processeur intelligent de patches avec mode guidé
Exec=gnome-terminal -- $exec_path --guided
Icon=text-x-patch
Terminal=true
Categories=Development;Utility;
Keywords=patch;diff;git;development;smart;intelligent;
StartupNotify=true
EOF

    # Entrée pour le mode wizard
    cat > "$desktop_dir/smart-patch-wizard.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Smart Patch Processor - Assistant
Comment=Assistant pas-à-pas pour débutants
Exec=gnome-terminal -- $exec_path --wizard
Icon=applications-development
Terminal=true
Categories=Development;Utility;
Keywords=patch;diff;git;development;wizard;assistant;
StartupNotify=true
EOF

    echo -e "${GREEN}✅ Entrées bureau créées${NC}"
    echo "   • Smart Patch Processor (mode guidé)"
    echo "   • Smart Patch Processor - Assistant (mode wizard)"
}

cleanup_on_error() {
    echo -e "${RED}❌ Erreur durant l'installation${NC}"
    echo "Nettoyage..."

    # Supprimer les fichiers créés en cas d'erreur
    [[ -f "$SCRIPT_DIR/smart-patch" ]] && rm -f "$SCRIPT_DIR/smart-patch"
    [[ -f "$INSTALL_DIR/smart-patch" ]] && sudo rm -f "$INSTALL_DIR/smart-patch" 2>/dev/null
    [[ -f "$HOME/.local/bin/smart-patch" ]] && rm -f "$HOME/.local/bin/smart-patch"
    [[ -d "$LIB_DIR" ]] && sudo rm -rf "$LIB_DIR" 2>/dev/null
    [[ -d "$HOME/.local/lib/smart-patch-processor" ]] && rm -rf "$HOME/.local/lib/smart-patch-processor"

    # Nettoyer les fichiers de build pip
    [[ -d "$SCRIPT_DIR/build" ]] && rm -rf "$SCRIPT_DIR/build"
    [[ -d "$SCRIPT_DIR/dist" ]] && rm -rf "$SCRIPT_DIR/dist"
    [[ -d "$SCRIPT_DIR"/*.egg-info ]] && rm -rf "$SCRIPT_DIR"/*.egg-info

    exit 1
}

show_post_install_info() {
    echo ""
    echo -e "${GREEN}${BOLD}🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !${NC}"
    echo ""

    case $1 in
        "local")
            echo -e "${CYAN}📁 Installation locale:${NC}"
            echo "   • Exécutable: $SCRIPT_DIR/smart-patch"
            echo "   • Modules Python: $SCRIPT_DIR/"
            ;;
        "global_complete")
            echo -e "${CYAN}📁 Installation globale complète:${NC}"
            echo "   • Exécutable: $INSTALL_DIR/smart-patch"
            echo "   • Modules Python: $LIB_DIR/"
            ;;
        "user")
            echo -e "${CYAN}📁 Installation utilisateur:${NC}"
            echo "   • Exécutable: $HOME/.local/bin/smart-patch"
            echo "   • Modules Python: $HOME/.local/lib/smart-patch-processor/"
            ;;
        "pip")
            echo -e "${CYAN}📁 Installation pip:${NC}"
            echo "   • Package installé via pip3"
            echo "   • Commandes disponibles: smart-patch, smart-patch-processor"
            ;;
        "wheel")
            echo -e "${CYAN}📁 Package wheel créé:${NC}"
            echo "   • Fichier: dist/smart_patch_processor-$VERSION-py3-none-any.whl"
            echo "   • Installation: pip3 install dist/smart_patch_processor-*.whl"
            ;;
        "alias")
            echo -e "${CYAN}📁 Alias configurés:${NC}"
            echo "   • smart-patch, smart-guided, smart-wizard"
            ;;
    esac

    echo ""
    echo -e "${CYAN}📁 Configuration:${NC}"
    echo "   • Répertoire: $CONFIG_DIR/"
    echo "   • Configuration rapide: $CONFIG_DIR/quick-config.sh"
    echo ""
    echo -e "${CYAN}🚀 Prochaines étapes:${NC}"
    echo "   1. Testez: smart-patch --help"
    echo "   2. Mode débutant: smart-patch --wizard"
    echo "   3. Mode guidé: smart-patch --guided patches/ output/"
    echo "   4. Configuration: smart-patch --create-config"
    echo ""
    echo -e "${YELLOW}💡 Aide et documentation:${NC}"
    echo "   • Mode guidé: smart-patch --guided --help"
    echo "   • Assistant: smart-patch --wizard"
    echo "   • Tests: smart-patch --test"
    echo "   • Toutes les options: smart-patch --help"
}

perform_installation() {
    local install_type="$1"

    # Configuration commune
    setup_config

    # Test d'installation
    test_installation "$install_type"
    local test_result=$?

    # Entrée bureau optionnelle (sauf pour wheel)
    if [[ "$install_type" != "wheel" ]]; then
        create_desktop_entry
    fi

    # Affichage des exemples d'usage
    show_usage_examples

    # Informations post-installation
    show_post_install_info "$install_type"

    return $test_result
}

main() {
    # Trap pour gérer les erreurs
    trap cleanup_on_error ERR

    print_header
    check_requirements
    create_executable

    install_method_selection

    # Effectuer l'installation selon le choix
    case $choice in
        1) perform_installation "local" ;;
        2) perform_installation "global_complete" ;;
        3) perform_installation "user" ;;
        4) perform_installation "pip" ;;
        5) perform_installation "pip" ;;
        6) perform_installation "wheel" ;;
        7) perform_installation "alias" ;;
    esac

    # Message de fin
    echo ""
    echo -e "${GREEN}${BOLD}✨ Installation Smart Patch Processor v2.0 terminée !${NC}"
    echo -e "${CYAN}Prêt à traiter vos patches intelligemment ! 🚀${NC}"
}

# Vérifier si le script est exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
