# -*- coding: utf-8 -*-
"""
Serviço de controle do player
"""

class PlayerService:
    """Gerencia reprodução de mídia"""
    
    def __init__(self):
        self.current_media = None
        self.is_playing = False
        self.position = 0
    
    def play(self, media_path):
        """Inicia reprodução"""
        pass
    
    def pause(self):
        """Pausa reprodução"""
        pass
    
    def stop(self):
        """Para reprodução"""
        pass
