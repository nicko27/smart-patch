"""Module streaming_file_reader.py - Classe StreamingFileReader."""

from pathlib import Path
import mmap
import stat

from streaming_config import StreamingConfig
from circular_buffer import CircularBuffer

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
    
    def read_lines_streaming(self):
        """Lit ligne par ligne en streaming"""
        line_buffer = bytearray()
        
        for chunk in self.read_chunks():
            line_buffer.extend(chunk)
            
            while b'\n' in line_buffer:
                line_end = line_buffer.find(b'\n')
                line_bytes = bytes(line_buffer[:line_end + 1])
                
                try:
                    line_str = line_bytes.decode(self.config.default_encoding, 
                                               self.config.encoding_errors)
                    yield line_str
                except UnicodeDecodeError:
                    pass
                
                line_buffer = line_buffer[line_end + 1:]
        
        # Dernière ligne
        if line_buffer:
            try:
                line_str = line_buffer.decode(self.config.default_encoding,
                                            self.config.encoding_errors)
                yield line_str
            except UnicodeDecodeError:
                pass
    
    def get_file_size(self) -> int:
        return self._size
    
    def close(self):
        if self._mmap:
            self._mmap.close()
        if self._file_handle:
            self._file_handle.close()
