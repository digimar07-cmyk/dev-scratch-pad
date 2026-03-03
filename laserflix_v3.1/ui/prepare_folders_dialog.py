#!/usr/bin/env python3
"""
prepare_folders_dialog.py — Dialog para executar prepare_folders.py na interface.

INTEGRA O SCRIPT STANDALONE NO APP:
  - Interface gráfica para prepare_folders.py
  - Executa em thread separada
  - Mostra output em tempo real
  - Barra de progresso
  - Relatório visual
"""

import tkinter as tk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
from utils.logging_setup import LOGGER

# Colors
BG_DARK = "#1a1a1a"
BG_CARD = "#2d2d2d"
GREEN = "#00ff00"
RED = "#ff0000"
WHITE = "#ffffff"
GRAY = "#888888"


class PrepareFoldersDialog(tk.Toplevel):
    """Dialog SIMPLES e FUNCIONAL para preparar pastas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("📦 PREPARAR PASTAS")
        self.geometry("900x700")
        self.configure(bg=BG_DARK)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 900) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"900x700+{x}+{y}")
        
        # Variáveis
        self.selected_path = ""
        self.mode_var = tk.StringVar(value="smart")
        self.is_running = False
        self.process = None
        
        self._build_ui()
        
        if parent:
            self.transient(parent)
            self.grab_set()
        
        LOGGER.info("PrepareFoldersDialog iniciado")

    def _build_ui(self):
        """Constrói interface SIMPLES."""
        
        # CONTAINER PRINCIPAL
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=30, pady=30)
        
        # ===== HEADER =====
        tk.Label(
            main,
            text="📦 PREPARAR PASTAS PARA IMPORTAÇÃO",
            font=("Arial", 20, "bold"),
            bg=BG_DARK,
            fg=WHITE
        ).pack(pady=(0, 10))
        
        tk.Label(
            main,
            text="Gera folder.jpg automaticamente em todas as pastas",
            font=("Arial", 12),
            bg=BG_DARK,
            fg=GRAY
        ).pack(pady=(0, 30))
        
        # ===== PASTA =====
        pasta_frame = tk.Frame(main, bg=BG_CARD)
        pasta_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            pasta_frame,
            text="📁 PASTA BASE:",
            font=("Arial", 14, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Input + Botão browse
        input_frame = tk.Frame(pasta_frame, bg=BG_CARD)
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.path_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg="#3a3a3a",
            fg=WHITE,
            relief="flat",
            insertbackground=WHITE
        )
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.path_entry.insert(0, "Clique em ... para selecionar")
        
        tk.Button(
            input_frame,
            text="...",
            command=self._browse,
            bg=RED,
            fg=WHITE,
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2",
            width=5
        ).pack(side="right", padx=(10, 0))
        
        # ===== MODO =====
        modo_frame = tk.Frame(main, bg=BG_CARD)
        modo_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            modo_frame,
            text="⚙️ MODO:",
            font=("Arial", 14, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        for value, label in [("smart", "Smart (Recomendado)"), ("all", "All"), ("list", "List (Dry-run)")]:
            tk.Radiobutton(
                modo_frame,
                text=label,
                variable=self.mode_var,
                value=value,
                bg=BG_CARD,
                fg=WHITE,
                selectcolor="#3a3a3a",
                activebackground=BG_CARD,
                font=("Arial", 11)
            ).pack(anchor="w", padx=30, pady=3)
        
        tk.Label(modo_frame, text="", bg=BG_CARD).pack(pady=5)  # Espaço
        
        # ===== OUTPUT =====
        output_frame = tk.Frame(main, bg=BG_CARD)
        output_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        tk.Label(
            output_frame,
            text="📋 OUTPUT:",
            font=("Arial", 14, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Text com scroll
        text_container = tk.Frame(output_frame, bg=BG_CARD)
        text_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side="right", fill="y")
        
        self.output_text = tk.Text(
            text_container,
            wrap="word",
            font=("Courier", 9),
            bg="#0a0a0a",
            fg=GREEN,
            yscrollcommand=scrollbar.set,
            relief="flat"
        )
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        # ===== BOTÕES ENORMES E VISÍVEIS =====
        btn_frame = tk.Frame(main, bg=BG_DARK)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        # BOTÃO EXECUTAR - VERDE ENORME
        self.run_btn = tk.Button(
            btn_frame,
            text="▶️ EXECUTAR",
            command=self._run,
            bg="#00cc00",
            fg="#000000",
            font=("Arial", 16, "bold"),
            relief="raised",
            cursor="hand2",
            bd=3,
            height=2
        )
        self.run_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # BOTÃO FECHAR
        tk.Button(
            btn_frame,
            text="FECHAR",
            command=self._close,
            bg="#666666",
            fg=WHITE,
            font=("Arial", 16, "bold"),
            relief="raised",
            cursor="hand2",
            bd=3,
            height=2
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))

    def _browse(self):
        """Seleciona pasta."""
        folder = filedialog.askdirectory(title="Selecione a Pasta Base")
        if folder:
            self.selected_path = folder
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)
            LOGGER.info(f"Pasta selecionada: {folder}")

    def _run(self):
        """Executa prepare_folders.py."""
        if not self.selected_path:
            self._log("❌ ERRO: Selecione uma pasta!\n")
            return
        
        if not os.path.exists(self.selected_path):
            self._log("❌ ERRO: Pasta não existe!\n")
            return
        
        if self.is_running:
            self._log("⚠️ Já está executando!\n")
            return
        
        # Limpa output
        self.output_text.delete("1.0", "end")
        
        # Desabilita botão
        self.is_running = True
        self.run_btn.config(
            state="disabled",
            text="⏸️ EXECUTANDO...",
            bg="#666666"
        )
        
        # Executa em thread
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        """Executa script."""
        try:
            # Localiza script
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script = os.path.join(script_dir, "prepare_folders.py")
            
            if not os.path.exists(script):
                self._log(f"❌ Script não encontrado: {script}\n")
                return
            
            # Comando
            mode = self.mode_var.get()
            cmd = [sys.executable, script, self.selected_path, f"--{mode}"]
            
            self._log(f"▶️ Executando: {' '.join(cmd)}\n\n")
            
            # Executa
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Lê output
            for line in self.process.stdout:
                self._log(line)
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self._log("\n✅ CONCLUÍDO COM SUCESSO!\n")
            else:
                self._log(f"\n❌ ERRO (código {self.process.returncode})\n")
        
        except Exception as e:
            self._log(f"\n❌ ERRO: {e}\n")
            LOGGER.error(f"Erro: {e}", exc_info=True)
        
        finally:
            self.is_running = False
            self.run_btn.config(
                state="normal",
                text="▶️ EXECUTAR",
                bg="#00cc00"
            )

    def _log(self, text: str):
        """Adiciona ao output."""
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.update_idletasks()

    def _close(self):
        """Fecha dialog."""
        if self.is_running and self.process:
            self.process.terminate()
        self.destroy()


# ================================================================
# FUNÇÃO DE INTEGRAÇÃO
# ================================================================

def add_prepare_button(main_window, parent_frame):
    """
    Adiciona botão no main_window.
    
    Uso:
        from ui.prepare_folders_dialog import add_prepare_button
        btn = add_prepare_button(self, frame)
        btn.pack(side="left", padx=5)
    """
    def on_click():
        dialog = PrepareFoldersDialog(main_window.root)
        main_window.root.wait_window(dialog)
    
    return tk.Button(
        parent_frame,
        text="📦 Preparar Arquivos",
        command=on_click,
        bg="#FF6B6B",
        fg="#FFFFFF",
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8
    )


# ================================================================
# TESTE STANDALONE
# ================================================================
if __name__ == '__main__':
    print("✅ Abrindo dialog de teste...")
    root = tk.Tk()
    root.withdraw()
    
    dialog = PrepareFoldersDialog(root)
    root.wait_window(dialog)
    
    print("✅ Dialog fechado")
    root.destroy()
