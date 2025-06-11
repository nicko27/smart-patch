from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module rollback_manager.py - Classe RollbackManager."""

import shutil
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from patch_processor_config import PatchProcessorConfig

class RollbackManager:
    """Gestionnaire de rollback pour annuler les modifications"""

    def __init__(self, config: PatchProcessorConfig):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.rollback')

        rollback_config = config.get_section('rollback')
        self.enabled = rollback_config.get('enabled', True)
        self.db_path = Path(rollback_config.get('database_path', '.smart_patch_rollback.db'))
        self.backup_dir = Path(rollback_config.get('backup_dir', '.rollback_backups'))

        if self.enabled:
            self._init_rollback_system()

    def _init_rollback_system(self):
        """Initialise le système de rollback"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            self._init_database()
        except Exception as e:
            self.logger.error(f"Erreur init rollback: {e}")
            self.enabled = False

    def _init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_file TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )"""
        conn.execute(create_table_sql)
        conn.commit()
        conn.close()

    def is_enabled(self) -> bool:
        return self.enabled

    def create_checkpoint(self, target_file: Path, patch_file: Path = None) -> Optional[int]:
        """Version legacy - utilisez create_checkpoint_secure"""
        return self.create_checkpoint_secure(target_file, patch_file)
    
    def create_checkpoint_secure(self, target_file: Path, patch_file: Path = None) -> Optional[int]:
        """Crée un point de sauvegarde avant modification"""
        if not self.enabled or not target_file.exists():
            return None

        try:
            timestamp = datetime.now().isoformat()
            backup_id = f"{timestamp.replace(':', '-')}_{target_file.name}"
            backup_path = self.backup_dir / backup_id

            # Créer la sauvegarde
            shutil.copy2(target_file, backup_path)

            # Enregistrer dans la base
            conn = sqlite3.connect(self.db_path)
            insert_sql = """
                INSERT INTO operations (timestamp, target_file, backup_path)
                VALUES (?, ?, ?)
            """
            conn.execute(insert_sql, (timestamp, str(target_file), str(backup_path)))

            operation_id = conn.lastrowid
            conn.commit()
            conn.close()

            return operation_id
        except Exception as e:
            self.logger.error(f"Erreur création checkpoint: {e}")
            return None

    def get_rollback_stats(self) -> Dict:
        """Statistiques du système de rollback"""
        if not self.enabled:
            return {'enabled': False}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('SELECT COUNT(*) FROM operations')
            total = cursor.fetchone()[0]
            conn.close()

            return {
                'enabled': True,
                'total_operations': total,
                'backup_directory': str(self.backup_dir)
            }
        except:
            return {'enabled': True, 'error': 'Database error'}

    def _check_disk_space(self, required_space: int) -> bool:
        """Vérifie l'espace disque disponible"""
        try:
            import shutil
            free_space = shutil.disk_usage(self.backup_dir).free
            return free_space > required_space * 2  # Marge de sécurité
        except Exception:
            return False
    
    def _verify_backup_integrity(self, original_file: Path, backup_file: Path) -> bool:
        """Vérifie l'intégrité du backup"""
        try:
            return (backup_file.exists() and 
                   backup_file.stat().st_size > 0 and
                   backup_file.stat().st_size == original_file.stat().st_size)
        except Exception:
            return False
    
    def create_checkpoint_secure(self, target_file: Path, patch_file: Path = None) -> Optional[int]:
        """Version sécurisée de create_checkpoint"""
        if not self.enabled or not target_file.exists():
            return None
        
        try:
            file_size = target_file.stat().st_size
            
            # Vérifier l'espace disque
            if not self._check_disk_space(file_size):
                self.logger.error("Espace disque insuffisant pour le backup")
                return None
            
            timestamp = datetime.now().isoformat()
            backup_id = f"{timestamp.replace(':', '-')}_{target_file.name}"
            backup_path = self.backup_dir / backup_id
            
            # Créer le backup avec vérification
            shutil.copy2(target_file, backup_path)
            
            # Vérifier l'intégrité
            if not self._verify_backup_integrity(target_file, backup_path):
                backup_path.unlink()  # Supprimer backup défaillant
                self.logger.error("Échec vérification intégrité backup")
                return None
            
            # Enregistrer avec verrous
            return self._save_to_database_safe(timestamp, target_file, backup_path)
            
        except Exception as e:
            self.logger.error(f"Erreur création checkpoint sécurisé: {e}")
            return None
    
    def _save_to_database_safe(self, timestamp: str, target_file: Path, backup_path: Path) -> Optional[int]:
        """Sauvegarde sécurisée en base de données"""
        try:
            import sqlite3
            import fcntl  # Pour les verrous sur Unix
            
            # Utiliser un verrou fichier pour éviter la corruption
            lock_file = self.db_path.with_suffix('.lock')
            
            with open(lock_file, 'w') as lock:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (OSError, ImportError):
                    # Fallback pour Windows ou si fcntl non disponible
                    pass
                
                conn = sqlite3.connect(str(self.db_path), timeout=30.0)
                try:
                    insert_sql = """
                        INSERT INTO operations (timestamp, target_file, backup_path, status)
                        VALUES (?, ?, ?, 'active')
                    """
                    conn.execute(insert_sql, (timestamp, str(target_file), str(backup_path)))
                    operation_id = conn.lastrowid
                    conn.commit()
                    return operation_id
                finally:
                    conn.close()
            
            # Nettoyer le verrou
            if lock_file.exists():
                lock_file.unlink()
                
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde base: {e}")
            return None