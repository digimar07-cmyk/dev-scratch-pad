"""
ui/main_window.py — Orquestrador puro do Laserflix.
Teto: 350 linhas. Nunca constrói widgets diretamente.

HOT-08: Paginação simples (Kent Beck style):
  - HOT-13: 36 cards por página (6 linhas × 6 cols)
  - Navegação: Início/Anterior/Próxima/Final
  - Atalhos: Home/End/Arrows
  - SIMPLES, PREVISÍVEL, FUNCIONAL

HOT-12: Scrollbar vertical (cards com categorias ficaram mais altos)
HOT-14: Busca bilíngue (EN + PT-BR) — FUNCIONA SEM OLLAMA!
HOT-15: Tradutor estático (utils/name_translator.py)
F-07: Filtros empilháveis (chips AND) — CORRIGIDO!

FEATURE: Ordenação FUNCIONAL na linha de paginação
FEATURE: Análise SEQUENCIAL pós-importação (categorias+tags → descrições)
F-03: Limpeza de órfãos (entradas sem path válido)
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
from core.thumbnail_preloader import ThumbnailPreloader
from core.project_scanner import ProjectScanner

from ai.ollama_client import OllamaClient
from ai.image_analyzer import ImageAnalyzer
from ai.text_generator import TextGenerator
from ai.fallbacks import FallbackGenerator
from ai.analysis_manager import AnalysisManager

from utils.logging_setup import LOGGER
from utils.platform_utils import open_folder
from utils.name_translator import search_bilingual  # HOT-15: Busca bilíngue SEM Ollama

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

        self.db_manager = DatabaseManager()
        self.db_manager.load_config()
        self.db_manager.load_database()
        
        self.thumbnail_preloader = ThumbnailPreloader(max_workers=4)
        self.scanner = ProjectScanner(self.db_manager.database)

        self.ollama             = OllamaClient(self.db_manager.config.get("models"))
        self.image_analyzer     = ImageAnalyzer(self.ollama)
        self.fallback_generator = FallbackGenerator(self.scanner)
        self.text_generator     = TextGenerator(
            self.ollama, self.image_analyzer, self.scanner, self.fallback_generator)
        self.analysis_manager   = AnalysisManager(
            self.text_generator, self.db_manager, self.ollama)
        self._setup_analysis_callbacks()

        self.database           = self.db_manager.database
        self.current_filter     = "all"
        self.current_categories = []
        self.current_tag        = None
        self.current_origin     = "all"
        self.search_query       = ""
        self.current_sort       = "date_desc"
        
        # F-07: Filtros empilháveis (chips AND)
        # Estrutura: [{"type": "category", "value": "Animais"}, {"type": "tag", "value": "colorido"}, ...]
        self.active_filters = []

        self._selection_mode    = False
        self._selected_paths    = set()
        
        self.items_per_page = 36
        self.current_page   = 1
        self.total_pages    = 1

        self.import_manager = RecursiveImportManager(
            parent=self.root, database=self.database,
            project_scanner=self.scanner, text_generator=self.text_generator,
            analysis_manager=self.analysis_manager,
            on_complete=self._on_import_complete,
        )

        self.root.title(f"LASERFLIX {VERSION}")
        self.root.state("zoomed")
        self.root.configure(bg=BG_PRIMARY)
        self._build_ui()
        self.display_projects()
        self.logger.info("✨ Laserflix v%s iniciado (busca bilíngue + filtros empilháveis)", VERSION)

    def __del__(self):
        if hasattr(self, 'thumbnail_preloader'):
            self.thumbnail_preloader.shutdown()

    # =========================================================================
    # UI
    # =========================================================================

    def _build_ui(self) -> None:
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
            "on_toggle_select":   self.toggle_selection_mode,
            "on_clean_orphans":   self.clean_orphans,
        })
        self.search_var = self.header.search_var

        main_container = tk.Frame(self.root, bg=BG_PRIMARY)
        main_container.pack(fill="both", expand=True)

        self.sidebar = SidebarPanel(main_container, {
            "on_origin":          self._on_origin_filter,
            "on_category":        self._on_category_filter,
            "on_tag":             self._on_tag_filter,
            "on_more_categories": self.open_categories_picker,
        })
        self.sidebar.refresh(self.database)

        content_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        content_frame.pack(side="left", fill="both", expand=True)
        
        # F-07: Barra de chips (filtros empilháveis)
        self.chips_bar = tk.Frame(content_frame, bg="#1A1A2E", height=50)
        self.chips_bar.pack_propagate(False)
        self.chips_container = tk.Frame(self.chips_bar, bg="#1A1A2E")
        self.chips_container.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        # Não pack() aqui — só aparece quando há filtros
        
        self.content_canvas = tk.Canvas(content_frame, bg=BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.content_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.scrollable_frame = tk.Frame(self.content_canvas, bg=BG_PRIMARY)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        self.content_canvas.bind("<MouseWheel>",
            lambda e: self.content_canvas.yview_scroll(int(-1*(e.delta/SCROLL_SPEED)), "units"))
        
        for i in range(COLS):
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="card")

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

        # Barra de seleção em massa
        self._sel_bar = tk.Frame(self.root, bg="#1A1A00", height=48)
        self._sel_bar.pack_propagate(False)
        self._sel_count_lbl = tk.Label(
            self._sel_bar, text="0 selecionado(s)",
            bg="#1A1A00", fg="#FFFF88", font=("Arial", 11, "bold"))
        self._sel_count_lbl.pack(side="left", padx=16)
        tk.Button(self._sel_bar, text="☑️ Tudo",
                  command=self._select_all,
                  bg="#333300", fg="#FFFF88", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=4)
        tk.Button(self._sel_bar, text="🔲 Nenhum",
                  command=self._deselect_all,
                  bg="#333300", fg="#FFFF88", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=4)
        tk.Button(self._sel_bar, text="🗑️ Remover selecionados",
                  command=self._remove_selected,
                  bg="#5A0000", fg="#FF8888", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=6
                  ).pack(side="left", padx=12)
        tk.Button(self._sel_bar, text="✕ Cancelar",
                  command=self.toggle_selection_mode,
                  bg="#1A1A00", fg="#888888", font=("Arial", 10),
                  relief="flat", cursor="hand2", padx=10, pady=6
                  ).pack(side="right", padx=16)
        
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<Home>", lambda e: self.first_page())
        self.root.bind("<End>", lambda e: self.last_page())

    # =========================================================================
    # F-07: FILTROS EMPILHÁVEIS (CHIPS)
    # =========================================================================

    def _update_chips_bar(self) -> None:
        """Reconstrói barra de chips baseado em active_filters."""
        for w in self.chips_container.winfo_children():
            w.destroy()
        
        if not self.active_filters:
            self.chips_bar.pack_forget()
            return
        
        # Insere ANTES do content_canvas (abaixo do header)
        self.chips_bar.pack(before=self.content_canvas, side="top", fill="x", padx=10, pady=(10, 0))
        
        # Ícones por tipo
        icons = {
            "category": "🏷️",
            "tag": "🔖",
            "origin": "📂",
            "analysis_ai": "🤖",
            "analysis_fallback": "⚡",
            "analysis_pending": "⏳",
        }
        
        for filt in self.active_filters:
            ftype = filt["type"]
            fval = filt["value"]
            icon = icons.get(ftype, "🔹")
            
            chip_frame = tk.Frame(self.chips_container, bg="#2E2E4E", relief="flat", bd=0)
            chip_frame.pack(side="left", padx=4)
            
            tk.Label(chip_frame, text=f"{icon} {fval}",
                     bg="#2E2E4E", fg="#FFFFFF", font=("Arial", 10),
                     padx=8, pady=4).pack(side="left")
            
            remove_btn = tk.Button(
                chip_frame, text="✕",
                command=lambda f=filt: self._remove_chip(f),
                bg="#2E2E4E", fg="#FF6B6B", font=("Arial", 9, "bold"),
                relief="flat", cursor="hand2", padx=4, pady=2, bd=0
            )
            remove_btn.pack(side="left")
            remove_btn.bind("<Enter>", lambda e, b=remove_btn: b.config(bg="#FF6B6B", fg="#FFFFFF"))
            remove_btn.bind("<Leave>", lambda e, b=remove_btn: b.config(bg="#2E2E4E", fg="#FF6B6B"))
        
        # Botão "Limpar tudo"
        if len(self.active_filters) > 1:
            clear_btn = tk.Button(
                self.chips_container, text="✕ Limpar tudo",
                command=self._clear_all_chips,
                bg="#4A1A1A", fg="#FFAAAA", font=("Arial", 9, "bold"),
                relief="flat", cursor="hand2", padx=10, pady=4
            )
            clear_btn.pack(side="right", padx=8)
            clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#8A1A1A"))
            clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#4A1A1A"))

    def _add_filter_chip(self, filter_type: str, value: str) -> None:
        """Adiciona chip se não existir (modo empilhável)."""
        new_chip = {"type": filter_type, "value": value}
        if new_chip not in self.active_filters:
            self.active_filters.append(new_chip)
            self._update_chips_bar()
            self.current_page = 1
            self.display_projects()

    def _remove_chip(self, filt: dict) -> None:
        """Remove chip específico."""
        if filt in self.active_filters:
            self.active_filters.remove(filt)
            self._update_chips_bar()
            self.current_page = 1
            self.display_projects()

    def _clear_all_chips(self) -> None:
        """Remove todos os chips."""
        self.active_filters.clear()
        self._update_chips_bar()
        self.current_page = 1
        self.display_projects()

    # =========================================================================
    # ORDENAÇÃO
    # =========================================================================

    def _on_sort(self, sort_type: str) -> None:
        """Callback quando usuário muda ordenação."""
        self.current_sort = sort_type
        self.current_page = 1
        self.display_projects()

    def _apply_sorting(self, projects: list) -> list:
        """Aplica ordenação aos projetos filtrados."""
        if not projects:
            return projects
        
        try:
            if self.current_sort == "date_desc":
                return sorted(projects, key=lambda p: p[1].get("added_date", ""), reverse=True)
            elif self.current_sort == "date_asc":
                return sorted(projects, key=lambda p: p[1].get("added_date", ""))
            elif self.current_sort == "name_asc":
                return sorted(projects, key=lambda p: p[1].get("name", "").lower())
            elif self.current_sort == "name_desc":
                return sorted(projects, key=lambda p: p[1].get("name", "").lower(), reverse=True)
            elif self.current_sort == "origin":
                return sorted(projects, key=lambda p: (p[1].get("origin", "zzz"), p[1].get("name", "").lower()))
            elif self.current_sort == "analyzed":
                return sorted(projects, key=lambda p: (not p[1].get("analyzed", False), p[1].get("name", "").lower()))
            elif self.current_sort == "not_analyzed":
                return sorted(projects, key=lambda p: (p[1].get("analyzed", False), p[1].get("name", "").lower()))
            else:
                return projects
        except Exception as e:
            self.logger.error("Erro ao ordenar: %s", e)
            return projects

    # =========================================================================
    # MODO DE SELEÇÃO EM MASSA
    # =========================================================================

    def toggle_selection_mode(self) -> None:
        self._selection_mode = not self._selection_mode
        self._selected_paths.clear()
        if self._selection_mode:
            self._sel_bar.pack(fill="x", before=self.content_canvas.master)
            self.header.set_select_btn_active(True)
        else:
            self._sel_bar.pack_forget()
            self.header.set_select_btn_active(False)
        self.display_projects()

    def toggle_card_selection(self, path: str) -> None:
        if path in self._selected_paths:
            self._selected_paths.discard(path)
        else:
            self._selected_paths.add(path)
        n = len(self._selected_paths)
        self._sel_count_lbl.config(text=f"{n} selecionado(s)")
        self.display_projects()

    def _select_all(self) -> None:
        self._selected_paths = set(self.get_filtered_projects())
        self._sel_count_lbl.config(text=f"{len(self._selected_paths)} selecionado(s)")
        self.display_projects()

    def _deselect_all(self) -> None:
        self._selected_paths.clear()
        self._sel_count_lbl.config(text="0 selecionado(s)")
        self.display_projects()

    def _remove_selected(self) -> None:
        n = len(self._selected_paths)
        if not n:
            messagebox.showinfo("Seleção vazia", "Nenhum projeto selecionado."); return
        if not messagebox.askyesno(
            "🗑️ Remover projetos",
            f"Remover {n} projeto(s) do banco?\n\nOs arquivos no disco NÃO serão apagados.",
            icon="warning"):
            return
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            f"Segunda confirmação.\nIsso removerá {n} projeto(s) permanentemente do banco.\n\nTem certeza?",
            icon="warning"):
            return
        for path in list(self._selected_paths):
            self.database.pop(path, None)
        self.db_manager.save_database()
        self._selected_paths.clear()
        self._selection_mode = False
        self._sel_bar.pack_forget()
        self.header.set_select_btn_active(False)
        self.sidebar.refresh(self.database)
        self.display_projects()
        self.status_bar.config(text=f"🗑️ {n} projeto(s) removido(s) do banco.")

    def remove_project(self, path: str) -> None:
        if path in self.database:
            name = self.database[path].get("name", path)
            self.database.pop(path)
            self.db_manager.save_database()
            self.sidebar.refresh(self.database)
            self.display_projects()
            self.status_bar.config(text=f"🗑️ '{name}' removido do banco.")

    # =========================================================================
    # F-03: LIMPEZA DE ÓRFÃOS
    # =========================================================================

    def clean_orphans(self) -> None:
        """
        F-03: Remove projetos cujo path não existe mais no disco.
        Kent Beck: Detectar é rápido, remover requer confirmação dupla.
        """
        orphans = [p for p in self.database.keys() if not os.path.isdir(p)]
        
        if not orphans:
            messagebox.showinfo(
                "✅ Banco limpo",
                "Nenhum órfão encontrado!\n\nTodos os projetos têm pastas válidas."
            )
            return
        
        # Primeira confirmação: mostra lista
        msg = f"Encontrei {len(orphans)} projeto(s) órfão(s):\n\n"
        msg += "\n".join(f"- {os.path.basename(p)}" for p in orphans[:10])
        if len(orphans) > 10:
            msg += f"\n... e mais {len(orphans) - 10}"
        msg += "\n\nEsses projetos não existem mais no disco.\nRemover do banco?"
        
        if not messagebox.askyesno("🧼 Limpar órfãos", msg, icon="warning"):
            return
        
        # Segunda confirmação
        if not messagebox.askyesno(
            "⚠️ Confirmar remoção",
            f"Segunda confirmação.\n\n{len(orphans)} projeto(s) serão removidos PERMANENTEMENTE do banco.\n\nTem certeza?",
            icon="warning"
        ):
            return
        
        # Remove
        for path in orphans:
            self.database.pop(path, None)
        
        self.db_manager.save_database()
        self.sidebar.refresh(self.database)
        self.display_projects()
        self.status_bar.config(text=f"🧼 {len(orphans)} órfão(s) removido(s) do banco.")
        
        messagebox.showinfo(
            "✅ Limpeza concluída",
            f"{len(orphans)} projeto(s) órfão(s) removido(s) do banco.\n\nBanco agora está sincronizado com o disco."
        )

    # =========================================================================
    # PAGINAÇÃO SIMPLES (HOT-08 / HOT-13)
    # =========================================================================

    def display_projects(self) -> None:
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        
        # 1. PREPARA DADOS
        all_filtered = [
            (p, self.database[p])
            for p in self.get_filtered_projects()
            if p in self.database
        ]
        
        # APLICA ORDENAÇÃO
        all_filtered = self._apply_sorting(all_filtered)
        
        total_count = len(all_filtered)
        
        # 2. CALCULA PAGINAÇÃO
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_count)
        page_items = all_filtered[start_idx:end_idx]
        
        # 3. HEADER COM CONTADOR + ORDENAÇÃO
        title_map = {
            "favorite": "⭐ Favoritos", "done": "✓ Já Feitos",
            "good":     "👍 Bons",      "bad":  "👎 Ruins",
        }
        title = title_map.get(self.current_filter, "Todos os Projetos")
        if self.current_origin     != "all":  title += f" — {self.current_origin}"
        if self.current_categories:           title += f" — {', '.join(self.current_categories)}"
        if self.current_tag:                  title += f" — #{self.current_tag}"
        if self.search_query:                 title += f' — "{self.search_query}"'
        
        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=COLS, sticky="ew", padx=10, pady=(0, 5))
        
        tk.Label(header_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).pack(side="left")
        
        # ══════════════════════════════════════════════════════════════════
        # MENU DE ORDENAÇÃO + NAVEGAÇÃO (CANTO DIREITO)
        # ══════════════════════════════════════════════════════════════════
        if total_count > 0:
            right_controls = tk.Frame(header_frame, bg=BG_PRIMARY)
            right_controls.pack(side="right", padx=10)
            
            # ORDENAÇÃO (dropdown)
            sort_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
            sort_frame.pack(side="left", padx=(0, 15))
            
            tk.Label(sort_frame, text="📊", bg=BG_PRIMARY,
                     fg=FG_TERTIARY, font=("Arial", 12)).pack(side="left", padx=(0, 5))
            
            # Mapeamento key → label
            sort_labels = {
                "date_desc":    "📅 Recentes",
                "date_asc":     "📅 Antigos",
                "name_asc":     "🔤 A→Z",
                "name_desc":    "🔥 Z→A",
                "origin":       "🏛️ Origem",
                "analyzed":     "🤖 Analisados",
                "not_analyzed": "⏳ Pendentes",
            }
            
            # Cria StringVar com KEY (não label)
            sort_var = tk.StringVar(value=self.current_sort)
            
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(
                "Sort.TCombobox",
                fieldbackground="#222222",
                background="#222222",
                foreground=FG_PRIMARY,
                arrowcolor=FG_PRIMARY,
                borderwidth=0,
            )
            style.map("Sort.TCombobox",
                fieldbackground=[("readonly", "#222222")],
                selectbackground=[("readonly", "#222222")],
                selectforeground=[("readonly", FG_PRIMARY)],
            )
            
            # Combobox recebe LABELS, mas retorna label selecionado
            sort_combo = ttk.Combobox(
                sort_frame,
                textvariable=sort_var,
                values=list(sort_labels.values()),  # ← LABELS
                state="readonly",
                width=14,
                font=("Arial", 9),
                style="Sort.TCombobox",
            )
            sort_combo.pack(side="left")
            
            # Define label inicial
            sort_combo.set(sort_labels[self.current_sort])
            
            # Callback: converte label → key
            def on_sort_change(event):
                selected_label = sort_combo.get()
                # Encontra key correspondente
                for key, label in sort_labels.items():
                    if label == selected_label:
                        self._on_sort(key)
                        break
            
            sort_combo.bind("<<ComboboxSelected>>", on_sort_change)
            
            # NAVEGAÇÃO DE PÁGINAS
            nav_frame = tk.Frame(right_controls, bg=BG_PRIMARY)
            nav_frame.pack(side="left")
            
            tk.Button(nav_frame, text="⏮",
                      command=self.first_page,
                      bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if self.current_page > 1 else "disabled"
                      ).pack(side="left", padx=1)
            
            tk.Button(nav_frame, text="◀",
                      command=self.prev_page,
                      bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if self.current_page > 1 else "disabled"
                      ).pack(side="left", padx=1)
            
            tk.Label(nav_frame, 
                     text=f"Pág {self.current_page}/{self.total_pages}",
                     bg=BG_PRIMARY, fg=ACCENT_GOLD, font=("Arial", 10, "bold")
                     ).pack(side="left", padx=8)
            
            tk.Button(nav_frame, text="▶",
                      command=self.next_page,
                      bg="#444444", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if self.current_page < self.total_pages else "disabled"
                      ).pack(side="left", padx=1)
            
            tk.Button(nav_frame, text="⏭",
                      command=self.last_page,
                      bg="#333333", fg=FG_PRIMARY, font=("Arial", 9),
                      relief="flat", cursor="hand2", padx=6, pady=3,
                      state="normal" if self.current_page < self.total_pages else "disabled"
                      ).pack(side="left", padx=1)
        # ══════════════════════════════════════════════════════════════════
        
        tk.Label(self.scrollable_frame, 
                 text=f"{total_count} projeto(s) | Mostrando {len(page_items)} itens",
                 font=("Arial", 11), bg=BG_PRIMARY, fg="#999999"
                 ).grid(row=1, column=0, columnspan=COLS, sticky="w", padx=10, pady=(0, 15))
        
        if not all_filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\nClique em 'Importar Pastas' para adicionar.",
                     font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return
        
        # 4. RENDERIZA CARDS
        card_cb = {
            "on_open_modal":         self.open_project_modal,
            "on_toggle_favorite":    self.toggle_favorite,
            "on_toggle_done":        self.toggle_done,
            "on_toggle_good":        self.toggle_good,
            "on_toggle_bad":         self.toggle_bad,
            "on_analyze_single":     self.analyze_single_project,
            "on_open_folder":        open_folder,
            "on_set_category":       lambda c: self._add_filter_chip("category", c),
            "on_set_tag":            lambda t: self._add_filter_chip("tag", t),
            "on_set_origin":         lambda o: self._add_filter_chip("origin", o),
            "get_cover_image_async": self._get_thumbnail_async,
            "selection_mode":        self._selection_mode,
            "selected_paths":        self._selected_paths,
            "on_toggle_select":      self.toggle_card_selection,
        }
        
        for i, (project_path, project_data) in enumerate(page_items):
            row = (i // COLS) + 2
            col = i % COLS
            build_card(self.scrollable_frame, project_path, project_data, 
                      card_cb, row, col)
        
        self.content_canvas.yview_moveto(0)

    def _get_thumbnail_async(self, project_path, callback, widget):
        def _ui_safe_callback(path, photo):
            try:
                if widget and widget.winfo_exists():
                    self.root.after(0, lambda: callback(path, photo))
            except Exception as e:
                self.logger.debug(f"Widget destruído antes do callback: {e}")
        
        self.thumbnail_preloader.preload_single(project_path, _ui_safe_callback)

    def next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_projects()

    def prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.display_projects()

    def first_page(self) -> None:
        self.current_page = 1
        self.display_projects()

    def last_page(self) -> None:
        self.current_page = self.total_pages
        self.display_projects()

    # =========================================================================
    # FILTROS
    # =========================================================================

    def set_filter(self, filter_type: str) -> None:
        self.current_filter = filter_type
        self.current_categories = []; self.current_tag = None; self.current_origin = "all"
        self.search_var.set("")
        self.sidebar.set_active_btn(None)
        self.active_filters.clear()
        self._update_chips_bar()
        self.current_page = 1
        self.display_projects()

    def _on_search(self) -> None:
        self.search_query = self.search_var.get().strip().lower()
        self.current_page = 1
        self.display_projects()

    def _on_origin_filter(self, origin, btn=None) -> None:
        self.current_filter = "all"; self.current_origin = origin
        self.current_categories = []; self.current_tag = None
        self.current_page = 1
        self.active_filters.clear()
        self._add_filter_chip("origin", origin)
        self.sidebar.set_active_btn(btn)
        count = sum(1 for d in self.database.values() if d.get("origin") == origin)
        self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")

    def _on_category_filter(self, cats, btn=None) -> None:
        self.current_filter = "all"; self.current_categories = cats
        self.current_tag = None; self.current_origin = "all"
        self.current_page = 1
        self.active_filters.clear()
        for cat in cats:
            self._add_filter_chip("category", cat)
        self.sidebar.set_active_btn(btn)

    def _on_tag_filter(self, tag, btn=None) -> None:
        self.current_filter = "all"; self.current_tag = tag
        self.current_categories = []; self.current_origin = "all"
        self.current_page = 1
        self.active_filters.clear()
        self._add_filter_chip("tag", tag)
        self.sidebar.set_active_btn(btn)

    def set_origin_filter(self, origin, btn=None):  self._add_filter_chip("origin", origin)
    def set_category_filter(self, cats, btn=None):  
        for cat in (cats if isinstance(cats, list) else [cats]):
            self._add_filter_chip("category", cat)
    def set_tag_filter(self, tag, btn=None):         self._add_filter_chip("tag", tag)

    def get_filtered_projects(self) -> list:
        result = []
        for path, data in self.database.items():
            # Filtro base (favoritos, feitos, bons, ruins)
            ok = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done"     and data.get("done"))
                or (self.current_filter == "good"     and data.get("good"))
                or (self.current_filter == "bad"      and data.get("bad"))
            )
            if not ok: continue
            
            # F-07: Filtros empilháveis (modo AND)
            passes_all_filters = True
            for filt in self.active_filters:
                ftype = filt["type"]
                fval = filt["value"]
                
                if ftype == "category":
                    if fval not in data.get("categories", []):
                        passes_all_filters = False
                        break
                elif ftype == "tag":
                    if fval not in data.get("tags", []):
                        passes_all_filters = False
                        break
                elif ftype == "origin":
                    if data.get("origin") != fval:
                        passes_all_filters = False
                        break
                elif ftype == "analysis_ai":
                    if not (data.get("analyzed") and data.get("analysis_type") == "ai"):
                        passes_all_filters = False
                        break
                elif ftype == "analysis_fallback":
                    if not (data.get("analyzed") and data.get("analysis_type") == "fallback"):
                        passes_all_filters = False
                        break
                elif ftype == "analysis_pending":
                    if data.get("analyzed"):
                        passes_all_filters = False
                        break
            
            if not passes_all_filters:
                continue
            
            # Compat: Filtros legados (current_categories, current_tag, current_origin)
            if self.current_origin != "all" and data.get("origin") != self.current_origin: continue
            if self.current_categories and not any(
                    c in data.get("categories", []) for c in self.current_categories): continue
            if self.current_tag and self.current_tag not in data.get("tags", []): continue
            
            # HOT-14/HOT-15: Busca bilíngue (EN + PT-BR) — SEM OLLAMA!
            if self.search_query:
                name_en = data.get("name", "")
                # Usa tradutor estático: busca "espelho" encontra "Nursery Mirror"
                if not search_bilingual(self.search_query, name_en):
                    continue
            
            result.append(path)
        return result

    # =========================================================================
    # MODAIS
    # =========================================================================

    def open_project_modal(self, project_path: str) -> None:
        if self._selection_mode:
            self.toggle_card_selection(project_path); return
        ProjectModal(
            root=self.root, project_path=project_path,
            database=self.database,
            cb={
                "get_all_paths":    lambda: [p for p in self.database if os.path.isdir(p)],
                "on_navigate":      self.open_project_modal,
                "on_toggle":        self._modal_toggle,
                "on_generate_desc": self._modal_generate_desc,
                "on_open_edit":     self.open_edit_mode,
                "on_reanalize":     self.analyze_single_project,
                "on_set_tag":       lambda t: self._add_filter_chip("tag", t),
                "on_remove":        self.remove_project,
            },
            cache=self.thumbnail_preloader,
            scanner=self.scanner,
        ).open()

    def _modal_toggle(self, path, key, value) -> None:
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

    def open_edit_mode(self, project_path: str) -> None:
        EditModal(self.root, project_path, self.database.get(project_path, {}),
                  self._on_edit_save)

    def _on_edit_save(self, path, new_cats, new_tags) -> None:
        if path in self.database:
            if new_cats: self.database[path]["categories"] = new_cats
            self.database[path]["tags"]     = new_tags
            self.database[path]["analyzed"] = True
            self.db_manager.save_database()
            self.sidebar.refresh(self.database)
            self.display_projects()
            self.status_bar.config(text="✓ Projeto atualizado!")

    # =========================================================================
    # TOGGLES
    # =========================================================================

    def toggle_favorite(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            if btn: btn.config(text="⭐" if nv else "☆", fg=ACCENT_GOLD if nv else FG_TERTIARY)

    def toggle_done(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            if btn: btn.config(text="✓" if nv else "○", fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_good(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv: self.database[path]["bad"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#00FF00" if nv else FG_TERTIARY)

    def toggle_bad(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv: self.database[path]["good"] = False
            self.db_manager.save_database()
            if btn: btn.config(fg="#FF0000" if nv else FG_TERTIARY)

    # =========================================================================
    # IA
    # =========================================================================

    def _setup_analysis_callbacks(self) -> None:
        self.analysis_manager.on_start    = self.show_progress_ui
        self.analysis_manager.on_progress = self.update_progress
        self.analysis_manager.on_complete = self._on_analysis_complete
        self.analysis_manager.on_error    = self._on_analysis_error

    def _on_analysis_complete(self, done, skipped) -> None:
        self.hide_progress_ui(); self.sidebar.refresh(self.database)
        self.display_projects()
        msg = f"✅ Análise concluída: {done} projeto(s)"
        if skipped: msg += f" ({skipped} pulados)"
        self.status_bar.config(text=msg)

    def _on_analysis_error(self, error_msg) -> None:
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

    def analyze_single_project(self, path) -> None:
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

    def _batch_generate_descriptions(self, targets) -> None:
        self.show_progress_ui()
        def _run():
            done = skipped = 0
            for i, path in enumerate(targets, 1):
                if self.ollama.stop_flag: break
                if not os.path.isdir(path): skipped += 1; continue
                try:
                    self.update_progress(i, len(targets),
                        f"📝 Gerando descrição para {os.path.basename(path)}")
                    desc = self.text_generator.generate_description(path, self.database[path])
                    self.database[path]["ai_description"] = desc
                    done += 1
                    if done % 5 == 0: self.db_manager.save_database()
                except Exception as e:
                    self.logger.error("Erro desc %s: %s", path, e); skipped += 1
            self.db_manager.save_database(); self.hide_progress_ui()
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
        self.root.wait_window(PrepareFoldersDialog(self.root))

    def open_model_settings(self) -> None:
        self.root.wait_window(ModelSettingsDialog(self.root, self.db_manager))

    def open_categories_picker(self) -> None:
        all_cats: dict = {}
        for d in self.database.values():
            for c in d.get("categories", []):
                c = (c or "").strip()
                if c and c != "Sem Categoria": all_cats[c] = all_cats.get(c, 0) + 1
        cats_sorted = sorted(all_cats.items(), key=lambda x: x[1], reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Todas as Categorias"); win.configure(bg=BG_PRIMARY)
        win.geometry("400x600"); win.transient(self.root); win.grab_set()
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
        cv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/SCROLL_SPEED)), "units"))
        for cat, count in cats_sorted:
            b = tk.Button(inner, text=f"{cat} ({count})",
                          command=lambda c=cat: (self._add_filter_chip("category", c), win.destroy()),
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
        self.current_page = 1
        self.display_projects()
        self.status_bar.config(text="✅ Importação concluída!")
