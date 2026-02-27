"""LaserflixApp - Main application orchestrator."""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import logging
from typing import List, Dict, Any, Optional

from laserflix_tkinter.config import Settings
from laserflix_tkinter.models import Project, DatabaseManager
from laserflix_tkinter.services import OllamaService, ImageService, AnalysisService
from laserflix_tkinter.ui import MainWindow, Sidebar, ProjectGrid
from laserflix_tkinter.utils.file_utils import (
    get_origin_from_path, clean_project_name, extract_tags_from_name, find_first_image
)

logger = logging.getLogger("Laserflix.App")


class LaserflixApp:
    """Main application controller - orchestrates all components."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        logger.info("Initializing LaserflixApp...")
        
        # Configuration
        self.settings = Settings()
        
        # Services
        self.ollama = OllamaService(
            base_url=self.settings.ollama_base_url,
            retries=self.settings.ollama_retries,
            health_timeout=self.settings.ollama_health_timeout
        )
        self.image_service = ImageService(cache_limit=self.settings.thumbnail_cache_limit)
        self.analysis_service = AnalysisService()
        
        # Database
        self.db = DatabaseManager(self.settings.db_file, self.settings.backup_folder)
        
        # UI Components
        self.main_window = MainWindow(root, self.settings.version)
        self.sidebar = Sidebar(self.main_window.get_main_container())
        self.grid = ProjectGrid(self.main_window.get_main_container())
        
        # State
        self.folders: List[str] = []
        self.current_filter = "all"
        self.current_categories: List[str] = []
        self.current_tag: Optional[str] = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        
        # Connect UI callbacks
        self._connect_callbacks()
        
        # Load config and display
        self._load_config()
        self._update_sidebar_data()
        self._display_projects()
        
        # Schedule auto backup
        self._schedule_auto_backup()
        
        logger.info("LaserflixApp initialized successfully")
    
    def _connect_callbacks(self):
        """Connect all UI callbacks to business logic."""
        # Main window
        self.main_window.on_filter_change = self._on_filter_change
        self.main_window.on_search_change = self._on_search_change
        self.main_window.on_add_folders = self._on_add_folders
        self.main_window.on_menu_action = self._on_menu_action
        self.main_window.stop_button.config(command=self._stop_analysis)
        
        # Sidebar
        self.sidebar.on_origin_filter = self._on_origin_filter
        self.sidebar.on_category_filter = self._on_category_filter
        self.sidebar.on_tag_filter = self._on_tag_filter
        
        # Grid
        self.grid.on_card_click = self._on_card_click
        self.grid.on_category_click = lambda cat: self._on_category_filter([cat])
        self.grid.on_tag_click = self._on_tag_filter
        self.grid.on_origin_click = self._on_origin_filter
        self.grid.on_open_folder = self._open_folder
        self.grid.on_toggle_favorite = self._toggle_favorite
        self.grid.on_toggle_done = self._toggle_done
        self.grid.on_toggle_good = self._toggle_good
        self.grid.on_toggle_bad = self._toggle_bad
        self.grid.on_analyze_project = self._analyze_single_project
        self.grid.get_thumbnail = self._get_thumbnail
    
    # -------------------------------------------------------------------------
    # CONFIG & PERSISTENCE
    # -------------------------------------------------------------------------
    
    def _load_config(self):
        """Load folders from config."""
        if os.path.exists(self.settings.config_file):
            import json
            with open(self.settings.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.folders = config.get("folders", [])
                saved_models = config.get("models", {})
                if saved_models:
                    self.settings.active_models.update(saved_models)
            logger.info(f"Loaded {len(self.folders)} folders from config")
    
    def _save_config(self):
        """Save folders and models to config."""
        import json
        config = {
            "folders": self.folders,
            "models": self.settings.active_models
        }
        with open(self.settings.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _schedule_auto_backup(self):
        """Schedule automatic backup every 30 minutes."""
        self.db.auto_backup()
        self.root.after(1800000, self._schedule_auto_backup)
    
    # -------------------------------------------------------------------------
    # FOLDER MANAGEMENT
    # -------------------------------------------------------------------------
    
    def _on_add_folders(self):
        """Add folders to scan."""
        new_folders = filedialog.askdirectory(title="Selecione pasta com projetos")
        if new_folders and new_folders not in self.folders:
            self.folders.append(new_folders)
            self._save_config()
            self._scan_folders()
            self.main_window.update_status(f"Pasta adicionada: {os.path.basename(new_folders)}")
    
    def _scan_folders(self):
        """Scan all folders and add new projects to database."""
        new_count = 0
        for folder in self.folders:
            if not os.path.exists(folder):
                continue
            for item in os.listdir(folder):
                project_path = os.path.join(folder, item)
                if os.path.isdir(project_path) and project_path not in self.db:
                    # Create new project
                    project = Project(
                        path=project_path,
                        name=clean_project_name(item),
                        origin=get_origin_from_path(project_path)
                    )
                    self.db[project_path] = project
                    new_count += 1
        
        if new_count > 0:
            self.db.save()
            logger.info(f"Added {new_count} new projects")
            self._update_sidebar_data()
            self._display_projects()
    
    # -------------------------------------------------------------------------
    # UI CALLBACKS - FILTERS
    # -------------------------------------------------------------------------
    
    def _on_filter_change(self, filter_type: str):
        """Handle main filter change."""
        self.current_filter = filter_type
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.sidebar.clear_active_button()
        self._display_projects()
    
    def _on_search_change(self, query: str):
        """Handle search query change."""
        self.search_query = query
        self._display_projects()
    
    def _on_origin_filter(self, origin: str):
        """Filter by origin."""
        self.current_origin = origin
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self._display_projects()
    
    def _on_category_filter(self, categories: List[str]):
        """Filter by categories."""
        self.current_categories = categories
        self.current_filter = "all"
        self.current_origin = "all"
        self.current_tag = None
        self._display_projects()
    
    def _on_tag_filter(self, tag: str):
        """Filter by tag."""
        self.current_tag = tag
        self.current_filter = "all"
        self.current_origin = "all"
        self.current_categories = []
        self._display_projects()
    
    # -------------------------------------------------------------------------
    # PROJECT DISPLAY
    # -------------------------------------------------------------------------
    
    def _get_filtered_projects(self) -> List[tuple]:
        """Get filtered projects based on current state."""
        projects = []
        
        for path, project in self.db.items():
            data = project.to_dict()
            
            # Main filter
            if self.current_filter == "favorite" and not project.favorite:
                continue
            elif self.current_filter == "done" and not project.done:
                continue
            elif self.current_filter == "good" and not project.good:
                continue
            elif self.current_filter == "bad" and not project.bad:
                continue
            
            # Origin filter
            if self.current_origin != "all" and project.origin != self.current_origin:
                continue
            
            # Category filter
            if self.current_categories:
                if not any(cat in project.categories for cat in self.current_categories):
                    continue
            
            # Tag filter
            if self.current_tag:
                if self.current_tag not in project.tags:
                    continue
            
            # Search filter
            if self.search_query:
                searchable = f"{project.name} {' '.join(project.categories)} {' '.join(project.tags)}".lower()
                if self.search_query not in searchable:
                    continue
            
            projects.append((path, data))
        
        return projects
    
    def _display_projects(self):
        """Display filtered projects in grid."""
        projects = self._get_filtered_projects()
        
        # Determine title
        if self.current_filter != "all":
            titles = {
                "favorite": "⭐ Favoritos",
                "done": "✓ Já Feitos",
                "good": "👍 Bons",
                "bad": "👎 Ruins"
            }
            title = titles.get(self.current_filter, "Projetos")
        elif self.current_categories:
            title = f"📂 {', '.join(self.current_categories)}"
        elif self.current_tag:
            title = f"🏷️ {self.current_tag}"
        elif self.current_origin != "all":
            title = f"🌐 {self.current_origin}"
        elif self.search_query:
            title = f"🔍 Busca: {self.search_query}"
        else:
            title = "🎬 Todos os Projetos"
        
        self.grid.display_projects(projects, title)
        self.main_window.update_status(f"{len(projects)} projeto(s) exibido(s)")
    
    def _get_thumbnail(self, project_path: str) -> Optional[Any]:
        """Get thumbnail for project."""
        image_path = find_first_image(project_path)
        if image_path:
            return self.image_service.get_thumbnail(image_path)
        return None
    
    def _update_sidebar_data(self):
        """Update sidebar with current statistics."""
        all_data = [p.to_dict() for p in self.db.values()]
        
        # Origins
        origins = self.analysis_service.get_origin_stats(all_data)
        self.sidebar.update_origins(origins)
        
        # Categories
        top_cats = self.analysis_service.get_top_categories(all_data, limit=50)
        self.sidebar.update_categories(top_cats[:8], len(top_cats) - 8 if len(top_cats) > 8 else 0)
        
        # Tags
        top_tags = self.analysis_service.get_top_tags(all_data, limit=20)
        total_tags = len(set(tag for p in all_data for tag in p.get("tags", [])))
        self.sidebar.update_tags(top_tags, total_tags)
    
    # -------------------------------------------------------------------------
    # PROJECT ACTIONS
    # -------------------------------------------------------------------------
    
    def _on_card_click(self, project_path: str):
        """Open project details modal."""
        logger.info(f"Card clicked: {project_path}")
        # TODO: Implement modal (project_modal.py)
        messagebox.showinfo("Detalhes", f"Modal em desenvolvimento\n\n{os.path.basename(project_path)}")
    
    def _open_folder(self, project_path: str):
        """Open project folder in file explorer."""
        try:
            import platform
            system = platform.system()
            if system == "Windows":
                os.startfile(project_path)
            elif system == "Darwin":  # macOS
                import subprocess
                subprocess.run(["open", project_path])
            else:  # Linux
                import subprocess
                subprocess.run(["xdg-open", project_path])
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")
    
    def _toggle_favorite(self, project_path: str, btn: tk.Button):
        """Toggle favorite state."""
        project = self.db.get(project_path)
        if project:
            project.favorite = not project.favorite
            btn.config(text="⭐" if project.favorite else "☆",
                      fg="#FFD700" if project.favorite else "#666666")
            self.db.save()
    
    def _toggle_done(self, project_path: str, btn: tk.Button):
        """Toggle done state."""
        project = self.db.get(project_path)
        if project:
            project.done = not project.done
            btn.config(text="✓" if project.done else "○",
                      fg="#00FF00" if project.done else "#666666")
            self.db.save()
    
    def _toggle_good(self, project_path: str, btn: tk.Button):
        """Toggle good state."""
        project = self.db.get(project_path)
        if project:
            project.good = not project.good
            if project.good:
                project.bad = False
            btn.config(fg="#00FF00" if project.good else "#666666")
            self.db.save()
            self._display_projects()
    
    def _toggle_bad(self, project_path: str, btn: tk.Button):
        """Toggle bad state."""
        project = self.db.get(project_path)
        if project:
            project.bad = not project.bad
            if project.bad:
                project.good = False
            btn.config(fg="#FF0000" if project.bad else "#666666")
            self.db.save()
            self._display_projects()
    
    # -------------------------------------------------------------------------
    # AI ANALYSIS
    # -------------------------------------------------------------------------
    
    def _analyze_single_project(self, project_path: str):
        """Analyze single project with AI."""
        project = self.db.get(project_path)
        if not project:
            return
        
        self.main_window.update_status(f"Analisando {project.name}...")
        
        # Structure analysis
        structure = self.analysis_service.analyze_structure(project_path)
        project.structure = structure
        
        # AI analysis
        categories, tags = self._analyze_project_with_ai(project_path, project)
        project.categories = categories
        project.tags = tags
        project.analyzed = True
        project.analyzed_model = self.settings.active_models["text_quality"]
        
        self.db.save()
        self._update_sidebar_data()
        self._display_projects()
        self.main_window.update_status(f"✅ {project.name} analisado")
    
    def _analyze_project_with_ai(self, project_path: str, project: Project) -> tuple:
        """Analyze project with AI (categories + tags)."""
        try:
            structure = project.structure or self.analysis_service.analyze_structure(project_path)
            
            # Build prompt
            name = project.name
            file_types = ", ".join(f"{ext} ({c}x)" for ext, c in structure.get("file_types", {}).items())
            
            tech_context = []
            if structure.get("has_svg"): tech_context.append("SVG")
            if structure.get("has_pdf"): tech_context.append("PDF")
            if structure.get("has_dxf"): tech_context.append("DXF/CAD")
            tech_str = ", ".join(tech_context) if tech_context else "formatos variados"
            
            # Vision context
            vision_line = ""
            cover_img = find_first_image(project_path)
            if cover_img:
                quality = self.image_service.assess_image_quality(cover_img)
                if quality.get("use_vision"):
                    img_b64 = self.image_service.prepare_image_for_vision(cover_img)
                    if img_b64:
                        vision_desc = self.ollama.generate_with_vision(
                            prompt="Describe the main laser-cut wooden object in the center. Ignore background and watermarks. One sentence.",
                            image_b64=img_b64,
                            model=self.settings.active_models["vision"],
                            timeout=(5, 60)
                        )
                        if vision_desc:
                            vision_line = f"\n🖼️ VISUAL: {vision_desc}"
            
            prompt = f"""Analise este produto de corte laser:

