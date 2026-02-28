# -*- coding: utf-8 -*-
"""
Serviço de cache de dados
"""

import json
from pathlib import Path

class CacheService:
    """Gerencia cache em disco"""
    
    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key):
        """Recupera item do cache"""
        pass
    
    def set(self, key, value):
        """Salva item no cache"""
        pass
    
    def clear(self):
        """Limpa todo o cache"""
        pass
