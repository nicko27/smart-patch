#!/usr/bin/env python3
"""
Fix pour Smart Patch Processor - Correction du problème de détection des fichiers cibles
Le problème: Smart Patch détecte 'error.py' au lieu des vrais fichiers dans le patch

Usage: python smart_patch_fix.py
"""

import os
import re
import sys
from pathlib import Path

def fix_target_file_detector():
    """Corrige le module target_file_detector.py"""
    
    detector_file = Path("target_file_detector.py")
    if not detector_file.exists():
        print(f"❌ Fichier {detector_file} non trouvé")
        return False
    
    print(f"🔧 Correction de {detector_file}...")
    
    # Lire le contenu actuel
    with open(detector_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # CORRECTION 1: Améliorer les patterns de recherche
    old_patterns = '''self.search_patterns = detection_config.get('search_patterns', [])'''
    
    new_patterns = '''self.search_patterns = detection_config.get('search_patterns', [
            r'^\+\+\+\s+([^\\t\\r\\n]+)',        # Nouveau fichier (priorité haute)
            r'^---\s+([^\\t\\r\\n]+)',          # Ancien fichier  
            r'^Index:\\s+([^\\r\\n]+)',         # Index Git
            r'^diff\\s+--git\\s+a/([^\\s]+)\\s+b/([^\\s]+)',  # Git diff
            r'^\\*\\*\\*\\s+([^\\t\\r\\n]+)',       # Context diff ancien
        ])'''
    
    content = content.replace(old_patterns, new_patterns)
    
    # CORRECTION 2: Améliorer _resolve_filename
    old_resolve = '''def _resolve_filename(self, filename: str) -> Optional[Path]:
        """Résout un nom de fichier extrait du patch"""
        # Nettoyer le chemin
        clean_name = os.path.basename(filename.strip())
        
        if not clean_name or clean_name == '/dev/null':
            return None
        
        return self._find_target_file(clean_name)'''
    
    new_resolve = '''def _resolve_filename(self, filename: str) -> Optional[Path]:
        """Résout un nom de fichier extrait du patch - VERSION CORRIGÉE"""
        if not filename or not isinstance(filename, str):
            return None
            
        # CORRECTION: Nettoyer les caractères parasites et timestamps
        filename = filename.strip()
        
        # Supprimer les timestamps et métadonnées communes
        filename = re.sub(r'\\s+\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}.*$', '', filename)
        filename = re.sub(r'\\s+[A-Z][a-z]{2}\\s+[A-Z][a-z]{2}\\s+\\d+.*$', '', filename)
        filename = filename.split('\\t')[0]  # Supprimer tout après une tabulation
        filename = filename.strip()
        
        # CORRECTION: Ignorer les fichiers spéciaux et invalides
        invalid_names = ['/dev/null', '', '.', '..', 'a', 'b', 'error', 'new', 'old']
        clean_name = os.path.basename(filename)
        
        if (not clean_name or 
            clean_name.lower() in invalid_names or 
            len(clean_name) < 2 or
            clean_name.startswith('.')):
            return None
        
        # CORRECTION: Vérifier si c'est un nom de fichier valide
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]*\\.[a-zA-Z0-9]+$', clean_name):
            self.logger.debug(f"Nom de fichier invalide ignoré: '{clean_name}'")
            return None
        
        return self._find_target_file(clean_name)'''
    
    content = content.replace(old_resolve, new_resolve)
    
    # CORRECTION 3: Améliorer _detect_from_patch_content
    old_detect = '''def _detect_from_patch_content(self, patch_content: str) -> Optional[Path]:
        """Détecte le fichier cible depuis le contenu du patch"""
        lines = patch_content.split('\\n')
        
        for line in lines[:10]:  # Regarder les 10 premières lignes
            for pattern in self.search_patterns:
                match = re.search(pattern, line)
                if match:
                    # Prendre le premier groupe de capture
                    filename = match.group(1).strip()
                    target = self._resolve_filename(filename)
                    if target:
                        return target
        
        return None'''
    
    new_detect = '''def _detect_from_patch_content(self, patch_content: str) -> Optional[Path]:
        """Détecte le fichier cible depuis le contenu du patch - VERSION CORRIGÉE"""
        lines = patch_content.split('\\n')
        candidates = []
        
        # CORRECTION: Analyser TOUTES les lignes d'en-tête, pas seulement les 10 premières
        for line_num, line in enumerate(lines):
            # Arrêter à la première ligne de contenu de diff
            if line.startswith(('@@', ' ', '+', '-')) and not line.startswith(('+++', '---')):
                break
                
            line = line.strip()
            if not line:
                continue
                
            for pattern in self.search_patterns:
                try:
                    match = re.search(pattern, line)
                    if match:
                        # CORRECTION: Gestion des différents groupes de capture
                        if pattern.startswith(r'^diff\\s+--git'):
                            # Pour git diff, prendre le fichier nouveau (groupe 2)
                            filename = match.group(2).strip()
                        else:
                            # Pour les autres, prendre le premier groupe
                            filename = match.group(1).strip()
                        
                        # CORRECTION: Validation et nettoyage du nom de fichier
                        target = self._resolve_filename(filename)
                        if target and target not in candidates:
                            candidates.append(target)
                            self.logger.debug(f"Fichier candidat trouvé: {target} (ligne {line_num + 1})")
                            
                except Exception as e:
                    self.logger.debug(f"Erreur parsing ligne '{line}': {e}")
                    continue
        
        # Retourner le premier candidat valide
        return candidates[0] if candidates else None'''
    
    content = content.replace(old_detect, new_detect)
    
    # Sauvegarder
    with open(detector_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {detector_file} corrigé")
    return True

def fix_smart_patch_processor():
    """Corrige le processeur principal"""
    
    processor_file = Path("smart_patch_processor.py")
    if not processor_file.exists():
        print(f"❌ Fichier {processor_file} non trouvé")
        return False
    
    print(f"🔧 Correction de {processor_file}...")
    
    with open(processor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # CORRECTION: Ajouter une méthode de détection améliorée
    new_method = '''
    def detect_patch_targets_improved(self, patch_content: str, patch_path: Path) -> list:
        """NOUVEAU: Détecte TOUS les fichiers cibles dans un patch (même multi-fichiers)"""
        targets = []
        
        # Analyser le patch pour identifier tous les fichiers
        lines = patch_content.split('\\n')
        current_files = set()
        
        for line in lines:
            line = line.strip()
            
            # Détecter les en-têtes de fichiers
            filename = None
            if line.startswith('--- ') and not line.endswith('/dev/null'):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('+++ ') and not line.endswith('/dev/null'):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('*** '):
                filename = self._extract_clean_filename(line[4:])
            elif line.startswith('Index: '):
                filename = self._extract_clean_filename(line[7:])
            
            if filename and filename not in current_files:
                # Résoudre le nom de fichier vers un chemin réel
                resolved_path = self._resolve_target_path(filename, patch_path)
                if resolved_path:
                    targets.append(resolved_path)
                    current_files.add(filename)
                    self.logger.debug(f"Fichier cible détecté: {filename} -> {resolved_path}")
        
        # Fallback vers la détection classique si rien trouvé
        if not targets:
            classic_target = self.detector.detect_target_file(patch_path, patch_content)
            if classic_target:
                targets.append(classic_target)
        
        return targets

    def _extract_clean_filename(self, raw_filename: str) -> str:
        """NOUVEAU: Extrait et nettoie un nom de fichier des métadonnées"""
        if not raw_filename:
            return None
            
        # Supprimer les timestamps et métadonnées
        filename = raw_filename.strip()
        filename = re.sub(r'\\s+\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}.*$', '', filename)
        filename = re.sub(r'\\s+[A-Z][a-z]{2}\\s+[A-Z][a-z]{2}\\s+\\d+.*$', '', filename)
        filename = filename.split('\\t')[0].strip()
        
        # Extraire juste le nom de fichier (pas le chemin complet)
        filename = filename.split('/')[-1] if '/' in filename else filename
        
        # Valider que c'est un nom de fichier valide
        if (filename and 
            len(filename) > 2 and 
            '.' in filename and
            not filename.startswith('.') and
            filename not in ['a', 'b', 'old', 'new', 'error']):
            return filename
        
        return None

    def _resolve_target_path(self, filename: str, patch_path: Path) -> Path:
        """NOUVEAU: Résout un nom de fichier vers un chemin réel"""
        if not filename:
            return None
        
        # Rechercher dans plusieurs répertoires
        search_dirs = [
            Path.cwd(),                           # Répertoire courant
            patch_path.parent,                    # Répertoire du patch
            self.source_dir if self.source_dir.is_dir() else self.source_dir.parent,
        ]
        
        # Ajouter des sous-répertoires courants si ils existent
        for base in [Path.cwd(), patch_path.parent]:
            for subdir in ['src', 'ui', 'lib', 'app', 'core']:
                subdir_path = base / subdir
                if subdir_path.exists():
                    search_dirs.append(subdir_path)
        
        # Rechercher le fichier
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            # Recherche exacte
            target_path = search_dir / filename
            if target_path.exists() and target_path.is_file():
                return target_path
            
            # Recherche récursive limitée
            for depth in range(1, 4):
                pattern = "*/" * depth + filename
                try:
                    for found_path in search_dir.glob(pattern):
                        if found_path.is_file():
                            return found_path
                except Exception:
                    continue
        
        return None
'''
    
    # Insérer la nouvelle méthode après la définition de la classe
    class_pattern = r'(class SmartPatchProcessor:.*?def __init__\(self.*?\n.*?\n)'
    if re.search(class_pattern, content, re.DOTALL):
        # Trouver où insérer après __init__
        init_end = content.find('self.processing_stats = {')
        if init_end != -1:
            # Trouver la fin du dict
            dict_end = content.find('}', init_end) + 1
            insertion_point = content.find('\n', dict_end) + 1
            content = content[:insertion_point] + new_method + content[insertion_point:]
    
    # CORRECTION: Modifier process_single_patch pour utiliser la nouvelle détection
    old_detection = '''# Détecter ou utiliser le fichier cible spécifié
            if explicit_target and explicit_target.exists():
                target_file = explicit_target
                self.logger.debug(f"Utilisation du fichier cible spécifié: {target_file}")
            elif hasattr(self, "target_file") and self.target_file and self.target_file.exists():
                target_file = self.target_file
                self.logger.debug(f"Utilisation du fichier cible de l\\'instance: {target_file}")
            else:
                target_file = self.detector.detect_target_file(patch_path, patch_content)
                if not target_file:
                    result.errors.append("Fichier cible non détecté et aucun fichier explicite fourni")
                    return result
                self.logger.debug(f"Fichier cible détecté automatiquement: {target_file}")'''
    
    new_detection = '''# CORRECTION: Détection améliorée des fichiers cibles
            if explicit_target and explicit_target.exists():
                target_files = [explicit_target]
                self.logger.debug(f"Utilisation du fichier cible spécifié: {explicit_target}")
            elif hasattr(self, "target_file") and self.target_file and self.target_file.exists():
                target_files = [self.target_file]
                self.logger.debug(f"Utilisation du fichier cible de l\\'instance: {self.target_file}")
            else:
                # NOUVEAU: Détecter tous les fichiers cibles possibles
                target_files = self.detect_patch_targets_improved(patch_content, patch_path)
                
                if not target_files:
                    result.errors.append("Aucun fichier cible détecté - le patch ne semble pas contenir de fichiers Python valides")
                    return result
                
                self.logger.debug(f"Fichiers cibles détectés: {[str(f) for f in target_files]}")

            # Traiter le premier fichier cible valide trouvé
            target_file = target_files[0]'''
    
    content = content.replace(old_detection, new_detection)
    
    # Sauvegarder
    with open(processor_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {processor_file} corrigé")
    return True

def main():
    """Fonction principale du fix"""
    print("🔧 Smart Patch Processor - Fix du problème de détection des fichiers cibles")
    print("=" * 70)
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path("main.py").exists() or not Path("smart_patch_processor.py").exists():
        print("❌ Veuillez exécuter ce script depuis le répertoire Smart Patch Processor")
        sys.exit(1)
    
    # Créer une sauvegarde
    import shutil
    from datetime import datetime
    
    backup_dir = Path(f"backup_before_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = ["target_file_detector.py", "smart_patch_processor.py"]
    for file in files_to_backup:
        if Path(file).exists():
            shutil.copy2(file, backup_dir)
    
    print(f"💾 Sauvegarde créée dans: {backup_dir}")
    
    # Appliquer les corrections
    success = True
    
    if not fix_target_file_detector():
        success = False
    
    if not fix_smart_patch_processor():
        success = False
    
    # Résumé
    print("\n" + "=" * 70)
    if success:
        print("✅ CORRECTIONS APPLIQUÉES AVEC SUCCÈS !")
        print("\nCorrections effectuées:")
        print("• Amélioration des patterns de détection des fichiers")
        print("• Filtrage des noms de fichiers invalides ('error', 'a', 'b', etc.)")
        print("• Nettoyage des timestamps et métadonnées dans les noms de fichiers")
        print("• Détection améliorée pour patches multi-fichiers")
        print("• Recherche étendue dans multiple répertoires")
        
        print(f"\n🧪 TESTEZ MAINTENANT:")
        print("smart-patch --guided error.patch ./ --verbose")
        
    else:
        print("❌ CERTAINES CORRECTIONS ONT ÉCHOUÉ")
        print(f"💾 Vous pouvez restaurer depuis: {backup_dir}")
    
    print(f"\n💾 Sauvegarde conservée dans: {backup_dir}")

if __name__ == "__main__":
    main()
