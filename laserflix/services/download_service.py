# -*- coding: utf-8 -*-
"""
Serviço de download de conteúdo (se aplicável)
"""

class DownloadService:
    """Gerencia downloads de mídia/metadados"""
    
    def __init__(self):
        self.queue = []
        self.current_download = None
    
    def add_to_queue(self, url, destination):
        """Adiciona item à fila de download"""
        pass
    
    def start(self):
        """Inicia processamento da fila"""
        pass
