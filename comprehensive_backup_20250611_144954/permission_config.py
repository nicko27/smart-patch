"""Module permission_config.py - Classe PermissionConfig."""

from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class PermissionConfig:
    """Configuration pour la gestion des permissions"""
    respect_existing_permissions: bool = True
    preserve_permissions_on_copy: bool = True
    restore_permissions_on_error: bool = True
    default_file_mode: int = 0o644
    default_dir_mode: int = 0o755
    backup_file_mode: int = 0o600
    allow_permission_elevation: bool = False
    enable_permission_backup: bool = True
    backup_database_path: Path = Path('.permission_backup.db')
    auto_restore_on_failure: bool = True
    log_all_permission_changes: bool = True
