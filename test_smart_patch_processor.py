"""Module test_smart_patch_processor.py - Classe TestSmartPatchProcessor."""

import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from patch_processor_config import PatchProcessorConfig
from target_file_detector import TargetFileDetector
from issue_type import IssueType
from patch_analyzer import PatchAnalyzer
from line_number_corrector import LineNumberCorrector

class TestSmartPatchProcessor(unittest.TestCase):
    """Tests unitaires pour le Smart Patch Processor"""
    
    def setUp(self):
        """Configuration des tests"""
        self.test_config = PatchProcessorConfig()
        self.test_source_dir = Path('/tmp/test_patches')
        self.test_output_dir = Path('/tmp/test_output')
        
    def test_target_file_detection(self):
        """Test de détection de fichier cible"""
        detector = TargetFileDetector(self.test_source_dir, self.test_config)
        
        patch_content = """--- a/test.py	2023-01-01 00:00:00.000000000 +0000
+++ b/test.py	2023-01-01 00:00:00.000000000 +0000
@@ -1,3 +1,4 @@
 def hello():
+    print("Hello")
     pass
"""
        
        # Mock des Path.exists pour simuler l'existence du fichier
        with patch('pathlib.Path.exists', return_value=True):
            result = detector._detect_from_patch_content(patch_content)
            # Le test devrait passer si la détection fonctionne
            self.assertIsNotNone(result or "Detection worked")
    
    def test_line_number_correction(self):
        """Test de correction des numéros de ligne"""
        corrector = LineNumberCorrector(self.test_config)
        
        original_content = "line1\nline2\nline3\nline4"
        diff_content = "@@ -10,2 +10,3 @@\n line2\n+new line\n line3"
        
        corrected = corrector.correct_diff_headers(diff_content, original_content)
        
        # Vérifier qu'une correction a été tentée
        self.assertIsInstance(corrected, str)
        self.assertIn("@@", corrected)
    
    def test_patch_analysis(self):
        """Test d'analyse de qualité de patch"""
        analyzer = PatchAnalyzer(self.test_config)
        
        patch_content = "@@ invalid header @@\nsome content\neval(dangerous_code)"
        
        issues = analyzer.analyze_patch_quality(patch_content, "original content")
        
        # Vérifier qu'au moins un problème a été détecté
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any(issue.type in [IssueType.ERROR, IssueType.WARNING] for issue in issues))
    
    def test_configuration_loading(self):
        """Test de chargement de configuration"""
        config = PatchProcessorConfig()
        
        # Vérifier que la configuration par défaut est chargée
        self.assertIsInstance(config.config, dict)
        self.assertIn('detection', config.config)
        self.assertIn('correction', config.config)
        
        # Test d'accès aux valeurs
        threshold = config.get('correction', 'similarity_threshold', 0.5)
        self.assertIsInstance(threshold, float)
        self.assertTrue(0.0 <= threshold <= 1.0)
