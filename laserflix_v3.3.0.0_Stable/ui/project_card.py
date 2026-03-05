"""
ui/project_card.py — Factory de card de projeto.
Função pura. Teto: 150 linhas.
"""
import tkinter as tk

from config.card_layout import CARD_W, CARD_H, COVER_H, CARD_PAD
from config.ui_constants import (
    CARD_NAME_MAX_LENGTH, CARD_NAME_TRUNCATE_AT,
    CARD_TAG_MAX_LENGTH, CARD_TAG_TRUNCATE_AT,
    CARD_CATEGORY_MAX_LENGTH,
    CARD_MAX_CATEGORIES, CARD_MAX_TAGS,
    BG_CARD, BG_SECONDARY,
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_TERTIARY,
    ORIGIN_COLORS, CATEGORY_COLORS,
    CARD_BANNED_STRINGS,
)


def _darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,int(r*.8)):02x}{max(0,int(g*.8)):02x}{max(0,int(b*.8)):02x}"


def build_card(
    parent: tk.Widget,
    project_path: str,
    data: dict,
    cb: dict,
    row: int,
    col: int,
    pad: int = CARD_PAD,
) -> None:
    selection_mode  = cb.get("selection_mode", False)
    selected_paths  = cb.get("selected_paths", set())
    is_selected     = project_path in selected_paths

    # Borda destaca se selecionado
    border_color = "#FFFF00" if is_selected else BG_CARD
    card = tk.Frame(parent, bg=border_color, width=CARD_W, height=CARD_H,
                    highlightbackground=border_color, highlightthickness=2 if is_selected else 0)
    card.grid(row=row, column=col, padx=pad, pady=pad, sticky="n")
    card.grid_propagate(False)

    inner = tk.Frame(card, bg=BG_CARD, width=CARD_W - 4, height=CARD_H - 4)
    inner.pack(fill="both", expand=True, padx=2 if is_selected else 0,
               pady=2 if is_selected else 0)
    inner.pack_propagate(False)

    # Checkbox de seleção (canto sup. esq. — só no modo seleção)
    if selection_mode:
        chk_var = tk.BooleanVar(value=is_selected)
        chk = tk.Checkbutton(
            inner, variable=chk_var, bg=BG_CARD,
            activebackground=BG_CARD, cursor="hand2",
            command=lambda: cb["on_toggle_select"](project_path),
        )
        chk.place(x=4, y=4)

    # Capa
    def _open_or_select(e=None):
        cb["on_open_modal"](project_path)

    cover_frm = tk.Frame(inner, bg=BG_SECONDARY, width=CARD_W, height=COVER_H)
    cover_frm.pack(fill="x")
    cover_frm.pack_propagate(False)
    cover_frm.bind("<Button-1>", _open_or_select)

    cover_img = cb.get("get_cover_image") and cb["get_cover_image"](project_path)
    if cover_img:
        lbl = tk.Label(cover_frm, image=cover_img, bg=BG_SECONDARY, cursor="hand2")
        lbl.image = cover_img
        lbl.pack(expand=True)
        lbl.bind("<Button-1>", _open_or_select)
    else:
        ph = tk.Label(cover_frm, text="📁", font=("Arial", 52),
                      bg=BG_SECONDARY, fg=FG_TERTIARY, cursor="hand2")
        ph.pack(expand=True)
        ph.bind("<Button-1>", _open_or_select)

    # Info
    info = tk.Frame(inner, bg=BG_CARD)
    info.pack(fill="both", expand=True, padx=8, pady=6)

    name = data.get("name", "Sem nome")
    nm = (name[:CARD_NAME_TRUNCATE_AT] + "...") if len(name) > CARD_NAME_MAX_LENGTH else name
    nl = tk.Label(info, text=nm, font=("Arial", 10, "bold"),
                  bg=BG_CARD, fg=FG_PRIMARY,
                  wraplength=CARD_W - 20, justify="left", cursor="hand2")
    nl.pack(anchor="w")
    nl.bind("<Button-1>", _open_or_select)

    # Categorias
    raw_cats = data.get("categories", []) or []
    cats = [c for c in raw_cats if c and c.strip() and c.strip().lower() not in CARD_BANNED_STRINGS]
    if cats:
        cf = tk.Frame(info, bg=BG_CARD)
        cf.pack(anchor="w", pady=(4, 0), fill="x")
        for i, cat in enumerate(cats[:CARD_MAX_CATEGORIES]):
            clr = CATEGORY_COLORS[i]
            b = tk.Button(cf, text=cat[:CARD_CATEGORY_MAX_LENGTH],
                          command=lambda cc=cat: cb["on_set_category"]([cc]),
                          bg=clr, fg="#000000", font=("Arial", 7, "bold"),
                          relief="flat", cursor="hand2", padx=4, pady=2)
            b.pack(side="left", padx=2, pady=1)
            b.bind("<Enter>", lambda e, bt=b, cl=clr: bt.config(bg=_darken(cl)))
            b.bind("<Leave>", lambda e, bt=b, cl=clr: bt.config(bg=cl))

    # Tags
    tags = data.get("tags", [])
    if tags:
        tf = tk.Frame(info, bg=BG_CARD)
        tf.pack(anchor="w", pady=(3, 0), fill="x")
        for tag in tags[:CARD_MAX_TAGS]:
            disp = (tag[:CARD_TAG_TRUNCATE_AT] + "...") if len(tag) > CARD_TAG_MAX_LENGTH else tag
            b = tk.Button(tf, text=disp, command=lambda t=tag: cb["on_set_tag"](t),
                          bg="#3A3A3A", fg=FG_PRIMARY, font=("Arial", 7),
                          relief="flat", cursor="hand2", padx=4, pady=1)
            b.pack(side="left", padx=2, pady=1)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=ACCENT_RED))
            b.bind("<Leave>", lambda e, w=b: w.config(bg="#3A3A3A"))

    # Origem
    origin = data.get("origin", "Desconhecido")
    origin_clr = ORIGIN_COLORS.get(origin, ORIGIN_COLORS["default"])
    tk.Button(info, text=origin, font=("Arial", 7),
              bg=origin_clr, fg=FG_PRIMARY, padx=4, pady=2,
              relief="flat", cursor="hand2",
              command=lambda o=origin: cb["on_set_origin"](o)
              ).pack(anchor="w", pady=(4, 0))

    # Ações (ocultas no modo seleção para não poluir)
    if not selection_mode:
        af = tk.Frame(info, bg=BG_CARD)
        af.pack(fill="x", pady=(6, 0))
        tk.Button(af, text="📂", font=("Arial", 12),
                  command=lambda: cb["on_open_folder"](project_path),
                  bg=BG_CARD, fg=ACCENT_GOLD, relief="flat", cursor="hand2"
                  ).pack(side="left", padx=1)
        btn_fav = tk.Button(af, font=("Arial", 12), bg=BG_CARD, relief="flat", cursor="hand2")
        btn_fav.config(
            text="⭐" if data.get("favorite") else "☆",
            fg=ACCENT_GOLD if data.get("favorite") else FG_TERTIARY,
            command=lambda b=btn_fav: cb["on_toggle_favorite"](project_path, b))
        btn_fav.pack(side="left", padx=1)
        btn_done = tk.Button(af, font=("Arial", 12), bg=BG_CARD, relief="flat", cursor="hand2")
        btn_done.config(
            text="✓" if data.get("done") else "○",
            fg="#00FF00" if data.get("done") else FG_TERTIARY,
            command=lambda b=btn_done: cb["on_toggle_done"](project_path, b))
        btn_done.pack(side="left", padx=1)
        btn_good = tk.Button(af, font=("Arial", 12), bg=BG_CARD, relief="flat", cursor="hand2")
        btn_good.config(
            text="👍",
            fg="#00FF00" if data.get("good") else FG_TERTIARY,
            command=lambda b=btn_good: cb["on_toggle_good"](project_path, b))
        btn_good.pack(side="left", padx=1)
        btn_bad = tk.Button(af, font=("Arial", 12), bg=BG_CARD, relief="flat", cursor="hand2")
        btn_bad.config(
            text="👎",
            fg="#FF0000" if data.get("bad") else FG_TERTIARY,
            command=lambda b=btn_bad: cb["on_toggle_bad"](project_path, b))
        btn_bad.pack(side="left", padx=1)
        if not data.get("analyzed"):
            tk.Button(af, text="🤖", font=("Arial", 12),
                      command=lambda: cb["on_analyze_single"](project_path),
                      bg=BG_CARD, fg=ACCENT_GREEN, relief="flat", cursor="hand2"
                      ).pack(side="left", padx=1)
