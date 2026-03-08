"""
ui/controllers/collection_controller.py - Gerencia colecoes/playlists.

FASE 7C.2: Extrai toda logica de colecoes do main_window.py
Reducao estimada: -50 linhas no main_window.py
"""

from tkinter import messagebox, simpledialog


class CollectionController:
    """
    Controller para gerenciar colecoes/playlists de projetos.
    
    Responsabilidades:
    - Adicionar projetos a colecoes
    - Remover projetos de colecoes
    - Criar novas colecoes com projetos
    """
    
    def __init__(self, collections_manager, database):
        self.collections_manager = collections_manager
        self.database = database
        
        # Callbacks para UI
        self.on_collection_changed = None  # callback()
    
    def add_project(self, path, collection_name):
        """Adiciona projeto a uma colecao."""
        if collection_name not in self.collections_manager.collections:
            self.collections_manager.collections[collection_name] = []
        
        if path not in self.collections_manager.collections[collection_name]:
            self.collections_manager.collections[collection_name].append(path)
            self.collections_manager.save()
            
            # Notificar UI
            if self.on_collection_changed:
                self.on_collection_changed()
    
    def remove_project(self, path, collection_name):
        """Remove projeto de uma colecao."""
        if collection_name in self.collections_manager.collections:
            if path in self.collections_manager.collections[collection_name]:
                self.collections_manager.collections[collection_name].remove(path)
                
                # Remover colecao se ficar vazia
                if not self.collections_manager.collections[collection_name]:
                    del self.collections_manager.collections[collection_name]
                
                self.collections_manager.save()
                
                # Notificar UI
                if self.on_collection_changed:
                    self.on_collection_changed()
    
    def create_collection_with_project(self, path, collection_name):
        """Cria nova colecao e adiciona projeto a ela."""
        if not collection_name:
            return
        
        if collection_name in self.collections_manager.collections:
            messagebox.showwarning(
                "Colecao existente",
                f"A colecao '{collection_name}' ja existe."
            )
            return
        
        # Criar nova colecao
        self.collections_manager.collections[collection_name] = [path]
        self.collections_manager.save()
        
        # Notificar UI
        if self.on_collection_changed:
            self.on_collection_changed()
