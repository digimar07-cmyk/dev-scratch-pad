"""
ui/header.py — Barra superior completa do Laserflix.
Teto: 150 linhas.

F-06: Dropdown de ordenação (Nome A-Z/Z-A, Data, Origem, Status)
      POSIÇÃO: DEPOIS da navegação, ANTES dos botões extras
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
        on_sort(sort_type)  ← F-06: NOVO
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
        self.sort_var = tk.StringVar(value="date_desc")  # ← F-06: Padrão = mais recentes
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

        # Logo
        tk.Label(hdr, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg=ACCENT_RED).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text=f"v{VERSION}", font=("Arial", 10),
                 bg="#000000", fg=FG_TERTIARY).pack(side="left", padx=5)

        # Navegação
        nav = tk.Frame(hdr, bg="#000000")
        nav.pack(side="left", padx=30)
        for label, ftype in [
            ("\U0001f3e0 Home", "all"),
            ("⭐ Favoritos",    "favorite"),
            ("✓ Já Feitos",    "done"),
            ("👍 Bons",         "good"),
            ("👎 Ruins",        "bad"),
        ]:
            btn = tk.Button(
                nav, text=label,
                command=lambda f=ftype: self._cb["on_filter"](f),
                bg="#000000", fg=FG_PRIMARY, font=("Arial", 12),
                relief="flat", cursor="hand2", padx=10,
            )
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg=ACCENT_RED))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg=FG_PRIMARY))

        # ══════════════════════════════════════════════════════════════════
        # F-06: DROPDOWN DE ORDENAÇÃO
        # POSIÇÃO: DEPOIS da navegação, ANTES dos botões extras
        # ══════════════════════════════════════════════════════════════════
        sort_frame = tk.Frame(hdr, bg="#000000")
        sort_frame.pack(side="left", padx=15)  # ← AQUI: lado esquerdo, depois da nav
        
        tk.Label(sort_frame, text="📊", bg="#000000",
                 fg=FG_TERTIARY, font=("Arial", 14)).pack(side="left", padx=(0, 5))
        
        # Combobox estilizado
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Sort.TCombobox",
            fieldbackground="#333333",
            background="#333333",
            foreground=FG_PRIMARY,
            arrowcolor=FG_PRIMARY,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Sort.TCombobox",
            fieldbackground=[("readonly", "#333333")],
            selectbackground=[("readonly", "#333333")],
            selectforeground=[("readonly", FG_PRIMARY)],
        )
        
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=[
                "date_desc",
                "date_asc",
                "name_asc",
                "name_desc",
                "origin",
                "analyzed",
                "not_analyzed",
            ],
            state="readonly",
            width=16,
            font=("Arial", 10),
            style="Sort.TCombobox",
        )
        sort_combo.pack(side="left")
        
        # Labels amigáveis
        sort_labels = {
            "date_desc":    "📅 Mais Recentes",
            "date_asc":     "📅 Mais Antigos",
            "name_asc":     "🔤 A→Z",
            "name_desc":    "🔥 Z→A",
            "origin":       "🏛️ Por Origem",
            "analyzed":     "🤖 Analisados",
            "not_analyzed": "⏳ Não Analisados",
        }
        
        def update_display(*args):
            current = self.sort_var.get()
            sort_combo.set(sort_labels.get(current, current))
            if "on_sort" in self._cb:
                self._cb["on_sort"](current)
        
        self.sort_var.trace_add("write", update_display)
        update_display()
        # ══════════════════════════════════════════════════════════════════

        # Busca (fica mais à direita)
        search_frm = tk.Frame(hdr, bg="#000000")
        search_frm.pack(side="right", padx=20)
        tk.Label(search_frm, text="🔍", bg="#000000",
                 fg=FG_PRIMARY, font=("Arial", 16)).pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *_: self._cb["on_search"]())
        tk.Entry(
            search_frm, textvariable=self.search_var,
            bg="#333333", fg=FG_PRIMARY, font=("Arial", 12),
            width=30, relief="flat", insertbackground=FG_PRIMARY,
        ).pack(side="left", padx=5, ipady=5)

        # Botões extras (IGUAIS AO ORIGINAL - SEM MUDANÇA)
        extras = tk.Frame(hdr, bg="#000000")
        extras.pack(side="right", padx=10)
        self._build_select_btn(extras)
        self._build_desc_btn(extras)
        self._build_ai_btn(extras)
        self._build_import_btn(extras)
        self._build_menu_btn(extras)

    def _build_menu_btn(self, parent) -> None:
        mb = tk.Menubutton(parent, text="⚙️ Menu", bg="#444444",
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        mb.pack(side="right", padx=5)
        m = tk.Menu(mb, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY)
        mb["menu"] = m
        m.add_command(label="📦 Preparar Pastas",       command=self._cb["on_prepare_folders"])
        m.add_separator()
        m.add_command(label="📥 Importar Banco",        command=self._cb["on_import_db"])
        m.add_command(label="💾 Exportar Banco",        command=self._cb["on_export_db"])
        m.add_command(label="🔄 Backup Manual",         command=self._cb["on_backup"])
        m.add_separator()
        m.add_command(label="🤖 Configurar Modelos IA", command=self._cb["on_model_settings"])

    def _build_import_btn(self, parent) -> None:
        tk.Button(parent, text="📁 Importar Pastas",
                  command=self._cb["on_import"],
                  bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  ).pack(side="right", padx=5)

    def _build_ai_btn(self, parent) -> None:
        ab = tk.Menubutton(parent, text="🤖 Análise", bg=ACCENT_GREEN,
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        ab.pack(side="right", padx=5)
        am = tk.Menu(ab, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY,
                     activebackground=ACCENT_RED, activeforeground=FG_PRIMARY)
        ab["menu"] = am
        am.add_command(label="🆕 Analisar apenas novos", command=self._cb["on_analyze_new"])
        am.add_command(label="🔄 Reanalisar todos",      command=self._cb["on_analyze_all"])

    def _build_desc_btn(self, parent) -> None:
        db = tk.Menubutton(parent, text="📝 Descrições", bg="#3A7BD5",
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        db.pack(side="right", padx=5)
        dm = tk.Menu(db, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY,
                     activebackground=ACCENT_RED, activeforeground=FG_PRIMARY)
        db["menu"] = dm
        dm.add_command(label="📝 Gerar para novos", command=self._cb["on_desc_new"])
        dm.add_command(label="📝 Gerar para todos", command=self._cb["on_desc_all"])

    def _build_select_btn(self, parent) -> None:
        self._select_btn = tk.Button(
            parent, text="☑️ Selecionar",
            command=self._cb["on_toggle_select"],
            bg="#444444", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=8,
        )
        self._select_btn.pack(side="right", padx=5)
