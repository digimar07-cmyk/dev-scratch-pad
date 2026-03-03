#!/usr/bin/env python3
"""
import_mode_dialog.py — Dialog para escolher modo de importação.

DIALOG SIMPLES:
  1. Escolhe modo: Puro ou Híbrido
  2. Seleciona pasta base
  3. Retorna (modo, pasta) ou None se cancelado

MODOS:
  - PURO: Apenas pastas com folder.jpg
  - HÍBRIDO: folder.jpg + fallback (primeira imagem)
"""

import customtkinter as ctk
from tkinter import filedialog
import os
from utils.logging_setup import LOGGER


class ImportModeDialog(ctk.CTkToplevel):
    """
    Dialog para escolher modo de importação e pasta base.
    
    Retorna tupla (modo, pasta) ou None se cancelado.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("🚀 Importação em Massa - Escolha o Modo")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")
        
        # Resultado
        self.result = None
        self.selected_path = ""
        
        # IMPORTANTE: Criar StringVar ANTES de criar RadioButtons
        self.mode_var = ctk.StringVar(value="hybrid")  # Padrão: Híbrido
        
        # Constrói UI
        self._build_ui()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        LOGGER.info("ImportModeDialog aberto")

    def _build_ui(self):
        """Constrói interface do dialog."""
        
        # Container principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ============================================================
        # HEADER
        # ============================================================
        header = ctk.CTkLabel(
            main_frame,
            text="🚀 Importação em Massa",
            font=("Segoe UI", 22, "bold")
        )
        header.pack(pady=(10, 5))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Escolha o modo de detecção de produtos",
            font=("Segoe UI", 12),
            text_color="gray70"
        )
        subtitle.pack(pady=(0, 20))
        
        # ============================================================
        # OPÇÕES DE MODO
        # ============================================================
        
        # Modo Híbrido (Recomendado)
        hybrid_frame = ctk.CTkFrame(main_frame)
        hybrid_frame.pack(fill="x", padx=10, pady=10)
        
        self.hybrid_radio = ctk.CTkRadioButton(
            hybrid_frame,
            text="",
            variable=self.mode_var,  # MESMA variable!
            value="hybrid",
            width=30
        )
        self.hybrid_radio.pack(side="left", padx=(15, 10), pady=15)
        
        hybrid_info = ctk.CTkFrame(hybrid_frame, fg_color="transparent")
        hybrid_info.pack(side="left", fill="x", expand=True, pady=10)
        
        ctk.CTkLabel(
            hybrid_info,
            text="🔄 Modo Híbrido (Recomendado)",
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            hybrid_info,
            text="• Busca folder.jpg + fallback\n"
                 "• Detecta mais produtos\n"
                 "• Preview antes de importar",
            font=("Segoe UI", 10),
            text_color="gray70",
            anchor="w",
            justify="left"
        ).pack(anchor="w", padx=10, pady=(5, 5))
        
        # Modo Puro
        pure_frame = ctk.CTkFrame(main_frame)
        pure_frame.pack(fill="x", padx=10, pady=10)
        
        self.pure_radio = ctk.CTkRadioButton(
            pure_frame,
            text="",
            variable=self.mode_var,  # MESMA variable!
            value="pure",
            width=30
        )
        self.pure_radio.pack(side="left", padx=(15, 10), pady=15)
        
        pure_info = ctk.CTkFrame(pure_frame, fg_color="transparent")
        pure_info.pack(side="left", fill="x", expand=True, pady=10)
        
        ctk.CTkLabel(
            pure_info,
            text="🔒 Modo Puro (Controle Total)",
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            pure_info,
            text="• Apenas pastas com folder.jpg\n"
                 "• Zero falsos positivos\n"
                 "• Você decide o que importar",
            font=("Segoe UI", 10),
            text_color="gray70",
            anchor="w",
            justify="left"
        ).pack(anchor="w", padx=10, pady=(5, 5))
        
        # ============================================================
        # SELEÇÃO DE PASTA
        # ============================================================
        ctk.CTkLabel(
            main_frame,
            text="📁 Pasta Base:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(20, 5))
        
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Selecione a pasta base...",
            height=40
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="...",
            width=60,
            height=40,
            command=self._browse_folder
        )
        browse_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # ============================================================
        # BOTÕES
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            fg_color="gray40",
            hover_color="gray50",
            width=120,
            height=40
        ).pack(side="right", padx=(10, 10))
        
        ctk.CTkButton(
            button_frame,
            text="▶️ Escanear",
            command=self._confirm,
            width=120,
            height=40
        ).pack(side="right")

    def _browse_folder(self):
        """Abre dialog para selecionar pasta."""
        folder = filedialog.askdirectory(
            title="Selecione a Pasta Base",
            mustexist=True
        )
        
        if folder:
            self.selected_path = folder
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def _confirm(self):
        """Confirma seleção."""
        if not self.selected_path:
            # Mostra feedback visual
            self.path_entry.configure(border_color="red")
            self.after(1000, lambda: self.path_entry.configure(border_color="gray50"))
            return
        
        mode = self.mode_var.get()
        self.result = (mode, self.selected_path)
        self.destroy()

    def _cancel(self):
        """Cancela dialog."""
        self.result = None
        self.destroy()

    def get_result(self):
        """Retorna resultado do dialog."""
        return self.result


# ================================================================
# FUNÇÃO HELPER
# ================================================================

def show_import_mode_dialog(parent=None):
    """
    Mostra dialog e retorna (modo, pasta) ou None.
    
    Args:
        parent: Janela pai (opcional)
    
    Returns:
        tuple: ("pure"|"hybrid", "caminho/pasta") ou None se cancelado
    
    Exemplo:
        result = show_import_mode_dialog(main_window)
        if result:
            mode, base_path = result
            print(f"Modo: {mode}, Pasta: {base_path}")
    """
    dialog = ImportModeDialog(parent)
    parent.wait_window(dialog) if parent else dialog.wait_window()
    return dialog.get_result()


# ================================================================
# TESTE STANDALONE
# ================================================================
if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    
    result = show_import_mode_dialog(root)
    
    if result:
        mode, path = result
        print(f"✅ Selecionado:")
        print(f"   Modo: {mode}")
        print(f"   Pasta: {path}")
    else:
        print("❌ Cancelado")
    
    root.destroy()
