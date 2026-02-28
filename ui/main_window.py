"""Janela principal da aplicação."""
import tkinter as tk
from tkinter import ttk
from ui.sidebar import create_sidebar
from ui.dashboard import open_dashboard, open_batch_edit
from ui.model_settings import open_model_settings
from ui.progress_ui import stop_analysis_process
from batch.batch_analyzer import analyze_only_new, reanalyze_all, analyze_current_filter, reanalyze_specific_category
from batch.batch_description import generate_descriptions_for_new, generate_descriptions_for_all, generate_descriptions_for_filter
from actions.scanning import add_folders
from data.persistence import export_database, import_database, manual_backup


def create_ui(app):
    # Header
    header = tk.Frame(app.root, bg="#000000", height=70)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)
    tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"),
             bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
    from core.config import VERSION
    tk.Label(header, text=f"v{VERSION}", font=("Arial", 10),
             bg="#000000", fg="#666666").pack(side="left", padx=5)
    
    # Nav
    nav_frame = tk.Frame(header, bg="#000000")
    nav_frame.pack(side="left", padx=30)
    for text, filter_type in [("🏠 Home","all"),("⭐ Favoritos","favorite"),
                               ("✓ Já Feitos","done"),("👍 Bons","good"),("👎 Ruins","bad")]:
        btn = tk.Button(nav_frame, text=text, command=lambda f=filter_type: set_filter(app, f),
                        bg="#000000", fg="#FFFFFF", font=("Arial", 12),
                        relief="flat", cursor="hand2", padx=10)
        btn.pack(side="left", padx=5)
        btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
        btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))
    
    # Search
    search_frame = tk.Frame(header, bg="#000000")
    search_frame.pack(side="right", padx=20)
    tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF", font=("Arial", 16)).pack(side="left", padx=5)
    app.search_var = tk.StringVar()
    app.search_var.trace_add("write", lambda *args: on_search(app))
    tk.Entry(search_frame, textvariable=app.search_var, bg="#333333", fg="#FFFFFF",
             font=("Arial", 12), width=30, relief="flat", insertbackground="#FFFFFF"
             ).pack(side="left", padx=5, ipady=5)
    
    # Menus
    extras_frame = tk.Frame(header, bg="#000000")
    extras_frame.pack(side="right", padx=10)
    
    # Menu principal
    menu_btn = tk.Menubutton(extras_frame, text="⚙️ Menu", bg="#1DB954", fg="#FFFFFF",
                             font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
    menu_btn.pack(side="left", padx=5)
    menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
    menu_btn["menu"] = menu
    menu.add_command(label="📊 Dashboard", command=lambda: open_dashboard(app))
    menu.add_command(label="📝 Edição em Lote", command=lambda: open_batch_edit(app))
    menu.add_separator()
    menu.add_command(label="🤖 Configurar Modelos IA", command=lambda: open_model_settings(app))
    menu.add_separator()
    menu.add_command(label="💾 Exportar Banco", command=lambda: export_database(app))
    menu.add_command(label="📥 Importar Banco", command=lambda: import_database(app))
    menu.add_command(label="🔄 Backup Manual", command=lambda: manual_backup(app))
    
    # Botão pastas
    tk.Button(extras_frame, text="➕ Pastas", command=lambda: add_folders(app),
              bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
              relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
    
    # Menu analisar
    ai_menu_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", bg="#1DB954", fg="#FFFFFF",
                                font=("Arial", 11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8)
    ai_menu_btn.pack(side="left", padx=5)
    ai_menu = tk.Menu(ai_menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                      font=("Arial", 10), activebackground="#E50914", activeforeground="#FFFFFF")
    ai_menu_btn["menu"] = ai_menu
    ai_menu.add_command(label="🆕 Analisar apenas novos", command=lambda: analyze_only_new(app))
    ai_menu.add_command(label="🔄 Reanalisar todos", command=lambda: reanalyze_all(app))
    ai_menu.add_command(label="📊 Analisar filtro atual", command=lambda: analyze_current_filter(app))
    ai_menu.add_separator()
    ai_menu.add_command(label="🎯 Reanalisar categoria específica", command=lambda: reanalyze_specific_category(app))
    ai_menu.add_separator()
    ai_menu.add_command(label="📝 Gerar descrições para novos", command=lambda: generate_descriptions_for_new(app))
    ai_menu.add_command(label="📝 Gerar descrições para todos", command=lambda: generate_descriptions_for_all(app))
    ai_menu.add_command(label="📝 Gerar descrições do filtro atual", command=lambda: generate_descriptions_for_filter(app))
    
    # Área de conteúdo
    main_container = tk.Frame(app.root, bg="#141414")
    main_container.pack(fill="both", expand=True)
    create_sidebar(app, main_container)
    
    content_frame = tk.Frame(main_container, bg="#141414")
    content_frame.pack(side="left", fill="both", expand=True)
    app.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
    content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=app.content_canvas.yview)
    app.scrollable_frame = tk.Frame(app.content_canvas, bg="#141414")
    app.scrollable_frame.bind("<Configure>",
        lambda e: app.content_canvas.configure(scrollregion=app.content_canvas.bbox("all")))
    app.content_canvas.create_window((0, 0), window=app.scrollable_frame, anchor="nw")
    app.content_canvas.configure(yscrollcommand=content_scrollbar.set)
    app.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    content_scrollbar.pack(side="right", fill="y")
    
    def _on_mw(event): app.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    app.content_canvas.bind("<Enter>", lambda e: app.content_canvas.bind("<MouseWheel>", _on_mw))
    app.content_canvas.bind("<Leave>", lambda e: app.content_canvas.unbind("<MouseWheel>"))
    
    # Status bar
    app.status_frame = tk.Frame(app.root, bg="#000000", height=50)
    app.status_frame.pack(side="bottom", fill="x")
    app.status_frame.pack_propagate(False)
    app.status_bar = tk.Label(app.status_frame, text="Pronto", bg="#000000",
                               fg="#FFFFFF", font=("Arial", 10), anchor="w")
    app.status_bar.pack(side="left", padx=10, fill="both", expand=True)
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Horizontal.TProgressbar",
                    troughcolor="#2A2A2A", background="#1DB954",
                    bordercolor="#000000", lightcolor="#1DB954", darkcolor="#1DB954")
    app.progress_bar = ttk.Progressbar(app.status_frame, mode="determinate",
                                        length=300, style="Custom.Horizontal.TProgressbar")
    app.progress_bar.pack(side="left", padx=10)
    app.progress_bar.pack_forget()
    
    app.stop_button = tk.Button(app.status_frame, text="⏹ Parar Análise",
                                 command=lambda: stop_analysis_process(app),
                                 bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"),
                                 relief="flat", cursor="hand2", padx=15, pady=8)
    app.stop_button.pack(side="right", padx=10)
    app.stop_button.pack_forget()


def set_filter(app, filter_type):
    app.current_filter = filter_type
    app.current_categories = []
    app.current_tag = None
    app.current_origin = "all"
    app.search_var.set("")
    from ui.sidebar import _set_active_sidebar_btn
    _set_active_sidebar_btn(app, None)
    from ui.project_grid import display_projects
    display_projects(app)


def on_search(app):
    app.search_query = app.search_var.get().strip().lower()
    from ui.project_grid import display_projects
    display_projects(app)
