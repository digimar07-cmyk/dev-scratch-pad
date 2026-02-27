"""Project grid UI component."""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger("Laserflix.UI.Grid")


class ProjectGrid:
    """Grid display for project cards."""
    
    def __init__(self, parent: tk.Frame):
        self.parent = parent
        
        # Callbacks
        self.on_card_click: Optional[Callable[[str], None]] = None
        self.on_category_click: Optional[Callable[[str], None]] = None
        self.on_tag_click: Optional[Callable[[str], None]] = None
        self.on_origin_click: Optional[Callable[[str], None]] = None
        self.on_open_folder: Optional[Callable[[str], None]] = None
        self.on_toggle_favorite: Optional[Callable[[str, tk.Button], None]] = None
        self.on_toggle_done: Optional[Callable[[str, tk.Button], None]] = None
        self.on_toggle_good: Optional[Callable[[str, tk.Button], None]] = None
        self.on_toggle_bad: Optional[Callable[[str, tk.Button], None]] = None
        self.on_analyze_project: Optional[Callable[[str], None]] = None
        self.get_thumbnail: Optional[Callable[[str], Any]] = None
        
        # Create grid container
        self._create_container()
    
    def _create_container(self):
        """Create scrollable container for grid."""
        content_frame = tk.Frame(self.parent, bg="#141414")
        content_frame.pack(side="left", fill="both", expand=True)
        
        self.content_canvas = tk.Canvas(content_frame, bg="#141414", highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                         command=self.content_canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.content_canvas, bg="#141414")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        
        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=content_scrollbar.set)
        self.content_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        content_scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scroll
        def on_mousewheel(event):
            self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.content_canvas.bind("<Enter>", lambda e: self.content_canvas.bind("<MouseWheel>", on_mousewheel))
        self.content_canvas.bind("<Leave>", lambda e: self.content_canvas.unbind("<MouseWheel>"))
    
    def display_projects(self, projects: List[tuple], title: str = "Todos os Projetos"):
        """Display projects in grid layout.
        
        Args:
            projects: List of (path, data_dict) tuples
            title: Grid title
        """
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(self.scrollable_frame, text=title, font=("Arial", 20, "bold"),
                bg="#141414", fg="#FFFFFF", anchor="w").grid(
                    row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 20))
        
        # Count
        tk.Label(self.scrollable_frame, text=f"{len(projects)} projeto(s)", 
                font=("Arial", 12), bg="#141414", fg="#999999").grid(
                    row=1, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 10))
        
        # Grid of cards
        row, col = 2, 0
        for project_path, data in projects:
            self._create_card(project_path, data, row, col)
            col += 1
            if col >= 5:
                col = 0
                row += 1
    
    def _create_card(self, project_path: str, data: Dict[str, Any], row: int, col: int):
        """Create a single project card."""
        card = tk.Frame(self.scrollable_frame, bg="#2A2A2A", width=220, height=420)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)
        
        # Cover image
        cover_frame = tk.Frame(card, bg="#1A1A1A", width=220, height=200)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)
        cover_frame.bind("<Button-1>", lambda e: self._on_card_click(project_path))
        
        if self.get_thumbnail:
            cover_image = self.get_thumbnail(project_path)
            if cover_image:
                lbl = tk.Label(cover_frame, image=cover_image, bg="#1A1A1A", cursor="hand2")
                lbl.image = cover_image  # Keep reference
                lbl.pack(expand=True)
                lbl.bind("<Button-1>", lambda e: self._on_card_click(project_path))
            else:
                self._create_placeholder(cover_frame, project_path)
        else:
            self._create_placeholder(cover_frame, project_path)
        
        # Info section
        info_frame = tk.Frame(card, bg="#2A2A2A")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Project name
        name = data.get("name", "Sem nome")
        if len(name) > 30:
            name = name[:27] + "..."
        
        name_lbl = tk.Label(info_frame, text=name, font=("Arial", 11, "bold"),
                           bg="#2A2A2A", fg="#FFFFFF", wraplength=200, 
                           justify="left", cursor="hand2")
        name_lbl.pack(anchor="w")
        name_lbl.bind("<Button-1>", lambda e: self._on_card_click(project_path))
        
        # Categories
        categories = data.get("categories", [])
        if categories:
            cats_display = tk.Frame(info_frame, bg="#2A2A2A")
            cats_display.pack(anchor="w", pady=(5, 0), fill="x")
            
            colors = ["#FF6B6B", "#4ECDC4", "#95E1D3"]
            for i, cat in enumerate(categories[:3]):
                color = colors[i] if i < 3 else "#9B59B6"
                btn = tk.Button(cats_display, text=cat[:12],
                              bg=color, fg="#000000", font=("Arial", 8, "bold"),
                              relief="flat", cursor="hand2", padx=6, pady=3)
                btn.config(command=lambda c=cat: self._on_category_click(c))
                btn.pack(side="left", padx=2, pady=2)
                
                orig_color = color
                btn.bind("<Enter>", lambda e, b=btn, c=orig_color: b.config(bg=self._darken_color(c)))
                btn.bind("<Leave>", lambda e, b=btn, c=orig_color: b.config(bg=c))
        
        # Tags
        tags = data.get("tags", [])
        if tags:
            tags_container = tk.Frame(info_frame, bg="#2A2A2A")
            tags_container.pack(anchor="w", pady=(5, 0), fill="x")
            
            for tag in tags[:3]:
                display = (tag[:10] + "...") if len(tag) > 12 else tag
                btn = tk.Button(tags_container, text=display,
                              bg="#3A3A3A", fg="#FFFFFF", font=("Arial", 8),
                              relief="flat", cursor="hand2", padx=6, pady=2)
                btn.config(command=lambda t=tag: self._on_tag_click(t))
                btn.pack(side="left", padx=2, pady=2)
                btn.bind("<Enter>", lambda e, w=btn: w.config(bg="#E50914"))
                btn.bind("<Leave>", lambda e, w=btn: w.config(bg="#3A3A3A"))
        
        # Origin badge
        origin = data.get("origin", "Desconhecido")
        colors = {"Creative Fabrica": "#FF6B35", "Etsy": "#F7931E", "Diversos": "#4ECDC4"}
        origin_btn = tk.Button(info_frame, text=origin, font=("Arial", 8),
                             bg=colors.get(origin, "#9B59B6"), fg="#FFFFFF",
                             padx=5, pady=2, relief="flat", cursor="hand2")
        origin_btn.config(command=lambda o=origin: self._on_origin_click(o))
        origin_btn.pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        actions_frame = tk.Frame(info_frame, bg="#2A2A2A")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Folder button
        tk.Button(actions_frame, text="📂", font=("Arial", 14),
                 command=lambda: self._on_open_folder(project_path),
                 bg="#2A2A2A", fg="#FFD700", relief="flat", 
                 cursor="hand2", activebackground="#3A3A3A").pack(side="left", padx=2)
        
        # Favorite button
        btn_fav = tk.Button(actions_frame, font=("Arial", 14), 
                           bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_fav.config(
            text="⭐" if data.get("favorite") else "☆",
            fg="#FFD700" if data.get("favorite") else "#666666",
            command=lambda b=btn_fav: self._on_toggle_favorite(project_path, b)
        )
        btn_fav.pack(side="left", padx=2)
        
        # Done button
        btn_done = tk.Button(actions_frame, font=("Arial", 14), 
                            bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_done.config(
            text="✓" if data.get("done") else "○",
            fg="#00FF00" if data.get("done") else "#666666",
            command=lambda b=btn_done: self._on_toggle_done(project_path, b)
        )
        btn_done.pack(side="left", padx=2)
        
        # Good button
        btn_good = tk.Button(actions_frame, text="👍", font=("Arial", 14),
                            bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_good.config(
            fg="#00FF00" if data.get("good") else "#666666",
            command=lambda b=btn_good: self._on_toggle_good(project_path, b)
        )
        btn_good.pack(side="left", padx=2)
        
        # Bad button
        btn_bad = tk.Button(actions_frame, text="👎", font=("Arial", 14),
                           bg="#2A2A2A", relief="flat", cursor="hand2")
        btn_bad.config(
            fg="#FF0000" if data.get("bad") else "#666666",
            command=lambda b=btn_bad: self._on_toggle_bad(project_path, b)
        )
        btn_bad.pack(side="left", padx=2)
        
        # Analyze button (if not analyzed)
        if not data.get("analyzed"):
            tk.Button(actions_frame, text="🤖", font=("Arial", 14),
                     command=lambda: self._on_analyze_project(project_path),
                     bg="#2A2A2A", fg="#1DB954", relief="flat", 
                     cursor="hand2").pack(side="left", padx=2)
    
    def _create_placeholder(self, frame: tk.Frame, project_path: str):
        """Create placeholder for missing thumbnail."""
        ph = tk.Label(frame, text="📁", font=("Arial", 60), 
                     bg="#1A1A1A", fg="#666666", cursor="hand2")
        ph.pack(expand=True)
        ph.bind("<Button-1>", lambda e: self._on_card_click(project_path))
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"
    
    def _on_card_click(self, project_path: str):
        if self.on_card_click:
            self.on_card_click(project_path)
    
    def _on_category_click(self, category: str):
        if self.on_category_click:
            self.on_category_click(category)
    
    def _on_tag_click(self, tag: str):
        if self.on_tag_click:
            self.on_tag_click(tag)
    
    def _on_origin_click(self, origin: str):
        if self.on_origin_click:
            self.on_origin_click(origin)
    
    def _on_open_folder(self, project_path: str):
        if self.on_open_folder:
            self.on_open_folder(project_path)
    
    def _on_toggle_favorite(self, project_path: str, btn: tk.Button):
        if self.on_toggle_favorite:
            self.on_toggle_favorite(project_path, btn)
    
    def _on_toggle_done(self, project_path: str, btn: tk.Button):
        if self.on_toggle_done:
            self.on_toggle_done(project_path, btn)
    
    def _on_toggle_good(self, project_path: str, btn: tk.Button):
        if self.on_toggle_good:
            self.on_toggle_good(project_path, btn)
    
    def _on_toggle_bad(self, project_path: str, btn: tk.Button):
        if self.on_toggle_bad:
            self.on_toggle_bad(project_path, btn)
    
    def _on_analyze_project(self, project_path: str):
        if self.on_analyze_project:
            self.on_analyze_project(project_path)
