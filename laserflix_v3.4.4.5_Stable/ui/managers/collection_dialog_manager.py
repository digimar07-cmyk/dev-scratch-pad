# -*- coding: utf-8 -*-
"""Gerencia diálogos de coleções."""
import os
from tkinter import simpledialog


class CollectionDialogManager:
    def __init__(self, parent, collections_manager, database, collection_ctrl):
        self.parent = parent
        self.collections_manager = collections_manager
        self.database = database
        self.collection_ctrl = collection_ctrl
        self.on_status_update = None
        self.on_refresh = None
    
    def add_to_collection(self, project_path: str, collection_name: str):
        self.collection_ctrl.add_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        if self.on_status_update:
            self.on_status_update(f"✅ '{name}' adicionado à coleção '{collection_name}'")
    
    def remove_from_collection(self, project_path: str, collection_name: str):
        self.collection_ctrl.remove_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        if self.on_status_update:
            self.on_status_update(f"🗑️ '{name}' removido da coleção '{collection_name}'")
    
    def new_collection_with(self, project_path: str):
        name = simpledialog.askstring("📁 Nova Coleção", "Nome da nova coleção:", parent=self.parent)
        if not name or not name.strip():
            return
        name = name.strip()
        self.collection_ctrl.create_collection_with_project(project_path, name)
        project_name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        if self.on_status_update:
            self.on_status_update(f"📁 Coleção '{name}' criada com '{project_name}'")
    
    def open_collections_dialog(self):
        from ui.collections_dialog import CollectionsDialog
        self.parent.wait_window(
            CollectionsDialog(
                parent=self.parent,
                collections_manager=self.collections_manager,
                database=self.database
            )
        )
        if self.on_refresh:
            self.on_refresh()
