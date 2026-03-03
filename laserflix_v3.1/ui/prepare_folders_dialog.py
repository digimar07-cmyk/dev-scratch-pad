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
    prep_btn = add_prepare_button(self, extras_frame)
    prep_btn.pack(side="left", padx=5)
"""

import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading
import os
import sys
from utils.logging_setup import LOGGER

# Colors (Netflix-style)
BG_PRIMARY = "#141414"
BG_SECONDARY = "#1F1F1F"
BG_CARD = "#2A2A2A"
ACCENT_RED = "#E50914"
ACCENT_GREEN = "#46D369"
FG_PRIMARY = "#FFFFFF"
FG_SECONDARY = "#B3B3B3"
FG_TERTIARY = "#808080"


class PrepareFoldersDialog(tk.Toplevel):
    """
    Dialog para executar prepare_folders.py com interface gráfica.
    
    Permite escolher modo e pasta, e exibe output em tempo real.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("📦 Preparar Pastas - Gerar folder.jpg")
        self.geometry("800x750")  # Aumentado para garantir visibilidade
        self.configure(bg=BG_PRIMARY)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"800x750+{x}+{y}")
        
        # Variáveis
        self.selected_path = ""
        self.mode_var = tk.StringVar(value="smart")
        self.is_running = False
        self.process = None
        
        # Constrói UI
        self._build_ui()
        
        # Modal
        if parent:
            self.transient(parent)
            self.grab_set()
        
        LOGGER.info("PrepareFoldersDialog aberto")

    def _build_ui(self):
        """Constrói interface."""
        
        # Container principal
        main_frame = tk.Frame(self, bg=BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ============================================================
        # HEADER
        # ============================================================
        header_frame = tk.Frame(main_frame, bg=BG_SECONDARY)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = tk.Label(
            header_frame,
            text="📦 Preparar Pastas para Importação",
            font=("Segoe UI", 18, "bold"),
            bg=BG_SECONDARY,
            fg=FG_PRIMARY
        )
        title.pack(pady=10)
        
        desc = tk.Label(
            header_frame,
            text="Gera folder.jpg automaticamente em pastas de produtos",
            font=("Segoe UI", 11),
            bg=BG_SECONDARY,
            fg=FG_SECONDARY
        )
        desc.pack(pady=(0, 10))
        
        # ============================================================
        # SELEÇÃO DE PASTA
        # ============================================================
        path_frame = tk.Frame(main_frame, bg=BG_CARD)
        path_frame.pack(fill="x", pady=(0, 20))
        
        path_label = tk.Label(
            path_frame,
            text="📁 Pasta Base:",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=FG_PRIMARY,
            anchor="w"
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        path_input_frame = tk.Frame(path_frame, bg=BG_CARD)
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.path_entry = tk.Entry(
            path_input_frame,
            bg="#333333",
            fg=FG_PRIMARY,
            font=("Segoe UI", 10),
            relief="flat",
            insertbackground=FG_PRIMARY
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=6)
        self.path_entry.insert(0, "Selecione a pasta base...")
        self.path_entry.config(fg=FG_TERTIARY)
        
        # Placeholder behavior
        def on_entry_focus_in(event):
            if self.path_entry.get() == "Selecione a pasta base...":
                self.path_entry.delete(0, "end")
                self.path_entry.config(fg=FG_PRIMARY)
        
        def on_entry_focus_out(event):
            if not self.path_entry.get():
                self.path_entry.insert(0, "Selecione a pasta base...")
                self.path_entry.config(fg=FG_TERTIARY)
        
        self.path_entry.bind("<FocusIn>", on_entry_focus_in)
        self.path_entry.bind("<FocusOut>", on_entry_focus_out)
        
        browse_btn = tk.Button(
            path_input_frame,
            text="...",
            command=self._browse_folder,
            bg=ACCENT_RED,
            fg=FG_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=6
        )
        browse_btn.pack(side="right")
        
        # ============================================================
        # MODO
        # ============================================================
        mode_frame = tk.Frame(main_frame, bg=BG_CARD)
        mode_frame.pack(fill="x", pady=(0, 20))
        
        mode_title = tk.Label(
            mode_frame,
            text="⚙️ Modo:",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=FG_PRIMARY,
            anchor="w"
        )
        mode_title.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Radio buttons
        smart_radio = tk.Radiobutton(
            mode_frame,
            text="🎯 Smart (Recomendado)",
            variable=self.mode_var,
            value="smart",
            bg=BG_CARD,
            fg=FG_PRIMARY,
            selectcolor="#333333",
            activebackground=BG_CARD,
            activeforeground=ACCENT_RED,
            font=("Segoe UI", 10)
        )
        smart_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        smart_desc = tk.Label(
            mode_frame,
            text="Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=FG_SECONDARY
        )
        smart_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        all_radio = tk.Radiobutton(
            mode_frame,
            text="🌐 All",
            variable=self.mode_var,
            value="all",
            bg=BG_CARD,
            fg=FG_PRIMARY,
            selectcolor="#333333",
            activebackground=BG_CARD,
            activeforeground=ACCENT_RED,
            font=("Segoe UI", 10)
        )
        all_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        all_desc = tk.Label(
            mode_frame,
            text="TODAS as pastas com imagens",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=FG_SECONDARY
        )
        all_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        list_radio = tk.Radiobutton(
            mode_frame,
            text="📋 List (Dry-run)",
            variable=self.mode_var,
            value="list",
            bg=BG_CARD,
            fg=FG_PRIMARY,
            selectcolor="#333333",
            activebackground=BG_CARD,
            activeforeground=ACCENT_RED,
            font=("Segoe UI", 10)
        )
        list_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        list_desc = tk.Label(
            mode_frame,
            text="Apenas lista, não cria nada",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=FG_SECONDARY
        )
        list_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        # ============================================================
        # OUTPUT
        # ============================================================
        output_frame = tk.Frame(main_frame, bg=BG_CARD)
        output_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        output_label = tk.Label(
            output_frame,
            text="📋 Output:",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=FG_PRIMARY,
            anchor="w"
        )
        output_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Text com scrollbar
        text_frame = tk.Frame(output_frame, bg=BG_CARD)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.output_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Consolas", 9),
            bg="#1A1A1A",
            fg=FG_SECONDARY,
            yscrollcommand=scrollbar.set,
            relief="flat",
            padx=10,
            pady=10
        )
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        # ============================================================
        # BOTÕES - ORDEM CORRIGIDA!
        # ============================================================
        button_frame = tk.Frame(main_frame, bg=BG_PRIMARY)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Fechar (à direita)
        self.close_btn = tk.Button(
            button_frame,
            text="Fechar",
            command=self._close,
            bg="#555555",
            fg=FG_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=12
        )
        self.close_btn.pack(side="right", padx=(10, 0))
        
        # Botão Executar (empacotado antes para aparecer à esquerda do Fechar)
        self.run_btn = tk.Button(
            button_frame,
            text="▶️ Executar",
            command=self._run,
            bg=ACCENT_GREEN,
            fg=FG_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=12
        )
        self.run_btn.pack(side="right", padx=(0, 10))

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
            self.path_entry.config(fg=FG_PRIMARY)

    def _run(self):
        """Executa prepare_folders.py."""
        # Validação
        if not self.selected_path or self.path_entry.get() == "Selecione a pasta base...":
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
        self.run_btn.config(state="disabled", text="⏸️ Executando...")
        
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
            self.run_btn.config(state="normal", text="▶️ Executar")

    def _log(self, text: str, tag: str = "normal"):
        """Adiciona texto ao output."""
        self.output_text.insert("end", text)
        self.output_text.see("end")  # Auto-scroll
        self.output_text.update_idletasks()

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

def add_prepare_button(main_window, parent_frame):
    """
    Adiciona botão "Preparar Pastas" no main_window.
    
    Args:
        main_window: Instância da janela principal
        parent_frame: Frame onde adicionar botão
    
    Uso:
        # No main_window.py:
        from ui.prepare_folders_dialog import add_prepare_button
        prep_btn = add_prepare_button(self, extras_frame)
        prep_btn.pack(side="left", padx=5)
    
    Returns:
        Button widget
    """
    def on_prepare():
        dialog = PrepareFoldersDialog(main_window.root)
        main_window.root.wait_window(dialog)
    
    btn = tk.Button(
        parent_frame,
        text="📦 Preparar Arquivos",
        command=on_prepare,
        bg="#FF6B6B",
        fg="#FFFFFF",
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8
    )
    
    return btn


# ================================================================
# TESTE STANDALONE
# ================================================================
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    
    dialog = PrepareFoldersDialog(root)
    root.wait_window(dialog)
    
    root.destroy()
