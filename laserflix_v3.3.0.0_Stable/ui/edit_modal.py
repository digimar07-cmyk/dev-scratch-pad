"""
ui/edit_modal.py — Janela de edição de projeto.
Responsabilidade única: coletar edits de categorias/tags e chamar on_save.
Teto: 120 linhas.
"""
import tkinter as tk
from tkinter import ttk, simpledialog

from config.ui_constants import (
    BG_CARD,
    ACCENT_RED, ACCENT_GREEN,
    FG_PRIMARY,
)


class EditModal:
    """
    Abre a janela de edição de projeto.

    on_save(project_path, new_categories: list, new_tags: list)
        — chamado quando o usuário clica em Salvar.
    """

    def __init__(
        self,
        root: tk.Tk,
        project_path: str,
        data: dict,
        on_save,
    ):
        self._root = root
        self._path = project_path
        self._data = data
        self._on_save = on_save
        self._build()

    def _build(self) -> None:
        win = tk.Toplevel(self._root)
        win.title("✏️ Editar Projeto")
        win.state("zoomed")
        win.configure(bg="#181818")
        win.transient(self._root)
        win.grab_set()
        self._win = win

        tk.Label(win, text="✏️ Editar Projeto", font=("Arial", 20, "bold"),
                 bg="#181818", fg=ACCENT_RED).pack(pady=20)

        # Nome (somente leitura)
        tk.Label(win, text="📁 Nome do Projeto", font=("Arial", 12, "bold"),
                 bg="#181818", fg=FG_PRIMARY).pack(anchor="w", padx=30, pady=(10, 5))
        name_txt = tk.Text(win, height=2, bg=BG_CARD, fg=FG_PRIMARY,
                           font=("Arial", 11), relief="flat", wrap="word")
        name_txt.insert("1.0", self._data.get("name", ""))
        name_txt.config(state="disabled")
        name_txt.pack(fill="x", padx=30, pady=(0, 15))

        # Categorias
        tk.Label(win, text="📂 Categorias (separadas por vírgula)",
                 font=("Arial", 12, "bold"), bg="#181818", fg=FG_PRIMARY
                 ).pack(anchor="w", padx=30, pady=(10, 5))
        self._cats_txt = tk.Text(win, height=3, bg=BG_CARD, fg=FG_PRIMARY,
                                 font=("Arial", 11), relief="flat", wrap="word")
        self._cats_txt.insert("1.0", ", ".join(self._data.get("categories", [])))
        self._cats_txt.pack(fill="x", padx=30, pady=(0, 15))

        # Tags
        tk.Label(win, text="🌷 Tags", font=("Arial", 12, "bold"),
                 bg="#181818", fg=FG_PRIMARY).pack(anchor="w", padx=30, pady=(10, 5))
        self._listbox, _ = self._build_tag_list(win)

        # Botões finais
        fb = tk.Frame(win, bg="#181818")
        fb.pack(fill="x", padx=30, pady=30)
        tk.Button(fb, text="💾 Salvar e Fechar", command=self._save,
                  bg=ACCENT_GREEN, fg=FG_PRIMARY, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12
                  ).pack(side="left", padx=5)
        tk.Button(fb, text="✕ Cancelar", command=win.destroy,
                  bg=ACCENT_RED, fg=FG_PRIMARY, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=12
                  ).pack(side="right", padx=5)

    def _build_tag_list(self, win: tk.Widget):
        container = tk.Frame(win, bg="#181818")
        container.pack(fill="x", padx=30, pady=(0, 10))
        list_frm = tk.Frame(container, bg=BG_CARD)
        list_frm.pack(side="left", fill="both", expand=True, padx=(0, 10))
        sb = ttk.Scrollbar(list_frm, orient="vertical")
        lb = tk.Listbox(list_frm, bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 10),
                        height=6, yscrollcommand=sb.set,
                        selectmode=tk.SINGLE, relief="flat")
        sb.config(command=lb.yview)
        lb.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sb.pack(side="right", fill="y")
        for tag in self._data.get("tags", []):
            lb.insert(tk.END, tag)
        btns = tk.Frame(container, bg="#181818")
        btns.pack(side="right")
        for text, cmd, color in [
            ("➕ Add",     lambda: self._add_tag(lb),       ACCENT_GREEN),
            ("➖ Remover", lambda: self._remove_tag(lb),    ACCENT_RED),
            ("🗑️ Limpar",  lambda: lb.delete(0, tk.END),   "#555555"),
        ]:
            tk.Button(btns, text=text, command=cmd, bg=color, fg=FG_PRIMARY,
                      font=("Arial", 10), relief="flat", cursor="hand2",
                      padx=10, pady=8, width=10).pack(pady=2)
        return lb, container

    def _add_tag(self, lb: tk.Listbox) -> None:
        tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=self._root)
        if tag and tag.strip() and tag.strip() not in lb.get(0, tk.END):
            lb.insert(tk.END, tag.strip())

    def _remove_tag(self, lb: tk.Listbox) -> None:
        sel = lb.curselection()
        if sel:
            lb.delete(sel[0])

    def _save(self) -> None:
        cats_str = self._cats_txt.get("1.0", "end-1c").strip()
        new_cats = [c.strip() for c in cats_str.split(",") if c.strip()]
        new_tags = list(self._listbox.get(0, tk.END))
        self._on_save(self._path, new_cats, new_tags)
        self._win.destroy()
