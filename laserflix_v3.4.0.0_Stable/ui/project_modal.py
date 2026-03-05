"""
ui/project_modal.py — Modal de detalhes de projeto.
Responsabilidade única: exibir + interagir com 1 projeto.
Teto: 450 linhas (expandido para F-01).
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from config.ui_constants import (
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
    ORIGIN_COLORS,
    SCROLL_SPEED,
)
from utils.platform_utils import open_file, open_folder


class ProjectModal:
    """
    Callbacks em `cb`:
        get_all_paths()             — retorna lista de paths válidos
        on_navigate(path)           — navegação ◄ ►
        on_toggle(path, key, value) — altera flag no banco
        on_generate_desc(path, lbl, btn, modal)
        on_open_edit(path)
        on_reanalize(path)
        on_set_tag(tag)
        on_remove(path)             — remove projeto do banco (F-02)
        on_save_name(path, name)    — F-01.1: salva nome PT-BR
    """

    _BG       = "#0F0F0F"
    _BG_CARD  = "#1A1A1A"
    _BG_HOVER = "#242424"
    _SEP      = "#2A2A2A"
    _FG_PRI   = "#F0F0F0"
    _FG_SEC   = "#999999"
    _FG_TER   = "#555555"
    _PAD      = 24
    _F_TITLE  = ("Arial", 24, "bold")
    _F_SEC    = ("Arial", 9, "bold")
    _F_BODY   = ("Arial", 11)
    _F_SMALL  = ("Arial", 9)

    def __init__(self, root, project_path, database, cb, cache, scanner):
        self._root     = root
        self._path     = project_path
        self._database = database
        self._cb       = cb
        self._cache    = cache
        self._scanner  = scanner
        self._modal    = None

    def open(self) -> None:
        data      = self._database.get(self._path, {})
        all_paths = self._cb["get_all_paths"]()
        try:    nav_idx = all_paths.index(self._path)
        except: nav_idx = 0
        nav_tot = len(all_paths)

        modal = tk.Toplevel(self._root)
        modal.title("Laserflix — Detalhes")
        modal.state("zoomed")
        modal.configure(bg=self._BG)
        modal.transient(self._root)
        modal.grab_set()
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.bind("<Left>",   lambda e: _nav(-1))
        modal.bind("<Right>",  lambda e: _nav(+1))
        self._modal = modal

        def _nav(delta):
            ni = nav_idx + delta
            if 0 <= ni < nav_tot:
                modal.destroy()
                self._cb["on_navigate"](all_paths[ni])

        main = tk.Frame(modal, bg=self._BG)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=1)

        left_outer = tk.Frame(main, bg=self._BG)
        left_outer.grid(row=0, column=0, sticky="nsew")
        lc  = tk.Canvas(left_outer, bg=self._BG, highlightthickness=0)
        lsb = ttk.Scrollbar(left_outer, orient="vertical", command=lc.yview)
        lp  = tk.Frame(lc, bg=self._BG)
        lp.bind("<Configure>", lambda e: lc.configure(scrollregion=lc.bbox("all")))
        lc_win = lc.create_window((0, 0), window=lp, anchor="nw")
        lc.configure(yscrollcommand=lsb.set)
        lc.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")
        lc.bind("<MouseWheel>",
                lambda ev: lc.yview_scroll(int(-1*(ev.delta/SCROLL_SPEED)), "units"))

        _desc_lbl_ref = [None]

        def _on_left_resize(e):
            w = e.width - 18
            if w < 60: return
            lc.itemconfig(lc_win, width=w)
            lbl = _desc_lbl_ref[0]
            if lbl:
                lbl.config(wraplength=w - self._PAD * 2 - 24)
        left_outer.bind("<Configure>", _on_left_resize)

        self._build_left_panel(lp, data, nav_idx, nav_tot, all_paths,
                               _nav, _desc_lbl_ref, modal)
        tk.Frame(main, bg=self._SEP, width=1).grid(row=0, column=1, sticky="ns")
        self._build_right_panel(main, modal)

    # ------------------------------------------------------------------

    def _build_left_panel(self, lp, data, nav_idx, nav_tot, all_paths,
                          _nav, _desc_lbl_ref, modal):
        P  = self._PAD
        BG = self._BG; BC = self._BG_CARD; SEP = self._SEP
        FP = self._FG_PRI; FS = self._FG_SEC; FT = self._FG_TER

        def _section(text):
            tk.Label(lp, text=text.upper(), font=self._F_SEC,
                     bg=BG, fg=FT, anchor="w").pack(fill="x", padx=P, pady=(20, 6))
        def _sep():
            tk.Frame(lp, bg=SEP, height=1).pack(fill="x", padx=P, pady=(4, 0))

        # Cabeçalho
        tk.Frame(lp, bg=BG, height=8).pack()
        origin  = data.get("origin", "Desconhecido")
        o_color = ORIGIN_COLORS.get(origin, ORIGIN_COLORS["default"])
        tk.Label(lp, text=f"  {origin}  ", font=self._F_SMALL,
                 bg=o_color, fg=FG_PRIMARY).pack(anchor="w", padx=P, pady=(8, 4))
        tk.Label(lp, text=data.get("name", "Sem nome"),
                 font=self._F_TITLE, bg=BG, fg=FP,
                 wraplength=500, justify="left", anchor="w"
                 ).pack(fill="x", padx=P, pady=(0, 4))

        # F-01.1: Nome PT-BR editável
        self._build_editable_name(lp, data, modal)

        # Marcadores
        _sep(); _section("Marcadores")
        act = tk.Frame(lp, bg=BG)
        act.pack(anchor="w", padx=P, pady=(0, 4))
        for emoji, label, key, afg in [
            ("⭐", "Favorito", "favorite", ACCENT_GOLD),
            ("✓",  "Feito",    "done",     ACCENT_GREEN),
            ("👍", "Bom",      "good",     "#4FC3F7"),
            ("👎", "Ruim",     "bad",      "#EF5350"),
        ]:
            self._make_toggle(act, emoji, label, key, afg, data, modal)

        # Descrição IA
        _sep(); _section("Descrição IA")
        desc_text = (data.get("ai_description") or "").strip()
        desc_box  = tk.Frame(lp, bg=BC)
        desc_box.pack(fill="x", padx=P, pady=(0, 8))
        desc_lbl  = tk.Label(
            desc_box,
            text=desc_text or "Nenhuma descrição gerada ainda.",
            font=self._F_BODY, bg=BC,
            fg=FS if desc_text else FT,
            justify="left", anchor="nw",
            wraplength=480, padx=16, pady=14,
        )
        desc_lbl.pack(fill="both", expand=True)
        _desc_lbl_ref[0] = desc_lbl
        gen_btn = tk.Button(lp, text="🤖  Gerar com IA",
                            bg=ACCENT_GREEN, fg=FG_PRIMARY, font=("Arial", 10, "bold"),
                            relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        gen_btn.config(command=lambda: self._cb["on_generate_desc"](
            self._path, desc_lbl, gen_btn, modal))
        gen_btn.pack(anchor="w", padx=P, pady=(0, 4))

        # Categorias
        _sep(); _section("Categorias")
        cats_row = tk.Frame(lp, bg=BG)
        cats_row.pack(anchor="w", padx=P, fill="x", pady=(0, 4))
        cats = data.get("categories", []) or []
        if cats:
            for cat in cats:
                tk.Label(cats_row, text=cat, font=self._F_SMALL,
                         bg="#1E3A2F", fg=ACCENT_GREEN,
                         padx=10, pady=5).pack(side="left", padx=(0, 6), pady=2)
        else:
            tk.Label(cats_row, text="Sem categoria",
                     font=self._F_SMALL, bg=BG, fg=FT).pack(anchor="w")

        # Tags
        _sep(); _section("Tags")
        tw = tk.Frame(lp, bg=BG)
        tw.pack(anchor="w", padx=P, fill="x", pady=(0, 4))
        for tag in (data.get("tags", []) or ["Nenhuma tag"]):
            t = tk.Label(tw, text=tag, font=self._F_SMALL,
                         bg=BC, fg=FS, padx=10, pady=5, cursor="hand2")
            t.pack(side="left", padx=(0, 4), pady=3)
            t.bind("<Enter>", lambda e, w=t: w.config(bg=ACCENT_RED, fg=FG_PRIMARY))
            t.bind("<Leave>", lambda e, w=t: w.config(bg=BC, fg=FS))
            t.bind("<Button-1>",
                   lambda e, tg=tag: (modal.destroy(), self._cb["on_set_tag"](tg)))

        # Arquivos
        _sep(); _section("Arquivos")
        struct = (data.get("structure")
                  or self._scanner.analyze_project_structure(self._path))
        fmt_row = tk.Frame(lp, bg=BG)
        fmt_row.pack(anchor="w", padx=P, pady=(0, 4))
        for lbl_t, lbl_c, present in [
            ("SVG", "#FF6B6B", struct.get("has_svg")),
            ("PDF", "#4ECDC4", struct.get("has_pdf")),
            ("DXF", "#95E1D3", struct.get("has_dxf")),
            ("AI",  "#F7DC6F", struct.get("has_ai")),
        ]:
            tk.Label(fmt_row, text=lbl_t, font=("Arial", 9, "bold"),
                     bg=BC if present else BG,
                     fg=lbl_c if present else FT,
                     padx=10, pady=5).pack(side="left", padx=(0, 4))
        tf = struct.get("total_files", 0)
        sf = struct.get("total_subfolders", 0)
        tk.Label(lp, text=f"{tf} arquivo(s)  ·  {sf} subpasta(s)",
                 font=self._F_SMALL, bg=BG, fg=FT
                 ).pack(anchor="w", padx=P, pady=(4, 4))

        # Localização
        _sep(); _section("Localização")
        par_f = os.path.basename(os.path.dirname(self._path))
        prj_n = os.path.basename(self._path)
        lr = tk.Frame(lp, bg=BG)
        lr.pack(fill="x", padx=P, pady=(0, 4))
        tk.Label(lr, text=f"{par_f} / {prj_n}",
                 font=self._F_SMALL, bg=BG, fg=FS).pack(side="left")

        def _copy_path():
            modal.clipboard_clear(); modal.clipboard_append(self._path)
            cp_btn.config(text="✅ Copiado!")
            modal.after(1500, lambda: cp_btn.config(text="📋 Copiar"))
        cp_btn = tk.Button(lr, text="📋 Copiar", command=_copy_path,
                           bg=BC, fg=FS, font=self._F_SMALL,
                           relief="flat", cursor="hand2", padx=8, pady=3, bd=0)
        cp_btn.pack(side="left", padx=10)
        added   = (data.get("added_date") or "")[:10] or "—"
        model_u = data.get("analyzed_model", "não analisado")
        tk.Label(lp, text=f"Adicionado: {added}   ·   Modelo IA: {model_u}",
                 font=self._F_SMALL, bg=BG, fg=FT
                 ).pack(anchor="w", padx=P, pady=(2, 4))

        # Barra de ações
        tk.Frame(lp, bg=SEP, height=1).pack(fill="x", pady=(16, 0))
        action_bar = tk.Frame(lp, bg=BG)
        action_bar.pack(fill="x", padx=P, pady=12)
        BTN_P   = dict(bg=ACCENT_RED,   fg=FG_PRIMARY, font=("Arial", 10, "bold"),
                       relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_G   = dict(bg=BC,           fg=FP,         font=("Arial", 10),
                       relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_DEL = dict(bg="#3A0000",    fg="#FF6B6B",  font=("Arial", 10),
                       relief="flat", cursor="hand2", padx=16, pady=9, bd=0)
        BTN_NAV = dict(bg=BC,           fg=FS,         font=("Arial", 11),
                       relief="flat", cursor="hand2", padx=14, pady=9, bd=0)

        tk.Button(action_bar, text="✏️  Editar",
                  command=lambda: (modal.destroy(),
                                   self._cb["on_open_edit"](self._path)),
                  **BTN_P).pack(side="left", padx=(0, 6))
        tk.Button(action_bar, text="📂  Pasta",
                  command=lambda: open_folder(self._path),
                  **BTN_G).pack(side="left", padx=(0, 6))
        tk.Button(action_bar, text="🤖  Reanalisar",
                  command=lambda: (modal.destroy(),
                                   self._cb["on_reanalize"](self._path)),
                  **BTN_G).pack(side="left", padx=(0, 6))

        # F-02: botão Remover individual
        tk.Button(action_bar, text="🗑️  Remover",
                  command=lambda: self._confirm_remove(modal),
                  **BTN_DEL).pack(side="left", padx=(0, 6))

        tk.Button(action_bar, text="✕", command=modal.destroy,
                  bg=BG, fg=FT, font=("Arial", 14),
                  relief="flat", cursor="hand2", padx=10, pady=9, bd=0
                  ).pack(side="right")
        tk.Label(action_bar, text=f"{nav_idx + 1} / {nav_tot}",
                 font=self._F_SMALL, bg=BG, fg=FT).pack(side="right", padx=8)
        tk.Button(action_bar, text="►", command=lambda: _nav(+1),
                  state="normal" if nav_idx < nav_tot - 1 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0, 2))
        tk.Button(action_bar, text="◄", command=lambda: _nav(-1),
                  state="normal" if nav_idx > 0 else "disabled",
                  **BTN_NAV).pack(side="right", padx=(0, 4))

    # ------------------------------------------------------------------
    # F-01.1: NOME PT-BR EDITÁVEL
    # ------------------------------------------------------------------

    def _build_editable_name(self, parent, data, modal):
        """
        Nome PT-BR editável.
        Kent Beck: Entry + botão toggle. Simples e funcional.
        """
        P  = self._PAD
        BG = self._BG; BC = self._BG_CARD
        FP = self._FG_PRI; FS = self._FG_SEC
        
        name_frame = tk.Frame(parent, bg=BG)
        name_frame.pack(fill="x", padx=P, pady=(8, 8))
        
        # Label header
        tk.Label(
            name_frame,
            text="📝 Nome em Português:",
            font=self._F_SEC,
            bg=BG,
            fg=FS
        ).pack(anchor="w", pady=(0, 4))
        
        # Container Entry + Botão
        input_frame = tk.Frame(name_frame, bg=BG)
        input_frame.pack(fill="x")
        
        # Entry (readonly inicial)
        name_var = tk.StringVar(value=data.get("name_ptbr", ""))
        
        name_entry = tk.Entry(
            input_frame,
            textvariable=name_var,
            font=self._F_BODY,
            bg="#222222",
            fg=FP,
            insertbackground=FP,
            relief="flat",
            state="readonly",
            bd=5
        )
        name_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        # Botão Editar/Salvar
        edit_btn = tk.Button(
            input_frame,
            text="✏️ Editar",
            command=lambda: self._toggle_name_edit(name_entry, name_var, edit_btn, modal),
            bg=ACCENT_GOLD,
            fg="#000000",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            bd=0
        )
        edit_btn.pack(side="right")

    def _toggle_name_edit(self, entry, var, btn, modal):
        """
        Toggle edit/readonly para nome PT-BR.
        Kent Beck: State machine simples. Editar → Salvar → Editar.
        """
        current_text = btn.cget("text")
        
        if current_text == "✏️ Editar":
            # Modo EDIT
            entry.config(state="normal", bg="#333333")
            entry.focus()
            entry.icursor(tk.END)
            btn.config(text="💾 Salvar", bg=ACCENT_GREEN)
        
        else:
            # SALVA
            new_name = var.get().strip()
            
            if not new_name:
                messagebox.showwarning("Nome vazio", "Digite um nome válido!")
                return
            
            # Salva no banco
            if self._path in self._database:
                self._database[self._path]["name_ptbr"] = new_name
                self._cb["on_save_name"](self._path, new_name)
            
            # Volta para readonly
            entry.config(state="readonly", bg="#222222")
            btn.config(text="✏️ Editar", bg=ACCENT_GOLD)
            
            messagebox.showinfo("✓ Salvo", f"Nome atualizado: \"{new_name}\"")

    # ------------------------------------------------------------------

    def _confirm_remove(self, modal) -> None:
        name = self._database.get(self._path, {}).get("name", self._path)
        if not messagebox.askyesno(
            "🗑️ Remover projeto",
            f"Remover '{name}' do banco?\n\nOs arquivos no disco NÃO serão apagados.",
            icon="warning",
        ):
            return
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            "Segunda confirmação necessária.\n\nTem certeza absoluta?",
            icon="warning",
        ):
            return
        modal.destroy()
        self._cb["on_remove"](self._path)

    def _make_toggle(self, parent, emoji, label, key, active_fg, data, modal):
        BG = self._BG; BC = self._BG_CARD; BH = self._BG_HOVER
        FS = self._FG_SEC; FT = self._FG_TER
        is_on = data.get(key, False)
        f = tk.Frame(parent, bg=BC, cursor="hand2")
        f.pack(side="left", padx=(0, 6), pady=4)
        inner = tk.Frame(f, bg=BC, padx=10, pady=7)
        inner.pack()
        il = tk.Label(inner, text=emoji, font=("Arial", 13), bg=BC,
                      fg=active_fg if is_on else FT)
        il.pack()
        tl = tk.Label(inner, text=label, font=("Arial", 8), bg=BC,
                      fg=FS if is_on else FT)
        tl.pack()
        all_w = [f, inner, il, tl]

        def _toggle(ev=None):
            nv = not self._database.get(self._path, {}).get(key, False)
            if self._path in self._database:
                if key == "good" and nv: self._database[self._path]["bad"]  = False
                if key == "bad"  and nv: self._database[self._path]["good"] = False
                self._cb["on_toggle"](self._path, key, nv)
                il.config(fg=active_fg if nv else FT)
                tl.config(fg=FS if nv else FT)

        for w in all_w:
            w.bind("<Button-1>", _toggle)
            w.bind("<Enter>",    lambda e, ws=all_w: [x.config(bg=BH) for x in ws])
            w.bind("<Leave>",    lambda e, ws=all_w: [x.config(bg=BC) for x in ws])

    def _build_right_panel(self, main, modal):
        """
        ← HOT-09b: FIX imagem modal - usa método público find_first_image()
        """
        right_outer = tk.Frame(main, bg="#0A0A0A")
        right_outer.grid(row=0, column=2, sticky="nsew")
        
        # ← HOT-09b: Agora usa método público (era _find_first_image privado)
        cover_path = self._cache.find_first_image(self._path)

        if not cover_path:
            tk.Label(right_outer, text="🖼️", font=("Arial", 64),
                     bg="#0A0A0A", fg="#1E1E1E").place(relx=0.5, rely=0.4, anchor="center")
            tk.Label(right_outer, text="Sem imagem de capa",
                     font=self._F_BODY, bg="#0A0A0A", fg=self._FG_TER
                     ).place(relx=0.5, rely=0.55, anchor="center")
            return

        cover_lbl = tk.Label(right_outer, bg="#0A0A0A", cursor="hand2", bd=0)
        cover_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        cover_lbl.bind("<Button-1>", lambda e: open_file(cover_path))
        _last_size = [0, 0]

        def _redraw(event=None):
            from PIL import Image, ImageTk
            cw = right_outer.winfo_width()
            ch = right_outer.winfo_height()
            if cw < 10 or ch < 10 or [cw, ch] == _last_size:
                return
            _last_size[0], _last_size[1] = cw, ch
            try:
                img   = Image.open(cover_path).convert("RGB")
                ratio = min(cw / img.width, ch / img.height)
                new_w = max(1, int(img.width  * ratio))
                new_h = max(1, int(img.height * ratio))
                img   = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                cover_lbl.config(image=photo)
                cover_lbl.image = photo
            except Exception:
                pass

        right_outer.bind("<Configure>", lambda e: _redraw())
        modal.after(80, _redraw)
