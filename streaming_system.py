from typing import Any, Dict, List, Optional, Tuple
"""
Système de streaming consolidé pour Smart Patch Processor
Regroupe: StreamingConfig, StreamingStats, CircularBuffer, StreamingFileReader, StreamingManager
"""

import logging
import threading
import mmap
import time
import weakref
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass

# ============================================================================
# CONFIGURATION ET STATS
# ============================================================================

@dataclass
class StreamingConfig:
    """Configuration pour le streaming de fichiers"""
    large_file_threshold_mb: int = 50
    huge_file_threshold_mb: int = 500
    default_chunk_size: int = 8192
    large_chunk_size: int = 65536
    huge_chunk_size: int = 1048576
    max_memory_usage_mb: int = 512
    buffer_pool_size: int = 10
    use_mmap: bool = True
    default_encoding: str = 'utf-8'
    encoding_errors: str = 'replace'

@dataclass
class StreamingStats:
    """Statistiques de performance du streaming"""
    files_processed: int = 0
    bytes_processed: int = 0
    streaming_files: int = 0
    mmap_files: int = 0
    memory_saved_mb: float = 0.0
    avg_processing_time_ms: float = 0.0

# ============================================================================
# BUFFER CIRCULAIRE
# ============================================================================

class CircularBuffer:
    """Buffer circulaire optimisé pour le streaming"""
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = bytearray(size)
        self.start = 0
        self.end = 0
        self.is_full = False
        self._lock = threading.Lock()
    
    def write(self, data: bytes) -> int:
        with self._lock:
            if not data or self.is_full:
                return 0
            
            data_len = min(len(data), self.size - self.available_data())
            if data_len == 0:
                return 0
            
            if self.end + data_len <= self.size:
                self.buffer[self.end:self.end + data_len] = data[:data_len]
                self.end = (self.end + data_len) % self.size
            else:
                first_part = self.size - self.end
                self.buffer[self.end:] = data[:first_part]
                self.buffer[:data_len - first_part] = data[first_part:data_len]
                self.end = data_len - first_part
            
            if self.end == self.start:
                self.is_full = True
            return data_len
    
    def read(self, size: int) -> bytes:
        with self._lock:
            if self.start == self.end and not self.is_full:
                return b''
            
            available = self.size if self.is_full else (self.end - self.start) % self.size
            to_read = min(size, available)
            
            if self.start + to_read <= self.size:
                result = bytes(self.buffer[self.start:self.start + to_read])
                self.start = (self.start + to_read) % self.size
            else:
                first_part = self.size - self.start
                result = bytes(self.buffer[self.start:] + self.buffer[:to_read - first_part])
                self.start = to_read - first_part
            
            self.is_full = False
            return result
    
    def available_data(self) -> int:
        if self.is_full:
            return self.size
        return (self.end - self.start) % self.size
    
    def clear(self):
        with self._lock:
            self.start = 0
            self.end = 0
            self.is_full = False

# ============================================================================
# LECTEUR DE FICHIER STREAMING
# ============================================================================

class StreamingFileReader:
    """Lecteur de fichier avec streaming intelligent"""
    
    def __init__(self, file_path: Path, config: StreamingConfig):
        self.file_path = file_path
        self.config = config
        self._file_handle = None
        self._mmap = None
        self._size = file_path.stat().st_size if file_path.exists() else 0
        self._use_mmap = (self._size > config.huge_file_threshold_mb * 1024 * 1024 
                         and config.use_mmap)
        self._buffer = CircularBuffer(config.large_chunk_size)
    
    def read_chunks(self, chunk_size: int = None):
        """Génère les chunks du fichier"""
        chunk_size = chunk_size or self.config.default_chunk_size
        
        if self._use_mmap:
            yield from self._read_chunks_mmap(chunk_size)
        else:
            yield from self._read_chunks_standard(chunk_size)
    
    def _read_chunks_mmap(self, chunk_size: int):
        """Lecture via mmap pour très gros fichiers"""
        try:
            with open(self.file_path, 'rb') as f:
                self._file_handle = f
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    self._mmap = mm
                    position = 0
                    
                    while position < len(mm):
                        chunk = mm[position:position + chunk_size]
                        position += len(chunk)
                        yield chunk
        finally:
            self._mmap = None
            self._file_handle = None
    
    def _read_chunks_standard(self, chunk_size: int):
        """Lecture standard avec buffer"""
        try:
            with open(self.file_path, 'rb') as f:
                self._file_handle = f
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        finally:
            self._file_handle = None
    
    def get_file_size(self) -> int:
        return self._size
    
    def close(self):
        if self._mmap:
            self._mmap.close()
        if self._file_handle:
            self._file_handle.close()

# ============================================================================
# GESTIONNAIRE DE STREAMING
# ============================================================================

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
