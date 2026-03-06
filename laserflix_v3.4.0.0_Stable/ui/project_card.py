"""
ui/project_card.py — Renderiza um card de projeto.
Responsabilidade única: construir 1 card (frame + thumb + nome + badges).
Teto: 250 linhas.

F-08: Badges de coleções visíveis + clique para aplicar filtro
"""
import os
import tkinter as tk
from tkinter import Menu

from config.card_layout import CARD_W, CARD_H, COVER_H, CARD_PAD
from config.ui_constants import (
    BG_CARD, BG_CARD_HOVER, BG_SEL,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
    ACCENT_GREEN, ACCENT_GOLD, ORIGIN_COLORS,
)


def build_card(parent: tk.Widget, path: str, data: dict, cb: dict,
               row: int, col: int) -> None:
    """
    Constrói um card completo de projeto.
    
    Args:
        parent:  Container (ex: scrollable_frame)
        path:    Caminho absoluto do projeto
        data:    Dict com dados do projeto
        cb:      Dict de callbacks (on_open_modal, on_toggle_*, on_open_folder, etc.)
        row/col: Posição na grid
    
    Callbacks esperados:
        on_open_modal(path)
        on_toggle_favorite(path, btn), on_toggle_done(path, btn),
        on_toggle_good(path, btn), on_toggle_bad(path, btn)
        on_analyze_single(path)
        on_open_folder(path)
        on_set_category(cat_name)
        on_set_tag(tag_name)
        on_set_origin(origin_name)
        on_set_collection(collection_name)       # F-08: Click em badge de coleção
        get_cover_image_async(path, callback, widget)
        selection_mode (bool)
        selected_paths (set)
        on_toggle_select(path)
        
        # F-08: Callbacks de menu contextual de coleções
        on_add_to_collection(path, collection_name)
        on_remove_from_collection(path, collection_name)
        on_new_collection_with(path)
        get_collections() -> list[str]
        get_project_collections(path) -> list[str]
    """
    is_selected = (cb.get("selection_mode") and path in cb.get("selected_paths", set()))
    card_bg = BG_SEL if is_selected else BG_CARD
    
    card_frame = tk.Frame(parent, bg=card_bg, width=CARD_W, height=CARD_H, relief="flat", bd=0)
    card_frame.grid(row=row, column=col, padx=CARD_PAD, pady=CARD_PAD, sticky="n")
    card_frame.grid_propagate(False)
    card_frame.pack_propagate(False)

    # Thumbnail
    thumb_frame = tk.Frame(card_frame, bg="#0A0A0A", width=CARD_W, height=COVER_H)
    thumb_frame.pack(fill="x")
    thumb_frame.pack_propagate(False)
    thumb_lbl = tk.Label(thumb_frame, text="🖼️", font=("Arial", 40),
                         bg="#0A0A0A", fg="#1E1E1E", bd=0)
    thumb_lbl.place(relx=0.5, rely=0.5, anchor="center")

    # Se modo seleção, exibe checkbox sobreposto
    if cb.get("selection_mode"):
        chk_lbl = tk.Label(thumb_frame, text="☑️" if is_selected else "☐",
                           font=("Arial", 32), bg="#0A0A0A", fg=ACCENT_GREEN if is_selected else "#444444",
                           bd=0, cursor="hand2")
        chk_lbl.place(x=8, y=8)
        chk_lbl.bind("<Button-1>", lambda e: cb["on_toggle_select"](path))

    # Carrega thumb assíncrona
    def _set_thumb(p, photo):
        if p == path and thumb_lbl.winfo_exists():
            thumb_lbl.config(image=photo, text="")
            thumb_lbl.image = photo
    cb["get_cover_image_async"](path, _set_thumb, thumb_lbl)

    # Content
    content = tk.Frame(card_frame, bg=card_bg)
    content.pack(fill="both", expand=True, padx=12, pady=(10, 8))

    # Nome
    name_lbl = tk.Label(
        content, text=data.get("name", "Sem nome"),
        font=("Arial", 11, "bold"), bg=card_bg, fg=FG_PRIMARY,
        anchor="w", justify="left", wraplength=CARD_W - 30
    )
    name_lbl.pack(fill="x", pady=(0, 6))

    # Categorias (badges)
    cats_row = tk.Frame(content, bg=card_bg)
    cats_row.pack(fill="x", pady=(0, 4))
    cats = data.get("categories", []) or []
    if cats:
        for i, cat in enumerate(cats[:2]):
            tk.Label(cats_row, text=cat, font=("Arial", 8),
                     bg="#1E3A2F", fg=ACCENT_GREEN, padx=6, pady=3,
                     cursor="hand2").pack(side="left", padx=(0, 4))
        if len(cats) > 2:
            tk.Label(cats_row, text=f"+{len(cats)-2}", font=("Arial", 8),
                     bg="#2A2A2A", fg=FG_SECONDARY, padx=6, pady=3).pack(side="left")

    # Tags (badges)
    tags_row = tk.Frame(content, bg=card_bg)
    tags_row.pack(fill="x", pady=(0, 4))
    tags = data.get("tags", []) or []
    if tags:
        for i, tag in enumerate(tags[:2]):
            t = tk.Label(tags_row, text=tag, font=("Arial", 8),
                         bg="#2A2A2A", fg=FG_SECONDARY, padx=6, pady=3, cursor="hand2")
            t.pack(side="left", padx=(0, 4))
            t.bind("<Button-1>", lambda e, tg=tag: cb["on_set_tag"](tg))
        if len(tags) > 2:
            tk.Label(tags_row, text=f"+{len(tags)-2}", font=("Arial", 8),
                     bg="#2A2A2A", fg=FG_TERTIARY, padx=6, pady=3).pack(side="left")

    # Origem
    origin = data.get("origin", "Desconhecido")
    origin_color = ORIGIN_COLORS.get(origin, ORIGIN_COLORS["default"])
    o_badge = tk.Label(content, text=f"📂 {origin}", font=("Arial", 8),
                       bg=card_bg, fg=origin_color, anchor="w", cursor="hand2")
    o_badge.pack(fill="x", pady=(0, 4))
    o_badge.bind("<Button-1>", lambda e: cb["on_set_origin"](origin))

    # F-08: Coleções (badges clicáveis)
    project_collections = cb.get("get_project_collections", lambda p: [])(path)
    if project_collections:
        colls_row = tk.Frame(content, bg=card_bg)
        colls_row.pack(fill="x", pady=(0, 4))
        for i, coll_name in enumerate(project_collections[:2]):
            c = tk.Label(
                colls_row, text=coll_name,  # F-08: Remove 📁 de cada badge
                font=("Arial", 8),
                bg="#1A2A3A", fg="#88CCFF", padx=6, pady=3, cursor="hand2"
            )
            c.pack(side="left", padx=(0, 4))
            c.bind("<Button-1>", lambda e, cn=coll_name: cb["on_set_collection"](cn))
        if len(project_collections) > 2:
            tk.Label(colls_row, text=f"+{len(project_collections)-2}",
                     font=("Arial", 8), bg="#2A2A2A", fg=FG_TERTIARY,
                     padx=6, pady=3).pack(side="left")

    # Ícones de ação (embaixo)
    icons_row = tk.Frame(content, bg=card_bg)
    icons_row.pack(fill="x", pady=(4, 0))

    # Favorito
    is_fav = data.get("favorite", False)
    fav_btn = tk.Button(
        icons_row, text="⭐" if is_fav else "☆",
        bg=card_bg, fg=ACCENT_GOLD if is_fav else FG_TERTIARY,
        font=("Arial", 14), relief="flat", cursor="hand2", bd=0, padx=2, pady=0
    )
    fav_btn.config(command=lambda: cb["on_toggle_favorite"](path, fav_btn))
    fav_btn.pack(side="left", padx=(0, 2))

    # Feito
    is_done = data.get("done", False)
    done_btn = tk.Button(
        icons_row, text="✓" if is_done else "○",
        bg=card_bg, fg="#00FF00" if is_done else FG_TERTIARY,
        font=("Arial", 12), relief="flat", cursor="hand2", bd=0, padx=2, pady=0
    )
    done_btn.config(command=lambda: cb["on_toggle_done"](path, done_btn))
    done_btn.pack(side="left", padx=(0, 2))

    # Bom
    is_good = data.get("good", False)
    good_btn = tk.Button(
        icons_row, text="👍",
        bg=card_bg, fg="#00FF00" if is_good else FG_TERTIARY,
        font=("Arial", 12), relief="flat", cursor="hand2", bd=0, padx=2, pady=0
    )
    good_btn.config(command=lambda: cb["on_toggle_good"](path, good_btn))
    good_btn.pack(side="left", padx=(0, 2))

    # Ruim
    is_bad = data.get("bad", False)
    bad_btn = tk.Button(
        icons_row, text="👎",
        bg=card_bg, fg="#FF0000" if is_bad else FG_TERTIARY,
        font=("Arial", 12), relief="flat", cursor="hand2", bd=0, padx=2, pady=0
    )
    bad_btn.config(command=lambda: cb["on_toggle_bad"](path, bad_btn))
    bad_btn.pack(side="left", padx=(0, 2))

    # Menu contextual (gear)
    gear_btn = tk.Button(
        icons_row, text="⚙️", bg=card_bg, fg=FG_TERTIARY,
        font=("Arial", 12), relief="flat", cursor="hand2", bd=0, padx=2, pady=0
    )
    gear_btn.pack(side="right")

    def _show_context_menu(event):
        menu = Menu(card_frame, tearoff=0,
                    bg="#1A1A1A", fg=FG_PRIMARY, activebackground="#2A2A2A")
        menu.add_command(label="🔍 Ver Detalhes", command=lambda: cb["on_open_modal"](path))
        menu.add_command(label="📂 Abrir Pasta", command=lambda: cb["on_open_folder"](path))
        menu.add_command(label="🤖 Reanalisar", command=lambda: cb["on_analyze_single"](path))
        
        # F-08: Submenu de coleções
        if "get_collections" in cb:
            collections = cb["get_collections"]()
            if collections:
                menu.add_separator()
                colls_menu = Menu(menu, tearoff=0,
                                  bg="#1A1A1A", fg=FG_PRIMARY, activebackground="#2A2A2A")
                for coll in collections:
                    if path in cb.get("get_project_collections", lambda p: [])(path) and coll in cb.get("get_project_collections", lambda p: [])(path):
                        colls_menu.add_command(
                            label=f"✔️ {coll}",
                            command=lambda c=coll: cb["on_remove_from_collection"](path, c)
                        )
                    else:
                        colls_menu.add_command(
                            label=f"   {coll}",
                            command=lambda c=coll: cb["on_add_to_collection"](path, c)
                        )
                colls_menu.add_separator()
                colls_menu.add_command(
                    label="➕ Nova Coleção...",
                    command=lambda: cb["on_new_collection_with"](path)
                )
                menu.add_cascade(label="📁 Coleções", menu=colls_menu)
        
        menu.post(event.x_root, event.y_root)

    gear_btn.bind("<Button-1>", _show_context_menu)

    # Hover / Click
    for w in [card_frame, content, name_lbl, thumb_frame, thumb_lbl,
              cats_row, tags_row, o_badge, icons_row]:
        if w != icons_row and w != thumb_frame:
            w.bind("<Enter>", lambda e: card_frame.config(bg=BG_CARD_HOVER) or content.config(bg=BG_CARD_HOVER))
            w.bind("<Leave>", lambda e: card_frame.config(bg=card_bg) or content.config(bg=card_bg))
        if not cb.get("selection_mode"):
            w.bind("<Button-1>", lambda e: cb["on_open_modal"](path))
        else:
            w.bind("<Button-1>", lambda e: cb["on_toggle_select"](path))
