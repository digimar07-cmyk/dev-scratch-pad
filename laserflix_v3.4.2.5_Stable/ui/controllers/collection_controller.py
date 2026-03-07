"""
ui/controllers/collection_controller.py - Gerencia coleções/playlists.

FASE 7C.2: Extrai toda lógica de coleções do main_window.py
Redução estimada: -60 linhas no main_window.py
"""
import os


class CollectionController:
    """
    Controller para gerenciar coleções/playlists de projetos.
    
    Responsabilidades:
    - Adicionar projeto a uma coleção
    - Remover projeto de uma coleção
    - Criar nova coleção com projeto
    """
    
    def __init__(self, collections_manager, database):
        self.collections_manager = collections_manager
        self.database = database
        
        # Callbacks para UI
        self.on_collection_changed = None  # callback()
    
    def add_project(self, path, collection_name):
        """
        Adiciona projeto a uma coleção existente.
        
        Args:
            path: Caminho do projeto
            collection_name: Nome da coleção
        
        Returns:
            bool: True se adicionado com sucesso
        """
        if path not in self.database:
            return False
        
        if collection_name not in self.collections_manager.collections:
            return False
        
        self.collections_manager.add_project_to_collection(collection_name, path)
        
        if self.on_collection_changed:
            self.on_collection_changed()
        
        return True
    
    def remove_project(self, path, collection_name):
        """
        Remove projeto de uma coleção.
        
        Args:
            path: Caminho do projeto
            collection_name: Nome da coleção
        
        Returns:
            bool: True se removido com sucesso
        """
        if collection_name not in self.collections_manager.collections:
            return False
        
        self.collections_manager.remove_project_from_collection(collection_name, path)
        
        if self.on_collection_changed:
            self.on_collection_changed()
        
        return True
    
    def create_collection_with_project(self, path, collection_name):
        """
        Cria nova coleção e adiciona projeto.
        
        Args:
            path: Caminho do projeto
            collection_name: Nome da nova coleção
        
        Returns:
            bool: True se criado com sucesso
        """
        if not collection_name or not collection_name.strip():
            return False
        
        if path not in self.database:
            return False
        
        # Criar coleção
        self.collections_manager.create_collection(collection_name)
        
        # Adicionar projeto
        self.collections_manager.add_project_to_collection(collection_name, path)
        
        if self.on_collection_changed:
            self.on_collection_changed()
        
        return True
    
    def get_project_collections(self, path):
        """
        Retorna lista de coleções que contêm o projeto.
        
        Args:
            path: Caminho do projeto
        
        Returns:
            list: Lista de nomes de coleções
        """
        return self.collections_manager.get_project_collections(path)
    
    def get_all_collections(self):
        """
        Retorna lista de todas as coleções.
        
        Returns:
            list: Lista de nomes de coleções
        """
        return list(self.collections_manager.collections.keys())
