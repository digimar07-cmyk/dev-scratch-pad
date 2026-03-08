"""
ui/builders/navigation_builder.py — Builder para controles de navegação e ordenação.

FASE-1B: Extrai _build_navigation_controls() de main_window.py
Redução: ~70 linhas do main_window.py

Responsabilidades:
- Construir combobox de ordenação
- Construir botões de navegação (⏮ ◀ ▶ ⏭)
- Construir label "Pág X/Y"
- Gerenciar callbacks de mudança
"""
import tkinter as tk
from tkinter import ttk

from config.ui_constants import BG_PRIMARY, FG_PRIMARY, FG_TERTIARY, ACCENT_GOLD


class NavigationBuilder:
    """Builder estático para controles de navegação/ordenação."""
    
    SORT_LABELS = {
        "date_desc": "📅 Recentes",
        "date_asc": "📅 Antigos",
        "name_asc": "🔤 A→Z",
        "name_desc": "🔥 Z→A",
        "origin": "🏛️ Origem",
        "analyzed": "🤖 Analisados",
        "not_analyzed": "⏳ Pendentes",
    }
    
    @staticmethod
    def build(parent: tk.Frame, page_info: dict, display_ctrl) -> None:
        """
        Constrói controles de ordenação + navegação.
        
        Args:
            parent: Frame pai onde inserir controles
            page_info: Dict com current_page, total_pages
            display_ctrl: DisplayController com métodos de navegação
        """
        right_controls = tk.Frame(parent, bg=BG_PRIMARY)
        right_controls.pack(side="right", padx=10)
        
        # Ordenação
        NavigationBuilder._build_sort_controls(right_controls, display_ctrl)
        
        # Navegação
        NavigationBuilder._build_nav_buttons(right_controls, page_info, display_ctrl)
    
    @staticmethod
    def _build_sort_controls(parent: tk.Frame, display_ctrl) -> None:
        """Constrói combobox de ordenação."""
        sort_frame = tk.Frame(parent, bg=BG_PRIMARY)
        sort_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(
            sort_frame, text="📊", bg=BG_PRIMARY,
            fg=FG_TERTIARY, font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        sort_var = tk.StringVar(value=display_ctrl.current_sort)
        
        # Estilo customizado
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
        
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=sort_var,
            values=list(NavigationBuilder.SORT_LABELS.values()),
            state="readonly",
            width=14,
            font=("Arial", 9),
            style="Sort.TCombobox"
        )
        sort_combo.pack(side="left")
        sort_combo.set(NavigationBuilder.SORT_LABELS[display_ctrl.current_sort])
        
        def on_sort_change(event):
            selected_label = sort_combo.get()
            for key, label in NavigationBuilder.SORT_LABELS.items():
                if label == selected_label:
                    display_ctrl.set_sorting(key)
                    break
        
        sort_combo.bind("<<ComboboxSelected>>", on_sort_change)
    
    @staticmethod
    def _build_nav_buttons(parent: tk.Frame, page_info: dict, display_ctrl) -> None:
        """Constrói botões de navegação."""
        nav_frame = tk.Frame(parent, bg=BG_PRIMARY)
        nav_frame.pack(side="left")
        
        current = page_info["current_page"]
        total = page_info["total_pages"]
        
        # Botão: Primeira página
        tk.Button(
            nav_frame, text="⏮",
            command=display_ctrl.first_page,
            bg="#333333", fg=FG_PRIMARY,
            font=("Arial", 9), relief="flat",
            cursor="hand2", padx=6, pady=3,
            state="normal" if current > 1 else "disabled"
        ).pack(side="left", padx=1)
        
        # Botão: Anterior
        tk.Button(
            nav_frame, text="◀",
            command=display_ctrl.prev_page,
            bg="#444444", fg=FG_PRIMARY,
            font=("Arial", 9), relief="flat",
            cursor="hand2", padx=6, pady=3,
            state="normal" if current > 1 else "disabled"
        ).pack(side="left", padx=1)
        
        # Label: Página atual
        tk.Label(
            nav_frame,
            text=f"Pág {current}/{total}",
            bg=BG_PRIMARY, fg=ACCENT_GOLD,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=8)
        
        # Botão: Próxima
        tk.Button(
            nav_frame, text="▶",
            command=display_ctrl.next_page,
            bg="#444444", fg=FG_PRIMARY,
            font=("Arial", 9), relief="flat",
            cursor="hand2", padx=6, pady=3,
            state="normal" if current < total else "disabled"
        ).pack(side="left", padx=1)
        
        # Botão: Última página
        tk.Button(
            nav_frame, text="⏭",
            command=display_ctrl.last_page,
            bg="#333333", fg=FG_PRIMARY,
            font=("Arial", 9), relief="flat",
            cursor="hand2", padx=6, pady=3,
            state="normal" if current < total else "disabled"
        ).pack(side="left", padx=1)
