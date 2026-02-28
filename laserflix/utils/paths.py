# -*- coding: utf-8 -*-
"""
Helpers de caminhos e diretórios
"""

import os
from pathlib import Path

def get_user_data_dir():
    """Retorna diretório de dados do usuário"""
    if os.name == 'nt':  # Windows
        base = Path(os.getenv('APPDATA'))
    else:  # Linux/Mac
        base = Path.home() / '.local' / 'share'
    
    app_dir = base / 'Laserflix'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def normalize_path(path):
    """Normaliza path para o SO atual"""
    return Path(path).resolve()
