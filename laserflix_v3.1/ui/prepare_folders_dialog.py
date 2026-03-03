#!/usr/bin/env python3
"""
prepare_folders_dialog.py — Dialog para executar prepare_folders.py na interface.

INTEGRA O SCRIPT STANDALONE NO APP:
  - Interface gráfica para prepare_folders.py
  - Executa em thread separada
  - Mostra output em tempo real
  - Barra de progresso
  - Relatório visual

USO NO MAIN_WINDOW:
    from ui.prepare_folders_dialog import add_prepare_button
    add_prepare_button(self)
"""

import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
from utils.logging_setup import LOGGER


class PrepareFoldersDialog(ctk.CTkToplevel):
    """
    Dialog para executar prepare_folders.py com interface gráfica.
    
    Permite escolher modo e pasta, e exibe output em tempo real.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("📦 Preparar Pastas - Gerar folder.jpg")
        self.geometry("800x700")
        self.resizable(True, True)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"800x700+{x}+{y}")
        
        # Variáveis
        self.selected_path = ""
        self.selected_mode = "smart"
        self.is_running = False
        self.process = None
        
        # Constrói UI
        self._build_ui()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        LOGGER.info("PrepareFoldersDialog aberto")

    def _build_ui(self):
        """Constrói interface."""
        
        # Container principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ============================================================
        # HEADER
        # ============================================================
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📦 Preparar Pastas para Importação",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=10)
        
        desc = ctk.CTkLabel(
            header_frame,
            text="Gera folder.jpg automaticamente em pastas de produtos",
            font=("Segoe UI", 11),
            text_color="gray70"
        )
        desc.pack(pady=(0, 10))
        
        # ============================================================
        # SELEÇÃO DE PASTA
        # ============================================================
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="📁 Pasta Base:",
            font=("Segoe UI", 12, "bold")
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        path_input_frame = ctk.CTkFrame(path_frame)
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            placeholder_text="Selecione a pasta base...",
            height=35
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="...",
            width=50,
            height=35,
            command=self._browse_folder
        )
        browse_btn.pack(side="right")
        
        # ============================================================
        # MODO
        # ============================================================
        mode_frame = ctk.CTkFrame(main_frame)
        mode_frame.pack(fill="x", pady=(0, 20))
        
        mode_title = ctk.CTkLabel(
            mode_frame,
            text="⚙️ Modo:",
            font=("Segoe UI", 12, "bold")
        )
        mode_title.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Radio buttons
        self.mode_var = ctk.StringVar(value="smart")
        
        smart_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🎯 Smart (Recomendado)",
            variable=self.mode_var,
            value="smart"
        )
        smart_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        smart_desc = ctk.CTkLabel(
            mode_frame,
            text="Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)",
            font=("Segoe UI", 10),
            text_color="gray70"
        )
        smart_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        all_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🌐 All",
            variable=self.mode_var,
            value="all"
        )
        all_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        all_desc = ctk.CTkLabel(
            mode_frame,
            text="TODAS as pastas com imagens",
            font=("Segoe UI", 10),
            text_color="gray70"
        )
        all_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        list_radio = ctk.CTkRadioButton(
            mode_frame,
            text="📝 List (Dry-run)",
            variable=self.mode_var,
            value="list"
        )
        list_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        list_desc = ctk.CTkLabel(
            mode_frame,
            text="Apenas lista, não cria nada",
            font=("Segoe UI", 10),
            text_color="gray70"
        )
        list_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        # ============================================================
        # OUTPUT
        # ============================================================
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="📝 Output:",
            font=("Segoe UI", 12, "bold")
        )
        output_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.output_text = ctk.CTkTextbox(
            output_frame,
            wrap="word",
            font=("Consolas", 10)
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # ============================================================
        # BOTÕES
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Fechar",
            width=120,
            height=40,
            fg_color="gray40",
            hover_color="gray50",
            command=self._close
        )
        self.close_btn.pack(side="right", padx=(10, 0))
        
        self.run_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Executar",
            width=120,
            height=40,
            command=self._run
        )
        self.run_btn.pack(side="right")

    def _browse_folder(self):
        """Abre dialog para selecionar pasta."""
        folder = filedialog.askdirectory(
            title="Selecione a Pasta Base",
            initialdir=os.path.expanduser("~")
        )
        
        if folder:
            self.selected_path = folder
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def _run(self):
        """Executa prepare_folders.py."""
        if not self.selected_path:
            self._log("⚠️ Selecione uma pasta base!\n", "error")
            return
        
        if not os.path.exists(self.selected_path):
            self._log("⚠️ Pasta não existe!\n", "error")
            return
        
        if self.is_running:
            self._log("⚠️ Já está executando!\n", "warning")
            return
        
        # Limpa output
        self.output_text.delete("1.0", "end")
        
        # Inicia execução em thread
        self.is_running = True
        self.run_btn.configure(state="disabled", text="⏸️ Executando...")
        
        thread = threading.Thread(target=self._execute_script, daemon=True)
        thread.start()

    def _execute_script(self):
        """Executa script em thread separada."""
        try:
            # Caminho do script
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(script_dir, "prepare_folders.py")
            
            if not os.path.exists(script_path):
                self._log(f"❌ Script não encontrado: {script_path}\n", "error")
                return
            
            # Comando
            mode = self.mode_var.get()
            cmd = [
                sys.executable,
                script_path,
                self.selected_path,
                f"--{mode}"
            ]
            
            self._log(f"▶️ Executando: {' '.join(cmd)}\n\n", "info")
            
            # Executa
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Lê output em tempo real
            for line in self.process.stdout:
                self._log(line)
            
            # Aguarda finalização
            self.process.wait()
            
            if self.process.returncode == 0:
                self._log("\n\n✅ Concluído com sucesso!\n", "success")
            else:
                self._log(f"\n\n❌ Erro (código {self.process.returncode})\n", "error")
        
        except Exception as e:
            self._log(f"\n\n❌ Erro: {e}\n", "error")
            LOGGER.error(f"Erro ao executar script: {e}", exc_info=True)
        
        finally:
            self.is_running = False
            self.run_btn.configure(state="normal", text="▶️ Executar")

    def _log(self, text: str, tag: str = "normal"):
        """Adiciona texto ao output."""
        self.output_text.insert("end", text)
        self.output_text.see("end")  # Auto-scroll

    def _close(self):
        """Fecha dialog."""
        if self.is_running:
            # Tenta matar processo
            if self.process:
                self.process.terminate()
        
        self.destroy()


# ================================================================
# FUNÇÃO DE INTEGRAÇÃO PARA MAIN_WINDOW
# ================================================================

def add_prepare_button(main_window, parent_frame=None):
    """
    Adiciona botão "Preparar Pastas" no main_window.
    
    Args:
        main_window: Instância da janela principal
        parent_frame: Frame onde adicionar botão (opcional)
    
    Uso:
        # No main_window.py:
        from ui.prepare_folders_dialog import add_prepare_button
        add_prepare_button(self, self.sidebar_frame)
    """
    def on_prepare():
        dialog = PrepareFoldersDialog(main_window)
        main_window.wait_window(dialog)
    
    btn = ctk.CTkButton(
        parent_frame or main_window,
        text="📦 Preparar Pastas",
        command=on_prepare,
        height=40
    )
    
    return btn


# ================================================================
# TESTE STANDALONE
# ================================================================
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    
    dialog = PrepareFoldersDialog(root)
    root.wait_window(dialog)
    
    root.destroy()
