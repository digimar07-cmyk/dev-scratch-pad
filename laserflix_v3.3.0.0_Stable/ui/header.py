"""
ui/header.py — Barra superior completa do Laserflix.
Responsabilidade única: montar e retornar o frame do header.
Não acessa database, não guarda estado — só recebe callbacks.
Teto: 120 linhas. Se ultrapassar, algo está errado.
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
    Monta a barra superior e expõe self.search_var (StringVar)
    para que o main_window possa rastrear mudanças de busca.

    Callbacks esperados em `cb` (dict):
        on_filter(filter_type)          — botões Home/Favoritos/etc.
        on_search()                     — chamado a cada keystroke
        on_import()                     — botão Importar Pastas
        on_analyze_new()                — menu Análise > Apenas novos
        on_analyze_all()                — menu Análise > Reanalisar todos
        on_desc_new()                   — menu Descrições > Novos
        on_desc_all()                   — menu Descrições > Todos
        on_prepare_folders()            — menu ⚙️ > Preparar Pastas
        on_import_db()                  — menu ⚙️ > Importar Banco
        on_export_db()                  — menu ⚙️ > Exportar Banco
        on_backup()                     — menu ⚙️ > Backup Manual
        on_model_settings()             — menu ⚙️ > Configurar Modelos IA
    """

    def __init__(self, parent: tk.Widget, cb: dict):
        self._cb = cb
        self.search_var = tk.StringVar()
        self._build(parent)

    def _build(self, parent: tk.Widget) -> None:
        hdr = tk.Frame(parent, bg="#000000", height=70)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Logo + versão
        tk.Label(hdr, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg=ACCENT_RED).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text=f"v{VERSION}", font=("Arial", 10),
                 bg="#000000", fg=FG_TERTIARY).pack(side="left", padx=5)

        # Navegação principal
        nav = tk.Frame(hdr, bg="#000000")
        nav.pack(side="left", padx=30)
        for label, ftype in [
            ("\U0001f3e0 Home", "all"),
            ("⭐ Favoritos",   "favorite"),
            ("✓ Já Feitos",   "done"),
            ("👍 Bons",        "good"),
            ("👎 Ruins",       "bad"),
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

        # Área direita: extras → busca (empacotados da direita para esquerda)
        extras = tk.Frame(hdr, bg="#000000")
        extras.pack(side="right", padx=10)
        self._build_menu_btn(extras)
        self._build_import_btn(extras)
        self._build_ai_btn(extras)
        self._build_desc_btn(extras)

        # Campo de busca
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

    # ------------------------------------------------------------------
    # Helpers de construção (cada um ≤ 15 linhas)
    # ------------------------------------------------------------------

    def _build_menu_btn(self, parent: tk.Widget) -> None:
        mb = tk.Menubutton(parent, text="⚙️ Menu", bg="#444444",
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        mb.pack(side="left", padx=5)
        m = tk.Menu(mb, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY)
        mb["menu"] = m
        m.add_command(label="📦 Preparar Pastas",      command=self._cb["on_prepare_folders"])
        m.add_separator()
        m.add_command(label="📥 Importar Banco",       command=self._cb["on_import_db"])
        m.add_command(label="💾 Exportar Banco",       command=self._cb["on_export_db"])
        m.add_command(label="🔄 Backup Manual",        command=self._cb["on_backup"])
        m.add_separator()
        m.add_command(label="🤖 Configurar Modelos IA", command=self._cb["on_model_settings"])

    def _build_import_btn(self, parent: tk.Widget) -> None:
        tk.Button(
            parent, text="📁 Importar Pastas",
            command=self._cb["on_import"],
            bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=8,
        ).pack(side="left", padx=5)

    def _build_ai_btn(self, parent: tk.Widget) -> None:
        ab = tk.Menubutton(parent, text="🤖 Análise", bg=ACCENT_GREEN,
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        ab.pack(side="left", padx=5)
        am = tk.Menu(ab, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY,
                     activebackground=ACCENT_RED, activeforeground=FG_PRIMARY)
        ab["menu"] = am
        am.add_command(label="🆕 Analisar apenas novos", command=self._cb["on_analyze_new"])
        am.add_command(label="🔄 Reanalisar todos",      command=self._cb["on_analyze_all"])

    def _build_desc_btn(self, parent: tk.Widget) -> None:
        db = tk.Menubutton(parent, text="📝 Descrições", bg="#3A7BD5",
                           fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                           relief="flat", cursor="hand2", padx=15, pady=8)
        db.pack(side="left", padx=5)
        dm = tk.Menu(db, tearoff=0, bg=BG_CARD, fg=FG_PRIMARY,
                     activebackground=ACCENT_RED, activeforeground=FG_PRIMARY)
        db["menu"] = dm
        dm.add_command(label="📝 Gerar para novos", command=self._cb["on_desc_new"])
        dm.add_command(label="📝 Gerar para todos", command=self._cb["on_desc_all"])
