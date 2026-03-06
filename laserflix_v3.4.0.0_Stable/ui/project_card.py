"""
ui/project_card.py — Factory de card de projeto.
Função pura. Teto: 150 linhas.

HOT-06c: Callback assíncrono thread-safe:
  - Passa widget (placeholder) para get_cover_image_async
  - Valida se widget existe antes de atualizar
  - Previne "main thread is not in main loop"

F-05: Badge de status de análise (🤖 IA / ⚡ Fallback / ⏳ Pendente)
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


def _create_analysis_badge(parent: tk.Frame, data: dict) -> None:
    """
    F-05: Cria badge de status de análise no canto superior direito.
    
    - 🤖 IA (verde): analisado por modelo
    - ⚡ Fallback (amarelo): análise de emergência
    - ⏳ Pendente (cinza): não analisado
    """
    analyzed = data.get("analyzed", False)
    model = data.get("analyzed_model", "fallback")
    
    if not analyzed:
        # Pendente
        badge_text = "⏳"
        badge_bg = "#4A4A4A"
        tooltip = "Pendente de análise"
    elif model == "fallback":
        # Fallback
        badge_text = "⚡"
        badge_bg = "#FFA500"
        tooltip = "Análise de emergência (Fallback)"
    else:
        # IA
        badge_text = "🤖"
        badge_bg = "#00AA00"
        tooltip = f"Analisado por IA: {model}"
    
    badge = tk.Label(
        parent,
        text=badge_text,
        font=("Arial", 14),
        bg=badge_bg,
        fg="#FFFFFF",
        padx=6,
        pady=2,
        relief="flat",
    )
    badge.place(relx=1.0, x=-4, y=4, anchor="ne")
    
    # Tooltip simples (hover)
    def _show_tooltip(e):
        # Simple tooltip via widget config (no external lib)
        pass  # Tooltip complexo seria overengineering
    
    badge.bind("<Enter>", _show_tooltip)


def build_card(
    parent: tk.Widget,
    project_path: str,
    data: dict,
    cb: dict,
    row: int,
    col: int,
    pad: int = CARD_PAD,
) -> tk.Frame:
    """
    Constrói um card de projeto.
    
    Returns:
        tk.Frame: Widget do card criado (para virtual scroll)
    """
    selection_mode  = cb.get("selection_mode", False)
    selected_paths  = cb.get("selected_paths", set())
    is_selected     = project_path in selected_paths

    # Card externo — altura fixa 410px (igual v3.2)
    border_color = "#FFFF00" if is_selected else BG_CARD
    card = tk.Frame(parent, bg=border_color, width=CARD_W, height=CARD_H,
                    highlightbackground=border_color, highlightthickness=2 if is_selected else 0)
    card.grid(row=row, column=col, padx=pad, pady=pad, sticky="n")
    card.grid_propagate(False)

    # Inner — conteúdo do card
    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill="both", expand=True, padx=2 if is_selected else 0, pady=2 if is_selected else 0)

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

    # ← NOVO: Carregamento assíncrono de thumbnail
    # Placeholder instantâneo
    placeholder = tk.Label(cover_frm, text="📁", font=("Arial", 52),
                           bg=BG_SECONDARY, fg=FG_TERTIARY, cursor="hand2")
    placeholder.pack(expand=True)
    placeholder.bind("<Button-1>", _open_or_select)
    
    # F-05: Badge de status de análise (sobre a capa)
    _create_analysis_badge(cover_frm, data)
    
    # Callback para quando thumbnail carregar
    def _on_thumb_loaded(path, photo):
        # Validação dupla: widget existe E ainda é válido
        try:
            if placeholder.winfo_exists():
                placeholder.config(image=photo, text="")  # Remove emoji, mostra imagem
                placeholder.image = photo  # Prevent garbage collection
        except tk.TclError:
            pass  # Widget já foi destruído
    
    # Agenda carregamento assíncrono
    get_cover_async = cb.get("get_cover_image_async")
    if get_cover_async:
        # ← HOT-06c: Passa placeholder como widget para validação
        get_cover_async(project_path, _on_thumb_loaded, placeholder)

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
    
    return card  # ← RETORNA o widget para virtual scroll
