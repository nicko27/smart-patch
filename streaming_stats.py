"""Module streaming_stats.py - Classe StreamingStats."""

from dataclasses import dataclass, field
@dataclass
class StreamingStats:
    """Statistiques de performance du streaming"""
    files_processed: int = 0
    bytes_processed: int = 0
    streaming_files: int = 0
    mmap_files: int = 0
    memory_saved_mb: float = 0.0
    avg_processing_time_ms: float = 0.0
