"""
core/database_controller.py — Controla operações de alto nível do database.

FASE 7F.2: Centraliza operações de database
Redução estimada: -30 linhas no main_window.py
"""
import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox


class DatabaseController:
    """
    Controla operações de alto nível do database.
    
    Responsabilidades:
    - Export de database
    - Backup manual
    - Import de database
    """
    
    def __init__(self, db_manager, database_ref, parent=None):
        self.db_manager = db_manager
        self.database = database_ref
        self.parent = parent
        
        # Callbacks
        self.on_database_changed = None
        self.on_status_message = None
    
    def export(self):
        """Exporta database para arquivo."""
        filename = filedialog.asksaveasfilename(
            title="Exportar Database",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            parent=self.parent
        )
        
        if filename:
            try:
                shutil.copy(self.db_manager.db_path, filename)
                messagebox.showinfo(
                    "✅ Export concluído",
                    f"Database exportado para:\n{filename}",
                    parent=self.parent
                )
                self._notify_status(f"Database exportado: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror(
                    "❌ Erro no export",
                    f"Não foi possível exportar:\n{str(e)}",
                    parent=self.parent
                )
    
    def manual_backup(self):
        """Cria backup manual do database."""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.json")
            
            shutil.copy(self.db_manager.db_path, backup_file)
            
            messagebox.showinfo(
                "✅ Backup criado",
                f"Backup salvo em:\n{backup_file}",
                parent=self.parent
            )
            self._notify_status(f"Backup criado: {os.path.basename(backup_file)}")
        except Exception as e:
            messagebox.showerror(
                "❌ Erro no backup",
                f"Não foi possível criar backup:\n{str(e)}",
                parent=self.parent
            )
    
    def import_from_file(self, filepath):
        """Importa database de arquivo."""
        if not os.path.exists(filepath):
            messagebox.showerror(
                "❌ Arquivo não encontrado",
                f"Arquivo não existe:\n{filepath}",
                parent=self.parent
            )
            return False
        
        try:
            # Backup antes de importar
            self.manual_backup()
            
            # Importar
            shutil.copy(filepath, self.db_manager.db_path)
            self.db_manager.load_database()
            
            messagebox.showinfo(
                "✅ Import concluído",
                f"Database importado de:\n{filepath}",
                parent=self.parent
            )
            
            self._notify_status(f"Database importado: {os.path.basename(filepath)}")
            self._notify_changed()
            return True
            
        except Exception as e:
            messagebox.showerror(
                "❌ Erro no import",
                f"Não foi possível importar:\n{str(e)}",
                parent=self.parent
            )
            return False
    
    def _notify_status(self, message):
        if self.on_status_message:
            self.on_status_message(message)
    
    def _notify_changed(self):
        if self.on_database_changed:
            self.on_database_changed()
