# -*- coding: utf-8 -*-
"""
Configurações e constantes da aplicação
"""

import os
from pathlib import Path

class Config:
    """Configurações centralizadas"""
    
    # App
    APP_NAME = "Laserflix"
    VERSION = "0.8.0"
    
    # Janela
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    
    # Caminhos
    BASE_DIR = Path(__file__).parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    ICONS_DIR = ASSETS_DIR / "icons"
    IMAGES_DIR = ASSETS_DIR / "images"
    
    # Media
    MEDIA_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]
    SUBTITLE_EXTENSIONS = [".srt", ".sub", ".ass"]
    
    # Cache
    CACHE_DIR = BASE_DIR / "cache"
    CACHE_ENABLED = True
