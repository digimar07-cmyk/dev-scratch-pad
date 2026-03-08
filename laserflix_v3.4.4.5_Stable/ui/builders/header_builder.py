"""
ui/builders/header_builder.py — Construtor de cabeçalho dinâmico.

FASE-1.2A: Extração do método _build_header() do main_window.py
Redução: ~30 linhas

Responsabilidades:
- Construir título dinâmico baseado em filtros ativos
- Integrar NavigationBuilder para controles de navegação
- Gerenciar layout do header frame
"""
import tkinter as tk
from config.card_layout import COLS
from config.ui_constants import BG_PRIMARY, FG_PRIMARY


class HeaderBuilder:
    """Construtor de cabeçalho com título dinâmico e navegação."""
    
    @staticmethod
    def build(parent, display_ctrl, cols=COLS):
        """
        Constrói cabeçalho com título dinâmico + navegação.
        
        Args:
            parent: Frame pai onde o header será inserido
            display_ctrl: DisplayController com estado dos filtros
            cols: Número de colunas do grid (padrão: COLS)
        
        Returns:
            Frame do header criado
        """
        # Calcular título baseado nos filtros ativos
        title = HeaderBuilder._build_title(display_ctrl)
        
        # Frame do header
        header_frame = tk.Frame(parent, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=cols, 
                         sticky="ew", padx=10, pady=(0, 5))
        
        # Label do título
        tk.Label(
            header_frame, 
            text=title,
            font=("Arial", 20, "bold"), 
            bg=BG_PRIMARY, 
            fg=FG_PRIMARY, 
            anchor="w"
        ).pack(side="left")
        
        # Navegação (se houver projetos filtrados)
        filtered_count = len(display_ctrl.get_filtered_projects())
        if filtered_count > 0:
            page_info = display_ctrl.get_page_info(filtered_count)
            HeaderBuilder._build_navigation(header_frame, page_info, display_ctrl)
        
        return header_frame
    
    @staticmethod
    def _build_title(display_ctrl):
        """
        Constrói título dinâmico baseado em filtros ativos.
        
        Args:
            display_ctrl: DisplayController com estado dos filtros
        
        Returns:
            String com título formatado
        """
        title_map = {
            "favorite": "⭐ Favoritos",
            "done": "✓ Já Feitos",
            "good": "👍 Bons",
            "bad": "👎 Ruins",
        }
        
        # Título base
        title = title_map.get(display_ctrl.current_filter, "Todos os Projetos")
        
        # Adicionar filtros ativos
        if display_ctrl.current_origin != "all":
            title += f" — {display_ctrl.current_origin}"
        
        if display_ctrl.current_categories:
            title += f" — {', '.join(display_ctrl.current_categories)}"
        
        if display_ctrl.current_tag:
            title += f" — #{display_ctrl.current_tag}"
        
        if display_ctrl.search_query:
            title += f' — "{display_ctrl.search_query}"'
        
        return title
    
    @staticmethod
    def _build_navigation(parent, page_info, display_ctrl):
        """
        Constrói controles de navegação usando NavigationBuilder.
        
        Args:
            parent: Frame pai onde a navegação será inserida
            page_info: Dicionário com informações da página
            display_ctrl: DisplayController para callbacks de navegação
        """
        from ui.builders.navigation_builder import NavigationBuilder
        NavigationBuilder.build(parent, page_info, display_ctrl)
