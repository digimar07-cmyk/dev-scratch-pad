"""
ui/builders/navigation_builder.py — Builder para controles de navegação e ordenação.

FASE-1.1: Extrai _build_navigation_controls() do main_window.py
Redução: ~67 linhas (11% do total)

Responsabilidades:
- Combobox de ordenação (data, nome, origem, análise)
- Botões de navegação (primeira, anterior, próxima, última página)
- Label de página atual
- Callbacks de mudança de ordenação
- Estados disabled baseados em paginação
"""

import tkinter as tk
from tkinter import ttk
from config.ui_constants import BG_PRIMARY, FG_PRIMARY, FG_TERTIARY, ACCENT_GOLD


class NavigationBuilder:
    """Builder estático para construir controles de navegação + ordenação."""
    
    @staticmethod
    def build(parent: tk.Frame, page_info: dict, display_ctrl) -> None:
        """
        Constrói controles de ordenação + navegação.
        
        Args:
            parent: Frame pai onde os controles serão adicionados
            page_info: Dict com current_page, total_pages
            display_ctrl: DisplayController com current_sort e set_sorting()
        """
        # Container principal (lado direito do header)
        right_controls = tk.Frame(parent, bg=BG_PRIMARY)
        right_controls.pack(side="right", padx=10)
        
        # === ORDENAÇÃO ===
        NavigationBuilder._build_sort_controls(right_controls, display_ctrl)
        
        # === NAVEGAÇÃO ===
        NavigationBuilder._build_pagination_controls(right_controls, page_info, display_ctrl)
    
    @staticmethod
    def _build_sort_controls(parent: tk.Frame, display_ctrl) -> None:
        """
        Constrói combobox de ordenação.
        
        Args:
            parent: Frame pai
            display_ctrl: DisplayController
        """
        sort_frame = tk.Frame(parent, bg=BG_PRIMARY)
        sort_frame.pack(side="left", padx=(0, 15))
        
        # Ícone
        tk.Label(
            sort_frame, 
            text="📊", 
            bg=BG_PRIMARY,
            fg=FG_TERTIARY, 
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        # Mapeamento de valores internos → labels visíveis
        sort_labels = {
            "date_desc": "📅 Recentes",
            "date_asc": "📅 Antigos",
            "name_asc": "🔤 A→Z",
            "name_desc": "🔥 Z→A",
            "origin": "🏛️ Origem",
            "analyzed": "🤖 Analisados",
            "not_analyzed": "⏳ Pendentes",
        }
        
        # Variável tkinter
        sort_var = tk.StringVar(value=display_ctrl.current_sort)
        
        # Estilo do combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Sort.TCombobox",
            fieldbackground="#222222",
            background="#222222",
            foreground=FG_PRIMARY,
            arrowcolor=FG_PRIMARY,
            borderwidth=0
        )
        style.map(
            "Sort.TCombobox",
            fieldbackground=[("readonly", "#222222")],
            selectbackground=[("readonly", "#222222")],
            selectforeground=[("readonly", FG_PRIMARY)]
        )
        
        # Combobox
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=sort_var,
            values=list(sort_labels.values()),
            state="readonly",
            width=14,
            font=("Arial", 9),
            style="Sort.TCombobox"
        )
        sort_combo.pack(side="left")
        sort_combo.set(sort_labels[display_ctrl.current_sort])
        
        # Callback de mudança
        def on_sort_change(event):
            selected_label = sort_combo.get()
            for key, label in sort_labels.items():
                if label == selected_label:
                    display_ctrl.set_sorting(key)
                    break
        
        sort_combo.bind("<<ComboboxSelected>>", on_sort_change)
    
    @staticmethod
    def _build_pagination_controls(parent: tk.Frame, page_info: dict, display_ctrl) -> None:
        """
        Constrói botões de navegação entre páginas.
        
        Args:
            parent: Frame pai
            page_info: Dict com current_page, total_pages
            display_ctrl: DisplayController
        """
        nav_frame = tk.Frame(parent, bg=BG_PRIMARY)
        nav_frame.pack(side="left")
        
        current_page = page_info["current_page"]
        total_pages = page_info["total_pages"]
        
        # Botão: Primeira página ⏮
        tk.Button(
            nav_frame,
            text="⏮",
            command=display_ctrl.first_page,
            bg="#333333",
            fg=FG_PRIMARY,
            font=("Arial", 9),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=3,
            state="normal" if current_page > 1 else "disabled"
        ).pack(side="left", padx=1)
        
        # Botão: Página anterior ◀
        tk.Button(
            nav_frame,
            text="◀",
            command=display_ctrl.prev_page,
            bg="#444444",
            fg=FG_PRIMARY,
            font=("Arial", 9),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=3,
            state="normal" if current_page > 1 else "disabled"
        ).pack(side="left", padx=1)
        
        # Label: Página atual
        tk.Label(
            nav_frame,
            text=f"Pág {current_page}/{total_pages}",
            bg=BG_PRIMARY,
            fg=ACCENT_GOLD,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=8)
        
        # Botão: Próxima página ▶
        tk.Button(
            nav_frame,
            text="▶",
            command=display_ctrl.next_page,
            bg="#444444",
            fg=FG_PRIMARY,
            font=("Arial", 9),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=3,
            state="normal" if current_page < total_pages else "disabled"
        ).pack(side="left", padx=1)
        
        # Botão: Última página ⏭
        tk.Button(
            nav_frame,
            text="⏭",
            command=display_ctrl.last_page,
            bg="#333333",
            fg=FG_PRIMARY,
            font=("Arial", 9),
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=3,
            state="normal" if current_page < total_pages else "disabled"
        ).pack(side="left", padx=1)
