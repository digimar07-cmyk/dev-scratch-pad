"""LASERFLIX v7.4.0 — UI Components
Componentes reutilizáveis de interface
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List


class StatusBar:
    """Barra de status com progressbar"""
    
    def __init__(self, parent, bg="#000000", height=50):
        self.frame = tk.Frame(parent, bg=bg, height=height)
        self.frame.pack(side="bottom", fill="x")
        self.frame.pack_propagate(False)
        
        self.label = tk.Label(
            self.frame,
            text="Pronto",
            bg=bg,
            fg="#FFFFFF",
            font=("Arial", 10),
            anchor="w"
        )
        self.label.pack(side="left", padx=10, fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#2A2A2A",
            background="#1DB954",
            bordercolor="#000000",
            lightcolor="#1DB954",
            darkcolor="#1DB954"
        )
        
        self.progress_bar = ttk.Progressbar(
            self.frame,
            mode="determinate",
            length=300,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.pack_forget()
        
        self.stop_button = tk.Button(
            self.frame,
            text="⏹ Parar Análise",
            bg="#E50914",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        )
        self.stop_button.pack(side="right", padx=10)
        self.stop_button.pack_forget()
    
    def set_text(self, text: str):
        """Atualiza texto da barra de status"""
        self.label.config(text=text)
    
    def show_progress(self):
        """Mostra progressbar e botão de parar"""
        self.progress_bar.pack(side="left", padx=10)
        self.stop_button.pack(side="right", padx=10)
        self.progress_bar["value"] = 0
    
    def hide_progress(self):
        """Esconde progressbar e botão de parar"""
        self.progress_bar.pack_forget()
        self.stop_button.pack_forget()
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Atualiza barra de progresso"""
        percentage = (current / total) * 100
        self.progress_bar["value"] = percentage
        self.set_text(f"{message} ({current}/{total} — {percentage:.1f}%)")
    
    def bind_stop(self, callback: Callable):
        """Vincula callback ao botão de parar"""
        self.stop_button.config(command=callback)


class NavigationBar:
    """Barra de navegação superior"""
    
    def __init__(self, parent, bg="#000000"):
        self.frame = tk.Frame(parent, bg=bg)
        
        self.buttons = {}
    
    def add_button(self, text: str, command: Callable, key: str = None):
        """Adiciona botão de navegação"""
        if key is None:
            key = text
        
        btn = tk.Button(
            self.frame,
            text=text,
            command=command,
            bg="#000000",
            fg="#FFFFFF",
            font=("Arial", 12),
            relief="flat",
            cursor="hand2",
            padx=10
        )
        btn.pack(side="left", padx=5)
        btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
        btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))
        
        self.buttons[key] = btn
        return btn
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)


class CategoryTag:
    """Tag de categoria colorida"""
    
    COLORS = [
        "#FF6B6B",  # Vermelho
        "#4ECDC4",  # Azul turquesa
        "#95E1D3",  # Verde água
        "#9B59B6",  # Roxo
        "#F7DC6F",  # Amarelo
    ]
    
    @staticmethod
    def create(parent, text: str, index: int = 0, command: Optional[Callable] = None):
        """Cria tag de categoria"""
        color = CategoryTag.COLORS[index % len(CategoryTag.COLORS)]
        
        btn = tk.Button(
            parent,
            text=text[:12],
            bg=color,
            fg="#000000",
            font=("Arial", 8, "bold"),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=3
        )
        
        if command:
            btn.config(command=command)
        
        # Hover effect
        def darken(hex_color):
            hex_color = hex_color.lstrip("#")
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"
        
        dark_color = darken(color)
        btn.bind("<Enter>", lambda e: btn.config(bg=dark_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        
        return btn


class ProjectTag:
    """Tag simples de projeto"""
    
    @staticmethod
    def create(parent, text: str, command: Optional[Callable] = None):
        """Cria tag de projeto"""
        display_text = (text[:10] + "...") if len(text) > 12 else text
        
        btn = tk.Button(
            parent,
            text=display_text,
            bg="#3A3A3A",
            fg="#FFFFFF",
            font=("Arial", 8),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=2
        )
        
        if command:
            btn.config(command=command)
        
        btn.bind("<Enter>", lambda e: btn.config(bg="#E50914"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#3A3A3A"))
        
        return btn


class ActionButton:
    """Botão de ação com ícone"""
    
    @staticmethod
    def create(
        parent,
        icon: str,
        command: Callable,
        active_color: str = "#1DB954",
        inactive_color: str = "#666666",
        is_active: bool = False
    ):
        """Cria botão de ação"""
        btn = tk.Button(
            parent,
            text=icon,
            font=("Arial", 14),
            command=command,
            bg="#2A2A2A",
            fg=active_color if is_active else inactive_color,
            relief="flat",
            cursor="hand2"
        )
        
        btn.bind("<Enter>", lambda e: btn.config(bg="#3A3A3A"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#2A2A2A"))
        
        return btn
