"""
ui/controllers/selection_controller.py - Gerencia seleção múltipla de projetos.

FASE 7C.1: Extrai toda lógica de seleção do main_window.py
Redução estimada: -80 linhas no main_window.py
"""
import os
from tkinter import messagebox


class SelectionController:
    """
    Controller para gerenciar seleção múltipla de projetos.
    
    Responsabilidades:
    - Ativar/desativar modo seleção
    - Adicionar/remover projetos da seleção
    - Remover projetos selecionados do banco
    """
    
    def __init__(self, database, db_manager, collections_manager):
        self.database = database
        self.db_manager = db_manager
        self.collections_manager = collections_manager
        
        # Estado
        self.selection_mode = False
        self.selected_paths = set()
        
        # Callbacks para UI (main_window conectará)
        self.on_mode_changed = None      # callback(bool: is_active)
        self.on_selection_changed = None # callback(int: count)
        self.on_projects_removed = None  # callback(int: count)
        self.on_refresh_needed = None    # callback()
    
    def toggle_mode(self):
        """Ativa/desativa modo seleção."""
        self.selection_mode = not self.selection_mode
        self.selected_paths.clear()
        
        if self.on_mode_changed:
            self.on_mode_changed(self.selection_mode)
        
        if self.on_selection_changed:
            self.on_selection_changed(0)
    
    def toggle_project(self, path):
        """Adiciona ou remove projeto da seleção."""
        if path in self.selected_paths:
            self.selected_paths.discard(path)
        else:
            self.selected_paths.add(path)
        
        if self.on_selection_changed:
            self.on_selection_changed(len(self.selected_paths))
    
    def select_all(self, paths):
        """Seleciona todos os projetos visíveis."""
        self.selected_paths = set(paths)
        
        if self.on_selection_changed:
            self.on_selection_changed(len(self.selected_paths))
    
    def deselect_all(self):
        """Remove todas as seleções."""
        self.selected_paths.clear()
        
        if self.on_selection_changed:
            self.on_selection_changed(0)
    
    def remove_selected(self, parent_window):
        """
        Remove projetos selecionados do banco.
        Inclui validações e confirmações duplas.
        """
        n = len(self.selected_paths)
        
        if not n:
            messagebox.showinfo(
                "Seleção vazia",
                "Nenhum projeto selecionado.",
                parent=parent_window
            )
            return False
        
        # Primeira confirmação
        if not messagebox.askyesno(
            "🗑️ Remover projetos",
            f"Remover {n} projeto(s) do banco?\n\nOs arquivos no disco NÃO serão apagados.",
            icon="warning",
            parent=parent_window
        ):
            return False
        
        # Segunda confirmação
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            f"Segunda confirmação.\nIsso removerá {n} projeto(s) permanentemente do banco.\n\nTem certeza?",
            icon="warning",
            parent=parent_window
        ):
            return False
        
        # Remover projetos
        for path in list(self.selected_paths):
            self.database.pop(path, None)
        
        self.db_manager.save_database()
        self.collections_manager.clean_orphan_projects(set(self.database.keys()))
        
        # Limpar seleção e desativar modo
        self.selected_paths.clear()
        self.selection_mode = False
        
        if self.on_mode_changed:
            self.on_mode_changed(False)
        
        if self.on_projects_removed:
            self.on_projects_removed(n)
        
        if self.on_refresh_needed:
            self.on_refresh_needed()
        
        return True
    
    def is_selected(self, path):
        """Verifica se projeto está selecionado."""
        return path in self.selected_paths
    
    def get_selection_count(self):
        """Retorna número de projetos selecionados."""
        return len(self.selected_paths)
    
    def is_mode_active(self):
        """Verifica se modo seleção está ativo."""
        return self.selection_mode
