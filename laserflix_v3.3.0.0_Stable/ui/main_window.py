"""
ui/main_window.py — Orquestrador puro do Laserflix.

Regra de ouro: este arquivo NUNCA deve passar de 250 linhas.
Se uma função crescer demais → vira módulo novo.

Responsabilidade: instanciar componentes, roteamento de callbacks,
loop de display, filtros, toggles, IA batch e utilitários simples.
Nenhuma construção de widget acontece aqui.
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config.settings import VERSION
from config.card_layout import COLS, CARD_PAD
from config.ui_constants import (
    BG_PRIMARY, BG_CARD, BG_SEPARATOR,
    ACCENT_RED, ACCENT_GREEN, ACCENT_GOLD,
    FG_PRIMARY, FG_SECONDARY, FG_TERTIARY,
    SCROLL_SPEED,
)

from core.database import DatabaseManager
from core.thumbnail_cache import ThumbnailCache
from core.project_scanner import ProjectScanner

from ai.ollama_client import OllamaClient
from ai.image_analyzer import ImageAnalyzer
from ai.text_generator import TextGenerator
from ai.fallbacks import FallbackGenerator
from ai.analysis_manager import AnalysisManager

from utils.logging_setup import LOGGER
from utils.platform_utils import open_folder

from ui.recursive_import_integration import RecursiveImportManager
from ui.prepare_folders_dialog import PrepareFoldersDialog
from ui.model_settings_dialog import ModelSettingsDialog
from ui.header import HeaderBar
from ui.sidebar import SidebarPanel
from ui.project_card import build_card
from ui.edit_modal import EditModal
from ui.project_modal import ProjectModal


class LaserflixMainWindow:
    def __init__(self, root: tk.Tk):
        self.root   = root
        self.logger = LOGGER

        # Core
        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()
        self.cache   = ThumbnailCache()
        self.scanner = ProjectScanner(self.db_manager.database)

        # IA
        self.ollama             = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer     = ImageAnalyzer(self.ollama)
        self.fallback_generator = FallbackGenerator(self.scanner)
        self.text_generator     = TextGenerator(
            self.ollama, self.image_analyzer, self.scanner, self.fallback_generator)
        self.analysis_manager   = AnalysisManager(
            self.text_generator, self.db_manager, self.ollama)
        self._setup_analysis_callbacks()

        # Estado de filtros
        self.database           = self.db_manager.database
        self.current_filter     = "all"
        self.current_categories = []
        self.current_tag        = None
        self.current_origin     = "all"
        self.search_query       = ""

        # Importação
        self.import_manager = RecursiveImportManager(
            parent=self.root, database=self.database,
            project_scanner=self.scanner, text_generator=self.text_generator,
            on_complete=self._on_import_complete,
        )

        # Janela
        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state("zoomed")
        self.root.configure(bg=BG_PRIMARY)
        self._build_ui()
        self.display_projects()
        self.logger.info("✨ Laserflix v%s iniciado", VERSION)

    # =========================================================================
    # UI — montagem dos componentes (sem widgets diretos aqui)
    # =========================================================================

    def _build_ui(self) -> None:
        # Header
        self.header = HeaderBar(self.root, {
            "on_filter":          self.set_filter,
            "on_search":          self._on_search,
            "on_import":          self.open_import_dialog,
            "on_analyze_new":     self.analyze_only_new,
            "on_analyze_all":     self.reanalyze_all,
            "on_desc_new":        self.generate_descriptions_for_new,
            "on_desc_all":        self.generate_descriptions_for_all,
            "on_prepare_folders": self.open_prepare_folders,
            "on_import_db":       self.import_database,
            "on_export_db":       self.export_database,
            "on_backup":          self.manual_backup,
            "on_model_settings":  self.open_model_settings,
        })
        self.search_var = self.header.search_var  # alias direto

        # Container central
        main_container = tk.Frame(self.root, bg=BG_PRIMARY)
        main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = SidebarPanel(main_container, {
            "on_origin":           self._on_origin_filter,
            "on_category":         self._on_category_filter,
            "on_tag":              self._on_tag_filter,
            "on_more_categories":  self.open_categories_picker,
        })
        self.sidebar.refresh(self.database)

        # Área de conteúdo (canvas scrollável)
        content_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        content_frame.pack(side="left", fill="both", expand=True)
        self.content_canvas = tk.Canvas(content_frame, bg=BG_PRIMARY, highlightthickness=0)
        content_sb = ttk.Scrollbar(content_frame, orient="vertical",
                                    command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg=BG_PRIMARY)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_sb.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        content_sb.pack(side="right", fill="y")
        for i in range(COLS):
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="card")
        self.content_canvas.bind(
            "<Enter>",
            lambda e: self.content_canvas.bind(
                "<MouseWheel>",
                lambda ev: self.content_canvas.yview_scroll(
                    int(-1*(ev.delta/SCROLL_SPEED)), "units")))
        self.content_canvas.bind(
            "<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))

        # Status bar
        sf = tk.Frame(self.root, bg="#000000", height=40)
        sf.pack(side="bottom", fill="x")
        sf.pack_propagate(False)
        self.status_bar = tk.Label(sf, text="Pronto.", bg="#000000", fg=FG_SECONDARY,
                                   font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("G.Horizontal.TProgressbar",
                        troughcolor=BG_CARD, background=ACCENT_GREEN, bordercolor="#000000")
        self.progress_bar = ttk.Progressbar(sf, mode="determinate", length=300,
                                             style="G.Horizontal.TProgressbar")
        self.stop_btn = tk.Button(sf, text="⏹ Parar",
                                   command=self.analysis_manager.stop,
                                   bg=ACCENT_RED, fg=FG_PRIMARY,
                                   font=("Arial", 10, "bold"), relief="flat", cursor="hand2")

    # =========================================================================
    # DISPLAY DE PROJETOS
    # =========================================================================

    def display_projects(self) -> None:
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        title_map = {
            "favorite": "⭐ Favoritos", "done": "✓ Já Feitos",
            "good":     "👍 Bons",      "bad":  "👎 Ruins",
        }
        title = title_map.get(self.current_filter, "Todos os Projetos")
        if self.current_origin     != "all":  title += f" — {self.current_origin}"
        if self.current_categories:           title += f" — {', '.join(self.current_categories)}"
        if self.current_tag:                  title += f" — #{self.current_tag}"
        if self.search_query:                 title += f' — "{self.search_query}"'
        tk.Label(self.scrollable_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).grid(row=0, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0, 5))
        filtered = [(p, self.database[p])
                    for p in self.get_filtered_projects() if p in self.database]
        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)",
                 font=("Arial", 12), bg=BG_PRIMARY, fg="#999999"
                 ).grid(row=1, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0, 15))
        if not filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em 'Importar Pastas' para adicionar.",
                     font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return
        card_cb = {
            "on_open_modal":     self.open_project_modal,
            "on_toggle_favorite": self.toggle_favorite,
            "on_toggle_done":    self.toggle_done,
            "on_toggle_good":    self.toggle_good,
            "on_toggle_bad":     self.toggle_bad,
            "on_analyze_single": self.analyze_single_project,
            "on_open_folder":    open_folder,
            "on_set_category":   self.set_category_filter,
            "on_set_tag":        self.set_tag_filter,
            "on_set_origin":     self.set_origin_filter,
            "get_cover_image":   self.cache.get_cover_image,
        }
        row, col = 2, 0
        for project_path, data in filtered:
            build_card(self.scrollable_frame, project_path, data, card_cb, row, col)
            col += 1
            if col >= COLS:
                col = 0; row += 1

    # =========================================================================
    # FILTROS
    # =========================================================================

    def set_filter(self, filter_type: str) -> None:
        self.current_filter = filter_type
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_var.set("")
        self.sidebar.set_active_btn(None)
        self.display_projects()

    def _on_search(self) -> None:
        self.search_query = self.search_var.get().strip().lower()
        self.display_projects()

    def _on_origin_filter(self, origin: str, btn=None) -> None:
        self.current_filter = "all"; self.current_origin = origin
        self.current_categories = []; self.current_tag = None
        self.sidebar.set_active_btn(btn)
        self.display_projects()
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")

    def _on_category_filter(self, cats: list, btn=None) -> None:
        self.current_filter = "all"; self.current_categories = cats
        self.current_tag = None; self.current_origin = "all"
        self.sidebar.set_active_btn(btn)
        self.display_projects()

    def _on_tag_filter(self, tag: str, btn=None) -> None:
        self.current_filter = "all"; self.current_tag = tag
        self.current_categories = []; self.current_origin = "all"
        self.sidebar.set_active_btn(btn)
        self.display_projects()

    # Aliases públicos usados por project_card e project_modal
    def set_origin_filter(self, origin, btn=None):     self._on_origin_filter(origin, btn)
    def set_category_filter(self, cats, btn=None):     self._on_category_filter(cats, btn)
    def set_tag_filter(self, tag, btn=None):            self._on_tag_filter(tag, btn)

    def get_filtered_projects(self) -> list:
        result = []
        for path, data in self.database.items():
            ok = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done"     and data.get("done"))
                or (self.current_filter == "good"     and data.get("good"))
                or (self.current_filter == "bad"      and data.get("bad"))
            )
            if not ok: continue
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(
                    c in data.get("categories", []) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags", []): continue
            if self.search_query and self.search_query not in data.get("name", "").lower(): continue
            result.append(path)
        return result

    # =========================================================================
    # MODAL DE PROJETO
    # =========================================================================

    def open_project_modal(self, project_path: str) -> None:
        ProjectModal(
            root=self.root,
            project_path=project_path,
            database=self.database,
            cb={
                "get_all_paths":    lambda: [p for p in self.database if os.path.isdir(p)],
                "on_navigate":      self.open_project_modal,
                "on_toggle":        self._modal_toggle,
                "on_generate_desc": self._modal_generate_desc,
                "on_open_edit":     self.open_edit_mode,
                "on_reanalize":     self.analyze_single_project,
                "on_set_tag":       self.set_tag_filter,
            },
            cache=self.cache,
            scanner=self.scanner,
        ).open()

    def _modal_toggle(self, path: str, key: str, value: bool) -> None:
        if path in self.database:
            self.database[path][key] = value
            self.db_manager.save_database()
            self.display_projects()

    def _modal_generate_desc(self, path, desc_lbl, gen_btn, modal) -> None:
        gen_btn.config(state="disabled", text="⏳ Gerando...")
        desc_lbl.config(text="⏳ Gerando descrição com IA...", fg="#555555")
        modal.update()
        def _run():
            try:
                desc = self.text_generator.generate_description(path, self.database[path])
                self.database[path]["ai_description"] = desc
                self.db_manager.save_database()
                modal.after(0, modal.destroy)
                modal.after(50, lambda: self.open_project_modal(path))
            except Exception as e:
                self.logger.error("Erro ao gerar descrição: %s", e)
                modal.after(0, lambda: desc_lbl.config(text="❌ Erro ao gerar", fg="#EF5350"))
                modal.after(0, lambda: gen_btn.config(state="normal", text="🤖  Gerar com IA"))
        threading.Thread(target=_run, daemon=True).start()

    # =========================================================================
    # EDIÇÃO
    # =========================================================================

    def open_edit_mode(self, project_path: str) -> None:
        data = self.database.get(project_path, {})
        EditModal(self.root, project_path, data, self._on_edit_save)

    def _on_edit_save(self, path: str, new_cats: list, new_tags: list) -> None:
        if path in self.database:
            if new_cats:
                self.database[path]["categories"] = new_cats
            self.database[path]["tags"]     = new_tags
            self.database[path]["analyzed"] = True
            self.db_manager.save_database()
            self.sidebar.refresh(self.database)
            self.display_projects()
            self.status_bar.config(text="✓ Projeto atualizado!")

    # =========================================================================
    # TOGGLES
    # =========================================================================

    def toggle_favorite(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            if btn: btn.config(text="⭐" if nv else "☆",
                               fg=ACCENT_GOLD if nv else FG_TERTIARY)

    def toggle_done(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            if btn: btn.config(text="✓" if nv else "○",
                               fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_good(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv: self.database[path]["bad"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_bad(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv: self.database[path]["good"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#FF0000" if nv else FG_TERTIARY)

    # =========================================================================
    # IA — ANÁLISE
    # =========================================================================

    def _setup_analysis_callbacks(self) -> None:
        self.analysis_manager.on_start    = self.show_progress_ui
        self.analysis_manager.on_progress = self.update_progress
        self.analysis_manager.on_complete = self._on_analysis_complete
        self.analysis_manager.on_error    = self._on_analysis_error

    def _on_analysis_complete(self, done, skipped) -> None:
        self.hide_progress_ui()
        self.sidebar.refresh(self.database)
        self.display_projects()
        msg = f"✅ Análise concluída: {done} projeto(s)"
        if skipped: msg += f" ({skipped} pulados)"
        self.status_bar.config(text=msg)

    def _on_analysis_error(self, error_msg) -> None:
        from tkinter import messagebox
        messagebox.showwarning("⚠️ Erro", error_msg)

    def show_progress_ui(self) -> None:
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0

    def hide_progress_ui(self) -> None:
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()

    def update_progress(self, current, total, message="") -> None:
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.status_bar.config(text=f"{message} ({current}/{total} — {pct:.1f}%)")
        self.root.update_idletasks()

    def analyze_single_project(self, path: str) -> None:
        self.analysis_manager.analyze_single(path, self.database)

    def analyze_only_new(self) -> None:
        targets = self.analysis_manager.get_unanalyzed_projects(self.database)
        if not targets:
            messagebox.showinfo("✅ Tudo analisado", "Todos os projetos já foram analisados!"); return
        if messagebox.askyesno("🤖 Analisar novos",
                               f"Encontrei {len(targets)} projeto(s) sem análise.\n\nIniciar agora?"):
            self.analysis_manager.analyze_batch(targets, self.database)

    def reanalyze_all(self) -> None:
        targets = self.analysis_manager.get_all_projects(self.database)
        if not targets:
            messagebox.showinfo("Vazio", "Nenhum projeto encontrado."); return
        if messagebox.askyesno("🔄 Reanalisar todos",
                               f"Isso vai reanalisar {len(targets)} projeto(s).\n\nConfirma?"):
            self.analysis_manager.analyze_batch(targets, self.database)

    # =========================================================================
    # IA — DESCRIÇÕES
    # =========================================================================

    def _batch_generate_descriptions(self, targets: list) -> None:
        self.show_progress_ui()
        def _run():
            done = skipped = 0
            for i, path in enumerate(targets, 1):
                if self.ollama.stop_flag: break
                if not os.path.isdir(path):
                    skipped += 1; continue
                try:
                    self.update_progress(i, len(targets),
                        f"📝 Gerando descrição para {os.path.basename(path)}")
                    desc = self.text_generator.generate_description(path, self.database[path])
                    self.database[path]["ai_description"] = desc
                    done += 1
                    if done % 5 == 0: self.db_manager.save_database()
                except Exception as e:
                    self.logger.error("Erro desc %s: %s", path, e)
                    skipped += 1
            self.db_manager.save_database()
            self.hide_progress_ui()
            self.display_projects()
            msg = f"✅ {done} descrição(oes) gerada(s)"
            if skipped: msg += f" ({skipped} puladas)"
            self.status_bar.config(text=msg)
        threading.Thread(target=_run, daemon=True).start()

    def generate_descriptions_for_new(self) -> None:
        targets = [p for p, d in self.database.items() if not d.get("ai_description", "").strip()]
        if not targets:
            messagebox.showinfo("✅ Completo", "Todos os projetos já têm descrição!"); return
        if messagebox.askyesno("📝 Gerar descrições",
                               f"Encontrei {len(targets)} projeto(s) sem descrição.\n\nGerar agora?"):
            self._batch_generate_descriptions(targets)

    def generate_descriptions_for_all(self) -> None:
        targets = list(self.database.keys())
        if not targets:
            messagebox.showinfo("Vazio", "Nenhum projeto encontrado."); return
        if messagebox.askyesno("📝 Gerar todas descrições",
                               f"Isso vai gerar descrições para {len(targets)} projeto(s).\n\nConfirma?"):
            self._batch_generate_descriptions(targets)

    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================

    def open_import_dialog(self) -> None:
        self.import_manager.database = self.database
        self.import_manager.start_import()

    def open_prepare_folders(self) -> None:
        dlg = PrepareFoldersDialog(self.root)
        self.root.wait_window(dlg)

    def open_model_settings(self) -> None:
        dlg = ModelSettingsDialog(self.root, self.db_manager)
        self.root.wait_window(dlg)

    def open_categories_picker(self) -> None:
        all_cats: dict = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria":
                    all_cats[c] = all_cats.get(c, 0) + 1
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Todas as Categorias")
        win.configure(bg=BG_PRIMARY)
        win.geometry("400x600")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Selecione uma categoria", font=("Arial", 13, "bold"),
                 bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=10)
        frm = tk.Frame(win, bg=BG_PRIMARY)
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        cv = tk.Canvas(frm, bg=BG_PRIMARY, highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=BG_PRIMARY)
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/SCROLL_SPEED)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})",
                          command=lambda c=cat: (self.set_category_filter([c]), win.destroy()),
                          bg=BG_CARD, fg=FG_PRIMARY, font=("Arial", 10),
                          relief="flat", cursor="hand2", anchor="w", padx=12, pady=8)
            b.pack(fill="x", pady=2, padx=5)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=ACCENT_RED))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=BG_CARD))
        tk.Button(win, text="Fechar", command=win.destroy,
                  bg="#555555", fg=FG_PRIMARY, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=8).pack(pady=10)

    def export_database(self) -> None:
        import shutil
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")],
            title="Exportar banco de dados")
        if path:
            shutil.copy2("laserflix_database.json", path)
            messagebox.showinfo("✅ Exportado", f"Banco exportado para:\n{path}")

    def import_database(self) -> None:
        import shutil
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")], title="Importar banco de dados")
        if path:
            shutil.copy2(path, "laserflix_database.json")
            self.db_manager.load_database()
            self.database = self.db_manager.database
            self.sidebar.refresh(self.database)
            self.display_projects()
            messagebox.showinfo("✅ Importado", "Banco importado com sucesso!")

    def manual_backup(self) -> None:
        self.db_manager.auto_backup()
        messagebox.showinfo("✅ Backup", "Backup criado com sucesso!")

    def _on_import_complete(self) -> None:
        self.database = self.db_manager.database
        self.import_manager.database = self.database
        self.db_manager.save_database()
        self.sidebar.refresh(self.database)
        self.display_projects()
        self.status_bar.config(text="✅ Importação concluída!")
