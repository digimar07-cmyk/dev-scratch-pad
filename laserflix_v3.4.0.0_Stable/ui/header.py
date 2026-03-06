"""
ui/header.py — Barra superior REFATORADA (Opção 1: Header Limpo).
Teto: 200 linhas.

UI/UX 2026 Best Practices:
- Hierarquia visual clara: Logo → Nav → Busca → Ação Primária → Menu
- Busca centralizada (mais acessível)
- Menu COLORIDO organizado por categorias lógicas
- Ação primária destacada (Importar)
- Redução de elementos visuais (8 vs 9)

F-04: Busca com debounce 300ms (performance + UX)
"""
import tkinter as tk
from tkinter import ttk
import threading

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
        self._search_timer = None  # F-04: Timer de debounce
        self._build(parent)

    def set_select_btn_active(self, active: bool) -> None:
        """Muda visual do botão ☑️ conforme modo de seleção."""
        if self._select_btn:
            self._select_btn.config(
                bg=ACCENT_RED   if active else "#444444",
                fg=FG_PRIMARY,
                text="✕ Seleção" if active else "☑️ Selecionar",
            )

    def _debounced_search(self) -> None:
        """
        F-04: Debounce 300ms — só busca após usuário parar de digitar.
        Cancela timer anterior se continuar digitando.
        """
        if self._search_timer:
            self._search_timer.cancel()
        
        self._search_timer = threading.Timer(0.3, self._cb["on_search"])
        self._search_timer.start()

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
        # CENTRO: Busca (mais acessível) + F-04 DEBOUNCE
        # ══════════════════════════════════════════════════════════════════
        search_frame = tk.Frame(hdr, bg="#000000")
        search_frame.pack(side="left", expand=True, padx=20)
        
        tk.Label(search_frame, text="🔍", bg="#000000",
                 fg=FG_PRIMARY, font=("Arial", 14)).pack(side="left", padx=5)
        
        self.search_var.trace_add("write", lambda *_: self._debounced_search())
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
        
        # MENU COLORIDO (ações secundárias agrupadas)
        self._build_colorful_menu(right_frame)

    def _build_colorful_menu(self, parent) -> None:
        """
        Menu COLORIDO organizado por categorias (UI/UX 2026).
        Cada categoria tem cor própria para fácil identificação visual.
        """
        menu_btn = tk.Menubutton(
            parent, text="⚙️ Ferramentas",
            bg="#444444", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=10,
        )
        menu_btn.pack(side="left")
        
        # Menu base (fundo escuro)
        m = tk.Menu(
            menu_btn, tearoff=0,
            bg="#1A1A1A", fg=FG_PRIMARY,
            font=("Arial", 10),
            activebackground=ACCENT_RED,
            activeforeground="#FFFFFF",
            relief="flat", borderwidth=1,
        )
        menu_btn["menu"] = m
        
        # ════════════════════════════════════
        # CATEGORIA 1: ANÁLISE IA (VERDE)
        # ════════════════════════════════════
        m.add_command(
            label="🤖 ANÁLISE IA",
            state="disabled",
            background="#0D4D0D",  # Verde escuro
            foreground="#88FF88",  # Verde claro
        )
        m.add_command(
            label="   🆕 Analisar apenas novos",
            command=self._cb["on_analyze_new"],
            foreground="#66DD66",  # Verde
        )
        m.add_command(
            label="   🔄 Reanalisar todos",
            command=self._cb["on_analyze_all"],
            foreground="#66DD66",
        )
        
        # ════════════════════════════════════
        # CATEGORIA 2: DESCRIÇÕES (AZUL)
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="📝 DESCRIÇÕES",
            state="disabled",
            background="#0D1D4D",  # Azul escuro
            foreground="#88BBFF",  # Azul claro
        )
        m.add_command(
            label="   📝 Gerar para novos",
            command=self._cb["on_desc_new"],
            foreground="#66AAFF",  # Azul
        )
        m.add_command(
            label="   📝 Gerar para todos",
            command=self._cb["on_desc_all"],
            foreground="#66AAFF",
        )
        
        # ════════════════════════════════════
        # CATEGORIA 3: SELEÇÃO (AMARELO)
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="☑️ SELEÇÃO",
            state="disabled",
            background="#4D4D0D",  # Amarelo escuro
            foreground="#FFFF88",  # Amarelo claro
        )
        m.add_command(
            label="   ☑️ Modo seleção em massa",
            command=self._cb["on_toggle_select"],
            foreground="#FFEE66",  # Amarelo
        )
        
        # ════════════════════════════════════
        # CATEGORIA 4: BANCO DE DADOS (ROXO)
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="📦 BANCO DE DADOS",
            state="disabled",
            background="#2D0D4D",  # Roxo escuro
            foreground="#CC88FF",  # Roxo claro
        )
        m.add_command(
            label="   📥 Importar banco",
            command=self._cb["on_import_db"],
            foreground="#BB77FF",  # Roxo
        )
        m.add_command(
            label="   💾 Exportar banco",
            command=self._cb["on_export_db"],
            foreground="#BB77FF",
        )
        m.add_command(
            label="   🔄 Backup manual",
            command=self._cb["on_backup"],
            foreground="#BB77FF",
        )
        
        # ════════════════════════════════════
        # CATEGORIA 5: CONFIGURAÇÕES (LARANJA)
        # ════════════════════════════════════
        m.add_separator()
        m.add_command(
            label="🛠️ CONFIGURAÇÕES",
            state="disabled",
            background="#4D2D0D",  # Laranja escuro
            foreground="#FFAA66",  # Laranja claro
        )
        m.add_command(
            label="   📦 Preparar pastas",
            command=self._cb["on_prepare_folders"],
            foreground="#FF9944",  # Laranja
        )
        m.add_command(
            label="   🤖 Configurar modelos IA",
            command=self._cb["on_model_settings"],
            foreground="#FF9944",
        )
