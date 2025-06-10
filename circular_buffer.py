"""Module circular_buffer.py - Classe CircularBuffer."""

import threading
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
