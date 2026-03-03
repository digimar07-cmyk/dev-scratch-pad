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
        self.geometry("600x550")  # Aumentado para garantir visibilidade
        self.resizable(False, False)
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"600x550+{x}+{y}")
        
        # Resultado
        self.result = None
        self.selected_path = ""
        
        # IMPORTANTE: Criar StringVar ANTES de criar RadioButtons
        self.mode_var = ctk.StringVar(value="hybrid")  # Padrão: Híbrido
        
        # Referências para frames
        self.hybrid_frame = None
        self.pure_frame = None
        
        # Constrói UI
        self._build_ui()
        
        # Inicializa seleção visual
        self._update_frame_borders()
        
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
        self.hybrid_frame = ctk.CTkFrame(main_frame, cursor="hand2")
        self.hybrid_frame.pack(fill="x", padx=10, pady=10)
        
        self.hybrid_radio = ctk.CTkRadioButton(
            self.hybrid_frame,
            text="",
            variable=self.mode_var,
            value="hybrid",
            width=30,
            cursor="hand2"
        )
        self.hybrid_radio.pack(side="left", padx=(15, 10), pady=15)
        
        hybrid_info = ctk.CTkFrame(self.hybrid_frame, fg_color="transparent", cursor="hand2")
        hybrid_info.pack(side="left", fill="x", expand=True, pady=10)
        
        hybrid_title = ctk.CTkLabel(
            hybrid_info,
            text="🔄 Modo Híbrido (Recomendado)",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
            cursor="hand2"
        )
        hybrid_title.pack(anchor="w", padx=10)
        
        hybrid_desc = ctk.CTkLabel(
            hybrid_info,
            text="• Busca folder.jpg + fallback\n"
                 "• Detecta mais produtos\n"
                 "• Preview antes de importar",
            font=("Segoe UI", 10),
            text_color="gray70",
            anchor="w",
            justify="left",
            cursor="hand2"
        )
        hybrid_desc.pack(anchor="w", padx=10, pady=(5, 5))
        
        # BIND: Tornar TODO o frame clicável
        self.hybrid_frame.bind("<Button-1>", lambda e: self._select_hybrid())
        hybrid_info.bind("<Button-1>", lambda e: self._select_hybrid())
        hybrid_title.bind("<Button-1>", lambda e: self._select_hybrid())
        hybrid_desc.bind("<Button-1>", lambda e: self._select_hybrid())
        
        # Hover effect
        self.hybrid_frame.bind("<Enter>", lambda e: self._on_hover_hybrid(True))
        self.hybrid_frame.bind("<Leave>", lambda e: self._on_hover_hybrid(False))
        hybrid_info.bind("<Enter>", lambda e: self._on_hover_hybrid(True))
        hybrid_info.bind("<Leave>", lambda e: self._on_hover_hybrid(False))
        
        # Modo Puro
        self.pure_frame = ctk.CTkFrame(main_frame, cursor="hand2")
        self.pure_frame.pack(fill="x", padx=10, pady=10)
        
        self.pure_radio = ctk.CTkRadioButton(
            self.pure_frame,
            text="",
            variable=self.mode_var,
            value="pure",
            width=30,
            cursor="hand2"
        )
        self.pure_radio.pack(side="left", padx=(15, 10), pady=15)
        
        pure_info = ctk.CTkFrame(self.pure_frame, fg_color="transparent", cursor="hand2")
        pure_info.pack(side="left", fill="x", expand=True, pady=10)
        
        pure_title = ctk.CTkLabel(
            pure_info,
            text="🔒 Modo Puro (Controle Total)",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
            cursor="hand2"
        )
        pure_title.pack(anchor="w", padx=10)
        
        pure_desc = ctk.CTkLabel(
            pure_info,
            text="• Apenas pastas com folder.jpg\n"
                 "• Zero falsos positivos\n"
                 "• Você decide o que importar",
            font=("Segoe UI", 10),
            text_color="gray70",
            anchor="w",
            justify="left",
            cursor="hand2"
        )
        pure_desc.pack(anchor="w", padx=10, pady=(5, 5))
        
        # BIND: Tornar TODO o frame clicável
        self.pure_frame.bind("<Button-1>", lambda e: self._select_pure())
        pure_info.bind("<Button-1>", lambda e: self._select_pure())
        pure_title.bind("<Button-1>", lambda e: self._select_pure())
        pure_desc.bind("<Button-1>", lambda e: self._select_pure())
        
        # Hover effect
        self.pure_frame.bind("<Enter>", lambda e: self._on_hover_pure(True))
        self.pure_frame.bind("<Leave>", lambda e: self._on_hover_pure(False))
        pure_info.bind("<Enter>", lambda e: self._on_hover_pure(True))
        pure_info.bind("<Leave>", lambda e: self._on_hover_pure(False))
        
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
        # BOTÕES - ORDEM CORRIGIDA!
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        # Botão Cancelar (à direita)
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            fg_color="gray40",
            hover_color="gray50",
            width=140,
            height=45
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Botão Escanear (à direita do Cancelar, mas empacotado primeiro)
        scan_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Escanear",
            command=self._confirm,
            width=140,
            height=45,
            font=("Segoe UI", 13, "bold")
        )
        scan_btn.pack(side="right", padx=(0, 10))
    
    # ================================================================
    # SELEÇÃO DE MODO
    # ================================================================
    
    def _select_hybrid(self):
        """Seleciona modo híbrido."""
        self.mode_var.set("hybrid")
        self._update_frame_borders()
    
    def _select_pure(self):
        """Seleciona modo puro."""
        self.mode_var.set("pure")
        self._update_frame_borders()
    
    def _update_frame_borders(self):
        """Atualiza borda dos frames baseado na seleção."""
        if not self.hybrid_frame or not self.pure_frame:
            return
        
        mode = self.mode_var.get()
        
        if mode == "hybrid":
            self.hybrid_frame.configure(border_width=2, border_color="#1f6aa5")
            self.pure_frame.configure(border_width=0)
        else:
            self.pure_frame.configure(border_width=2, border_color="#1f6aa5")
            self.hybrid_frame.configure(border_width=0)
    
    def _on_hover_hybrid(self, entering: bool):
        """Feedback visual ao passar mouse no frame híbrido."""
        if entering:
            if self.mode_var.get() != "hybrid":
                self.hybrid_frame.configure(border_width=1, border_color="gray50")
        else:
            if self.mode_var.get() != "hybrid":
                self.hybrid_frame.configure(border_width=0)
    
    def _on_hover_pure(self, entering: bool):
        """Feedback visual ao passar mouse no frame puro."""
        if entering:
            if self.mode_var.get() != "pure":
                self.pure_frame.configure(border_width=1, border_color="gray50")
        else:
            if self.mode_var.get() != "pure":
                self.pure_frame.configure(border_width=0)

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
        LOGGER.info(f"Confirmação: modo={mode}, pasta={self.selected_path}")
        self.destroy()

    def _cancel(self):
        """Cancela dialog."""
        self.result = None
        LOGGER.info("Dialog cancelado")
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
