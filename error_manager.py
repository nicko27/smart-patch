from typing import Any, List, Optional
"""
Gestionnaire d'erreurs centralisé pour Smart Patch Processor
"""

import logging
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ProcessorError:
    """Représente une erreur du processeur"""
    message: str
    severity: ErrorSeverity
    context: str
    timestamp: datetime
    exception: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.context}: {self.message}"


class ErrorManager:
    """Gestionnaire centralisé des erreurs"""
    
    def __init__(self):
        self.errors: List[ProcessorError] = []
        self.logger = logging.getLogger('smart_patch_processor.errors')
    
    def add_error(self, message: str, severity: ErrorSeverity, 
                  context: str, exception: Optional[Exception] = None) -> ProcessorError:
        """Ajoute une erreur au gestionnaire"""
        error = ProcessorError(
            message=message,
            severity=severity,
            context=context,
            timestamp=datetime.now(),
            exception=exception
        )
        
        self.errors.append(error)
        
        # Logger selon la sévérité
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(str(error))
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(str(error))
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(str(error))
        else:
            self.logger.info(str(error))
        
        return error
    
    def has_critical_errors(self) -> bool:
        """Vérifie s'il y a des erreurs critiques"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)
    
    def has_errors(self) -> bool:
        """Vérifie s'il y a des erreurs (non warnings)"""
        return any(e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR] for e in self.errors)
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ProcessorError]:
        """Récupère les erreurs par sévérité"""
        return [e for e in self.errors if e.severity == severity]
    
    def clear_errors(self) -> None:
        """Efface toutes les erreurs"""
        self.errors.clear()
    
    def get_summary(self) -> dict:
        """Résumé des erreurs"""
        return {
            'total': len(self.errors),
            'critical': len(self.get_errors_by_severity(ErrorSeverity.CRITICAL)),
            'errors': len(self.get_errors_by_severity(ErrorSeverity.ERROR)),
            'warnings': len(self.get_errors_by_severity(ErrorSeverity.WARNING)),
            'info': len(self.get_errors_by_severity(ErrorSeverity.INFO))
        }


# Instance globale du gestionnaire d'erreurs
error_manager = ErrorManager()


def handle_error(message: str, context: str, exception: Optional[Exception] = None, 
                critical: bool = False) -> ProcessorError:
    """Fonction helper pour gérer les erreurs"""
    severity = ErrorSeverity.CRITICAL if critical else ErrorSeverity.ERROR
    return error_manager.add_error(message, severity, context, exception)


def handle_warning(message: str, context: str) -> ProcessorError:
    """Fonction helper pour gérer les avertissements"""
    return error_manager.add_error(message, ErrorSeverity.WARNING, context)
