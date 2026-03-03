#!/usr/bin/env python3
"""
prepare_folders_dialog.py — Dialog para executar prepare_folders.py.

INTEGRA O SCRIPT STANDALONE NO APP:
  - Interface gráfica CustomTkinter
  - Executa em thread separada
  - Mostra output em tempo real
  - Visual harmonizado com import_mode_dialog
"""

import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
from utils.logging_setup import LOGGER


class PrepareFoldersDialog(ctk.CTkToplevel):
    """Dialog para preparar pastas com visual harmonizado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("📦 Preparar Pastas")
        self.geometry("750x850")
        self.resizable(True, True)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 750) // 2
        y = (self.winfo_screenheight() - 850) // 2
        self.geometry(f"750x850+{x}+{y}")
        
        # Variáveis
        self.selected_path = ""
        self.mode_var = ctk.StringVar(value="smart")
        self.is_running = False
        self.process = None
        
        self._build_ui()
        
        if parent:
            self.transient(parent)
            self.grab_set()
        
        LOGGER.info("PrepareFoldersDialog aberto")

    def _build_ui(self):
        """Constrói interface."""
        
        # CONTAINER PRINCIPAL
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== HEADER =====
        ctk.CTkLabel(
            main,
            text="📦 Preparar Pastas para Importação",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            main,
            text="Gera folder.jpg automaticamente em todas as pastas de produtos",
            font=("Segoe UI", 12),
            text_color="gray70"
        ).pack(pady=(0, 20))
        
        # ===== PASTA =====
        ctk.CTkLabel(
            main,
            text="📁 Pasta Base:",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        path_frame = ctk.CTkFrame(main)
        path_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Selecione a pasta base...",
            height=40
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkButton(
            path_frame,
            text="...",
            width=60,
            height=40,
            command=self._browse
        ).pack(side="right", padx=(5, 10), pady=10)
        
        # ===== BOTÕES (MOVIDOS PARA CÁ!) =====
        btn_frame = ctk.CTkFrame(main)
        btn_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Botão Fechar (à direita)
        ctk.CTkButton(
            btn_frame,
            text="Fechar",
            command=self._close,
            fg_color="gray40",
            hover_color="gray50",
            width=140,
            height=45
        ).pack(side="right", padx=(10, 0))
        
        # Botão Executar
        self.run_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ Executar",
            command=self._run,
            width=140,
            height=45,
            font=("Segoe UI", 13, "bold")
        )
        self.run_btn.pack(side="right", padx=(0, 10))
        
        # ===== MODO =====
        ctk.CTkLabel(
            main,
            text="⚙️ Modo de Preparação:",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(10, 10))
        
        mode_frame = ctk.CTkFrame(main)
        mode_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        modes = [
            ("smart", "🎯 Smart (Recomendado)", "Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)"),
            ("all", "🌐 All", "TODAS as pastas com imagens"),
            ("list", "📋 List (Dry-run)", "Apenas lista, não cria nada")
        ]
        
        for value, label, desc in modes:
            radio_container = ctk.CTkFrame(mode_frame)
            radio_container.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkRadioButton(
                radio_container,
                text=label,
                variable=self.mode_var,
                value=value,
                font=("Segoe UI", 12)
            ).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkLabel(
                radio_container,
                text=desc,
                font=("Segoe UI", 10),
                text_color="gray70",
                anchor="w"
            ).pack(anchor="w", padx=30, pady=(0, 5))
        
        # ===== OUTPUT =====
        ctk.CTkLabel(
            main,
            text="📋 Output / Log:",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        output_frame = ctk.CTkFrame(main)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=("Courier", 9),
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mensagem inicial
        self.output_text.insert("1.0", "✅ Pronto para executar.\nℹ️ Selecione a pasta e clique em EXECUTAR.\n")
        self.output_text.configure(state="disabled")

    def _browse(self):
        """Seleciona pasta."""
        folder = filedialog.askdirectory(
            title="Selecione a Pasta Base",
            mustexist=True
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
            self.path_entry.configure(border_color="red")
            self.after(1000, lambda: self.path_entry.configure(border_color="gray50"))
            return
        
        if not os.path.exists(self.selected_path):
            self._log("\n❌ ERRO: Pasta não existe!\n")
            return
        
        if self.is_running:
            self._log("\n⚠️ Já está executando!\n")
            return
        
        # Limpa output
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        
        # Desabilita botão
        self.is_running = True
        self.run_btn.configure(
            state="disabled",
            text="⏸️ Executando...",
            fg_color="gray50"
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
            
            # Executa com encoding UTF-8
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            # Lê output
            for line in self.process.stdout:
                self._log(line)
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self._log("\n\n✅ CONCLUÍDO COM SUCESSO!\n")
                LOGGER.info("Preparação concluída")
            else:
                self._log(f"\n\n❌ ERRO (código {self.process.returncode})\n")
                LOGGER.error(f"Erro: {self.process.returncode}")
        
        except Exception as e:
            self._log(f"\n\n❌ ERRO: {e}\n")
            LOGGER.error(f"Erro: {e}", exc_info=True)
        
        finally:
            self.is_running = False
            self.run_btn.configure(
                state="normal",
                text="▶️ Executar",
                fg_color=["#3B8ED0", "#1F6AA5"]
            )

    def _log(self, text: str):
        """Adiciona ao output."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
        self.output_text.update_idletasks()

    def _close(self):
        """Fecha dialog."""
        if self.is_running and self.process:
            self.process.terminate()
            LOGGER.info("Processo terminado")
        self.destroy()


# ================================================================
# FUNÇÃO DE INTEGRAÇÃO
# ================================================================

def add_prepare_button(main_window, parent_frame):
    """
    Adiciona botão no main_window.
    """
    import tkinter as tk
    
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
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    print("✅ Abrindo dialog...")
    root = ctk.CTk()
    root.withdraw()
    
    dialog = PrepareFoldersDialog(root)
    root.wait_window(dialog)
    
    print("✅ Dialog fechado")
    root.destroy()
