"""
virtual_scroll.py — Grid com renderização virtual para performance.

RENDERIZA APENAS CARDS VISÍVEIS:
  - Calcula quais cards estão na viewport atual
  - Renderiza ~30-40 cards por vez (em vez de 500+)
  - Recalcula ao fazer scroll
  - Scroll suave sem flicks

USO:
    grid = VirtualScrollGrid(parent_canvas, scrollable_frame, cols=4)
    grid.update_items(filtered_projects, card_builder_callback)
"""
import tkinter as tk
from typing import List, Tuple, Callable, Any
from config.card_layout import CARD_H, CARD_PAD


class VirtualScrollGrid:
    """
    Grid virtual que renderiza apenas cards visíveis.
    
    Performance:
      - 500 projetos: renderiza ~30 cards (10x mais rápido)
      - Scroll suave sem flicks
      - Memória constante (não cresce com mais projetos)
    """
    
    def __init__(self, canvas: tk.Canvas, container: tk.Frame, cols: int = 4):
        """
        Args:
            canvas: Canvas pai que contém o scroll
            container: Frame onde os cards serão renderizados
            cols: Número de colunas no grid
        """
        self.canvas    = canvas
        self.container = container
        self.cols      = cols
        
        # Estado
        self.items        = []  # Lista de (path, data)
        self.card_builder = None  # Callback para construir card
        self.visible_rows = set()  # Linhas atualmente renderizadas
        self.row_widgets  = {}  # Cache: {row: [widgets]}
        
        # Constantes
        self.SCROLL_PIXELS = 60   # Pixels por clique do mouse (mais suave)
        self.BUFFER_ROWS   = 2    # Linhas extras acima/abaixo
        self.HEADER_HEIGHT = 100  # Altura aproximada do header (title + contador)
        
        # Bind de scroll suave
        self._setup_smooth_scroll()
    
    def _setup_smooth_scroll(self) -> None:
        """
        Configura scroll suave (sem flicks).
        Reduz delta do mousewheel para movimento mais fluido.
        """
        def _smooth_scroll(event):
            # Delta original é ±120 por clique
            # Dividimos por SCROLL_PIXELS para suavizar
            delta_units = int(-1 * (event.delta / self.SCROLL_PIXELS))
            self.canvas.yview_scroll(delta_units, "units")
            # Atualiza cards visíveis após scroll (delay para suavidade)
            self.canvas.after(50, self._update_visible_cards)
            return "break"  # Previne propagação
        
        # Remove bindings antigos
        self.canvas.unbind_all("<MouseWheel>")
        
        # Novo binding suave
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind("<MouseWheel>", _smooth_scroll))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind("<MouseWheel>"))
    
    def update_items(self, items: List[Tuple[str, dict]], card_builder: Callable) -> None:
        """
        Atualiza lista de items e renderiza cards visíveis.
        
        Args:
            items: Lista de tuplas (project_path, project_data)
            card_builder: Callback(container, path, data, row, col) -> widget
        """
        self.items        = items
        self.card_builder = card_builder
        
        # Limpa cache de widgets antigos
        self._clear_all_widgets()
        
        # Calcula altura total do grid
        total_rows = (len(items) + self.cols - 1) // self.cols  # Ceil division
        cards_height = total_rows * (CARD_H + CARD_PAD * 2)
        total_height = self.HEADER_HEIGHT + cards_height + 100  # +100 margem final
        
        # Ajusta scrollregion do canvas
        self.canvas.configure(scrollregion=(0, 0, 1, total_height))
        
        # Renderiza cards visíveis iniciais
        self._update_visible_cards()
    
    def _update_visible_cards(self) -> None:
        """
        Recalcula quais linhas estão visíveis e renderiza apenas essas.
        Chamado após scroll ou update_items().
        
        BUGFIX HOT-04: Agora considera offset do header corretamente.
        """
        if not self.items or not self.card_builder:
            return
        
        # Obtém viewport atual do canvas
        try:
            scroll_top    = self.canvas.yview()[0]  # Fração 0.0-1.0
            scroll_bottom = self.canvas.yview()[1]
            
            # Obtém altura total do scrollregion
            scrollregion  = self.canvas.cget("scrollregion").split()
            if len(scrollregion) < 4:
                return  # Canvas não está pronto
            
            total_height = int(scrollregion[3])
            
            # Converte fração em pixels absolutos
            visible_top_px    = scroll_top * total_height
            visible_bottom_px = scroll_bottom * total_height
            
        except (tk.TclError, ValueError, ZeroDivisionError):
            # Fallback: renderiza primeiras linhas
            self._render_initial_cards()
            return
        
        # ← BUGFIX: Subtrai offset do header ANTES de calcular linhas
        cards_start_px = self.HEADER_HEIGHT
        
        # Apenas renderiza se scroll passou do header
        if visible_bottom_px < cards_start_px:
            return  # Ainda no header
        
        # Ajusta viewport para coordenadas relativas aos cards
        cards_top_px    = max(0, visible_top_px - cards_start_px)
        cards_bottom_px = visible_bottom_px - cards_start_px
        
        # Calcula linhas visíveis (com buffer)
        row_height = CARD_H + CARD_PAD * 2
        first_visible_row = max(0, int(cards_top_px / row_height) - self.BUFFER_ROWS)
        last_visible_row  = int(cards_bottom_px / row_height) + self.BUFFER_ROWS
        
        # Total de linhas
        total_rows = (len(self.items) + self.cols - 1) // self.cols
        last_visible_row = min(last_visible_row, total_rows - 1)
        
        # Linhas que devem estar renderizadas
        target_rows = set(range(first_visible_row, last_visible_row + 1))
        
        # Remove linhas que saíram da viewport
        rows_to_remove = self.visible_rows - target_rows
        for row in rows_to_remove:
            self._destroy_row(row)
        
        # Adiciona linhas que entraram na viewport
        rows_to_add = target_rows - self.visible_rows
        for row in sorted(rows_to_add):  # Renderiza em ordem
            self._render_row(row)
        
        self.visible_rows = target_rows
    
    def _render_initial_cards(self) -> None:
        """
        Renderiza primeiras ~3 linhas (fallback quando canvas não está pronto).
        """
        total_rows = (len(self.items) + self.cols - 1) // self.cols
        initial_rows = min(3, total_rows)
        
        for row in range(initial_rows):
            self._render_row(row)
        
        self.visible_rows = set(range(initial_rows))
    
    def _render_row(self, row: int) -> None:
        """
        Renderiza uma linha específica do grid.
        
        Args:
            row: Índice da linha (0-based, sem contar header)
        """
        if row in self.row_widgets:
            return  # Já renderizada
        
        widgets = []
        start_idx = row * self.cols
        end_idx   = min(start_idx + self.cols, len(self.items))
        
        for col_offset, idx in enumerate(range(start_idx, end_idx)):
            if idx >= len(self.items):
                break
            
            project_path, project_data = self.items[idx]
            
            # Callback build_card com callbacks fechados (closure)
            widget = self.card_builder(
                self.container, 
                project_path, 
                project_data, 
                row + 2,  # +2 para pular header (rows 0-1)
                col_offset
            )
            widgets.append(widget)
        
        self.row_widgets[row] = widgets
    
    def _destroy_row(self, row: int) -> None:
        """
        Remove widgets de uma linha específica.
        
        Args:
            row: Índice da linha a remover
        """
        if row not in self.row_widgets:
            return
        
        for widget in self.row_widgets[row]:
            if widget and widget.winfo_exists():
                widget.destroy()
        
        del self.row_widgets[row]
    
    def _clear_all_widgets(self) -> None:
        """
        Limpa todos os widgets renderizados e cache.
        Usado antes de update_items().
        """
        for row in list(self.row_widgets.keys()):
            self._destroy_row(row)
        
        self.visible_rows.clear()
        self.row_widgets.clear()
    
    def refresh(self) -> None:
        """
        Força recalculo de cards visíveis.
        Útil após mudanças de estado (favorito, done, etc).
        """
        self._update_visible_cards()
    
    def scroll_to_top(self) -> None:
        """
        Scrolla para o topo do grid.
        """
        self.canvas.yview_moveto(0)
        self.canvas.after(50, self._update_visible_cards)
