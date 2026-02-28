"""Core App - Classe principal LaserflixNetflix"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import threading
import time
import subprocess
import platform
import shutil
from datetime import datetime
from collections import OrderedDict

from core.config import VERSION, OLLAMA_MODELS
from core.logging_setup import LOGGER
from core.persistence import PersistenceManager
from core.helpers import get_origin_from_path, darken_color
from ai.ollama_client import OllamaClient
from ai.vision import VisionAnalyzer
from ai.analyzer import ProjectAnalyzer
from ai.description_generator import DescriptionGenerator
from ui.image_manager import ImageManager


class LaserflixNetflix:
    def __init__(self, root):
        self.root = root
        self.logger = LOGGER
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")

        self.folders = []
        self.database = {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False

        self.active_models = dict(OLLAMA_MODELS)

        # Managers
        self.persistence = PersistenceManager()
        self.image_manager = ImageManager()
        
        # AI modules
        self.ollama = OllamaClient(self.active_models)
        self.vision = VisionAnalyzer(self.ollama)
        self.analyzer = ProjectAnalyzer(self.ollama, self.vision)
        self.desc_generator = DescriptionGenerator(self.ollama, self.vision, self.analyzer)

        # Load data
        self.folders = self.persistence.load_config(self.active_models)
        self.database = self.persistence.load_database()
        
        # UI
        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()

    def schedule_auto_backup(self):
        self.persistence.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)

    def save_config(self):
        self.persistence.save_config(self.folders, self.active_models)

    def save_database(self):
        self.persistence.save_database(self.database)

    # -----------------------------------------------------------------------
    # AÇÕES INDIVIDUAIS
    # -----------------------------------------------------------------------
    def toggle_favorite(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("favorite", False)
            self.database[project_path]["favorite"] = new_val
            self.save_database()
            if btn:
                btn.config(text="⭐" if new_val else "☆",
                           fg="#FFD700" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_done(self, project_path, btn=None):
        if project_path in self.database:
            new_val = not self.database[project_path].get("done", False)
            self.database[project_path]["done"] = new_val
            self.save_database()
            if btn:
                btn.config(text="✓" if new_val else "○",
                           fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_good(self, project_path, btn=None):
        if project_path in self.database:
            current = self.database[project_path].get("good", False)
            new_val = not current
            self.database[project_path]["good"] = new_val
            if new_val:
                self.database[project_path]["bad"] = False
            self.save_database()
            if btn:
                btn.config(fg="#00FF00" if new_val else "#666666")
            else:
                self.display_projects()

    def toggle_bad(self, project_path, btn=None):
        if project_path in self.database:
            current = self.database[project_path].get("bad", False)
            new_val = not current
            self.database[project_path]["bad"] = new_val
            if new_val:
                self.database[project_path]["good"] = False
            self.save_database()
            if btn:
                btn.config(fg="#FF0000" if new_val else "#666666")
            else:
                self.display_projects()

    def analyze_single_project(self, project_path):
        self.status_bar.config(text="🤖 Analisando com IA...")
        def analyze():
            categories, tags = self.analyzer.analyze_with_ai(project_path, batch_size=1)
            self.database[project_path]["categories"] = categories
            self.database[project_path]["tags"] = tags
            self.database[project_path]["analyzed"] = True
            self.database[project_path]["analyzed_model"] = self.ollama._model_name("text_quality")
            self.save_database()
            self.root.after(0, self.update_sidebar)
            self.root.after(0, self.display_projects)
            self.root.after(0, lambda: self.status_bar.config(text="✓ Análise concluída"))
        threading.Thread(target=analyze, daemon=True).start()

    def open_folder(self, folder_path):
        try:
            if not os.path.exists(folder_path):
                messagebox.showerror("Erro", f"Pasta não encontrada:\n{folder_path}")
                return
            if platform.system() == "Windows":
                os.startfile(os.path.abspath(folder_path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta:\n{e}")

    def open_image(self, image_path):
        try:
            if platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", image_path])
            else:
                subprocess.run(["xdg-open", image_path])
        except Exception:
            messagebox.showerror("Erro", "Erro ao abrir imagem")

    def add_tag_to_listbox(self, listbox):
        new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=self.root)
        if new_tag and new_tag.strip():
            new_tag = new_tag.strip()
            if new_tag not in listbox.get(0, tk.END):
                listbox.insert(tk.END, new_tag)

    def remove_tag_from_listbox(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    # -----------------------------------------------------------------------
    # SCAN / FILTROS
    # -----------------------------------------------------------------------
    def add_folders(self):
        folder = filedialog.askdirectory(title="Selecione uma pasta de projetos")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.save_config()
            self.scan_projects()
            messagebox.showinfo("✓", f"Pasta adicionada!\n{folder}")

    def scan_projects(self):
        new_count = 0
        for root_folder in self.folders:
            if not os.path.exists(root_folder):
                continue
            for item in os.listdir(root_folder):
                project_path = os.path.join(root_folder, item)
                if os.path.isdir(project_path) and project_path not in self.database:
                    self.database[project_path] = {
                        "name": item,
                        "origin": get_origin_from_path(project_path),
                        "favorite": False, "done": False, "good": False, "bad": False,
                        "categories": [], "tags": [], "analyzed": False,
                        "ai_description": "", "added_date": datetime.now().isoformat(),
                    }
                    new_count += 1
        if new_count > 0:
            self.save_database()
            self.update_sidebar()
            self.display_projects()
            self.status_bar.config(text=f"✓ {new_count} novos projetos")

    def get_filtered_projects(self):
        filtered = []
        for project_path, data in self.database.items():
            show = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done"     and data.get("done"))
                or (self.current_filter == "good"     and data.get("good"))
                or (self.current_filter == "bad"      and data.get("bad"))
            )
            if not show: continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(c in data.get("categories", []) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags", []): continue
            if self.search_query and self.search_query not in data.get("name", "").lower(): continue
            filtered.append(project_path)
        return filtered

    # -----------------------------------------------------------------------
    # BACKUP MANUAL / IMPORT / EXPORT
    # -----------------------------------------------------------------------
    def manual_backup(self):
        try:
            backup_file = self.persistence.manual_backup()
            if backup_file:
                messagebox.showinfo("✓", f"Backup criado!\n{backup_file}")
            else:
                messagebox.showwarning("Aviso", "Nenhum banco para backup.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    def export_database(self):
        from core.config import DB_FILE
        filename = filedialog.asksaveasfilename(
            title="Exportar Banco", defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"laserflix_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        if filename:
            try:
                shutil.copy2(DB_FILE, filename)
                messagebox.showinfo("✓", f"Banco exportado!\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

    def import_database(self):
        from core.config import DB_FILE
        import json
        if messagebox.askyesno("⚠️ Atenção", "Importar substituirá todos os dados. Fazer backup?"):
            self.manual_backup()
        filename = filedialog.askopenfilename(title="Importar Banco", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    imported_data = json.load(f)
                if not isinstance(imported_data, dict):
                    messagebox.showerror("Erro", "Arquivo inválido!")
                    return
                shutil.copy2(DB_FILE, DB_FILE + ".pre-import.backup")
                self.database = imported_data
                self.save_database()
                self.update_sidebar()
                self.display_projects()
                messagebox.showinfo("✓", f"Banco importado! {len(self.database)} projetos.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

    # -----------------------------------------------------------------------
    # CONFIGURAÇÕES DE MODELOS
    # -----------------------------------------------------------------------
    def open_model_settings(self):
        win = tk.Toplevel(self.root)
        win.title("⚙️ Configurar Modelos de IA")
        win.configure(bg="#141414")
        win.geometry("600x420")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="⚙️ Configurar Modelos Ollama", font=("Arial", 16, "bold"),
                 bg="#141414", fg="#E50914").pack(pady=15)

        available = []
        try:
            resp = self.ollama.http_session.get(f"{self.ollama.ollama_base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                available = [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass

        roles_labels = {
            "text_quality": "🧠 Modelo Qualidade (análise individual/descrições)",
            "text_fast":    "⚡ Modelo Rápido (lotes grandes)",
            "vision":       "👁️ Modelo Visão (análise de imagens)",
            "embed":        "🔗 Modelo Embeddings (busca semântica)",
        }

        entries = {}
        for role, label in roles_labels.items():
            frame = tk.Frame(win, bg="#141414")
            frame.pack(fill="x", padx=25, pady=6)
            tk.Label(frame, text=label, font=("Arial", 10, "bold"),
                     bg="#141414", fg="#CCCCCC", width=48, anchor="w").pack(side="left")
            var = tk.StringVar(value=self.active_models.get(role, ""))
            if available:
                cb = ttk.Combobox(frame, textvariable=var, values=available, width=32, state="normal")
            else:
                cb = tk.Entry(frame, textvariable=var, bg="#2A2A2A", fg="#FFFFFF",
                              font=("Arial", 10), width=35, relief="flat")
            cb.pack(side="left", padx=5)
            entries[role] = var

        status_lbl = tk.Label(win, text="", bg="#141414", fg="#1DB954", font=("Arial", 10))
        status_lbl.pack(pady=5)

        if not available:
            status_lbl.config(text="⚠️ Ollama offline — digitando modelos manualmente", fg="#FF6B6B")

        def save_models():
            for role, var in entries.items():
                val = var.get().strip()
                if val:
                    self.active_models[role] = val
            self.save_config()
            status_lbl.config(text="✓ Modelos salvos!", fg="#1DB954")
            self.root.after(1500, win.destroy)

        btn_frame = tk.Frame(win, bg="#141414")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="💾 Salvar", command=save_models,
                  bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="✕ Cancelar", command=win.destroy,
                  bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
