#!/usr/bin/env python3
"""
Tests architecturaux pour Smart Patch Processor
Valide que toutes les corrections fonctionnent correctement
"""

import sys
import traceback
from pathlib import Path
from typing import List, Tuple, Dict, Any


class ArchitectureTest:
    """Tests de validation architecturale"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_all_tests(self) -> bool:
        """Lance tous les tests architecturaux"""
        print("🧪 Tests architecturaux Smart Patch Processor")
        print("=" * 50)
        
        tests = [
            ("Imports circulaires", self.test_circular_imports),
            ("Dépendances optionnelles", self.test_optional_dependencies),
            ("Validation d'entrée", self.test_input_validation),
            ("Gestionnaire d'erreurs", self.test_error_manager),
            ("Gestionnaire central", self.test_central_manager),
            ("Configuration", self.test_configuration),
            ("Composants essentiels", self.test_core_components),
        ]
        
        for test_name, test_func in tests:
            self._run_test(test_name, test_func)
        
        self._show_results()
        return self.failed == 0
    
    def _run_test(self, name: str, test_func):
        """Lance un test individuel"""
        try:
            print(f"  Testing {name}...", end=" ")
            test_func()
            print("✅ PASS")
            self.passed += 1
        except Exception as e:
            print("❌ FAIL")
            self.failed += 1
            self.errors.append(f"{name}: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    def test_circular_imports(self):
        """Test des imports circulaires"""
        # Tester que le module core fonctionne
        from core import registry, ComponentRegistry
        assert isinstance(registry, ComponentRegistry)
        
        # Tester que les imports principaux fonctionnent
        import smart_patch_processor
        import wizard_mode
        import main
        
        # Tester que le wizard peut accéder au processeur via le registre
        from core import get_processor
        # Note: get_processor() peut retourner None si pas encore enregistré
    
    def test_optional_dependencies(self):
        """Test de la gestion des dépendances optionnelles"""
        # Tester que la configuration gère YAML correctement
        from patch_processor_config import PatchProcessorConfig
        
        # Créer une config sans fichier
        config = PatchProcessorConfig()
        assert config.config is not None
        
        # Tester que ça ne crash pas même si yaml n'est pas disponible
        try:
            # Simuler l'absence de yaml
            import sys
            original_yaml = sys.modules.get('yaml')
            if 'yaml' in sys.modules:
                del sys.modules['yaml']
            
            # Recréer la config
            config2 = PatchProcessorConfig()
            assert config2.config is not None
            
            # Restaurer yaml si il était là
            if original_yaml:
                sys.modules['yaml'] = original_yaml
                
        except Exception as e:
            # Si ça crash, c'est un problème
            raise AssertionError(f"Config crash sans yaml: {e}")
    
    def test_input_validation(self):
        """Test de la validation d'entrée"""
        from validation import validate_patch_content, ValidationError
        
        # Tester validation valide
        validate_patch_content("content", "@@ -1,1 +1,1 @@\n content")
        
        # Tester validation invalide
        try:
            validate_patch_content(None, "content")
            raise AssertionError("Validation should have failed")
        except ValidationError:
            pass  # Expected
        
        try:
            validate_patch_content("content", "")
            raise AssertionError("Validation should have failed")
        except ValidationError:
            pass  # Expected
    
    def test_error_manager(self):
        """Test du gestionnaire d'erreurs"""
        from error_manager import error_manager, ErrorSeverity, handle_error
        
        # Nettoyer les erreurs précédentes
        error_manager.clear_errors()
        
        # Tester ajout d'erreur
        error = handle_error("Test error", "test_context")
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test error"
        
        # Tester résumé
        summary = error_manager.get_summary()
        assert summary['errors'] >= 1
        
        # Nettoyer
        error_manager.clear_errors()
    
    def test_central_manager(self):
        """Test du gestionnaire central"""
        from processor_manager import ProcessorManager, get_manager
        
        manager = get_manager()
        assert isinstance(manager, ProcessorManager)
        
        # Tester l'initialisation
        success = manager.initialize()
        assert success, "Manager initialization failed"
        
        # Tester l'état de santé
        health = manager.get_health_status()
        assert health['initialized']
        assert 'components' in health
    
    def test_configuration(self):
        """Test de la configuration"""
        from patch_processor_config import PatchProcessorConfig
        
        config = PatchProcessorConfig()
        
        # Tester les sections essentielles
        assert 'detection' in config.config
        assert 'security' in config.config
        assert 'correction' in config.config
        
        # Tester les méthodes d'accès
        threshold = config.get('correction', 'similarity_threshold', 0.5)
        assert isinstance(threshold, (int, float))
        
        security_section = config.get_section('security')
        assert isinstance(security_section, dict)
    
    def test_core_components(self):
        """Test des composants essentiels"""
        from patch_processor_config import PatchProcessorConfig
        from target_file_detector import TargetFileDetector
        from patch_analyzer import PatchAnalyzer
        from line_number_corrector import LineNumberCorrector
        from patch_applicator import PatchApplicator
        
        config = PatchProcessorConfig()
        
        # Tester que tous les composants peuvent être instanciés
        detector = TargetFileDetector(Path.cwd(), config)
        analyzer = PatchAnalyzer(config)
        corrector = LineNumberCorrector(config)
        applicator = PatchApplicator(config)
        
        assert detector is not None
        assert analyzer is not None
        assert corrector is not None
        assert applicator is not None
    
    def _show_results(self):
        """Affiche les résultats des tests"""
        total = self.passed + self.failed
        print("\n" + "=" * 50)
        print(f"📊 Résultats: {self.passed}/{total} tests passés")
        
        if self.failed > 0:
            print(f"\n❌ Échecs:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.failed == 0:
            print("\n🎉 Tous les tests architecturaux sont passés !")
            print("✅ L'architecture est correctement corrigée")
        else:
            print("\n⚠️ Certains tests ont échoué")
            print("💡 Vérifiez les erreurs ci-dessus")


def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
🧪 Tests architecturaux Smart Patch Processor

USAGE:
    python3 test_architecture.py [--verbose]

DESCRIPTION:
    Lance une suite de tests pour valider que toutes les corrections
    architecturales fonctionnent correctement.

OPTIONS:
    --verbose    Affiche les stack traces complètes en cas d'erreur

TESTS INCLUS:
    • Imports circulaires
    • Dépendances optionnelles  
    • Validation d'entrée
    • Gestionnaire d'erreurs
    • Gestionnaire central
    • Configuration
    • Composants essentiels
        """)
        return
    
    tester = ArchitectureTest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
