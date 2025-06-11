"""Module streaming_config.py - Classe StreamingConfig."""

from dataclasses import dataclass, field

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
