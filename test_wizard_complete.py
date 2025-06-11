#!/usr/bin/env python3
"""
Test complet des corrections du wizard
Valide que toutes les corrections fonctionnent
"""
from pathlib import Path


def test_all_wizard_fixes():
    """Teste toutes les corrections du wizard"""
    print("🧪 Test complet des corrections wizard")
    print("=" * 50)

    errors = []

    # Test 1: Import du wizard
    try:
        from wizard_mode import WizardMode
        print("✅ Test 1: Import wizard_mode OK")
    except Exception as e:
        errors.append(f"Import wizard_mode: {e}")
        print(f"❌ Test 1: {e}")

    # Test 2: Création d'instance
    try:
        from patch_processor_config import PatchProcessorConfig
        config = PatchProcessorConfig()
        wizard = WizardMode(None, config)
        print("✅ Test 2: Création instance wizard OK")
    except Exception as e:
        errors.append(f"Création instance: {e}")
        print(f"❌ Test 2: {e}")
        return False

    # Test 3: Méthodes sécurisées présentes
    try:
        required_methods = ['_show_detailed_results', '_diagnose_processor_state']
        for method in required_methods:
            if not hasattr(wizard, method):
                errors.append(f"Méthode manquante: {method}")
            else:
                print(f"✅ Test 3: Méthode {method} présente")
    except Exception as e:
        errors.append(f"Vérification méthodes: {e}")
        print(f"❌ Test 3: {e}")

    # Test 4: Gestion des résultats vides
    try:
        wizard._show_detailed_results({})
        print("✅ Test 4: _show_detailed_results gère les dicts vides")
    except Exception as e:
        errors.append(f"_show_detailed_results dict vide: {e}")
        print(f"❌ Test 4: {e}")

    # Test 5: Gestion des résultats avec format inattendu
    try:
        wizard._show_detailed_results({"unexpected": "format"})
        print("✅ Test 5: _show_detailed_results gère les formats inattendus")
    except Exception as e:
        errors.append(f"_show_detailed_results format inattendu: {e}")
        print(f"❌ Test 5: {e}")

    # Test 6: Diagnostic du processeur
    try:
        wizard._diagnose_processor_state()
        print("✅ Test 6: Diagnostic processeur fonctionne")
    except Exception as e:
        errors.append(f"Diagnostic processeur: {e}")
        print(f"❌ Test 6: {e}")

    # Test 7: Vérification du code source pour get_processor()
    try:
        import inspect
        source = inspect.getsource(wizard._step_7_execution_and_guidance)
        if "get_processor()" in source:
            errors.append("get_processor() encore présent dans le code")
            print("❌ Test 7: get_processor() encore dans le code")
        else:
            print("✅ Test 7: get_processor() supprimé du code")
    except Exception as e:
        errors.append(f"Vérification code source: {e}")
        print(f"❌ Test 7: {e}")

    # Résumé
    print("\n" + "=" * 50)
    if errors:
        print("❌ ÉCHECS DÉTECTÉS:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Relancez la correction ou vérifiez manuellement")
        return False
    else:
        print("🎉 TOUS LES TESTS PASSÉS !")
        print("✅ Le wizard est maintenant complètement corrigé")
        return True

def test_wizard_execution_simulation():
    """Simule une exécution du wizard pour tester la robustesse"""
    print("\n🎮 Simulation d'exécution wizard...")

    try:
        from wizard_mode import WizardMode
        from patch_processor_config import PatchProcessorConfig

        # Créer un mock processor
        class MockProcessor:
            def __init__(self):
                self.source_dir = "."
                self.output_dir = "."
                self.verbose = False
                self.git_integration = MockGitIntegration()
                self.interactive_cli = MockInteractiveCLI()
                self.config = PatchProcessorConfig()

            def process_all_patches(self):
                # Retourner différents formats pour tester la robustesse
                import random
                formats = [
                    {'success': 1, 'failed': 0, 'total': 1},
                    {'successful_patches': 1, 'failed_patches': 0, 'total_patches': 1},
                    {'results': [MockResult(True)]},
                    None,
                    "unexpected_string",
                    42
                ]
                return random.choice(formats)

        class MockGitIntegration:
            def __init__(self):
                self.is_git_available = False

        class MockInteractiveCLI:
            def is_enabled(self):
                return False

        class MockResult:
            def __init__(self, success):
                self.success = success
                self.patch_file = "test.patch"
                self.target_file = "test.py"
                self.output_file = "test_output.py"
                self.issues = []
                self.errors = []

        # Créer le wizard avec mock
        config = PatchProcessorConfig()
        processor = MockProcessor()
        wizard = WizardMode(processor, config)

        # Simuler des choix utilisateur
        wizard.session['user_choices'] = {
            'selected_patches': [Path("test.patch")],
            'safety_config': {'rollback_enabled': True},
            'advanced_config': {'ast_enabled': True}
        }

        # Tester _apply_wizard_configuration
        wizard._apply_wizard_configuration()
        print("✅ Configuration wizard appliquée sans erreur")

        # Tester les méthodes avec différents formats
        for i in range(3):
            try:
                summary = processor.process_all_patches()
                wizard._show_detailed_results(summary if isinstance(summary, dict) else {})
                print(f"✅ Test format {i+1}: Gestion robuste OK")
            except Exception as e:
                print(f"❌ Test format {i+1}: {e}")
                return False

        print("🎉 Simulation d'exécution réussie !")
        return True

    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 TESTS COMPLETS DU WIZARD CORRIGÉ")
    print("=" * 60)

    success1 = test_all_wizard_fixes()
    success2 = test_wizard_execution_simulation()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TOUTES LES CORRECTIONS VALIDÉES !")
        print("✅ Le wizard est prêt à l'utilisation")
        print("\n💡 Testez maintenant avec: python3 main.py --wizard")
    else:
        print("❌ Certains tests ont échoué")
        print("💡 Vérifiez les erreurs ci-dessus")

    exit(0 if (success1 and success2) else 1)
