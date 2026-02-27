"""Main window UI for Laserflix application."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import logging

logger = logging.getLogger("Laserflix.UI")


class MainWindow:
    """Main application window with header, navigation, and content area."""
    
    def __init__(self, root: tk.Tk, version: str):
        self.root = root
        self.version = version
        
        # UI State
        self.current_filter = "all"
        self.search_var = tk.StringVar()
        
        # Callbacks (to be set by app controller)
        self.on_filter_change: Optional[Callable[[str], None]] = None
        self.on_search_change: Optional[Callable[[str], None]] = None
        self.on_add_folders: Optional[Callable[[], None]] = None
        self.on_menu_action: Optional[Callable[[str], None]] = None
        
        # Setup window
        self.root.title(f"LASERFLIX {version}")
        self.root.state('zoomed')
        self.root.configure(bg="#141414")
        
        # Create UI components
        self._create_header()
        self._create_main_container()
        self._create_status_bar()
        
        # Bind search
        self.search_var.trace_add("write", lambda *args: self._on_search())
    
    def _create_header(self):
        """Create header with branding, navigation, and search."""
        header = tk.Frame(self.root, bg="#000000", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Logo
        tk.Label(header, text="LASERFLIX", font=("Arial", 28, "bold"),
                 bg="#000000", fg="#E50914").pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"v{self.version}", font=("Arial", 10),
                 bg="#000000", fg="#666666").pack(side="left", padx=5)
        
        # Navigation
        nav_frame = tk.Frame(header, bg="#000000")
        nav_frame.pack(side="left", padx=30)
        
        nav_items = [
            ("🏠 Home", "all"),
            ("⭐ Favoritos", "favorite"),
            ("✓ Já Feitos", "done"),
            ("👍 Bons", "good"),
            ("👎 Ruins", "bad"),
        ]
        
        for text, filter_type in nav_items:
            btn = tk.Button(nav_frame, text=text, 
                          command=lambda f=filter_type: self._set_filter(f),
                          bg="#000000", fg="#FFFFFF", font=("Arial", 12),
                          relief="flat", cursor="hand2", padx=10)
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e, w=btn: w.config(fg="#E50914"))
            btn.bind("<Leave>", lambda e, w=btn: w.config(fg="#FFFFFF"))
        
        # Search
        search_frame = tk.Frame(header, bg="#000000")
        search_frame.pack(side="right", padx=20)
        tk.Label(search_frame, text="🔍", bg="#000000", fg="#FFFFFF", 
                font=("Arial", 16)).pack(side="left", padx=5)
        tk.Entry(search_frame, textvariable=self.search_var, 
                bg="#333333", fg="#FFFFFF", font=("Arial", 12), width=30,
                relief="flat", insertbackground="#FFFFFF"
                ).pack(side="left", padx=5, ipady=5)
        
        # Extras (Menu + Add Folders + Analyze)
        extras_frame = tk.Frame(header, bg="#000000")
        extras_frame.pack(side="right", padx=10)
        
        # Main menu
        menu_btn = tk.Menubutton(extras_frame, text="⚙️ Menu", 
                                bg="#1DB954", fg="#FFFFFF",
                                font=("Arial", 11, "bold"), relief="flat", 
                                cursor="hand2", padx=15, pady=8)
        menu_btn.pack(side="left", padx=5)
        menu = tk.Menu(menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF")
        menu_btn["menu"] = menu
        menu.add_command(label="📊 Dashboard", command=lambda: self._menu_action("dashboard"))
        menu.add_command(label="📝 Edição em Lote", command=lambda: self._menu_action("batch_edit"))
        menu.add_separator()
        menu.add_command(label="🤖 Configurar Modelos IA", command=lambda: self._menu_action("model_settings"))
        menu.add_separator()
        menu.add_command(label="💾 Exportar Banco", command=lambda: self._menu_action("export_db"))
        menu.add_command(label="📥 Importar Banco", command=lambda: self._menu_action("import_db"))
        menu.add_command(label="🔄 Backup Manual", command=lambda: self._menu_action("manual_backup"))
        
        # Add folders button
        tk.Button(extras_frame, text="➕ Pastas", 
                 command=self._add_folders_clicked,
                 bg="#E50914", fg="#FFFFFF", font=("Arial", 11, "bold"),
                 relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
        
        # Analyze menu
        ai_menu_btn = tk.Menubutton(extras_frame, text="🤖 Analisar", 
                                   bg="#1DB954", fg="#FFFFFF",
                                   font=("Arial", 11, "bold"), relief="flat", 
                                   cursor="hand2", padx=15, pady=8)
        ai_menu_btn.pack(side="left", padx=5)
        ai_menu = tk.Menu(ai_menu_btn, tearoff=0, bg="#2A2A2A", fg="#FFFFFF",
                         font=("Arial", 10), activebackground="#E50914", 
                         activeforeground="#FFFFFF")
        ai_menu_btn["menu"] = ai_menu
        ai_menu.add_command(label="🆕 Analisar apenas novos", command=lambda: self._menu_action("analyze_new"))
        ai_menu.add_command(label="🔄 Reanalisar todos", command=lambda: self._menu_action("analyze_all"))
        ai_menu.add_command(label="📊 Analisar filtro atual", command=lambda: self._menu_action("analyze_filter"))
        ai_menu.add_separator()
        ai_menu.add_command(label="🎯 Reanalisar categoria específica", command=lambda: self._menu_action("analyze_category"))
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Gerar descrições para novos", command=lambda: self._menu_action("describe_new"))
        ai_menu.add_command(label="📝 Gerar descrições para todos", command=lambda: self._menu_action("describe_all"))
        ai_menu.add_command(label="📝 Gerar descrições do filtro atual", command=lambda: self._menu_action("describe_filter"))
    
    def _create_main_container(self):
        """Create main content container."""
        self.main_container = tk.Frame(self.root, bg="#141414")
        self.main_container.pack(fill="both", expand=True)
    
    def _create_status_bar(self):
        """Create status bar with progress indicator."""
        self.status_frame = tk.Frame(self.root, bg="#000000", height=50)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        self.status_bar = tk.Label(self.status_frame, text="Pronto", 
                                   bg="#000000", fg="#FFFFFF", 
                                   font=("Arial", 10), anchor="w")
        self.status_bar.pack(side="left", padx=10, fill="both", expand=True)
        
        # Progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor="#2A2A2A", background="#1DB954",
                       bordercolor="#000000", lightcolor="#1DB954", 
                       darkcolor="#1DB954")
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode="determinate",
                                           length=300, style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.pack_forget()
        
        # Stop button
        self.stop_button = tk.Button(self.status_frame, text="⏹ Parar Análise",
                                     bg="#E50914", fg="#FFFFFF", 
                                     font=("Arial", 10, "bold"),
                                     relief="flat", cursor="hand2", 
                                     padx=15, pady=8)
        self.stop_button.pack(side="right", padx=10)
        self.stop_button.pack_forget()
    
    def _set_filter(self, filter_type: str):
        """Handle filter change."""
        self.current_filter = filter_type
        if self.on_filter_change:
            self.on_filter_change(filter_type)
    
    def _on_search(self):
        """Handle search input."""
        query = self.search_var.get().strip().lower()
        if self.on_search_change:
            self.on_search_change(query)
    
    def _add_folders_clicked(self):
        """Handle add folders button click."""
        if self.on_add_folders:
            self.on_add_folders()
    
    def _menu_action(self, action: str):
        """Handle menu action."""
        if self.on_menu_action:
            self.on_menu_action(action)
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_bar.config(text=message)
    
    def show_progress(self, current: int, total: int, message: str = ""):
        """Show progress bar with current status."""
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_bar["value"] = percentage
        self.status_bar.config(text=f"{message} ({current}/{total} — {percentage:.1f}%)")
        self.root.update_idletasks()
    
    def show_progress_ui(self):
        """Show progress bar and stop button."""
        self.progress_bar.pack(side="left", padx=10)
        self.stop_button.pack(side="right", padx=10)
        self.progress_bar["value"] = 0
    
    def hide_progress_ui(self):
        """Hide progress bar and stop button."""
        self.progress_bar.pack_forget()
        self.stop_button.pack_forget()
    
    def get_main_container(self) -> tk.Frame:
        """Get main container for adding content."""
        return self.main_container
    
    def clear_search(self):
        """Clear search box."""
        self.search_var.set("")
