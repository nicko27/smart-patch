from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module permission_manager.py - Classe PermissionManager."""

import os
import shutil
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
import stat

from permission_config import PermissionConfig
from permission_reader import PermissionReader
from platform_capabilities import PlatformCapabilities

class PermissionManager:
    """Gestionnaire des permissions de fichiers"""
    
    def __init__(self, config: PermissionConfig):
        self.config = config
        self.capabilities = PlatformCapabilities()
        self.reader = PermissionReader(self.capabilities)
        self.logger = logging.getLogger('smart_patch_processor.permissions.manager')
        
        if config.enable_permission_backup:
            self._init_backup_database()
    
    def _init_backup_database(self):
        with sqlite3.connect(self.config.backup_database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permission_backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    original_mode INTEGER NOT NULL,
                    original_owner_uid INTEGER NOT NULL,
                    original_group_gid INTEGER NOT NULL,
                    backup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    restore_time TIMESTAMP NULL,
                    change_reason TEXT,
                    restored BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()
    
    def ensure_file_writable(self, file_path: Path, backup_original: bool = True) -> bool:
        """S'assure qu'un fichier est accessible en écriture"""
        if not file_path.exists():
            return False
        
        # Vérifier l'accès actuel
        if os.access(file_path, os.W_OK):
            return True
        
        if not self.config.allow_permission_elevation:
            self.logger.warning(f"Écriture refusée pour {file_path}, élévation désactivée")
            return False
        
        # Sauvegarder les permissions originales
        if backup_original and self.config.enable_permission_backup:
            self.backup_permissions(file_path, "ensure_writable")
        
        try:
            current_permissions = self.reader.read_permissions(file_path)
            if not current_permissions:
                return False
            
            # Ajouter les permissions d'écriture pour le propriétaire
            new_mode = current_permissions.mode | stat.S_IWUSR
            os.chmod(file_path, new_mode)
            
            self.logger.info(f"Permissions d'écriture ajoutées à {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur modification permissions {file_path}: {e}")
            return False
    
    def backup_permissions(self, file_path: Path, reason: str = "") -> bool:
        """Sauvegarde les permissions actuelles d'un fichier"""
        if not self.config.enable_permission_backup:
            return False
        
        permissions = self.reader.read_permissions(file_path)
        if not permissions:
            return False
        
        try:
            with sqlite3.connect(self.config.backup_database_path) as conn:
                conn.execute('INSERT INTO permission_backups (file_path, original_mode, original_owner_uid, original_group_gid, change_reason) VALUES (?, ?, ?, ?, ?)', (
                    str(file_path),
                    permissions.mode,
                    permissions.owner_uid,
                    permissions.group_gid,
                    reason
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde permissions {file_path}: {e}")
            return False
    
    def restore_file_permissions(self, file_path: Path) -> bool:
        """Restaure les permissions d'un fichier depuis la sauvegarde"""
        if not self.config.enable_permission_backup:
            return False
        
        try:
            with sqlite3.connect(self.config.backup_database_path) as conn:
                cursor = conn.execute("SELECT original_mode, id FROM permission_backups WHERE file_path = ? AND restored = FALSE ORDER BY backup_time DESC LIMIT 1", (str(file_path),))
                
                backup_row = cursor.fetchone()
                if not backup_row:
                    return False
                
                original_mode, backup_id = backup_row
                
                # Restaurer les permissions
                os.chmod(file_path, original_mode)
                
                # Marquer comme restauré
                conn.execute("UPDATE permission_backups SET restored = TRUE, restore_time = CURRENT_TIMESTAMP WHERE id = ?", (backup_id,))
                conn.commit()
                
                self.logger.info(f"Permissions restaurées pour {file_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur restauration permissions {file_path}: {e}")
            return False
    
    @contextmanager
    def temporary_permissions(self, file_path: Path, temp_mode: int):
        """Context manager pour permissions temporaires"""
        original_permissions = self.reader.read_permissions(file_path)
        changed = False
        
        try:
            if original_permissions and original_permissions.mode != temp_mode:
                os.chmod(file_path, temp_mode)
                changed = True
            
            yield changed
            
        finally:
            if changed and original_permissions:
                os.chmod(file_path, original_permissions.mode)
    
    def copy_with_permissions(self, source_path: Path, dest_path: Path) -> bool:
        """Copie un fichier en préservant les permissions"""
        try:
            shutil.copy2(source_path, dest_path)
            
            if self.config.preserve_permissions_on_copy:
                source_permissions = self.reader.read_permissions(source_path)
                if source_permissions:
                    os.chmod(dest_path, source_permissions.mode)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur copie avec permissions {source_path} -> {dest_path}: {e}")
            return False
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des capacités de permissions"""
        return {
            'platform_capabilities': self.capabilities.get_supported_operations(),
            'backup_enabled': self.config.enable_permission_backup,
            'permission_elevation_allowed': self.config.allow_permission_elevation,
            'preserve_permissions_on_copy': self.config.preserve_permissions_on_copy
        }
