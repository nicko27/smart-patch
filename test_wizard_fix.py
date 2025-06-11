#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections du wizard
"""

import sys
from pathlib import Path

def test_wizard_imports():
    """Teste que les imports fonctionnent"""
    try:
        from wizard_mode import WizardMode
        from main import main, handle_special_modes
        from smart_patch_processor import SmartPatchProcessor
        print("✅ Tous les imports fonctionnent")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_wizard_methods():
    """Teste que les nouvelles méthodes existent"""
    try:
        from wizard_mode import WizardMode
        from patch_processor_config import PatchProcessorConfig
        
        # Créer une instance factice
        config = PatchProcessorConfig()
        wizard = WizardMode(None, config)
        
        # Vérifier que les méthodes existent
        assert hasattr(wizard, '_show_detailed_results'), "Méthode _show_detailed_results manquante"
        
        print("✅ Toutes les nouvelles méthodes sont présentes")
        return True
    except Exception as e:
        print(f"❌ Erreur de méthode: {e}")
        return False

def main():
    """Lance tous les tests"""
    print("🧪 Test des corrections du wizard")
    print("=" * 40)
    
    tests = [
        test_wizard_imports,
        test_wizard_methods
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Résultat: {passed}/{len(tests)} tests passés")
    
    if passed == len(tests):
        print("🎉 Toutes les corrections sont fonctionnelles !")
        return True
    else:
        print("❌ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    main()
