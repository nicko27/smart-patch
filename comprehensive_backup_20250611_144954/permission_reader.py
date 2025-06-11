"""Module permission_reader.py - Classe PermissionReader."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
import pwd
import grp

from platform_capabilities import PlatformCapabilities
from file_permissions import FilePermissions

class PermissionReader:
    """Lecteur de permissions multi-plateforme"""
    
    def __init__(self, capabilities: PlatformCapabilities):
        self.capabilities = capabilities
        self.logger = logging.getLogger('smart_patch_processor.permissions.reader')
    
    def read_permissions(self, file_path: Path) -> Optional[FilePermissions]:
        if not file_path.exists():
            return None
        
        try:
            stat_result = file_path.stat()
            
            permissions = FilePermissions(
                path=file_path,
                mode=stat_result.st_mode,
                owner_uid=stat_result.st_uid,
                group_gid=stat_result.st_gid,
                is_directory=file_path.is_dir()
            )
            
            # Ajouter les noms si possible
            if self.capabilities.has_pwd_grp:
                try:
                    permissions.owner_name = pwd.getpwuid(stat_result.st_uid).pw_name
                    permissions.group_name = grp.getgrgid(stat_result.st_gid).gr_name
                except:
                    pass
            
            # Tester les accès
            permissions.is_readable = os.access(file_path, os.R_OK)
            permissions.is_writable = os.access(file_path, os.W_OK)
            permissions.is_executable = os.access(file_path, os.X_OK)
            
            return permissions
            
        except Exception as e:
            self.logger.error(f"Erreur lecture permissions {file_path}: {e}")
            return None
