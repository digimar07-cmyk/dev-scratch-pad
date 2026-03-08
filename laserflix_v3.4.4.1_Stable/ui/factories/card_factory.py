"""
ui/factories/card_factory.py — Factory para criação de project cards.

FASE 7F.3: Extrai lógica de criação de cards
Redução estimada: -40 linhas no main_window.py
"""
import tkinter as tk
from ui.components.card import ProjectCard


class CardFactory:
    """
    Factory para criação de project cards.
    
    Responsabilidades:
    - Criar cards com configuração padrão
    - Injetar callbacks
    - Gerenciar estado de seleção
    """
    
    def __init__(self):
        # Callbacks que serão injetados nos cards
        self.on_open = None
        self.on_toggle_favorite = None
        self.on_toggle_done = None
        self.on_toggle_good = None
        self.on_toggle_bad = None
        self.on_add_to_collection = None
        self.on_remove_from_collection = None
        self.on_new_collection = None
        self.on_remove_project = None
        self.on_card_click = None
    
    def create_card(self, parent, project_data, path, is_selected=False):
        """
        Cria um project card com todos os callbacks configurados.
        
        Args:
            parent: Widget pai
            project_data: Dict com dados do projeto
            path: Caminho do projeto
            is_selected: Se está selecionado (modo seleção)
        
        Returns:
            ProjectCard configurado
        """
        card = ProjectCard(
            parent=parent,
            project_data=project_data,
            path=path
        )
        
        # Injetar callbacks
        card.on_open = lambda p: self.on_open(p) if self.on_open else None
        card.on_toggle_favorite = lambda p, b: self.on_toggle_favorite(p, b) if self.on_toggle_favorite else None
        card.on_toggle_done = lambda p, b: self.on_toggle_done(p, b) if self.on_toggle_done else None
        card.on_toggle_good = lambda p, b: self.on_toggle_good(p, b) if self.on_toggle_good else None
        card.on_toggle_bad = lambda p, b: self.on_toggle_bad(p, b) if self.on_toggle_bad else None
        card.on_add_to_collection = lambda p, c: self.on_add_to_collection(p, c) if self.on_add_to_collection else None
        card.on_remove_from_collection = lambda p, c: self.on_remove_from_collection(p, c) if self.on_remove_from_collection else None
        card.on_new_collection = lambda p: self.on_new_collection(p) if self.on_new_collection else None
        card.on_remove_project = lambda p: self.on_remove_project(p) if self.on_remove_project else None
        card.on_card_click = lambda p: self.on_card_click(p) if self.on_card_click else None
        
        # Aplicar estado de seleção
        if is_selected:
            card.set_selected(True)
        
        return card
    
    def create_batch(self, parent, projects_data, selected_paths=None):
        """
        Cria múltiplos cards de uma vez.
        
        Args:
            parent: Widget pai
            projects_data: List de tuples (path, project_data)
            selected_paths: Set de paths selecionados
        
        Returns:
            List de ProjectCards
        """
        if selected_paths is None:
            selected_paths = set()
        
        cards = []
        for path, data in projects_data:
            is_selected = path in selected_paths
            card = self.create_card(parent, data, path, is_selected)
            cards.append(card)
        
        return cards
