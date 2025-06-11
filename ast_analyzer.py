from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module ast_analyzer.py - Classe ASTAnalyzer."""

import ast
import re
import logging
from pathlib import Path
import libcst as cst

from patch_processor_config import PatchProcessorConfig
from ast_analyzer_factory import ASTAnalyzerFactory
try:
    import libcst
    LIBCST_AVAILABLE = True
except ImportError:
    LIBCST_AVAILABLE = False
class ASTAnalyzer:
    """Analyseur syntaxique pour améliorer la détection et correction des patches"""
    
    def __init__(self, config: PatchProcessorConfig):

        # Cache pour les analyses
        self._analysis_cache = {}

        # Factory pour créer les analyseurs spécialisés
        self.factory = ASTAnalyzerFactory()

        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.ast_analyzer')
        
        correction_config = config.get_section('correction')
        self.enabled = correction_config.get('ast_analysis_enabled', True)
        self.prefer_ast = correction_config.get('prefer_ast_detection', False)
        
        # Parsers supportés par langage
        self.language_parsers = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript,
            '.ts': self._analyze_typescript,
            '.php': self._analyze_php,
            '.jsx': self._analyze_javascript,
            '.tsx': self._analyze_typescript
        }
        

    def is_language_supported(self, file_path: Path) -> Tuple[bool, str]:
        """Vérifie si un langage est supporté par l'analyseur AST"""
        file_ext = file_path.suffix.lower()
        
        supported_languages = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.php': 'PHP',
            '.jsx': 'JavaScript/JSX',
            '.tsx': 'TypeScript/TSX'
        }
        
        if file_ext in self.language_parsers:
            lang_name = supported_languages.get(file_ext, 'Unknown')
            return True, lang_name
        else:
            return False, f"Unsupported extension: {file_ext}"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Retourne la liste des langages supportés"""
        return {ext: 'Supported' for ext in self.language_parsers.keys()}
        
    def analyze_patch_context(self, patch_content: str, target_file: Path) -> Optional[Dict]:
        """Analyse le contexte syntaxique du patch pour améliorer la localisation"""
        if not self.enabled or not target_file.exists():
            return None
            
        file_ext = target_file.suffix.lower()
        if file_ext not in self.language_parsers:
            self.logger.debug(f"Pas d'analyseur AST pour {file_ext}")
            return None
            
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Analyse du fichier cible
            target_analysis = self.language_parsers[file_ext](source_code)
            
            # Analyse du patch pour extraire le contexte modifié
            patch_context = self._extract_patch_context(patch_content)
            
            # Matching intelligent basé sur l'AST
            location_hints = self._find_ast_location(target_analysis, patch_context)
            
            return {
                'target_analysis': target_analysis,
                'patch_context': patch_context,
                'location_hints': location_hints,
                'confidence': self._calculate_ast_confidence(location_hints)
            }
            
        except Exception as e:
            self.logger.warning(f"Erreur analyse AST: {e}")
            return None
            
    def _analyze_python(self, source_code: str) -> Dict:
        """Analyse Python avec AST standard et libcst si disponible"""
        analysis = {
            'language': 'python',
            'functions': [],
            'classes': [],
            'imports': [],
            'structure': []
        }
        
        try:
            # Parse avec AST standard
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'col': node.col_offset,
                        'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        'args': [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'col': node.col_offset,
                        'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append({
                                'type': 'import',
                                'module': alias.name,
                                'alias': alias.asname,
                                'line': node.lineno
                            })
                    else:  # ImportFrom
                        for alias in node.names:
                            analysis['imports'].append({
                                'type': 'from_import',
                                'module': node.module,
                                'name': alias.name,
                                'alias': alias.asname,
                                'line': node.lineno
                            })
                            
            # Analyse structurelle avec libcst si disponible
            if LIBCST_AVAILABLE:
                try:
                    import libcst as cst
                    cst_tree = cst.parse_module(source_code)
                    analysis['cst_available'] = True
                    analysis['structure'] = []  # Peut être étendu
                except Exception as e:
                    self.logger.debug(f"Erreur libcst: {e}")
                    analysis['cst_available'] = False
            
        except SyntaxError as e:
            analysis['syntax_error'] = str(e)
            analysis['valid'] = False
        except Exception as e:
            analysis['parse_error'] = str(e)
            analysis['valid'] = False
        else:
            analysis['valid'] = True
            
        return analysis
        
    def _analyze_javascript(self, source_code: str) -> Dict:
        """Analyse JavaScript/JSX basique"""
        analysis = {
            'language': 'javascript',
            'functions': [],
            'classes': [],
            'imports': [],
            'valid': True
        }
        
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Fonctions
            func_match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)', line)
            if func_match:
                analysis['functions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'args': [arg.strip() for arg in func_match.group(2).split(',') if arg.strip()]
                })
                
            # Classes
            class_match = re.search(r'class\s+(\w+)', line)
            if class_match:
                analysis['classes'].append({
                    'name': class_match.group(1),
                    'line': i
                })
                
        return analysis
        
    def _analyze_typescript(self, source_code: str) -> Dict:
        """Analyse TypeScript (extension de JavaScript)"""
        analysis = self._analyze_javascript(source_code)
        analysis['language'] = 'typescript'
        return analysis
        

    def _analyze_php(self, source_code: str) -> Dict:
        """Analyse PHP avec détection des fonctions, classes, traits, etc."""
        analysis = {
            'language': 'php',
            'functions': [],
            'classes': [],
            'traits': [],
            'interfaces': [],
            'namespaces': [],
            'uses': [],
            'constants': [],
            'valid': True
        }
        
        lines = source_code.split('\n')
        current_namespace = None
        in_class = None
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Namespace
            namespace_match = re.search(r'namespace\s+([^;\s]+)', line)
            if namespace_match:
                current_namespace = namespace_match.group(1)
                analysis['namespaces'].append({
                    'name': current_namespace,
                    'line': i
                })
            
            # Classes
            class_match = re.search(r'(?:abstract\s+)?class\s+(\w+)', line)
            if class_match:
                in_class = class_match.group(1)
                analysis['classes'].append({
                    'name': class_match.group(1),
                    'line': i,
                    'namespace': current_namespace
                })
            
            # Functions/Methods
            func_match = re.search(r'(?:public|private|protected)?\s*function\s+(\w+)', line)
            if func_match:
                analysis['functions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'class': in_class,
                    'namespace': current_namespace
                })
        
        return analysis
        
    def _extract_patch_context(self, patch_content: str) -> Dict:
        """Extrait le contexte syntaxique du patch"""
        context = {
            'modified_functions': [],
            'modified_classes': [],
            'added_imports': [],
            'removed_imports': []
        }
        
        lines = patch_content.split('\n')
        
        for line in lines:
            if line.startswith(('+', '-')) and len(line) > 1:
                content = line[1:].strip()
                prefix = line[0]
                
                # Fonctions modifiées
                func_match = re.search(r'(?:def|function|class)\s+(\w+)', content)
                if func_match:
                    func_name = func_match.group(1)
                    target_list = context['modified_functions'] if 'def' in content or 'function' in content else context['modified_classes']
                    
                    if func_name not in [item['name'] for item in target_list]:
                        target_list.append({
                            'name': func_name,
                            'modification_type': 'removed' if prefix == '-' else 'added',
                            'content': content
                        })
                        
        return context
        
    def _find_ast_location(self, target_analysis: Dict, patch_context: Dict) -> List[Dict]:
        """Trouve les emplacements probables basés sur l'analyse AST"""
        location_hints = []
        
        if not target_analysis.get('valid', True):
            return location_hints
            
        # Correspondance par fonctions modifiées
        for modified_func in patch_context['modified_functions']:
            func_name = modified_func['name']
            
            for target_func in target_analysis.get('functions', []):
                if target_func['name'] == func_name:
                    location_hints.append({
                        'type': 'function_match',
                        'name': func_name,
                        'line': target_func['line'],
                        'confidence': 0.9,
                        'context': target_func
                    })
                    
        return location_hints
        
    def _calculate_ast_confidence(self, location_hints: List[Dict]) -> float:
        """Calcule la confiance globale de l'analyse AST"""
        if not location_hints:
            return 0.0
            
        total_confidence = sum(hint.get('confidence', 0.0) for hint in location_hints)
        return min(1.0, total_confidence / len(location_hints))
        
    def get_best_location_hint(self, location_hints: List[Dict]) -> Optional[Dict]:
        """Retourne le meilleur indice de localisation"""
        if not location_hints:
            return None
            
        return max(location_hints, key=lambda x: x.get('confidence', 0.0))
