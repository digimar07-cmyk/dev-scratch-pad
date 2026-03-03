"""
import_mode_dialog.py — Dialog para seleção de modo de importação.

Permite ao usuário escolher:
  1. Modo PURO: Apenas pastas com folder.jpg
  2. Modo HÍBRIDO: folder.jpg + fallback inteligente
  3. Pasta base para escanear

USO:
    dialog = ImportModeDialog(parent)
    
    if dialog.exec_():
        mode = dialog.get_mode()        # 'pure' ou 'hybrid'
        path = dialog.get_base_path()   # caminho selecionado
"""

import customtkinter as ctk
from tkinter import filedialog
import os
from utils.logging_setup import LOGGER


class ImportModeDialog(ctk.CTkToplevel):
    """
    Dialog para escolher modo de importação e pasta base.
    
    Retorna:
        mode: 'pure' ou 'hybrid'
        base_path: caminho da pasta selecionada
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("🗂️ Importar Produtos - Modo Avançado")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Centraliza na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"600x400+{x}+{y}")
        
        # Variáveis
        self.selected_mode = "hybrid"  # Default
        self.selected_path = ""
        self.result = None  # None = cancelado, dict = confirmado
        
        # Constrói interface
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
        # TÍTULO
        # ============================================================
        title_label = ctk.CTkLabel(
            main_frame,
            text="🗂️ Importação Recursiva de Produtos",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # ============================================================
        # SELEÇÃO DE PASTA BASE
        # ============================================================
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="📁 Pasta Base:",
            font=("Segoe UI", 12, "bold")
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Entry + Botão
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
        # MODOS DE DETECÇÃO
        # ============================================================
        mode_frame = ctk.CTkFrame(main_frame)
        mode_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        mode_title = ctk.CTkLabel(
            mode_frame,
            text="🎯 Modo de Detecção:",
            font=("Segoe UI", 12, "bold")
        )
        mode_title.pack(anchor="w", padx=10, pady=(10, 10))
        
        # MODO HÍBRIDO (default)
        self.hybrid_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🔄 Modo Híbrido (Recomendado)",
            variable=ctk.StringVar(value="hybrid"),
            value="hybrid",
            command=lambda: self._set_mode("hybrid")
        )
        self.hybrid_radio.pack(anchor="w", padx=20, pady=(0, 5))
        self.hybrid_radio.select()  # Seleciona por padrão
        
        hybrid_desc = ctk.CTkLabel(
            mode_frame,
            text="✓ Detecta pastas com folder.jpg\n✓ + Fallback inteligente (arquivos .svg, .pdf, etc)",
            font=("Segoe UI", 10),
            text_color="gray70"
        )
        hybrid_desc.pack(anchor="w", padx=40, pady=(0, 15))
        
        # MODO PURO
        self.pure_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🔒 Modo Puro (Rigoroso)",
            variable=ctk.StringVar(value="hybrid"),
            value="pure",
            command=lambda: self._set_mode("pure")
        )
        self.pure_radio.pack(anchor="w", padx=20, pady=(0, 5))
        
        pure_desc = ctk.CTkLabel(
            mode_frame,
            text="✓ APENAS pastas com folder.jpg\n✓ Controle total, zero falsos positivos",
            font=("Segoe UI", 10),
            text_color="gray70"
        )
        pure_desc.pack(anchor="w", padx=40, pady=(0, 10))
        
        # ============================================================
        # BOTÕES
        # ============================================================
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=120,
            height=40,
            fg_color="gray40",
            hover_color="gray50",
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        self.import_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Escanear",
            width=120,
            height=40,
            command=self._confirm
        )
        self.import_btn.pack(side="right")

    def _set_mode(self, mode: str):
        """Define modo selecionado."""
        self.selected_mode = mode
        LOGGER.debug(f"Modo selecionado: {mode}")

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
            LOGGER.info(f"Pasta selecionada: {folder}")

    def _confirm(self):
        """Confirma e fecha dialog."""
        if not self.selected_path:
            # Mostra aviso
            self._show_warning("⚠️ Selecione uma pasta base!")
            return
        
        if not os.path.exists(self.selected_path):
            self._show_warning("⚠️ Pasta não existe!")
            return
        
        # Salva resultado
        self.result = {
            'mode': self.selected_mode,
            'base_path': self.selected_path
        }
        
        LOGGER.info(
            f"Confirmação: mode={self.selected_mode}, path={self.selected_path}"
        )
        
        self.destroy()

    def _cancel(self):
        """Cancela e fecha dialog."""
        self.result = None
        LOGGER.info("Importação cancelada")
        self.destroy()

    def _show_warning(self, message: str):
        """Mostra aviso temporário."""
        # Cria label de aviso
        warning = ctk.CTkLabel(
            self,
            text=message,
            font=("Segoe UI", 11, "bold"),
            text_color="#FF6B6B"
        )
        warning.place(relx=0.5, rely=0.92, anchor="center")
        
        # Remove após 3 segundos
        self.after(3000, warning.destroy)

    # ================================================================
    # MÉTODOS PÚBLICOS
    # ================================================================

    def get_result(self):
        """
        Retorna resultado do dialog.
        
        Returns:
            dict com 'mode' e 'base_path' ou None se cancelado
        """
        return self.result

    def get_mode(self):
        """Retorna modo selecionado ('pure' ou 'hybrid')."""
        return self.result['mode'] if self.result else None

    def get_base_path(self):
        """Retorna caminho da pasta base."""
        return self.result['base_path'] if self.result else None


# ================================================================
# TESTE
# ================================================================
if __name__ == '__main__':
    # Teste standalone
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()  # Esconde janela principal
    
    dialog = ImportModeDialog(root)
    root.wait_window(dialog)  # Espera dialog fechar
    
    result = dialog.get_result()
    
    if result:
        print(f"\n✅ CONFIRMADO:")
        print(f"  Modo: {result['mode']}")
        print(f"  Pasta: {result['base_path']}")
    else:
        print("\n❌ CANCELADO")
    
    root.destroy()
