"""
import_preview_dialog.py — Preview antes de importar.
Tkinter puro — sem customtkinter.

Mostra resumo de novos e existentes. Confirmar ou cancelar.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from utils.logging_setup import LOGGER


class ImportPreviewDialog(tk.Toplevel):
    def __init__(self, parent, new_products: List[Dict],
                 existing_products: List[Dict], mode: str):
        super().__init__(parent)
        self.title("📊 Preview de Importação")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(bg="#1a1a1a")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 400
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f"800x600+{x}+{y}")

        self.new_products      = new_products
        self.existing_products = existing_products
        self.mode              = mode
        self._confirmed        = False

        self._build_ui()
        self.transient(parent)
        self.grab_set()
        LOGGER.info("ImportPreviewDialog: %d novos, %d existentes",
                    len(new_products), len(existing_products))

    def _build_ui(self):
        BG      = "#1a1a1a"
        BG_CARD = "#2a2a2a"
        FG      = "#f0f0f0"
        FG_SEC  = "#999999"
        GREEN   = "#4caf50"
        RED     = "#e50914"
        GOLD    = "#ffa500"

        mode_label = "Híbrido" if self.mode == "hybrid" else "Puro"

        tk.Label(self, text="📊 Preview de Importação",
                 font=("Arial", 16, "bold"), bg=BG, fg=FG).pack(pady=(18, 4))
        tk.Label(self, text=f"Modo: {mode_label}",
                 font=("Arial", 10), bg=BG, fg=FG_SEC).pack()

        # Resumo
        summary = tk.Frame(self, bg=BG_CARD)
        summary.pack(fill="x", padx=20, pady=12)

        for label, value, color in [
            ("✅ Novos para importar",    len(self.new_products),      GREEN),
            ("⚠️ Já existentes (pulados)", len(self.existing_products), GOLD),
            ("📁 Total encontrado",        len(self.new_products) + len(self.existing_products), FG),
        ]:
            row = tk.Frame(summary, bg=BG_CARD)
            row.pack(fill="x", padx=16, pady=4)
            tk.Label(row, text=label, font=("Arial", 11), bg=BG_CARD,
                     fg=FG_SEC, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=("Arial", 12, "bold"),
                     bg=BG_CARD, fg=color, anchor="e").pack(side="right")

        # Lista de novos
        tk.Label(self, text="Produtos que serão importados:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG
                 ).pack(anchor="w", padx=20, pady=(8, 4))

        list_frame = tk.Frame(self, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        if self.new_products:
            for p in self.new_products:
                row = tk.Frame(inner, bg="#252525")
                row.pack(fill="x", pady=2, padx=4)
                tk.Label(row, text=f"📂 {p.get('name','?')}",
                         font=("Arial", 10), bg="#252525", fg=FG,
                         anchor="w").pack(side="left", padx=8, pady=5)
                tk.Label(row, text=p.get('path',''),
                         font=("Arial", 8), bg="#252525", fg=FG_SEC,
                         anchor="e").pack(side="right", padx=8)
        else:
            tk.Label(inner, text="Nenhum produto novo para importar.",
                     font=("Arial", 11), bg=BG, fg=FG_SEC).pack(pady=20)

        # Botões
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=14)

        tk.Button(btn_row, text="Cancelar", command=self._cancel,
                  bg="#555555", fg=FG, font=("Arial", 11),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right", padx=(8, 0))

        state = "normal" if self.new_products else "disabled"
        tk.Button(btn_row, text=f"▶️ Importar {len(self.new_products)} produto(s)",
                  command=self._confirm, state=state,
                  bg=GREEN if self.new_products else "#555555",
                  fg=FG, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right")

    def _confirm(self):
        self._confirmed = True
        LOGGER.info("ImportPreviewDialog: confirmado")
        self.destroy()

    def _cancel(self):
        self._confirmed = False
        LOGGER.info("ImportPreviewDialog: cancelado")
        self.destroy()

    def get_confirmed(self) -> bool:
        return self._confirmed
