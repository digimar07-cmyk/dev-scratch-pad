"""
duplicate_resolution_dialog.py — Dialog para resolver duplicatas.
Tkinter puro — sem customtkinter.

Retorna dict {normalized_name: 'skip'|'replace'|'merge'} ou None.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional
from utils.logging_setup import LOGGER


class DuplicateResolutionDialog(tk.Toplevel):
    def __init__(self, parent, duplicates: List[Dict]):
        super().__init__(parent)
        self.title("⚠️ Produtos Duplicados Encontrados")
        self.geometry("900x640")
        self.resizable(True, True)
        self.configure(bg="#1a1a1a")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 450
        y = (self.winfo_screenheight() // 2) - 320
        self.geometry(f"900x640+{x}+{y}")

        self.duplicates   = duplicates
        self.choice_vars  = {}
        self.result       = None

        self._build_ui()
        self.transient(parent)
        self.grab_set()
        LOGGER.info("DuplicateResolutionDialog aberto: %d duplicatas", len(duplicates))

    def _build_ui(self):
        BG      = "#1a1a1a"
        BG_CARD = "#2a2a2a"
        FG      = "#f0f0f0"
        FG_SEC  = "#999999"
        ORANGE  = "#ffa500"
        GREEN   = "#4caf50"
        RED     = "#e50914"

        # Header
        tk.Label(self,
                 text=f"⚠️ {len(self.duplicates)} Produto(s) Duplicado(s) Encontrado(s)",
                 font=("Arial", 16, "bold"), bg=BG, fg=ORANGE).pack(pady=(18, 4))
        tk.Label(self, text="Escolha como resolver cada duplicata:",
                 font=("Arial", 11), bg=BG, fg=FG_SEC).pack(pady=(0, 12))

        # Lista scrollable
        list_container = tk.Frame(self, bg=BG)
        list_container.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(list_container, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for dup in self.duplicates:
            self._create_item(inner, dup, BG_CARD, FG, FG_SEC)

        # Ações em massa
        bulk = tk.Frame(self, bg=BG)
        bulk.pack(fill="x", padx=20, pady=(8, 0))
        tk.Label(bulk, text="Ações em Massa:",
                 font=("Arial", 10, "bold"), bg=BG, fg=FG).pack(side="left", padx=(0, 10))
        for label, choice, color in [
            ("Skip Todos",    "skip",    "#555555"),
            ("Replace Todos", "replace", RED),
            ("Merge Todos",   "merge",   "#4ecdc4"),
        ]:
            tk.Button(bulk, text=label,
                      command=lambda c=choice: self._set_all(c),
                      bg=color, fg=FG, font=("Arial", 9, "bold"),
                      relief="flat", cursor="hand2", padx=12, pady=6
                      ).pack(side="left", padx=4)

        # Botões
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=12)
        tk.Button(btn_row, text="Cancelar Importação",
                  command=self._cancel,
                  bg="#555555", fg=FG, font=("Arial", 11),
                  relief="flat", cursor="hand2", padx=16, pady=10
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="✅ Confirmar e Continuar",
                  command=self._confirm,
                  bg=GREEN, fg=FG, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=16, pady=10
                  ).pack(side="right")

    def _create_item(self, parent, dup: Dict, BG_CARD, FG, FG_SEC):
        norm_name = dup['normalized_name']
        frame = tk.Frame(parent, bg=BG_CARD, relief="flat")
        frame.pack(fill="x", padx=6, pady=5)

        info = tk.Frame(frame, bg=BG_CARD)
        info.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        tk.Label(info, text=f"📦 {dup['name']}",
                 font=("Arial", 11, "bold"), bg=BG_CARD, fg=FG,
                 anchor="w").pack(anchor="w")

        existing_path = dup['existing'].get('path', 'Desconhecido')
        new_path      = dup['new'].get('path', 'Desconhecido')
        tk.Label(info,
                 text=f"❌ Existente: {existing_path}\n✅ Novo: {new_path}",
                 font=("Arial", 8), bg=BG_CARD, fg=FG_SEC,
                 justify="left", anchor="w").pack(anchor="w", pady=(4, 0))

        opts = tk.Frame(frame, bg=BG_CARD)
        opts.pack(side="right", padx=12, pady=10)

        var = tk.StringVar(value="skip")
        self.choice_vars[norm_name] = var

        for label, value in [
            ("Skip (Manter)",       "skip"),
            ("Replace (Substituir)","replace"),
            ("Merge (Mesclar)",     "merge"),
        ]:
            tk.Radiobutton(opts, text=label, variable=var, value=value,
                           bg=BG_CARD, fg=FG, selectcolor="#1e3a2f",
                           activebackground=BG_CARD, font=("Arial", 9)
                           ).pack(anchor="w", pady=2)

    def _set_all(self, choice: str):
        for var in self.choice_vars.values():
            var.set(choice)
        LOGGER.info("Ação em massa: %s para %d duplicatas", choice, len(self.choice_vars))

    def _confirm(self):
        self.result = {norm: var.get() for norm, var in self.choice_vars.items()}
        LOGGER.info("Resolução confirmada: %s", self.result)
        self.destroy()

    def _cancel(self):
        self.result = None
        LOGGER.info("Resolução cancelada")
        self.destroy()

    def get_result(self):
        return self.result


def show_duplicate_resolution(parent, duplicates: List[Dict]) -> Optional[Dict]:
    if not duplicates:
        return {}
    dialog = DuplicateResolutionDialog(parent, duplicates)
    if parent:
        parent.wait_window(dialog)
    else:
        dialog.wait_window()
    return dialog.get_result()
