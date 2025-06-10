"""Module rollback_manager.py - Classe RollbackManager."""

import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
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
        create_table_sql = " CREATE TABLE IF NOT EXISTS operations (id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT NOT NULL,target_file TEXT NOT NULL,backup_path TEXT NOT NULL, status TEXT DEFAULT 'active')"
        conn.execute(create_table_sql)
        conn.commit()
        conn.close()
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def create_checkpoint(self, target_file: Path, patch_file: Path = None) -> Optional[int]:
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
