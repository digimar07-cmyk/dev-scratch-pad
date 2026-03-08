# -*- coding: utf-8 -*-
"""Gerencia toggles (favorito, done, good, bad)."""
from config.ui_constants import ACCENT_GOLD, FG_TERTIARY


class ToggleManager:
    def __init__(self, database, db_manager):
        self.database = database
        self.db_manager = db_manager
        self.on_invalidate_cache = None
    
    def toggle_favorite(self, path: str, btn=None):
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(text="⭐" if nv else "☆", fg=ACCENT_GOLD if nv else FG_TERTIARY)
    
    def toggle_done(self, path: str, btn=None):
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(text="✓" if nv else "○", fg="#00FF00" if nv else FG_TERTIARY)
    
    def toggle_good(self, path: str, btn=None):
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv:
                self.database[path]["bad"] = False
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(fg="#00FF00" if nv else FG_TERTIARY)
    
    def toggle_bad(self, path: str, btn=None):
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv:
                self.database[path]["good"] = False
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(fg="#FF0000" if nv else FG_TERTIARY)
