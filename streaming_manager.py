"""Module streaming_manager.py - Classe StreamingManager."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
from contextlib import contextmanager
import time
import weakref
import stat

from streaming_stats import StreamingStats
from streaming_config import StreamingConfig
from streaming_file_reader import StreamingFileReader

class StreamingManager:
    """Gestionnaire du streaming de fichiers"""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.stats = StreamingStats()
        self.logger = logging.getLogger('smart_patch_processor.streaming')
        self._active_readers = weakref.WeakSet()
    
    def should_use_streaming(self, file_path: Path) -> bool:
        """Détermine si un fichier doit utiliser le streaming"""
        if not file_path.exists():
            return False
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        return file_size_mb > self.config.large_file_threshold_mb
    
    def create_reader(self, file_path: Path) -> StreamingFileReader:
        """Crée un lecteur streaming pour un fichier"""
        reader = StreamingFileReader(file_path, self.config)
        self._active_readers.add(reader)
        
        if self.should_use_streaming(file_path):
            self.stats.streaming_files += 1
            if reader._use_mmap:
                self.stats.mmap_files += 1
        
        return reader
    
    @contextmanager
    def streaming_context(self, file_path: Path):
        """Context manager pour gérer automatiquement un lecteur"""
        reader = None
        start_time = time.time()
        
        try:
            reader = self.create_reader(file_path)
            yield reader
        finally:
            if reader:
                processing_time = time.time() - start_time
                self.stats.files_processed += 1
                self.stats.bytes_processed += reader.get_file_size()
                self.stats.avg_processing_time_ms = (
                    (self.stats.avg_processing_time_ms * 0.9) +
                    (processing_time * 1000 * 0.1)
                )
                reader.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du streaming"""
        return {
            'files_processed': self.stats.files_processed,
            'bytes_processed': self.stats.bytes_processed,
            'streaming_files': self.stats.streaming_files,
            'mmap_files': self.stats.mmap_files,
            'memory_saved_mb': self.stats.memory_saved_mb,
            'avg_processing_time_ms': self.stats.avg_processing_time_ms
        }
