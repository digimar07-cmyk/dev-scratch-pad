# -*- coding: utf-8 -*-
"""
Classe principal da aplicação Laserflix
Reproduz EXATAMENTE o comportamento do v740 original
"""

import tkinter as tk

VERSION = "7.4.0"

class LaserflixApp(tk.Tk):
    """Aplicação principal do Laserflix - equivalente ao root + LaserflixNetflix do v740"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações EXATAS do v740 (linha 72-74)
        self.title(f"LASERFLIX {VERSION}")
        self.state('zoomed')
        self.configure(bg="#141414")
        
        # Placeholder para componentes futuros
        # No v740: folders, database, filters, etc serão migrados gradualmente
        # Por enquanto: janela funcional que abre maximizada com fundo correto
