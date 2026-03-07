"""
ui/sidebar.py — Painel lateral do Laserflix.
Responsabilidade única: renderizar e atualizar a sidebar.
Nunca acessa o banco diretamente — recebe `database` via refresh().
Teto: 250 linhas.

F-08: Seção de Coleções (filtros + gerenciamento)
"""
import tkinter as tk
from tkinter import ttk

from config.ui_constants import (
    SIDEBAR_MAX_CATEGORIES, SIDEBAR_MAX_TAGS,
    BG_SECONDARY, BG_CARD, BG_SEPARATOR,
    ACCENT_RED,
    FG_PRIMARY, FG_TERTIARY,
    ORIGIN_COLORS,
    SCROLL_SPEED,
)


class SidebarPanel:
    """
    Callbacks esperados em `cb` (dict):
        on_origin(origin, btn)          — clique em origem
        on_category(cats_list, btn)     — clique em categoria
        on_tag(tag, btn)                — clique em tag
        on_more_categories()            — botão "+ Ver mais"
        on_collection(name, btn)        — F-08: clique em coleção
        on_manage_collections()         — F-08: botão "Gerenciar"
    """

    def __init__(self, parent: tk.Widget, cb: dict):
        self._cb = cb
        self._active_btn = None
        self._canvas = None
        self._content = None
        self._origins_frame = None
        self._collections_frame = None  # F-08: Nova seção
        self._categories_frame = None
        self._tags_frame = None
        self._collections_manager = None  # F-08: Referência ao manager
        self._build(parent)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self, database: dict, collections_manager=None) -> None:
        """
        Atualiza toda a sidebar com o banco atual. Chame sempre que o banco mudar.
        
        Args:
            database: Banco de dados de projetos
            collections_manager: F-08: Manager de coleções (opcional)
        """
        self._database = database
        self._collections_manager = collections_manager  # F-08
        self._update_origins()
        self._update_collections()  # F-08
        self._update_categories()
        self._update_tags()
        self._bind_scroll(self._content)

    def set_active_btn(self, btn) -> None:
        """Destaca o botão ativo e remove destaque do anterior."""
        try:
            if self._active_btn:
                self._active_btn.config(bg=BG_SECONDARY)
        except Exception:
            pass
        self._active_btn = btn
        try:
            if btn:
                btn.config(bg=ACCENT_RED)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Construção do layout
    # ------------------------------------------------------------------

    def _build(self, parent: tk.Widget) -> None:
        container = tk.Frame(parent, bg=BG_SECONDARY, width=250)
        container.pack(side="left", fill="both")
        container.pack_propagate(False)

        self._canvas = tk.Canvas(container, bg=BG_SECONDARY, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        self._content = tk.Frame(self._canvas, bg=BG_SECONDARY)
        self._content.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.create_window((0, 0), window=self._content, anchor="nw", width=230)
        self._canvas.configure(yscrollcommand=sb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / SCROLL_SPEED)), "units"),
        )

        # F-08: Adicionada seção Coleções entre Origem e Categorias
        for title, attr in [
            ("🌐 Origem",             "_origins_frame"),
            ("📁 Coleções",           "_collections_frame"),  # F-08: Nova seção
            ("📂 Categorias",          "_categories_frame"),
            ("🏷️ Tags Populares", "_tags_frame"),
        ]:
            tk.Label(self._content, text=title, font=("Arial", 14, "bold"),
                     bg=BG_SECONDARY, fg=FG_PRIMARY, anchor="w"
                     ).pack(fill="x", padx=15, pady=(15, 5))
            frame = tk.Frame(self._content, bg=BG_SECONDARY)
            frame.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, frame)
            tk.Frame(self._content, bg=BG_SEPARATOR, height=2).pack(fill="x", padx=10, pady=10)

        tk.Frame(self._content, bg=BG_SECONDARY, height=50).pack(fill="x")

    # ------------------------------------------------------------------
    # Atualização de cada seção
    # ------------------------------------------------------------------

    def _update_origins(self) -> None:
        for w in self._origins_frame.winfo_children():
            w.destroy()
        origins: dict = {}
        for d in self._database.values():
            o = d.get("origin", "Desconhecido")
            origins[o] = origins.get(o, 0) + 1
        for origin in sorted(origins):
            color = ORIGIN_COLORS.get(origin, ORIGIN_COLORS["default"])
            btn = tk.Button(
                self._origins_frame,
                text=f"{origin} ({origins[origin]})",
                bg=BG_SECONDARY, fg=color, font=("Arial", 10, "bold"),
                relief="flat", cursor="hand2", anchor="w", padx=15, pady=8,
            )
            btn.config(command=lambda o=origin, b=btn: self._cb["on_origin"](o, b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>",  lambda e, b=btn: b.config(bg=BG_CARD)     if b is not self._active_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SECONDARY) if b is not self._active_btn else None)
        self._bind_scroll(self._origins_frame)

    def _update_collections(self) -> None:
        """
        F-08: Atualiza seção de coleções.
        Lista todas as coleções com contador de projetos.
        Botão "Gerenciar" para abrir dialog.
        """
        for w in self._collections_frame.winfo_children():
            w.destroy()
        
        # Se não tem manager, mostra mensagem
        if not self._collections_manager:
            tk.Label(
                self._collections_frame,
                text="Aguardando...",
                bg=BG_SECONDARY, fg=FG_TERTIARY, font=("Arial", 10, "italic"),
                anchor="w", padx=15, pady=10
            ).pack(fill="x")
            return
        
        collections = self._collections_manager.get_all_collections()
        
        if not collections:
            tk.Label(
                self._collections_frame,
                text="Nenhuma coleção",
                bg=BG_SECONDARY, fg=FG_TERTIARY, font=("Arial", 10, "italic"),
                anchor="w", padx=15, pady=10
            ).pack(fill="x")
        else:
            for collection_name in collections:
                size = self._collections_manager.get_collection_size(collection_name)
                btn = tk.Button(
                    self._collections_frame,
                    text=f"📁 {collection_name} ({size})",
                    bg=BG_SECONDARY, fg="#88CCFF", font=("Arial", 10),
                    relief="flat", cursor="hand2", anchor="w", padx=15, pady=8,
                )
                btn.config(command=lambda n=collection_name, b=btn: self._cb["on_collection"](n, b))
                btn.pack(fill="x", pady=2)
                btn.bind("<Enter>",  lambda e, b=btn: b.config(bg=BG_CARD)     if b is not self._active_btn else None)
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SECONDARY) if b is not self._active_btn else None)
        
        # Botão "Gerenciar" sempre visível
        tk.Button(
            self._collections_frame,
            text="⚙️ Gerenciar",
            bg=BG_CARD, fg="#888888", font=("Arial", 9),
            relief="flat", cursor="hand2", anchor="w", padx=15, pady=6,
            command=self._cb["on_manage_collections"],
        ).pack(fill="x", pady=(4, 2))
        
        self._bind_scroll(self._collections_frame)

    def _update_categories(self) -> None:
        for w in self._categories_frame.winfo_children():
            w.destroy()
        all_cats: dict = {}
        for d in self._database.values():
            for c in d.get("categories", []):
                c = c.strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        if not all_cats:
            tk.Label(self._categories_frame, text="Nenhuma categoria",
                     bg=BG_SECONDARY, fg=FG_TERTIARY, font=("Arial", 10, "italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        for cat, count in cats_sorted[:SIDEBAR_MAX_CATEGORIES]:
            btn = tk.Button(
                self._categories_frame,
                text=f"{cat} ({count})",
                bg=BG_SECONDARY, fg="#CCCCCC", font=("Arial", 10),
                relief="flat", cursor="hand2", anchor="w", padx=15, pady=8,
            )
            btn.config(command=lambda c=cat, b=btn: self._cb["on_category"]([c], b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>",  lambda e, b=btn: b.config(bg=BG_CARD)     if b is not self._active_btn else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SECONDARY) if b is not self._active_btn else None)
        if len(cats_sorted) > SIDEBAR_MAX_CATEGORIES:
            tk.Button(
                self._categories_frame,
                text=f"+ Ver mais ({len(cats_sorted) - SIDEBAR_MAX_CATEGORIES})",
                bg=BG_CARD, fg="#888888", font=("Arial", 9),
                relief="flat", cursor="hand2", anchor="w", padx=15, pady=6,
                command=self._cb["on_more_categories"],
            ).pack(fill="x", pady=(4, 2))
        self._bind_scroll(self._categories_frame)

    def _update_tags(self) -> None:
        for w in self._tags_frame.winfo_children():
            w.destroy()
        tag_count: dict = {}
        for d in self._database.values():
            for t in d.get("tags", []):
                t = t.strip()
                if t:
                    tag_count[t] = tag_count.get(t, 0) + 1
        tags_sorted = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        if not tags_sorted:
            tk.Label(self._tags_frame, text="Nenhuma tag",
                     bg=BG_SECONDARY, fg=FG_TERTIARY, font=("Arial", 10, "italic"),
                     anchor="w", padx=15, pady=10).pack(fill="x")
            return
        for tag, count in tags_sorted[:SIDEBAR_MAX_TAGS]:
            btn = tk.Button(
                self._tags_frame,
                text=f"{tag} ({count})",
                bg=BG_SECONDARY, fg="#CCCCCC", font=("Arial", 10),
                relief="flat", cursor="hand2", anchor="w", padx=15, pady=6,
            )
            btn.config(command=lambda t=tag, b=btn: self._cb["on_tag"](t, b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg=BG_CARD))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg=BG_SECONDARY))
        self._bind_scroll(self._tags_frame)

    # ------------------------------------------------------------------
    # Scroll recursivo
    # ------------------------------------------------------------------

    def _bind_scroll(self, widget: tk.Widget) -> None:
        widget.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / SCROLL_SPEED)), "units"),
        )
        for child in widget.winfo_children():
            self._bind_scroll(child)