📁 NOME: {name}
📊 ARQUIVOS: {structure.get('total_files', 0)} arquivos
🗂️ TIPOS: {file_types}
🔧 FORMATOS: {tech_str}{vision_line}

### TAREFA 1 — CATEGORIAS (3-5)
1. Data Comemorativa: Páscoa, Natal, Dia das Mães, Dia dos Pais, Aniversário, Casamento, etc.
2. Função/Tipo: Porta-Retrato, Caixa, Luminária, Quadro, Nome Decorativo, etc.
3. Ambiente: Quarto, Sala, Cozinha, Quarto Infantil, etc.

### TAREFA 2 — TAGS (8 tags relevantes)

### FORMATO:
Categorias: [cat1], [cat2], [cat3]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8]"""
            
            text = self.ollama.generate_text(
                prompt=prompt,
                model=self.settings.active_models["text_quality"],
                timeout=(5, 120),
                temperature=0.65,
                num_predict=200
            )
            
            categories, tags = [], []
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("Categorias:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]
                    elif line.startswith("Tags:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]
            
            # Fallback
            if len(categories) < 3:
                categories = self.analysis_service.generate_fallback_categories(project_path, categories)
            if not tags:
                tags = extract_tags_from_name(name)
            
            return categories[:8], tags[:10]
        
        except Exception as e:
            logger.error(f"AI analysis failed for {project_path}: {e}", exc_info=True)
            return self.analysis_service.generate_fallback_categories(project_path), extract_tags_from_name(project.name)
    
    def _stop_analysis(self):
        """Stop ongoing analysis."""
        self.analyzing = False
        self.ollama.stop_flag = True
        self.main_window.hide_progress_ui()
        self.main_window.update_status("⏸️ Análise interrompida")
    
    # -------------------------------------------------------------------------
    # MENU ACTIONS
    # -------------------------------------------------------------------------
    
    def _on_menu_action(self, action: str):
        """Handle menu actions."""
        logger.info(f"Menu action: {action}")
        
        if action == "dashboard":
            messagebox.showinfo("Dashboard", "Dashboard em desenvolvimento")
        elif action == "batch_edit":
            messagebox.showinfo("Edição em Lote", "Edição em lote em desenvolvimento")
        elif action == "model_settings":
            messagebox.showinfo("Configurações", "Configurações de modelos em desenvolvimento")
        elif action == "export_db":
            self._export_database()
        elif action == "import_db":
            self._import_database()
        elif action == "manual_backup":
            backup_file = self.db.manual_backup()
            if backup_file:
                messagebox.showinfo("Backup", f"Backup criado:\n{backup_file}")
        elif action.startswith("analyze_"):
            self._handle_analyze_action(action)
        elif action.startswith("describe_"):
            messagebox.showinfo("Descrições", "Geração de descrições em desenvolvimento")
    
    def _handle_analyze_action(self, action: str):
        """Handle analyze menu actions."""
        if action == "analyze_new":
            to_analyze = [p for p in self.db.values() if not p.analyzed]
            if not to_analyze:
                messagebox.showinfo("Análise", "Todos os projetos já foram analisados!")
                return
            self._batch_analyze(to_analyze)
        elif action == "analyze_all":
            self._batch_analyze(list(self.db.values()))
        elif action == "analyze_filter":
            projects = [self.db.get(path) for path, _ in self._get_filtered_projects()]
            self._batch_analyze([p for p in projects if p])
    
    def _batch_analyze(self, projects: List[Project]):
        """Batch analyze projects."""
        if not projects:
            return
        
        self.analyzing = True
        self.ollama.stop_flag = False
        self.main_window.show_progress_ui()
        
        total = len(projects)
        for i, project in enumerate(projects, 1):
            if not self.analyzing or self.ollama.stop_flag:
                break
            
            self.main_window.show_progress(i, total, f"Analisando {project.name}")
            self._analyze_single_project(project.path)
        
        self.analyzing = False
        self.main_window.hide_progress_ui()
        self.main_window.update_status(f"✅ {i} projetos analisados")
    
    def _export_database(self):
        """Export database to JSON."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Exportar Banco de Dados"
        )
        if filepath:
            import shutil
            shutil.copy2(self.settings.db_file, filepath)
            messagebox.showinfo("Exportar", f"Banco exportado para:\n{filepath}")
    
    def _import_database(self):
        """Import database from JSON."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Importar Banco de Dados"
        )
        if filepath:
            if messagebox.askyesno("Confirmar", "Isso vai substituir o banco atual. Continuar?"):
                import shutil
                shutil.copy2(filepath, self.settings.db_file)
                self.db.load()
                self._update_sidebar_data()
                self._display_projects()
                messagebox.showinfo("Importar", "Banco importado com sucesso!")
