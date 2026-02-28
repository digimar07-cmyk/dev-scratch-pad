# -*- coding: utf-8 -*-
"""
Estado compartilhado da aplicação
"""

class AppState:
    """Gerenciador de estado global da aplicação"""
    
    def __init__(self):
        self.current_page = None
        self.current_media = None
        self.library = []
        self.user_preferences = {}
        self.playback_history = []
    
    def set_current_page(self, page_name):
        """Define a página atual"""
        self.current_page = page_name
    
    def set_current_media(self, media):
        """Define a mídia em reprodução"""
        self.current_media = media
