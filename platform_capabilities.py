"""Module platform_capabilities.py - Classe PlatformCapabilities."""

import os
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
import platform
class PlatformCapabilities:
    """Détecte les capacités de gestion des permissions selon la plateforme"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_unix_like = self.platform in ['linux', 'darwin', 'freebsd']
        self.is_windows = self.platform == 'windows'
        self.is_root = getattr(os, 'geteuid', lambda: 1)() == 0
        self.has_chmod = hasattr(os, 'chmod')
        self.has_chown = hasattr(os, 'chown')
        self.has_stat = hasattr(os, 'stat')
        self.has_pwd_grp = self._test_pwd_grp()
    
    def _test_pwd_grp(self) -> bool:
        try:
            import pwd, grp
            return True
        except ImportError:
            return False
    
    def get_supported_operations(self) -> Dict[str, bool]:
        return {
            'read_permissions': self.has_stat,
            'modify_permissions': self.has_chmod,
            'change_ownership': self.has_chown and self.is_root,
            'symbolic_links': self.is_unix_like,
            'special_bits': self.is_unix_like
        }
