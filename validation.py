"""
Module de validation d'entrée pour Smart Patch Processor
Centralise toutes les validations pour éviter les erreurs
"""

import os
from pathlib import Path
from typing import Union, Optional


class ValidationError(Exception):
    """Erreur de validation d'entrée"""
    pass


def validate_patch_content(original_content: str, diff_content: str) -> None:
    """Valide le contenu des patches"""
    if not isinstance(original_content, str):
        raise ValidationError(f"original_content must be string, got {type(original_content)}")
    
    if not isinstance(diff_content, str):
        raise ValidationError(f"diff_content must be string, got {type(diff_content)}")
    
    if len(diff_content.strip()) == 0:
        raise ValidationError("diff_content cannot be empty")
    
    # Vérifier que c'est un diff valide
    if not any(line.startswith(('@@', '---', '+++', '+', '-')) for line in diff_content.split('\n')):
        raise ValidationError("diff_content does not appear to be a valid diff")


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> Path:
    """Valide un chemin de fichier"""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    if not isinstance(file_path, Path):
        raise ValidationError(f"file_path must be string or Path, got {type(file_path)}")
    
    # Vérifier contre path traversal
    try:
        resolved = file_path.resolve()
        # Vérifier que le chemin résolu ne sort pas du répertoire de travail
        cwd = Path.cwd().resolve()
        resolved.relative_to(cwd)
    except ValueError:
        raise ValidationError(f"Unsafe path detected: {file_path}")
    
    if must_exist and not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    return file_path


def validate_config_section(config_dict: dict, section: str, required_keys: list = None) -> None:
    """Valide une section de configuration"""
    if not isinstance(config_dict, dict):
        raise ValidationError(f"Config must be dict, got {type(config_dict)}")
    
    if section not in config_dict:
        raise ValidationError(f"Missing config section: {section}")
    
    section_dict = config_dict[section]
    if not isinstance(section_dict, dict):
        raise ValidationError(f"Config section {section} must be dict, got {type(section_dict)}")
    
    if required_keys:
        missing = [key for key in required_keys if key not in section_dict]
        if missing:
            raise ValidationError(f"Missing required keys in {section}: {missing}")


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour éviter les problèmes de sécurité"""
    if not isinstance(filename, str):
        raise ValidationError(f"filename must be string, got {type(filename)}")
    
    # Supprimer les caractères dangereux
    import re
    cleaned = re.sub(r'[<>:"/\|?*]', '_', filename)
    
    # Supprimer les noms réservés Windows
    reserved = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    if cleaned.upper() in reserved:
        cleaned = f"_{cleaned}"
    
    # Limiter la longueur
    if len(cleaned) > 255:
        cleaned = cleaned[:255]
    
    return cleaned
