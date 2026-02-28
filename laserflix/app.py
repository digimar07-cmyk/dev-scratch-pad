# -*- coding: utf-8 -*-
"""
LASERFLIX v7.4.0 - Classe Principal
Extraído integralmente do v740_Ofline_Stable.py (linhas 68-1304)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import threading
import time
import requests
import subprocess
import platform
import shutil
import logging
from logging.handlers import RotatingFileHandler
from PIL import Image, ImageTk
from datetime import datetime
from collections import Counter, OrderedDict
import re
import base64
import io

from .config import (
    VERSION, CONFIG_FILE, DB_FILE, BACKUP_FOLDER,
    OLLAMA_MODELS, FAST_MODEL_THRESHOLD, TIMEOUTS
)
from .logger import setup_logging

LOGGER = setup_logging()


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

        # HTTP session reutilizável
        self.http_session = requests.Session()
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_retries = 3
        self.ollama_health_timeout = 4
        self._ollama_health_cache = {"ts": 0.0, "ok": None}

        # Modelos ativos (podem ser alterados via configurações)
        self.active_models = dict(OLLAMA_MODELS)

        # Cache de thumbnails (LRU simples)
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300

        os.makedirs(BACKUP_FOLDER, exist_ok=True)

        self.load_config()
        self.load_database()
        self.create_ui()
        self.display_projects()
        self.schedule_auto_backup()

    # -----------------------------------------------------------------------
    # BACKUP / PERSISTÊNCIA
    # -----------------------------------------------------------------------
    def schedule_auto_backup(self):
        self.auto_backup()
        self.root.after(1800000, self.schedule_auto_backup)

    def auto_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_FOLDER, f"auto_backup_{timestamp}.json")
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, backup_file)
            backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.startswith("auto_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(BACKUP_FOLDER, old_backup))
        except Exception:
            LOGGER.exception("Falha no auto-backup")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.folders = config.get("folders", [])
                saved_models = config.get("models", {})
                if saved_models:
                    self.active_models.update(saved_models)

    def save_json_atomic(self, filepath, data, make_backup=True):
        tmp_file = filepath + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if make_backup and os.path.exists(filepath):
                try:
                    shutil.copy2(filepath, filepath + ".bak")
                except Exception:
                    self.logger.warning("Falha ao criar .bak de %s", filepath, exc_info=True)
            os.replace(tmp_file, filepath)
        except Exception:
            self.logger.error("Falha ao salvar JSON atômico: %s", filepath, exc_info=True)
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    def save_config(self):
        self.save_json_atomic(
            CONFIG_FILE,
            {"folders": self.folders, "models": self.active_models},
            make_backup=True,
        )

    def load_database(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                self.database = json.load(f)
                for path, data in self.database.items():
                    if "category" in data and "categories" not in data:
                        old_cat = data.get("category", "")
                        data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                        del data["category"]

    def save_database(self):
        self.save_json_atomic(DB_FILE, self.database, make_backup=True)

    # -----------------------------------------------------------------------
    # OLLAMA — HELPERS DE BAIXO NÍVEL
    # -----------------------------------------------------------------------
    def _ollama_is_available(self) -> bool:
        """Checa disponibilidade do Ollama com cache de 5s."""
        try:
            now = time.time()
            cached = self._ollama_health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            resp = self.http_session.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=self.ollama_health_timeout,
            )
            ok = resp.status_code == 200
            self._ollama_health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._ollama_health_cache = {"ts": time.time(), "ok": False}
            return False

    def _model_name(self, role: str) -> str:
        """Retorna o nome do modelo configurado para o papel dado."""
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))

    def _timeout(self, role: str):
        return TIMEOUTS.get(role, (5, 30))

    def _ollama_generate_text(
        self,
        prompt: str,
        *,
        role: str = "text_quality",
        temperature: float = 0.7,
        num_predict: int = 350,
    ) -> str:
        """
        Gera texto com o modelo definido por `role`.
        Usa instruction format adequado para Qwen2.5-Instruct.
        """
        if getattr(self, "stop_analysis", False):
            return ""
        if not self._ollama_is_available():
            self.logger.warning("Ollama indisponível. Usando fallback.")
            return ""

        model = self._model_name(role)
        timeout = self._timeout(role)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente especialista em produtos de corte laser, "
                        "decoração artesanal e objetos afetivos personalizados. "
                        "Responda SEMPRE em português brasileiro. "
                        "Siga as instruções de formato com precisão."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": num_predict,
                "repeat_penalty": 1.1,
            },
        }

        last_err = None
        for attempt in range(1, self.ollama_retries + 1):
            if getattr(self, "stop_analysis", False):
                return ""
            try:
                resp = self.http_session.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                self.logger.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
            except Exception as e:
                last_err = e
                self.logger.warning("Ollama falhou (tentativa %d/%d) [%s]: %s", attempt, self.ollama_retries, model, e)
                if attempt < self.ollama_retries:
                    time.sleep(2.0)
        if last_err:
            self.logger.error("Ollama falhou definitivamente [%s]: %s", model, last_err, exc_info=True)
        return ""

    # -----------------------------------------------------------------------
    # MÉTODOS STUB - SERÃO IMPLEMENTADOS EM MÓDULOS SEPARADOS
    # -----------------------------------------------------------------------
    def _image_quality_score(self, image_path: str) -> dict:
        """TODO: Migrar para services/vision.py"""
        return {"brightness": 0, "saturation": 100, "white_pct": 0, "use_vision": True}

    def _ollama_describe_image(self, image_path: str) -> str:
        """TODO: Migrar para services/vision.py"""
        return ""

    def analyze_with_ai(self, project_path: str, batch_size: int = 1):
        """TODO: Migrar para services/analysis.py"""
        return self.fallback_analysis(project_path)

    def generate_ai_description(self, project_path: str, data: dict):
        """TODO: Migrar para services/description.py"""
        return None

    def fallback_categories(self, project_path, existing_categories):
        """TODO: Migrar para services/fallback.py"""
        return ["Diversos", "Diversos", "Diversos"]

    def fallback_analysis(self, project_path):
        """TODO: Migrar para services/fallback.py"""
        return (["Diversos"], [])

    def generate_fallback_description(self, project_path, data, structure):
        """TODO: Migrar para services/fallback.py"""
        return "Descrição em desenvolvimento"

    def get_origin_from_path(self, project_path):
        """TODO: Migrar para services/project.py"""
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

    def analyze_project_structure(self, project_path):
        """TODO: Migrar para services/project.py"""
        structure = {
            "total_files": 0, "total_subfolders": 0,
            "file_types": {}, "subfolders": [],
            "images": [], "documents": [],
            "has_svg": False, "has_pdf": False, "has_dxf": False, "has_ai": False,
        }
        try:
            for root, dirs, files in os.walk(project_path):
                structure["total_files"] += len(files)
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    if ext == ".svg": structure["has_svg"] = True
                    elif ext == ".pdf": structure["has_pdf"] = True
                    elif ext == ".dxf": structure["has_dxf"] = True
                    elif ext == ".ai":  structure["has_ai"]  = True
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        except Exception:
            LOGGER.exception("Falha ao analisar estrutura de %s", project_path)
        return structure

    def extract_tags_from_name(self, name):
        """TODO: Migrar para services/project.py"""
        name_clean = name
        for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
            name_clean = name_clean.replace(ext, "")
        name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
        name_clean = name_clean.replace("-", " ").replace("_", " ")
        stop_words = {"file", "files", "project", "design", "laser", "cut", "svg",
                      "pdf", "vector", "bundle", "pack", "set", "collection"}
        words = [w for w in name_clean.split() if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words]
        tags = []
        if len(words) >= 2:
            phrase = " ".join(words[:4])
            if len(phrase) > 3:
                tags.append(phrase.title())
        for w in words[:5]:
            if len(w) >= 3:
                tags.append(w.capitalize())
        seen, unique = set(), []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        return unique[:5]

    def _find_first_image_path(self, project_path):
        """TODO: Migrar para services/images.py"""
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        return None

    def _load_thumbnail_photo(self, img_path):
        """TODO: Migrar para services/images.py"""
        img = Image.open(img_path)
        img.thumbnail((220, 200), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def get_cover_image(self, project_path):
        """TODO: Migrar para services/images.py"""
        img_path = self._find_first_image_path(project_path)
        if not img_path:
            return None
        try:
            mtime = os.path.getmtime(img_path)
        except Exception:
            return None
        try:
            cached = self.thumbnail_cache.get(img_path)
            if cached:
                cached_mtime, cached_photo = cached
                if cached_mtime == mtime:
                    self.thumbnail_cache.move_to_end(img_path)
                    return cached_photo
            photo = self._load_thumbnail_photo(img_path)
            self.thumbnail_cache[img_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(img_path)
            while len(self.thumbnail_cache) > self.thumbnail_cache_limit:
                self.thumbnail_cache.popitem(last=False)
            return photo
        except Exception:
            LOGGER.exception("Erro ao gerar thumbnail de %s", img_path)
            return None

    def get_hero_image(self, project_path):
        """TODO: Migrar para services/images.py"""
        try:
            valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    img_path = os.path.join(project_path, item)
                    img = Image.open(img_path)
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception:
            LOGGER.exception("Falha ao carregar hero image de %s", project_path)
        return None

    def get_all_project_images(self, project_path):
        """TODO: Migrar para services/images.py"""
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        images = []
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    images.append(os.path.join(project_path, item))
        except Exception:
            LOGGER.exception("Falha ao listar imagens de %s", project_path)
        return sorted(images)

    # -----------------------------------------------------------------------
    # AÇÕES INDIVIDUAIS - TODO: migrar para controllers/
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
        """TODO: migrar para controllers/analysis.py"""
        pass

    def open_folder(self, folder_path):
        """TODO: migrar para utils/system.py"""
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
        """TODO: migrar para utils/system.py"""
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
        """TODO: migrar para ui/dialogs.py"""
        new_tag = simpledialog.askstring("Nova Tag", "Digite a nova tag:", parent=self.root)
        if new_tag and new_tag.strip():
            new_tag = new_tag.strip()
            if new_tag not in listbox.get(0, tk.END):
                listbox.insert(tk.END, new_tag)

    def remove_tag_from_listbox(self, listbox):
        """TODO: migrar para ui/dialogs.py"""
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])

    def darken_color(self, hex_color):
        """TODO: migrar para ui/utils.py"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"

    # -----------------------------------------------------------------------
    # MÉTODOS STUB DE UI - SERÃO IMPLEMENTADOS EM ui/
    # -----------------------------------------------------------------------
    def create_ui(self):
        """TODO: Migrar para ui/main_window.py"""
        tk.Label(self.root, text="LASERFLIX v7.4.0 - Carregando UI...",
                 font=("Arial", 24), bg="#141414", fg="#E50914").pack(expand=True)

    def display_projects(self):
        """TODO: Migrar para ui/project_grid.py"""
        pass

    def update_sidebar(self):
        """TODO: Migrar para ui/sidebar.py"""
        pass

    def add_folders(self):
        """TODO: Migrar para controllers/folders.py"""
        pass

    def scan_projects(self):
        """TODO: Migrar para controllers/scanner.py"""
        pass

    def get_filtered_projects(self):
        """TODO: Migrar para services/filters.py"""
        return []

    def set_filter(self, filter_type):
        """TODO: Migrar para controllers/filters.py"""
        self.current_filter = filter_type

    def on_search(self):
        """TODO: Migrar para controllers/search.py"""
        pass

    def open_project_modal(self, project_path):
        """TODO: Migrar para ui/modals/project_modal.py"""
        pass

    def open_dashboard(self):
        """TODO: Migrar para ui/modals/dashboard.py"""
        pass

    def open_batch_edit(self):
        """TODO: Migrar para ui/modals/batch_edit.py"""
        pass

    def manual_backup(self):
        """TODO: Migrar para controllers/backup.py"""
        pass

    def export_database(self):
        """TODO: Migrar para controllers/database.py"""
        pass

    def import_database(self):
        """TODO: Migrar para controllers/database.py"""
        pass

    def open_model_settings(self):
        """TODO: Migrar para ui/modals/settings.py"""
        pass
