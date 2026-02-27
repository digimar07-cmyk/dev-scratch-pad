"""
LASERFLIX — Application Core
Orquestração principal: integra database, ollama, UI, workers
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
import threading

from .database import Database
from .backup import BackupManager
from .config import Config
from .filter import Filter
from ..ollama import OllamaManager
from ..ui.main_window import MainWindow
from ..workers.analysis import AnalysisWorker
from ..media import MediaManager


VERSION = "7.4.0"


class LaserflixApp:
    """Aplicativo principal Laserflix"""

    def __init__(self, root):
        self.root = root
        self.version = VERSION
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state("zoomed")
        self.root.configure(bg="#141414")

        # Estado
        self.analyzing = False
        self.stop_analysis = False

        # Core modules (ORDEM IMPORTANTE!)
        self.config = Config()
        self.database = Database()
        self.backup = BackupManager()
        self.filter = Filter(self.database)
        self.ollama = OllamaManager(self)
        self.media = MediaManager()

        # UI ANTES dos Workers (workers precisam de app.ui)
        self.ui = MainWindow(self)

        # Workers (agora app.ui já existe)
        self.analysis_worker = AnalysisWorker(self)

        # Init
        self.config.load()
        self.database.load()
        self.ui.create_ui()
        self.ui.update_sidebar()
        self.ui.display_projects()
        self.schedule_auto_backup()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUTO-BACKUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def schedule_auto_backup(self):
        self.backup.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)  # 30min

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SCAN / FOLDERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def add_folders(self):
        folder = filedialog.askdirectory(title="Selecione uma pasta de projetos")
        if folder and folder not in self.config.folders:
            self.config.folders.append(folder)
            self.config.save()
            self.scan_projects()
            messagebox.showinfo("✓", f"Pasta adicionada!\n{folder}")

    def scan_projects(self):
        new_count = 0
        for root_folder in self.config.folders:
            if not os.path.exists(root_folder):
                continue
            for item in os.listdir(root_folder):
                project_path = os.path.join(root_folder, item)
                if os.path.isdir(project_path) and project_path not in self.database.data:
                    self.database.data[project_path] = {
                        "name": item,
                        "origin": self._get_origin_from_path(project_path),
                        "favorite": False,
                        "done": False,
                        "good": False,
                        "bad": False,
                        "categories": [],
                        "tags": [],
                        "analyzed": False,
                        "ai_description": "",
                        "added_date": datetime.now().isoformat(),
                    }
                    new_count += 1
        if new_count > 0:
            self.database.save()
            self.ui.update_sidebar()
            self.ui.display_projects()
            self.ui.status_bar.config(text=f"✓ {new_count} novos projetos")

    def _get_origin_from_path(self, project_path):
        try:
            parent_folder = os.path.basename(os.path.dirname(project_path))
            parent_upper = parent_folder.upper()
            if "CREATIVE" in parent_upper or "FABRICA" in parent_upper:
                return "Creative Fabrica"
            elif "ETSY" in parent_upper:
                return "Etsy"
            else:
                return parent_folder
        except Exception:
            return "Diversos"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TOGGLES (favorito/done/good/bad)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def toggle_favorite(self, project_path, btn=None):
        if project_path in self.database.data:
            new_val = not self.database.data[project_path].get("favorite", False)
            self.database.data[project_path]["favorite"] = new_val
            self.database.save()
            if btn:
                btn.config(text="⭐" if new_val else "☆", fg="#FFD700" if new_val else "#666666")
            else:
                self.ui.display_projects()

    def toggle_done(self, project_path, btn=None):
        if project_path in self.database.data:
            new_val = not self.database.data[project_path].get("done", False)
            self.database.data[project_path]["done"] = new_val
            self.database.save()
            if btn:
                btn.config(text="✓" if new_val else "○", fg="#00FF00" if new_val else "#666666")
            else:
                self.ui.display_projects()

    def toggle_good(self, project_path, btn=None):
        if project_path in self.database.data:
            new_val = not self.database.data[project_path].get("good", False)
            self.database.data[project_path]["good"] = new_val
            if new_val:
                self.database.data[project_path]["bad"] = False
            self.database.save()
            if btn:
                btn.config(fg="#00FF00" if new_val else "#666666")
            else:
                self.ui.display_projects()

    def toggle_bad(self, project_path, btn=None):
        if project_path in self.database.data:
            new_val = not self.database.data[project_path].get("bad", False)
            self.database.data[project_path]["bad"] = new_val
            if new_val:
                self.database.data[project_path]["good"] = False
            self.database.save()
            if btn:
                btn.config(fg="#FF0000" if new_val else "#666666")
            else:
                self.ui.display_projects()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ANÁLISE INDIVIDUAL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def analyze_single_project(self, project_path):
        self.ui.status_bar.config(text="🤖 Analisando com IA...")

        def analyze():
            categories, tags = self.ollama.analyze_with_ai(project_path, batch_size=1)
            self.database.data[project_path]["categories"] = categories
            self.database.data[project_path]["tags"] = tags
            self.database.data[project_path]["analyzed"] = True
            self.database.data[project_path]["analyzed_model"] = self.ollama._model_name("text_quality")
            self.database.save()
            self.root.after(0, self.ui.update_sidebar)
            self.root.after(0, self.ui.display_projects)
            self.root.after(0, lambda: self.ui.status_bar.config(text="✓ Análise concluída"))

        threading.Thread(target=analyze, daemon=True).start()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ANÁLISE EM LOTE (delega para worker)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def analyze_only_new(self):
        self.analysis_worker.analyze_only_new()

    def reanalyze_all(self):
        self.analysis_worker.reanalyze_all()

    def analyze_current_filter(self):
        self.analysis_worker.analyze_current_filter()

    def reanalyze_specific_category(self):
        messagebox.showinfo("Em Desenvolvimento", "Reanálise por categoria em desenvolvimento...")

    def generate_descriptions_for_new(self):
        self.analysis_worker.generate_descriptions_for_new()

    def generate_descriptions_for_all(self):
        self.analysis_worker.generate_descriptions_for_all()

    def generate_descriptions_for_filter(self):
        self.analysis_worker.generate_descriptions_for_filter()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MEDIA (delega para media manager)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def get_cover_image(self, project_path):
        return self.media.get_cover_image(project_path)

    def get_all_project_images(self, project_path):
        return self.media.get_all_project_images(project_path)

    def open_folder(self, folder_path):
        self.media.open_folder(folder_path)

    def open_image(self, image_path):
        self.media.open_image(image_path)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MODALS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def open_project_modal(self, project_path):
        from ..ui.project_modal import ProjectModal
        ProjectModal(self, project_path)

    def open_dashboard(self):
        from ..ui.dashboard import Dashboard
        Dashboard(self)

    def open_batch_edit(self):
        messagebox.showinfo("Em Desenvolvimento", "Edição em lote em desenvolvimento...")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # IMPORT / EXPORT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def export_database(self):
        filename = filedialog.asksaveasfilename(
            title="Exportar Banco",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"laserflix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        if filename:
            self.database.export_to(filename)
            messagebox.showinfo("✓", f"Banco exportado!\n{filename}")

    def import_database(self):
        if messagebox.askyesno("⚠️ Atenção", "Importar substituirá todos os dados. Fazer backup?"):
            self.backup.manual_backup()
        filename = filedialog.askopenfilename(title="Importar Banco", filetypes=[("JSON files", "*.json")])
        if filename:
            self.database.import_from(filename)
            self.ui.update_sidebar()
            self.ui.display_projects()
            messagebox.showinfo("✓", f"Banco importado! {len(self.database.data)} projetos.")
