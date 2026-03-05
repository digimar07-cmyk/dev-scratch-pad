"""
ui/header.py — Barra superior REFATORADA (Opção 1: Header Limpo).
Teto: 180 linhas.

UI/UX 2026 Best Practices:
- Hierarquia visual clara: Logo → Nav → Busca → Ação Primária → Menu
- Busca centralizada (mais acessível)
- Menu organizado por categorias lógicas
- Ação primária destacada (Importar)
- Redução de elementos visuais (8 vs 9)
"""
import tkinter as tk
from tkinter import ttk

from config.settings import VERSION
from config.ui_constants import (
    BG_CARD,
    ACCENT_RED, ACCENT_GREEN,
    FG_PRIMARY, FG_TERTIARY,
)


class HeaderBar:
    """
    Callbacks em `cb`:
        on_filter(filter_type)
        on_search()
        on_import()
        on_analyze_new()  /  on_analyze_all()
        on_desc_new()     /  on_desc_all()
        on_prepare_folders() / on_import_db() / on_export_db()
        on_backup()       /  on_model_settings()
        on_toggle_select()   — ativa/desativa modo de seleção em massa
    """

    def __init__(self, parent: tk.Widget, cb: dict):
        self._cb = cb
        self._select_btn = None
        self.search_var = tk.StringVar()
        self._build(parent)

    def set_select_btn_active(self, active: bool) -> None:
        """Muda visual do botão ☑️ conforme modo de seleção."""
        if self._select_btn:
            self._select_btn.config(
                bg=ACCENT_RED   if active else "#444444",
                fg=FG_PRIMARY,
                text="✕ Seleção" if active else "☑️ Selecionar",
            )

    def _build(self, parent: tk.Widget) -> None:
        hdr = tk.Frame(parent, bg="#000000", height=70)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # ══════════════════════════════════════════════════════════════════
        # ESQUERDA: Logo + Navegação
        # ══════════════════════════════════════════════════════════════════
        left_frame = tk.Frame(hdr, bg="#000000")
        left_frame.pack(side="left", padx=20, pady=10)
        
        # Logo
        tk.Label(left_frame, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg=ACCENT_RED).pack(side="left")
        tk.Label(left_frame, text=f"v{VERSION}", font=("Arial", 9),
                 bg="#000000", fg=FG_TERTIARY).pack(side="left", padx=(8, 20))
        
        # Navegação (filtros rápidos)
        for label, ftype in [
            ("🏠",    "all"),
            ("⭐",       "favorite"),
            ("✓",       "done"),
            ("👍",      "good"),
            ("👎",      "bad"),
        ]:
            btn = tk.Button(
                left_frame, text=label,
                command=lambda f=ftype: self._cb["on_filter"](f),
                bg="#000000", fg=FG_PRIMARY, font=("Arial", 16),
                relief="flat", cursor="hand2", padx=8,
            )
            btn.pack(side="left", padx=3)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg=ACCENT_RED))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg=FG_PRIMARY))

        # ══════════════════════════════════════════════════════════════════
        # CENTRO: Busca (mais acessível)
        # ══════════════════════════════════════════════════════════════════
        search_frame = tk.Frame(hdr, bg="#000000")
        search_frame.pack(side="left", expand=True, padx=20)
        
        tk.Label(search_frame, text="🔍", bg="#000000",
                 fg=FG_PRIMARY, font=("Arial", 14)).pack(side="left", padx=5)
        
        self.search_var.trace_add("write", lambda *_: self._cb["on_search"]())
        tk.Entry(
            search_frame, textvariable=self.search_var,
            bg="#222222", fg=FG_PRIMARY, font=("Arial", 12),
            width=35, relief="flat", insertbackground=FG_PRIMARY,
            highlightthickness=1, highlightbackground="#444444", highlightcolor=ACCENT_RED,
        ).pack(side="left", ipady=6)

        # ══════════════════════════════════════════════════════════════════
        # DIREITA: Ação Primária + Menu Organizado
        # ══════════════════════════════════════════════════════════════════
        right_frame = tk.Frame(hdr, bg="#000000")
        right_frame.pack(side="right", padx=20, pady=10)
        
        # AÇÃO PRIMÁRIA: Importar (destacado)
        tk.Button(
            right_frame, text="📁 Importar Pastas",
            command=self._cb["on_import"],
            bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2", padx=18, pady=10,
        ).pack(side="left", padx=(0, 10))
        
        # MENU ORGANIZADO (ações secundárias agrupadas)
        self._build_organized_menu(right_frame)

    def _build_organized_menu(self, parent) -> None:
        """
        Menu organizado por categorias lógicas (UI/UX best practice).
        """
        menu_btn = tk.Menubutton(
            parent, text="⚙️ Ferramentas",
            bg="#444444", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=10,
        )
        menu_btn.pack(side="left")
        
        m = tk.Menu(menu_btn, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 10))
        menu_btn["menu"] = m
        
        # ════════════════════════════════════
        # CATEGORIA 1: ANÁLISE IA
        # ════════════════════════════════════
        m.add_command(
            label="🤖 ANÁLISE IA",
            state="disabled",
            background="#1A1A1A",
            foreground="#888888",
        )
        m.add_command(
            label="   🆕 Analisar apenas novos",
            command=self._cb["on_analyze_new"],
        )
        m.add_command(
            label="   🔄 Reanalisar todos",
            command=self._cb["on_analyze_all"],
        )
        
        # ════════════════════════════════════
        # CATEGORIA 2: DESCRIÇÕES
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="📝 DESCRIÇÕES",
            state="disabled",
            background="#1A1A1A",
            foreground="#888888",
        )
        m.add_command(
            label="   📝 Gerar para novos",
            command=self._cb["on_desc_new"],
        )
        m.add_command(
            label="   📝 Gerar para todos",
            command=self._cb["on_desc_all"],
        )
        
        # ════════════════════════════════════
        # CATEGORIA 3: SELEÇÃO
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="☑️ SELEÇÃO",
            state="disabled",
            background="#1A1A1A",
            foreground="#888888",
        )
        m.add_command(
            label="   ☑️ Modo seleção em massa",
            command=self._cb["on_toggle_select"],
        )
        
        # ════════════════════════════════════
        # CATEGORIA 4: BANCO DE DADOS
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="📦 BANCO DE DADOS",
            state="disabled",
            background="#1A1A1A",
            foreground="#888888",
        )
        m.add_command(
            label="   📥 Importar banco",
            command=self._cb["on_import_db"],
        )
        m.add_command(
            label="   💾 Exportar banco",
            command=self._cb["on_export_db"],
        )
        m.add_command(
            label="   🔄 Backup manual",
            command=self._cb["on_backup"],
        )
        
        # ════════════════════════════════════
        # CATEGORIA 5: CONFIGURAÇÕES
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="🛠️ CONFIGURAÇÕES",
            state="disabled",
            background="#1A1A1A",
            foreground="#888888",
        )
        m.add_command(
            label="   📦 Preparar pastas",
            command=self._cb["on_prepare_folders"],
        )
        m.add_command(
            label="   🤖 Configurar modelos IA",
            command=self._cb["on_model_settings"],
        )
