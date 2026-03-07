"""
prepare_folders_dialog.py — Dialog para executar prepare_folders.py.
Tkinter puro — sem customtkinter.

Executa o script standalone em thread separada e mostra output em tempo real.
"""

import tkinter as tk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
from utils.logging_setup import LOGGER


class PrepareFoldersDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("📦 Preparar Pastas")
        self.geometry("750x820")
        self.resizable(True, True)
        self.configure(bg="#1a1a1a")

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 750) // 2
        y = (self.winfo_screenheight() - 820) // 2
        self.geometry(f"750x820+{x}+{y}")

        self.selected_path = ""
        self.mode_var  = tk.StringVar(value="smart")
        self.is_running = False
        self.process    = None

        self._build_ui()

        if parent:
            self.transient(parent)
            self.grab_set()

        LOGGER.info("PrepareFoldersDialog aberto")

    def _build_ui(self):
        BG      = "#1a1a1a"
        BG_CARD = "#2a2a2a"
        FG      = "#f0f0f0"
        FG_SEC  = "#999999"
        GREEN   = "#4caf50"

        # Header
        tk.Label(self, text="📦 Preparar Pastas para Importação",
                 font=("Arial", 16, "bold"), bg=BG, fg=FG).pack(pady=(18, 4))
        tk.Label(self, text="Gera folder.jpg automaticamente em pastas de produtos",
                 font=("Arial", 10), bg=BG, fg=FG_SEC).pack(pady=(0, 12))

        # Pasta
        tk.Label(self, text="📁 Pasta Base:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG
                 ).pack(anchor="w", padx=20, pady=(8, 4))

        path_row = tk.Frame(self, bg=BG)
        path_row.pack(fill="x", padx=20)
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(path_row, textvariable=self.path_var,
                                   bg="#333333", fg=FG, font=("Arial", 10),
                                   relief="flat", insertbackground=FG)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(path_row, text="...", command=self._browse,
                  bg="#555555", fg=FG, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10
                  ).pack(side="left", padx=(6, 0))

        # Modo
        tk.Label(self, text="⚙️ Modo de Preparação:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG
                 ).pack(anchor="w", padx=20, pady=(14, 6))

        mode_frame = tk.Frame(self, bg=BG_CARD)
        mode_frame.pack(fill="x", padx=20)

        modes = [
            ("smart", "🎯 Smart (Recomendado)",
             "Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)"),
            ("all",   "🌐 All",
             "TODAS as pastas com imagens"),
            ("list",  "📋 List (Dry-run)",
             "Apenas lista, não cria nada"),
        ]
        for value, label, desc in modes:
            row = tk.Frame(mode_frame, bg=BG_CARD)
            row.pack(fill="x", padx=10, pady=4)
            tk.Radiobutton(row, text=label, variable=self.mode_var, value=value,
                           bg=BG_CARD, fg=FG, selectcolor="#1e3a2f",
                           activebackground=BG_CARD,
                           font=("Arial", 11, "bold")
                           ).pack(anchor="w", padx=8)
            tk.Label(row, text=desc, font=("Arial", 9), bg=BG_CARD, fg=FG_SEC,
                     anchor="w").pack(anchor="w", padx=28)

        # Botões
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=14)

        tk.Button(btn_row, text="Fechar", command=self._close,
                  bg="#555555", fg=FG, font=("Arial", 11),
                  relief="flat", cursor="hand2", padx=18, pady=10
                  ).pack(side="right", padx=(8, 0))

        self.run_btn = tk.Button(btn_row, text="▶️ Executar",
                                  command=self._run,
                                  bg=GREEN, fg=FG, font=("Arial", 11, "bold"),
                                  relief="flat", cursor="hand2",
                                  padx=18, pady=10)
        self.run_btn.pack(side="right")

        # Output
        tk.Label(self, text="📋 Output / Log:",
                 font=("Arial", 11, "bold"), bg=BG, fg=FG
                 ).pack(anchor="w", padx=20, pady=(8, 4))

        output_frame = tk.Frame(self, bg=BG_CARD)
        output_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        sb = tk.Scrollbar(output_frame)
        sb.pack(side="right", fill="y")

        self.output_text = tk.Text(
            output_frame, font=("Courier", 9), wrap="word",
            bg="#111111", fg="#cccccc",
            relief="flat", yscrollcommand=sb.set
        )
        self.output_text.pack(fill="both", expand=True)
        sb.config(command=self.output_text.yview)

        self._log("✅ Pronto para executar.\nℹ️ Selecione a pasta e clique em EXECUTAR.\n")
        self.output_text.config(state="disabled")

    def _browse(self):
        folder = filedialog.askdirectory(title="Selecione a Pasta Base", mustexist=True)
        if folder:
            self.selected_path = folder
            self.path_var.set(folder)
            self._log(f"\n✅ Pasta: {folder}\n")
            LOGGER.info("Pasta selecionada: %s", folder)

    def _run(self):
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            self._log("\n❌ ERRO: Selecione uma pasta válida!\n")
            self.path_entry.config(bg="#5a1a1a")
            self.after(1000, lambda: self.path_entry.config(bg="#333333"))
            return
        if self.is_running:
            self._log("\n⚠️ Já está executando!\n")
            return

        self.selected_path = path
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.is_running = True
        self.run_btn.config(state="disabled", text="⏸️ Executando...", bg="#555555")
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script = os.path.join(script_dir, "prepare_folders.py")
            if not os.path.exists(script):
                self._log(f"\n❌ Script não encontrado: {script}\n")
                return
            mode = self.mode_var.get()
            cmd = [sys.executable, script, self.selected_path, f"--{mode}"]
            self._log(f"▶️ Executando: {' '.join(cmd)}\n\n")
            LOGGER.info("Executando: %s", cmd)
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', bufsize=1
            )
            for line in self.process.stdout:
                self._log(line)
            self.process.wait()
            if self.process.returncode == 0:
                self._log("\n✅ CONCLUÍDO COM SUCESSO!\n")
                LOGGER.info("Preparação concluída")
            else:
                self._log(f"\n❌ ERRO (código {self.process.returncode})\n")
                LOGGER.error("Erro: %d", self.process.returncode)
        except Exception as e:
            self._log(f"\n❌ ERRO: {e}\n")
            LOGGER.error("Erro: %s", e, exc_info=True)
        finally:
            self.is_running = False
            self.after(0, lambda: self.run_btn.config(
                state="normal", text="▶️ Executar", bg="#4caf50"))

    def _log(self, text: str):
        try:
            self.output_text.config(state="normal")
            self.output_text.insert("end", text)
            self.output_text.see("end")
            self.output_text.config(state="disabled")
            self.output_text.update_idletasks()
        except Exception:
            pass

    def _close(self):
        if self.is_running and self.process:
            self.process.terminate()
            LOGGER.info("Processo terminado")
        self.destroy()
