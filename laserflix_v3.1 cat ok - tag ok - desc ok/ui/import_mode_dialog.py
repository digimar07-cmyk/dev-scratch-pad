"""
import_mode_dialog.py — Dialog para escolher modo de importação.
Tkinter puro — sem customtkinter.

Retorna (modo, pasta) ou None se cancelado.
Modos: 'pure' | 'hybrid'
"""

import tkinter as tk
from tkinter import filedialog
import os
from utils.logging_setup import LOGGER


class ImportModeDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("🚀 Importação em Massa - Escolha o Modo")
        self.geometry("600x480")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 240
        self.geometry(f"600x480+{x}+{y}")

        self.result = None
        self.selected_path = ""
        self.mode_var = tk.StringVar(value="hybrid")

        self._build_ui()

        self.transient(parent)
        self.grab_set()
        LOGGER.info("ImportModeDialog aberto")

    def _build_ui(self):
        BG       = "#1a1a1a"
        BG_CARD  = "#2a2a2a"
        BG_SEL   = "#1e3a2f"
        FG       = "#f0f0f0"
        FG_SEC   = "#999999"
        ACCENT   = "#e50914"
        GREEN    = "#4caf50"

        tk.Label(self, text="🚀 Importação em Massa",
                 font=("Arial", 18, "bold"), bg=BG, fg=FG).pack(pady=(20, 4))
        tk.Label(self, text="Escolha o modo de detecção de produtos",
                 font=("Arial", 11), bg=BG, fg=FG_SEC).pack(pady=(0, 16))

        # --- Modo Híbrido ---
        self.hybrid_frame = tk.Frame(self, bg=BG_SEL, relief="flat", bd=2,
                                     cursor="hand2")
        self.hybrid_frame.pack(fill="x", padx=30, pady=6)

        inner_h = tk.Frame(self.hybrid_frame, bg=BG_SEL, padx=16, pady=12)
        inner_h.pack(fill="x")

        tk.Radiobutton(inner_h, variable=self.mode_var, value="hybrid",
                       bg=BG_SEL, activebackground=BG_SEL,
                       command=self._update_frames).pack(side="left")

        info_h = tk.Frame(inner_h, bg=BG_SEL)
        info_h.pack(side="left", padx=10)
        tk.Label(info_h, text="🔄 Modo Híbrido (Recomendado)",
                 font=("Arial", 12, "bold"), bg=BG_SEL, fg=FG,
                 anchor="w").pack(anchor="w")
        tk.Label(info_h,
                 text="• Busca folder.jpg + fallback\n• Detecta mais produtos\n• Preview antes de importar",
                 font=("Arial", 9), bg=BG_SEL, fg=FG_SEC,
                 justify="left", anchor="w").pack(anchor="w", pady=(4, 0))

        for w in [self.hybrid_frame, inner_h, info_h]:
            w.bind("<Button-1>", lambda e: (self.mode_var.set("hybrid"), self._update_frames()))

        # --- Modo Puro ---
        self.pure_frame = tk.Frame(self, bg=BG_CARD, relief="flat", bd=2,
                                   cursor="hand2")
        self.pure_frame.pack(fill="x", padx=30, pady=6)

        inner_p = tk.Frame(self.pure_frame, bg=BG_CARD, padx=16, pady=12)
        inner_p.pack(fill="x")

        tk.Radiobutton(inner_p, variable=self.mode_var, value="pure",
                       bg=BG_CARD, activebackground=BG_CARD,
                       command=self._update_frames).pack(side="left")

        info_p = tk.Frame(inner_p, bg=BG_CARD)
        info_p.pack(side="left", padx=10)
        tk.Label(info_p, text="🔒 Modo Puro (Controle Total)",
                 font=("Arial", 12, "bold"), bg=BG_CARD, fg=FG,
                 anchor="w").pack(anchor="w")
        tk.Label(info_p,
                 text="• Apenas pastas com folder.jpg\n• Zero falsos positivos\n• Você decide o que importar",
                 font=("Arial", 9), bg=BG_CARD, fg=FG_SEC,
                 justify="left", anchor="w").pack(anchor="w", pady=(4, 0))

        for w in [self.pure_frame, inner_p, info_p]:
            w.bind("<Button-1>", lambda e: (self.mode_var.set("pure"), self._update_frames()))

        # --- Pasta ---
        tk.Label(self, text="📁 Pasta Base:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG).pack(
                     anchor="w", padx=30, pady=(16, 4))

        path_row = tk.Frame(self, bg=BG)
        path_row.pack(fill="x", padx=30)

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(path_row, textvariable=self.path_var,
                                   bg="#333333", fg=FG, font=("Arial", 10),
                                   relief="flat", insertbackground=FG)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=6)

        tk.Button(path_row, text="...", command=self._browse,
                  bg="#555555", fg=FG, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10
                  ).pack(side="left", padx=(6, 0))

        # --- Botões ---
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=30, pady=20)

        tk.Button(btn_row, text="Cancelar", command=self._cancel,
                  bg="#555555", fg=FG, font=("Arial", 11),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right", padx=(8, 0))

        tk.Button(btn_row, text="▶️ Escanear", command=self._confirm,
                  bg=GREEN, fg=FG, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right")

    def _update_frames(self):
        BG_SEL  = "#1e3a2f"
        BG_CARD = "#2a2a2a"
        mode = self.mode_var.get()
        h_bg = BG_SEL  if mode == "hybrid" else BG_CARD
        p_bg = BG_SEL  if mode == "pure"   else BG_CARD
        for w in self.hybrid_frame.winfo_children():
            try: w.config(bg=h_bg)
            except: pass
        for w in self.pure_frame.winfo_children():
            try: w.config(bg=p_bg)
            except: pass
        self.hybrid_frame.config(bg=h_bg)
        self.pure_frame.config(bg=p_bg)

    def _browse(self):
        folder = filedialog.askdirectory(title="Selecione a Pasta Base", mustexist=True)
        if folder:
            self.selected_path = folder
            self.path_var.set(folder)

    def _confirm(self):
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            self.path_entry.config(bg="#5a1a1a")
            self.after(1000, lambda: self.path_entry.config(bg="#333333"))
            return
        self.selected_path = path
        self.result = (self.mode_var.get(), self.selected_path)
        LOGGER.info("Confirmação: modo=%s, pasta=%s", self.result[0], self.result[1])
        self.destroy()

    def _cancel(self):
        self.result = None
        LOGGER.info("ImportModeDialog cancelado")
        self.destroy()

    def get_result(self):
        return self.result


def show_import_mode_dialog(parent=None):
    dialog = ImportModeDialog(parent)
    if parent:
        parent.wait_window(dialog)
    else:
        dialog.wait_window()
    return dialog.get_result()
