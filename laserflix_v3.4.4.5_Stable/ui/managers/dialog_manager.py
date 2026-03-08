"""
ui/managers/dialog_manager.py — Gerenciador centralizado de diálogos.
Extrai todos os diálogos e configurações do main_window.py.

FASE-F: DialogManager (reorganização segura)
- Move 77 linhas de diálogos para cá
- main_window mantém apenas wrappers de 1 linha
- ZERO mudança de lógica, apenas reorganização
"""
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config.ui_constants import (
    BG_PRIMARY, BG_CARD, ACCENT_RED,
    FG_PRIMARY, FG_SECONDARY, SCROLL_SPEED
)

from ui.prepare_folders_dialog import PrepareFoldersDialog
from ui.model_settings_dialog import ModelSettingsDialog


class DialogManager:
    """Gerenciador de diálogos e configurações do Laserflix."""
    
    @staticmethod
    def open_categories_picker(window) -> None:
        """
        Abre diálogo de seleção de categorias.
        
        Args:
            window: Instância de LaserflixMainWindow com:
                - database
                - display_ctrl (com add_filter_chip)
                - _update_chips_bar()
        """
        all_cats: dict = {}
        for d in window.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria": 
                    all_cats[c] = all_cats.get(c, 0) + 1
        
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        
        win = tk.Toplevel(window.root)
        win.title("Categorias")
        win.configure(bg=BG_PRIMARY)
        win.geometry("400x600")
        win.transient(window.root)
        win.grab_set()
        
        tk.Label(
            win, text="Selecione categoria",
            font=("Arial", 13, "bold"),
            bg=BG_PRIMARY, fg=FG_PRIMARY
        ).pack(pady=10)
        
        frm = tk.Frame(win, bg=BG_PRIMARY)
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        
        cv = tk.Canvas(frm, bg=BG_PRIMARY, highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=BG_PRIMARY)
        
        inner.bind(
            "<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all"))
        )
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        cv.bind(
            "<MouseWheel>",
            lambda e: cv.yview_scroll(int(-1*(e.delta/SCROLL_SPEED)), "units")
        )
        
        for cat, count in cats_sorted:
            def on_click(c=cat):
                window.display_ctrl.add_filter_chip("category", c)
                window._update_chips_bar()
                win.destroy()
            
            b = tk.Button(
                inner, text=f"{cat} ({count})",
                command=on_click,
                bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 10),
                relief="flat", cursor="hand2", anchor="w",
                padx=12, pady=8
            )
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=ACCENT_RED))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=BG_CARD))
        
        tk.Button(
            win, text="Fechar",
            command=win.destroy,
            bg="#555555", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=14, pady=8
        ).pack(pady=10)
    
    @staticmethod
    def export_database(window) -> None:
        """
        Exporta database para arquivo JSON.
        
        Args:
            window: Instância de LaserflixMainWindow
        """
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Exportar banco"
        )
        
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo(
                "✅ Exportado",
                f"Banco exportado:\n{path}"
            )
    
    @staticmethod
    def import_database(window) -> None:
        """
        Importa database de arquivo JSON.
        
        Args:
            window: Instância de LaserflixMainWindow com:
                - db_manager
                - database
                - sidebar (com refresh)
                - collections_manager
                - _invalidate_cache()
                - display_projects()
        """
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Importar banco"
        )
        
        if path:
            shutil.copy2(path, "laserflix_database.json")
            window.db_manager.load_database()
            window.database = window.db_manager.database
            window.sidebar.refresh(window.database, window.collections_manager)
            window._invalidate_cache()
            window.display_projects()
            messagebox.showinfo("✅ Importado", "Banco importado!")
    
    @staticmethod
    def manual_backup(window) -> None:
        """
        Cria backup manual do database.
        
        Args:
            window: Instância de LaserflixMainWindow com db_manager
        """
        window.db_manager.auto_backup()
        messagebox.showinfo("✅ Backup", "Backup criado!")
    
    @staticmethod
    def open_prepare_folders(window) -> None:
        """
        Abre diálogo de preparação de pastas.
        
        Args:
            window: Instância de LaserflixMainWindow com root
        """
        window.root.wait_window(PrepareFoldersDialog(window.root))
    
    @staticmethod
    def open_model_settings(window) -> None:
        """
        Abre diálogo de configurações de modelo.
        
        Args:
            window: Instância de LaserflixMainWindow com root e db_manager
        """
        window.root.wait_window(ModelSettingsDialog(window.root, window.db_manager))
