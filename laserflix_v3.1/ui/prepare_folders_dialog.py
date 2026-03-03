#!/usr/bin/env python3
"""
prepare_folders_dialog.py — Dialog para executar prepare_folders.py na interface.
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
GREEN = "#00dd00"
RED = "#E50914"
WHITE = "#ffffff"
GRAY = "#888888"


class PrepareFoldersDialog(tk.Toplevel):
    """Dialog para preparar pastas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("📦 Preparar Pastas")
        self.configure(bg=BG_DARK)
        
        # MAXIMIZA A JANELA
        self.state('zoomed')  # Windows/Linux
        try:
            self.attributes('-zoomed', True)  # macOS
        except:
            pass
        
        # Variáveis
        self.selected_path = ""
        self.mode_var = tk.StringVar(value="smart")
        self.is_running = False
        self.process = None
        
        self._build_ui()
        
        if parent:
            self.transient(parent)
            self.grab_set()
        
        LOGGER.info("PrepareFoldersDialog aberto (MAXIMIZADO)")

    def _build_ui(self):
        """Constrói interface."""
        
        # CONTAINER PRINCIPAL
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== BOTÕES NO TOPO (PRIMEIRO!) =====
        btn_frame = tk.Frame(main, bg=BG_DARK)
        btn_frame.pack(fill="x", pady=(0, 30))
        
        # BOTÃO EXECUTAR
        self.run_btn = tk.Button(
            btn_frame,
            text="▶️ EXECUTAR PREPARAÇÃO",
            command=self._run,
            bg=GREEN,
            fg="#000000",
            font=("Arial", 14, "bold"),
            relief="raised",
            cursor="hand2",
            bd=4,
            height=3,
            width=30
        )
        self.run_btn.pack(side="left", padx=(0, 15))
        
        # BOTÃO FECHAR
        tk.Button(
            btn_frame,
            text="FECHAR",
            command=self._close,
            bg="#555555",
            fg=WHITE,
            font=("Arial", 14, "bold"),
            relief="raised",
            cursor="hand2",
            bd=4,
            height=3,
            width=20
        ).pack(side="left")
        
        # ===== HEADER =====
        tk.Label(
            main,
            text="📦 Preparar Pastas para Importação",
            font=("Arial", 16, "bold"),
            bg=BG_DARK,
            fg=WHITE
        ).pack(pady=(0, 5))
        
        tk.Label(
            main,
            text="Gera folder.jpg automaticamente em todas as pastas de produtos",
            font=("Arial", 11),
            bg=BG_DARK,
            fg=GRAY
        ).pack(pady=(0, 20))
        
        # ===== PASTA =====
        pasta_frame = tk.Frame(main, bg=BG_CARD)
        pasta_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            pasta_frame,
            text="📁 Pasta Base:",
            font=("Arial", 12, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 8))
        
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
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.path_entry.insert(0, "Clique em [...] para selecionar a pasta")
        
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
        modo_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            modo_frame,
            text="⚙️ Modo de Preparação:",
            font=("Arial", 12, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        modes = [
            ("smart", "Smart (Recomendado) - Apenas pastas com arquivos de projeto"),
            ("all", "All - TODAS as pastas com imagens"),
            ("list", "List (Dry-run) - Apenas lista, não cria nada")
        ]
        
        for value, label in modes:
            tk.Radiobutton(
                modo_frame,
                text=label,
                variable=self.mode_var,
                value=value,
                bg=BG_CARD,
                fg=WHITE,
                selectcolor="#3a3a3a",
                activebackground=BG_CARD,
                font=("Arial", 10)
            ).pack(anchor="w", padx=30, pady=2)
        
        tk.Label(modo_frame, text="", bg=BG_CARD).pack(pady=5)
        
        # ===== OUTPUT =====
        output_frame = tk.Frame(main, bg=BG_CARD)
        output_frame.pack(fill="both", expand=True)
        
        tk.Label(
            output_frame,
            text="📋 Output / Log:",
            font=("Arial", 12, "bold"),
            bg=BG_CARD,
            fg=WHITE
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
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
        
        # Mensagem inicial
        self.output_text.insert("1.0", "✅ Pronto para executar.\nℹ️ Selecione a pasta e clique em EXECUTAR PREPARAÇÃO.\n")

    def _browse(self):
        """Seleciona pasta."""
        folder = filedialog.askdirectory(
            title="Selecione a Pasta Base",
            initialdir=os.path.expanduser("~")
        )
        if folder:
            self.selected_path = folder
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)
            self._log(f"\n✅ Pasta selecionada: {folder}\n")
            LOGGER.info(f"Pasta selecionada: {folder}")

    def _run(self):
        """Executa prepare_folders.py."""
        if not self.selected_path:
            self._log("\n❌ ERRO: Selecione uma pasta primeiro!\n")
            return
        
        if not os.path.exists(self.selected_path):
            self._log("\n❌ ERRO: Pasta não existe!\n")
            return
        
        if self.is_running:
            self._log("\n⚠️ Já está executando!\n")
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
                self._log(f"\n❌ Script não encontrado: {script}\n")
                return
            
            # Comando
            mode = self.mode_var.get()
            cmd = [sys.executable, script, self.selected_path, f"--{mode}"]
            
            self._log(f"▶️ Executando: {' '.join(cmd)}\n\n")
            LOGGER.info(f"Executando: {cmd}")
            
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
                self._log("\n\n✅ CONCLUÍDO COM SUCESSO!\n")
                LOGGER.info("Preparação concluída com sucesso")
            else:
                self._log(f"\n\n❌ ERRO (código {self.process.returncode})\n")
                LOGGER.error(f"Erro na preparação: {self.process.returncode}")
        
        except Exception as e:
            self._log(f"\n\n❌ ERRO: {e}\n")
            LOGGER.error(f"Erro ao executar: {e}", exc_info=True)
        
        finally:
            self.is_running = False
            self.run_btn.config(
                state="normal",
                text="▶️ EXECUTAR PREPARAÇÃO",
                bg=GREEN
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
            LOGGER.info("Processo terminado pelo usuário")
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
    print("✅ Abrindo dialog MAXIMIZADO...")
    root = tk.Tk()
    root.withdraw()
    
    dialog = PrepareFoldersDialog(root)
    
    print("✅ Dialog aberto. O BOTÃO VERDE ESTÁ NO TOPO!")
    
    root.wait_window(dialog)
    print("✅ Dialog fechado")
    root.destroy()
