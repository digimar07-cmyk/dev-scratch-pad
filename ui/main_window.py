"""
LASERFLIX — UI Principal (Main Window)
Interface Netflix-style: sidebar + grid de projetos + header + status bar
"""

import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Gerencia a janela principal e grid de projetos"""

    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.db = app.database
        self.filter = app.filter
        self.search_var = tk.StringVar()
        self._active_sidebar_btn = None

    def create_ui(self):
        """Monta estrutura: header + main (sidebar + content) + status bar"""
        self._create_header()
        self._create_main_area()
        self._create_status_bar()

    def _create_header(self):
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"), bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"v{self.app.version}", font=("Arial", 10), bg="#000000", fg="#666666").pack(side="left", padx=5)
        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        for text, ftype in [("🏠 Home", "all"), ("⭐ Favoritos", "favorite"), ("✓ Já Feitos", "done"), ("👍 Bons", "good"), ("👎 Ruins", "bad")]:
            btn = tk.Button(nav_frame, text=text, command=lambda f=ftype: self.set_filter(f), bg="#000000", fg="#FFFFFF", font=("Arial", 12), relief="flat", cursor="hand2", padx=10)
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))
        search_frame = tk.Frame(header, bg="#000000")
        search_frame.pack(side="right", padx=20)
        tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF", font=("Arial", 16)).pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *a: self.on_search())
        tk.Entry(search_frame, textvariable=self.search_var, bg="#333333", fg="#FFFFFF", font=("Arial", 12), width=30, relief="flat", insertbackground="#FFFFFF").pack(side="left", padx=5, ipady=5)
        extras_frame = tk.Frame(header, bg="#000000")
        extras_frame.pack(side="right", padx=10)
        menu_btn = tk.Menubutton(extras_frame, text="⚙️ Menu", bg="#1DB954", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📊 Dashboard", command=self.app.open_dashboard)
        menu.add_command(label="📝 Edição em Lote", command=self.app.open_batch_edit)
        menu.add_separator()
        menu.add_command(label="🤖 Configurar Modelos IA", command=self.app.ollama.open_model_settings)
        menu.add_separator()
        menu.add_command(label="💾 Exportar Banco", command=self.app.export_database)
        menu.add_command(label="📥 Importar Banco", command=self.app.import_database)
        menu.add_command(label="🔄 Backup Manual", command=self.app.backup.manual_backup)
        tk.Button(extras_frame, text="➕ Pastas", command=self.app.add_folders, bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
        ai_menu_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", bg="#1DB954", fg="#FFFFFF", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
        ai_menu_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF", font=("Arial", 10), activebackground="#E50914", activeforeground="#FFFFFF")
        ai_menu_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos", command=self.app.analyze_only_new)
        ai_menu.add_command(label="🔄 Reanalisar todos", command=self.app.reanalyze_all)
        ai_menu.add_command(label="📊 Analisar filtro atual", command=self.app.analyze_current_filter)
        ai_menu.add_separator()
        ai_menu.add_command(label="🎯 Reanalisar categoria específica", command=self.app.reanalyze_specific_category)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições para novos", command=self.app.generate_descriptions_for_new)
        ai_menu.add_command(label="📝 Gerar descrições para todos", command=self.app.generate_descriptions_for_all)
        ai_menu.add_command(label="📝 Gerar descrições do filtro atual", command=self.app.generate_descriptions_for_filter)

    def _create_main_area(self):
        main_container = tk.Frame(self.root, bg="#141414")
        main_container.pack(fill="both", expand=True)
        self._create_sidebar(main_container)
        self._create_content_area(main_container)

    def _create_sidebar(self, parent):
        sidebar_container = tk.Frame(parent, bg="#1A1A1A", width=250)
        sidebar_container.pack(side="left", fill="both")
        sidebar_container.pack_propagate(False)
        self.sidebar_canvas = tk.Canvas(sidebar_container, bg="#1A1A1A", highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind("<Configure>", lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        self.sidebar_canvas.bind("<MouseWheel>", lambda e: self.sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        for title, attr in [("🌐 Origem", "origins_frame"), ("📂 Categorias", "categories_frame"), ("🏷️ Tags Populares", "tags_frame")]:
            tk.Label(self.sidebar_content, text=title, font=("Arial", 14, "bold"), bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
            frame = tk.Frame(self.sidebar_content, bg="#1A1A1A")
            frame.pack(fill="x", padx=10, pady=5)
            setattr(self, attr, frame)
            tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)
        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")

    def _create_content_area(self, parent):
        content_frame = tk.Frame(parent, bg="#141414")
        content_frame.pack(side="left", fill="both", expand=True)
        self.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg="#141414")
        self.scrollable_frame.bind("<Configure>", lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")))
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_scrollbar.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        content_scrollbar.pack(side="right", fill="y")
        def _on_mw(event):
            self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", _on_mw))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))

    def _create_status_bar(self):
        self.status_frame = tk.Frame(self.root, bg="#000000", height=50)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        self.status_bar = tk.Label(self.status_frame, text="Pronto", bg="#000000", fg="#FFFFFF", font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="#2A2A2A", background="#1DB954", bordercolor="#000000", lightcolor="#1DB954", darkcolor="#1DB954")
        self.progress_bar = ttk.Progressbar(self.status_frame, mode="determinate", length=300, style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.pack_forget()
        self.stop_button = tk.Button(self.status_frame, text="⏹ Parar Análise", command=self.stop_analysis_process, bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
        self.stop_button.pack(side="right", padx=10)
        self.stop_button.pack_forget()

    def update_progress(self, current, total, message=""):
        percentage = (current / total) * 100
        self.progress_bar["value"] = percentage
        self.status_bar.config(text=f"{message} ({current}/{total} — {percentage:.1f}%)")
        self.root.update_idletasks()

    def show_progress_ui(self):
        self.progress_bar.pack(side="left", padx=10)
        self.stop_button.pack(side="right", padx=10)
        self.progress_bar["value"] = 0

    def hide_progress_ui(self):
        self.progress_bar.pack_forget()
        self.stop_button.pack_forget()

    def stop_analysis_process(self):
        self.app.stop_analysis = True
        self.status_bar.config(text="⏹ Parando análise...")

    def set_filter(self, filter_type):
        self.filter.current = filter_type
        self.filter.categories = []
        self.filter.tag = None
        self.filter.origin = "all"
        self.search_var.set("")
        self._set_active_sidebar_btn(None)
        self.display_projects()

    def on_search(self):
        self.filter.query = self.search_var.get().strip().lower()
        self.display_projects()

    def update_sidebar(self):
        from ui.sidebar import SidebarManager
        SidebarManager(self).update_all()

    def _set_active_sidebar_btn(self, btn):
        try:
            if self._active_sidebar_btn:
                self._active_sidebar_btn.config(bg="#1A1A1A")
        except:
            pass
        self._active_sidebar_btn = btn
        try:
            if btn:
                btn.config(bg="#E50914")
        except:
            pass

    def display_projects(self):
        from ui.project_card import ProjectCard
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        title_text = "Todos os Projetos"
        if self.filter.current == "favorite":
            title_text = "⭐ Favoritos"
        elif self.filter.current == "done":
            title_text = "✓ Já Feitos"
        elif self.filter.current == "good":
            title_text = "👍 Bons"
        elif self.filter.current == "bad":
            title_text = "👎 Ruins"
        if self.filter.origin != "all":
            title_text += f" — 🌐 {self.filter.origin}"
        if self.filter.categories:
            title_text += f" — {', '.join(self.filter.categories)}"
        if self.filter.tag:
            title_text += f" — 🏷️ {self.filter.tag}"
        if self.filter.query:
            title_text += f' ("{self.filter.query}")'
        tk.Label(self.scrollable_frame, text=title_text, font=("Arial", 20, "bold"), bg="#141414", fg="#FFFFFF", anchor="w").grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 20))
        filtered = [(p, self.db.data[p]) for p in self.filter.get_filtered_projects() if p in self.db.data]
        tk.Label(self.scrollable_frame, text=f"{len(filtered)} projeto(s)", font=("Arial", 12), bg="#141414", fg="#999999").grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 10))
        row, col = 2, 0
        for project_path, data in filtered:
            ProjectCard(self.app).create(project_path, data, self.scrollable_frame, row, col)
            col += 1
            if col >= 5:
                col = 0
                row += 1
