"""
ui/controllers/project_management_controller.py - Gerencia remoção e flags.

FASE 7C.3: Extrai toda lógica de gerenciamento de projetos do main_window.py
Redução estimada: -60 linhas no main_window.py
"""
import os
from tkinter import messagebox


class ProjectManagementController:
    """
    Controller para gerenciar remoção de projetos e flags (favorite, done, good, bad).
    
    Responsabilidades:
    - Remover projeto individual do banco
    - Limpar órfãos (projetos sem arquivos)
    - Toggle de flags (favorite, done, good, bad)
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
        """
        Remove projeto individual do banco (com confirmação dupla).
        
        Args:
            path: Caminho do projeto
            parent_window: Janela pai para modals
        
        Returns:
            bool: True se removido com sucesso
        """
        if path not in self.database:
            return False
        
        project_name = self.database[path].get("name", os.path.basename(path))
        
        # Primeira confirmação
        if not messagebox.askyesno(
            "🗑️ Remover projeto",
            f"Remover '{project_name}' do banco?\n\nOs arquivos no disco NÃO serão apagados.",
            icon="warning",
            parent=parent_window
        ):
            return False
        
        # Remover
        self.database.pop(path, None)
        self.db_manager.save_database()
        self.collections_manager.clean_orphan_projects(set(self.database.keys()))
        
        if self.on_project_removed:
            self.on_project_removed(project_name)
        
        return True
    
    def clean_orphans(self, parent_window):
        """
        Remove projetos órfãos (sem arquivos no disco).
        
        Args:
            parent_window: Janela pai para modals
        
        Returns:
            int: Número de órfãos removidos
        """
        orphans = []
        
        for path in list(self.database.keys()):
            if not os.path.exists(path):
                orphans.append(path)
        
        if not orphans:
            messagebox.showinfo(
                "✨ Sem órfãos",
                "Não há projetos órfãos no banco.",
                parent=parent_window
            )
            return 0
        
        # Confirmação
        n = len(orphans)
        if not messagebox.askyesno(
            "🧹 Limpar órfãos",
            f"Encontrados {n} projeto(s) sem arquivos no disco.\n\nRemover do banco?",
            icon="warning",
            parent=parent_window
        ):
            return 0
        
        # Remover órfãos
        for path in orphans:
            self.database.pop(path, None)
        
        self.db_manager.save_database()
        self.collections_manager.clean_orphan_projects(set(self.database.keys()))
        
        if self.on_orphans_cleaned:
            self.on_orphans_cleaned(n)
        
        return n
    
    def toggle_flag(self, path, flag_name, button=None):
        """
        Alterna flag (favorite, done, good, bad) de um projeto.
        
        Args:
            path: Caminho do projeto
            flag_name: Nome da flag ('favorite', 'done', 'good', 'bad')
            button: Botão UI para atualizar (opcional)
        
        Returns:
            bool: Novo estado da flag
        """
        if path not in self.database:
            return False
        
        current = self.database[path].get(flag_name, False)
        new_value = not current
        
        self.database[path][flag_name] = new_value
        self.db_manager.save_database()
        
        # Atualizar botão (se fornecido)
        if button:
            bg_color = "#FFD700" if flag_name == "favorite" else (
                "#28a745" if flag_name == "done" else (
                "#90EE90" if flag_name == "good" else "#FF6347"
            ))
            button.config(
                relief="sunken" if new_value else "raised",
                bg=bg_color if new_value else "SystemButtonFace"
            )
        
        if self.on_flag_toggled:
            self.on_flag_toggled()
        
        return new_value
