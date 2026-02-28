# -*- coding: utf-8 -*-
"""
Serviço de indexação de arquivos de mídia
"""

import os
from pathlib import Path

class MediaIndexer:
    """Varre e indexa arquivos de vídeo"""
    
    def __init__(self, base_paths):
        self.base_paths = base_paths
        self.catalog = []
    
    def scan(self):
        """Escaneia diretórios em busca de mídia"""
        pass
    
    def get_catalog(self):
        """Retorna catálogo indexado"""
        return self.catalog
