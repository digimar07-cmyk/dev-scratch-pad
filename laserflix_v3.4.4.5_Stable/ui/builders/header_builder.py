"""
ui/builders/header_builder.py — Construtor de cabeçalho dinâmico.

FASE-1.2A: Extração do método _build_header() do main_window.py
FASE-1.2.1: Integração do label contador
Redução: ~34 linhas

Responsabilidades:
- Construir título dinâmico baseado em filtros ativos
- Integrar NavigationBuilder para controles de navegação
- Exibir contador de projetos (total + mostrando)
- Gerenciar layout do header frame
"""
import tkinter as tk
from config.card_layout import COLS
from config.ui_constants import BG_PRIMARY, FG_PRIMARY


class HeaderBuilder:
    """Construtor de cabeçalho com título dinâmico, contador e navegação."""
    
    @staticmethod
    def build(parent, display_ctrl, cols=COLS, total_count=None, showing_count=None):
        """
        Constrói cabeçalho completo com título, contador e navegação.
        
        Args:
            parent: Frame pai onde o header será inserido
            display_ctrl: DisplayController com estado dos filtros
            cols: Número de colunas do grid (padrão: COLS)
            total_count: Total de projetos filtrados (opcional)
            showing_count: Quantidade de projetos exibidos na página (opcional)
        
        Returns:
            Frame do header criado
        """
        # Calcular título baseado nos filtros ativos
        title = HeaderBuilder._build_title(display_ctrl)
        
        # Frame do header (row 0)
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
        
        # Contador de projetos (row 1)
        if total_count is not None and showing_count is not None:
            HeaderBuilder._build_counter(parent, total_count, showing_count, cols)
        
        return header_frame
    
    @staticmethod
    def _build_counter(parent, total_count, showing_count, cols):
        """
        Constrói label contador de projetos.
        
        Args:
            parent: Frame pai onde o contador será inserido
            total_count: Total de projetos filtrados
            showing_count: Quantidade de projetos exibidos na página
            cols: Número de colunas do grid
        """
        tk.Label(
            parent,
            text=f"{total_count} projeto(s) | Mostrando {showing_count} itens",
            font=("Arial", 11), 
            bg=BG_PRIMARY, 
            fg="#999999"
        ).grid(row=1, column=0, columnspan=cols, sticky="w", padx=10, pady=(0, 15))
    
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
