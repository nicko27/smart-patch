"""Module file_permissions.py - Classe FilePermissions."""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
from datetime import datetime
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import stat
@dataclass
class FilePermissions:
    """Représentation des permissions d'un fichier"""
    path: Path
    mode: int
    owner_uid: int
    group_gid: int
    owner_name: Optional[str] = None
    group_name: Optional[str] = None
    is_readable: bool = False
    is_writable: bool = False
    is_executable: bool = False
    is_directory: bool = False
    last_checked: datetime = field(default_factory=datetime.now)
    
    @property
    def octal_mode(self) -> str:
        return oct(self.mode)[-3:]
    
    @property
    def symbolic_mode(self) -> str:
        mode_str = ""
        # Propriétaire
        mode_str += "r" if self.mode & stat.S_IRUSR else "-"
        mode_str += "w" if self.mode & stat.S_IWUSR else "-"
        mode_str += "x" if self.mode & stat.S_IXUSR else "-"
        # Groupe
        mode_str += "r" if self.mode & stat.S_IRGRP else "-"
        mode_str += "w" if self.mode & stat.S_IWGRP else "-"
        mode_str += "x" if self.mode & stat.S_IXGRP else "-"
        # Autres
        mode_str += "r" if self.mode & stat.S_IROTH else "-"
        mode_str += "w" if self.mode & stat.S_IWOTH else "-"
        mode_str += "x" if self.mode & stat.S_IXOTH else "-"
        return mode_str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': str(self.path),
            'mode': self.mode,
            'octal_mode': self.octal_mode,
            'symbolic_mode': self.symbolic_mode,
            'owner_uid': self.owner_uid,
            'group_gid': self.group_gid,
            'owner_name': self.owner_name,
            'group_name': self.group_name,
            'is_readable': self.is_readable,
            'is_writable': self.is_writable,
            'is_executable': self.is_executable,
            'is_directory': self.is_directory
        }
