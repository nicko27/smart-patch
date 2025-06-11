"""Module colors.py - Classe Colors."""

class Colors:
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    END = '\033[0m'
    
    @classmethod
    def disable_colors(cls):
        """Désactiver toutes les couleurs"""
        for attr in dir(cls):
            if not attr.startswith('__') and attr != 'disable_colors':
                setattr(cls, attr, '')
