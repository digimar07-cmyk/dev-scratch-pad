"""
ui/controllers/project_management_controller.py - Gerencia remocao e flags.

FASE 7C.3: Extrai logica de gerenciamento de projetos do main_window.py
Reducao estimada: -70 linhas no main_window.py
"""

import os
from tkinter import messagebox


class ProjectManagementController:
    """
    Controller para gerenciar projetos individuais.
    
    Responsabilidades:
    - Remover projeto individual
    - Limpar projetos orfaos (pasta nao existe)
    - Alternar flags (favorite, done, good, bad)
    """
    
    def __init__(self, database, db_manager, collections_manager):
        self.database = database
        self.db_manager = db_manager
        self.collections_manager = collections_manager
        
        # Callbacks para UI
        self.on_project_removed = None  # callback(str: project_name)
        self.on_orphans_cleaned = None  # callback(int: count)
        self.on_flag_toggled = None     # callback()
    
    def remove_project(self, path, parent_window):
        """Remove projeto individual do banco."""
        if path not in self.database:
            return
        
        project_name = os.path.basename(path)
        
        confirm = messagebox.askyesno(
            "Confirmar remocao",
            f"Remover '{project_name}' do banco?\n\n"
            "Essa acao nao pode ser desfeita.",
            parent=parent_window
        )
        
        if not confirm:
            return
        
        # Remover do banco
        del self.database[path]
        
        # Remover de colecoes
        for collection_name in list(self.collections_manager.collections.keys()):
            if path in self.collections_manager.collections[collection_name]:
                self.collections_manager.collections[collection_name].remove(path)
                
                # Remover colecao se ficar vazia
                if not self.collections_manager.collections[collection_name]:
                    del self.collections_manager.collections[collection_name]
        
        # Salvar alteracoes
        self.db_manager.save()
        self.collections_manager.save()
        
        # Notificar UI
        if self.on_project_removed:
            self.on_project_removed(project_name)
    
    def clean_orphans(self, parent_window):
        """Remove projetos orfaos (pasta nao existe mais)."""
        orphans = [
            path for path in self.database.keys()
            if not os.path.exists(path)
        ]
        
        if not orphans:
            messagebox.showinfo(
                "Nenhum orfao",
                "Nao ha projetos orfaos no banco.",
                parent=parent_window
            )
            return
        
        count = len(orphans)
        confirm = messagebox.askyesno(
            "Confirmar limpeza",
            f"Encontrados {count} projeto(s) orfao(s).\n\n"
            "Remover todos do banco?",
            parent=parent_window
        )
        
        if not confirm:
            return
        
        # Remover orfaos
        for path in orphans:
            del self.database[path]
            
            # Remover de colecoes
            for collection_name in list(self.collections_manager.collections.keys()):
                if path in self.collections_manager.collections[collection_name]:
                    self.collections_manager.collections[collection_name].remove(path)
                    
                    # Remover colecao se ficar vazia
                    if not self.collections_manager.collections[collection_name]:
                        del self.collections_manager.collections[collection_name]
        
        # Salvar alteracoes
        self.db_manager.save()
        self.collections_manager.save()
        
        # Notificar UI
        if self.on_orphans_cleaned:
            self.on_orphans_cleaned(count)
    
    def toggle_flag(self, path, flag_name, button=None):
        """Alterna flag de projeto (favorite, done, good, bad)."""
        if path not in self.database:
            return
        
        # Alternar flag
        current = self.database[path].get(flag_name, False)
        self.database[path][flag_name] = not current
        
        # Salvar
        self.db_manager.save()
        
        # Atualizar botao se fornecido
        if button:
            new_state = self.database[path][flag_name]
            if flag_name == 'favorite':
                button.config(text="★" if new_state else "☆")
            elif flag_name == 'done':
                button.config(text="✓" if new_state else "○")
            elif flag_name == 'good':
                button.config(text="👍" if new_state else "○")
            elif flag_name == 'bad':
                button.config(text="👎" if new_state else "○")
        
        # Notificar UI
        if self.on_flag_toggled:
            self.on_flag_toggled()
