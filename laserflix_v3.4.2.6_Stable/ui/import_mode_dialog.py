"""
import_mode_dialog.py — Dialog central de importação de pastas.
Tkinter puro — sem customtkinter.

Três modos disponíveis:
  'hybrid'  — Recursivo com folder.jpg + fallback
  'pure'    — Recursivo apenas com folder.jpg
  'simple'  — Importação Simples (1 nível, herda dedup)

Retorna (modo, pasta) ou None se cancelado.
"""

import tkinter as tk
from tkinter import filedialog
import os
from utils.logging_setup import LOGGER


class ImportModeDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("🚀 Importar Pastas")
        self.geometry("620x580")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 310
        y = (self.winfo_screenheight() // 2) - 290
        self.geometry(f"620x580+{x}+{y}")

        self.result       = None
        self.selected_path = ""
        self.mode_var     = tk.StringVar(value="hybrid")

        self._build_ui()
        self.transient(parent)
        self.grab_set()
        LOGGER.info("ImportModeDialog aberto")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        BG      = "#1a1a1a"
        BG_CARD = "#2a2a2a"
        BG_SEL  = "#1e3a2f"
        FG      = "#f0f0f0"
        FG_SEC  = "#999999"
        GREEN   = "#4caf50"

        tk.Label(self, text="📁 Importar Pastas",
                 font=("Arial", 18, "bold"), bg=BG, fg=FG).pack(pady=(20, 4))
        tk.Label(self, text="Escolha o modo de importação",
                 font=("Arial", 11), bg=BG, fg=FG_SEC).pack(pady=(0, 14))

        # ---- opções ----
        modes = [
            (
                "hybrid",
                "🔄 Recursivo Híbrido  (Recomendado)",
                "• Desce todas as subpastas\n"
                "• Detecta folder.jpg + arquivos válidos\n"
                "• Mais flexível, pega mais produtos",
            ),
            (
                "pure",
                "🔒 Recursivo Puro  (Controle Total)",
                "• Desce todas as subpastas\n"
                "• Importa APENAS pastas com folder.jpg\n"
                "• Zero falsos positivos",
            ),
            (
                "simple",
                "➡️ Importação Simples  (1 nível)",
                "• Importa subpastas diretas da pasta selecionada\n"
                "• Não desce em subpastas\n"
                "• Verifica duplicatas automaticamente",
            ),
        ]

        self._mode_frames = {}
        for value, title, desc in modes:
            active = value == self.mode_var.get()
            bg = BG_SEL if active else BG_CARD
            frame = tk.Frame(self, bg=bg, cursor="hand2")
            frame.pack(fill="x", padx=28, pady=5)
            self._mode_frames[value] = frame

            inner = tk.Frame(frame, bg=bg, padx=14, pady=10)
            inner.pack(fill="x")

            rb = tk.Radiobutton(inner, variable=self.mode_var, value=value,
                                bg=bg, activebackground=bg,
                                command=self._update_frames)
            rb.pack(side="left", anchor="n", pady=2)

            info = tk.Frame(inner, bg=bg)
            info.pack(side="left", padx=10)
            tk.Label(info, text=title, font=("Arial", 11, "bold"),
                     bg=bg, fg=FG, anchor="w").pack(anchor="w")
            tk.Label(info, text=desc, font=("Arial", 9),
                     bg=bg, fg=FG_SEC, justify="left", anchor="w"
                     ).pack(anchor="w", pady=(3, 0))

            # clique em qualquer lugar seleciona
            for w in [frame, inner, info, rb]:
                w.bind("<Button-1>",
                       lambda e, v=value: (self.mode_var.set(v), self._update_frames()))
            for child in info.winfo_children():
                child.bind("<Button-1>",
                           lambda e, v=value: (self.mode_var.set(v), self._update_frames()))

        # ---- pasta ----
        tk.Label(self, text="📁 Pasta Base:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG
                 ).pack(anchor="w", padx=28, pady=(18, 4))

        path_row = tk.Frame(self, bg=BG)
        path_row.pack(fill="x", padx=28)

        self.path_var   = tk.StringVar()
        self.path_entry = tk.Entry(path_row, textvariable=self.path_var,
                                   bg="#333333", fg=FG, font=("Arial", 10),
                                   relief="flat", insertbackground=FG)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(path_row, text="...", command=self._browse,
                  bg="#555555", fg=FG, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10
                  ).pack(side="left", padx=(6, 0))

        # ---- botões ----
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=28, pady=20)

        tk.Button(btn_row, text="Cancelar", command=self._cancel,
                  bg="#555555", fg=FG, font=("Arial", 11),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="▶️ Continuar", command=self._confirm,
                  bg=GREEN, fg=FG, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right")

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _update_frames(self):
        BG_SEL  = "#1e3a2f"
        BG_CARD = "#2a2a2a"
        mode = self.mode_var.get()
        for value, frame in self._mode_frames.items():
            bg = BG_SEL if value == mode else BG_CARD
            self._repaint(frame, bg)

    def _repaint(self, widget, bg):
        try:
            widget.config(bg=bg)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._repaint(child, bg)

    def _browse(self):
        folder = filedialog.askdirectory(title="Selecione a Pasta Base",
                                         mustexist=True)
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
        LOGGER.info("ImportMode confirmado: modo=%s pasta=%s",
                    self.result[0], self.result[1])
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
