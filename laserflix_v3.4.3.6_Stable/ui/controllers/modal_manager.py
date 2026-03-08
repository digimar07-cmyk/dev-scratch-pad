"""
ui/controllers/modal_manager.py — Gerencia todos os modals/dialogs da aplicação.

FASE 7F.1: Centraliza gerenciamento de dialogs
Redução estimada: -35 linhas no main_window.py
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from ui.dialogs.collection_dialog import CollectionDialog
from ui.dialogs.prepare_folders_dialog import PrepareFoldersDialog
from ui.dialogs.import_dialog import ImportDialog
from ui.dialogs.model_settings_dialog import ModelSettingsDialog


class ModalManager:
    """
    Gerencia abertura e coordenação de todos os dialogs.
    
    Responsabilidades:
    - Abrir/fechar dialogs
    - Callbacks de confirmação
    - State management entre dialogs
    """
    
    def __init__(self, parent, collections_manager=None):
        self.parent = parent
        self.collections_manager = collections_manager
        
        # Callbacks
        self.on_modal_closed = None
        self.on_data_changed = None
    
    def open_collections(self, on_close=None):
        """Abre dialog de coleções."""
        dialog = CollectionDialog(
            parent=self.parent,
            collections_manager=self.collections_manager
        )
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def open_prepare_folders(self, on_close=None):
        """Abre dialog de preparação de pastas."""
        dialog = PrepareFoldersDialog(parent=self.parent)
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def open_import(self, on_import_done=None):
        """Abre dialog de importação."""
        dialog = ImportDialog(parent=self.parent)
        
        if on_import_done:
            dialog.on_import_completed = on_import_done
    
    def open_model_settings(self, on_close=None):
        """Abre dialog de configurações de modelo."""
        dialog = ModelSettingsDialog(parent=self.parent)
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def confirm(self, title, message):
        """Mostra dialog de confirmação."""
        return messagebox.askyesno(title, message, parent=self.parent)
    
    def info(self, title, message):
        """Mostra dialog de informação."""
        messagebox.showinfo(title, message, parent=self.parent)
    
    def error(self, title, message):
        """Mostra dialog de erro."""
        messagebox.showerror(title, message, parent=self.parent)
    
    def warning(self, title, message):
        """Mostra dialog de aviso."""
        messagebox.showwarning(title, message, parent=self.parent)
    
    def ask_string(self, title, prompt, initial=""):
        """Pede string ao usuário."""
        return simpledialog.askstring(title, prompt, initialvalue=initial, parent=self.parent)
    
    def _handle_close(self, dialog, callback):
        """Handler genérico de fechamento."""
        dialog.destroy()
        if callback:
            callback()
        if self.on_modal_closed:
            self.on_modal_closed()
