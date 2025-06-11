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

def validate_file_path_secure(file_path: Union[str, Path], must_exist: bool = True,
                             allowed_dirs: List[Path] = None) -> Path:
    """Validation sécurisée contre path traversal et autres attaques"""
    import os

    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not isinstance(file_path, Path):
        raise ValidationError(f"file_path must be string or Path, got {type(file_path)}")

    # Nettoyer le chemin de caractères dangereux
    str_path = str(file_path)
    dangerous_patterns = ['../', '..\\\\', '\\0', '|', ';', '&', '$', '`']
    for pattern in dangerous_patterns:
        if pattern in str_path:
            raise ValidationError(f"Dangerous pattern detected in path: {pattern}")

    # Vérifier contre path traversal avancé
    try:
        resolved = file_path.resolve()

        # Définir les répertoires autorisés
        if allowed_dirs is None:
            allowed_dirs = [
                Path.cwd(),
                Path.home() / '.config' / 'smart-patch',
                Path('/tmp') if os.name == 'posix' else Path.cwd() / 'temp'
            ]

        # Vérifier que le chemin est dans un répertoire autorisé
        is_allowed = False
        for allowed_dir in allowed_dirs:
            try:
                resolved.relative_to(allowed_dir.resolve())
                is_allowed = True
                break
            except ValueError:
                continue

        if not is_allowed:
            raise ValidationError(f"Path outside allowed directories: {resolved}")

        # Vérifications supplémentaires
        if resolved.is_symlink():
            # Vérifier que le lien symbolique pointe vers un endroit sûr
            target = resolved.readlink()
            if target.is_absolute():
                validate_file_path_secure(target, must_exist=False, allowed_dirs=allowed_dirs)

    except (OSError, ValueError) as e:
        raise ValidationError(f"Path validation failed: {e}")

    if must_exist and not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")

    return file_path

def validate_patch_content_secure(original_content: str, diff_content: str,
                                 max_size_mb: int = 50) -> None:
    """Validation sécurisée du contenu avec protection DoS"""
    import re

    # Validation de type
    if not isinstance(original_content, str):
        raise ValidationError(f"original_content must be string, got {type(original_content)}")

    if not isinstance(diff_content, str):
        raise ValidationError(f"diff_content must be string, got {type(diff_content)}")

    # Protection contre DoS par taille
    max_size_bytes = max_size_mb * 1024 * 1024
    if len(original_content.encode('utf-8')) > max_size_bytes:
        raise ValidationError(f"Original content too large (>{max_size_mb}MB)")

    if len(diff_content.encode('utf-8')) > max_size_bytes:
        raise ValidationError(f"Diff content too large (>{max_size_mb}MB)")

    # Validation de contenu
    if len(diff_content.strip()) == 0:
        raise ValidationError("diff_content cannot be empty")

    # Vérifier que c'est un diff valide avec protection ReDoS
    valid_patterns = [
        r'^@@',
        r'^---',
        r'^\+\+\+',
        r'^\+[^+]',
        r'^-[^-]',
        r'^ '
    ]

    lines = diff_content.split('\n')[:1000]  # Limiter pour éviter DoS
    has_valid_content = False

    for line in lines:
        if len(line) > 1000:  # Ligne suspecte
            continue
        for pattern in valid_patterns:
            if re.match(pattern, line):
                has_valid_content = True
                break
        if has_valid_content:
            break

    if not has_valid_content:
        raise ValidationError("diff_content does not appear to be a valid diff")

    # Détection de patterns suspects
    suspicious_patterns = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'subprocess\.',
        r'os\.system',
        r'shell=True'
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, diff_content, re.IGNORECASE):
            raise ValidationError(f"Suspicious pattern detected: {pattern}")

def sanitize_filename_secure(filename: str, max_length: int = 100) -> str:
    """Nettoyage sécurisé de nom de fichier"""
    import re
    import unicodedata

    if not isinstance(filename, str):
        raise ValidationError(f"filename must be string, got {type(filename)}")

    if len(filename) > max_length * 2:  # Protection contre les noms très longs
        raise ValidationError(f"Filename too long (>{max_length * 2} chars)")

    # Normaliser Unicode pour éviter les attaques de spoofing
    filename = unicodedata.normalize('NFKC', filename)

    # Supprimer caractères de contrôle et dangereux
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

    # Supprimer caractères dangereux pour les systèmes de fichiers
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Supprimer espaces multiples et début/fin
    filename = re.sub(r'\s+', ' ', filename).strip()

    # Vérifier contre noms réservés (étendus)
    reserved_names = {
        'windows': ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                   'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'],
        'unix': ['.', '..', '']
    }

    # Vérifier contre tous les noms réservés
    base_name = filename.split('.')[0].upper()
    if base_name in reserved_names['windows'] or filename in reserved_names['unix']:
        filename = f"safe_{filename}"

    # Limiter la longueur finale
    if len(filename) > max_length:
        name_part = filename[:max_length-10]
        ext_part = filename[max_length-10:] if '.' in filename else ''
        filename = name_part + ext_part

    # S'assurer qu'il reste quelque chose de valide
    if not filename or filename in ['.', '..']:
        filename = f"safe_file_{hash(original_filename) % 1000}"

    return filename
