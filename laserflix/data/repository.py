# -*- coding: utf-8 -*-
"""
Repositório de dados (DAO)
"""

import json
from pathlib import Path

class Repository:
    """Persistência de dados da aplicação"""
    
    def __init__(self, data_file="data.json"):
        self.data_file = Path(data_file)
        self.data = self._load()
    
    def _load(self):
        """Carrega dados do arquivo"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save(self):
        """Salva dados no arquivo"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
