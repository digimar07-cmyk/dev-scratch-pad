"""Sidebar UI component with filters."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple, Optional, Callable
import logging

logger = logging.getLogger("Laserflix.UI.Sidebar")


class Sidebar:
    """Sidebar with origin, category, and tag filters."""
    
    def __init__(self, parent: tk.Frame):
        self.parent = parent
        
        # Callbacks
        self.on_origin_filter: Optional[Callable[[str], None]] = None
        self.on_category_filter: Optional[Callable[[List[str]], None]] = None
        self.on_tag_filter: Optional[Callable[[str], None]] = None
        self.on_show_all_categories: Optional[Callable[[], None]] = None
        
        # Active button tracking
        self._active_btn: Optional[tk.Button] = None
        
        # Create sidebar
        self._create_sidebar()
    
    def _create_sidebar(self):
        """Create sidebar container with scrollable content."""
        sidebar_container = tk.Frame(self.parent, bg="#1A1A1A", width=250)
        sidebar_container.pack(side="left", fill="both")
        sidebar_container.pack_propagate(False)
        
        self.sidebar_canvas = tk.Canvas(sidebar_container, bg="#1A1A1A", 
                                        highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", 
                                         command=self.sidebar_canvas.yview)
        
        self.sidebar_content = tk.Frame(self.sidebar_canvas, bg="#1A1A1A")
        self.sidebar_content.bind(
            "<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        )
        
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_content, 
                                         anchor="nw", width=230)
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scroll
        self.sidebar_canvas.bind(
            "<MouseWheel>",
            lambda e: self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        )
        
        # Create sections
        self.origins_frame = self._create_section("🌐 Origem")
        self.categories_frame = self._create_section("📂 Categorias")
        self.tags_frame = self._create_section("🏷️ Tags Populares")
        
        # Bottom padding
        tk.Frame(self.sidebar_content, bg="#1A1A1A", height=50).pack(fill="x")
    
    def _create_section(self, title: str) -> tk.Frame:
        """Create a section with title and content frame."""
        tk.Label(self.sidebar_content, text=title, font=("Arial", 14, "bold"),
                bg="#1A1A1A", fg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        
        frame = tk.Frame(self.sidebar_content, bg="#1A1A1A")
        frame.pack(fill="x", padx=10, pady=5)
        
        # Separator
        tk.Frame(self.sidebar_content, bg="#333333", height=2).pack(fill="x", padx=10, pady=10)
        
        return frame
    
    def update_origins(self, origins: Dict[str, int]):
        """Update origins list with counts."""
        for w in self.origins_frame.winfo_children():
            w.destroy()
        
        colors = {
            "Creative Fabrica": "#FF6B35",
            "Etsy": "#F7931E",
            "Diversos": "#4ECDC4"
        }
        
        for origin in sorted(origins):
            count = origins[origin]
            color = colors.get(origin, "#9B59B6")
            
            btn = tk.Button(self.origins_frame, text=f"{origin} ({count})",
                          bg="#1A1A1A", fg=color, font=("Arial", 10, "bold"),
                          relief="flat", cursor="hand2", anchor="w", 
                          padx=15, pady=8)
            btn.config(command=lambda o=origin, b=btn: self._on_origin_click(o, b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
        
        self._bind_scroll_recursive(self.origins_frame)
    
    def update_categories(self, categories: List[Tuple[str, int]], show_more_count: int = 0):
        """Update categories list with top 8 + show more button."""
        for w in self.categories_frame.winfo_children():
            w.destroy()
        
        if not categories:
            tk.Label(self.categories_frame, text="Nenhuma categoria", 
                    bg="#1A1A1A", fg="#666666",
                    font=("Arial", 10, "italic"), anchor="w", 
                    padx=15, pady=10).pack(fill="x")
            return
        
        # Top 8 categories
        for cat, count in categories[:8]:
            btn = tk.Button(self.categories_frame, text=f"{cat} ({count})",
                          bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10),
                          relief="flat", cursor="hand2", anchor="w", 
                          padx=15, pady=8)
            btn.config(command=lambda c=cat, b=btn: self._on_category_click([c], b))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
        
        # Show more button
        if show_more_count > 0:
            more_btn = tk.Button(self.categories_frame, text=f"+ Ver mais ({show_more_count})",
                               bg="#2A2A2A", fg="#888888", font=("Arial", 9),
                               relief="flat", cursor="hand2", anchor="w", 
                               padx=15, pady=6)
            more_btn.config(command=self._on_show_all_categories)
            more_btn.pack(fill="x", pady=(4, 2))
            more_btn.bind("<Enter>", lambda e, w=more_btn: w.config(fg="#FFFFFF"))
            more_btn.bind("<Leave>", lambda e, w=more_btn: w.config(fg="#888888"))
        
        self._bind_scroll_recursive(self.categories_frame)
    
    def update_tags(self, tags: List[Tuple[str, int]], total_count: int = 0):
        """Update tags list with top 20."""
        for w in self.tags_frame.winfo_children():
            w.destroy()
        
        if not tags:
            tk.Label(self.tags_frame, text="Nenhuma tag", 
                    bg="#1A1A1A", fg="#666666",
                    font=("Arial", 10, "italic"), anchor="w", 
                    padx=15, pady=10).pack(fill="x")
            return
        
        # Header if showing subset
        if total_count > len(tags):
            tk.Label(self.tags_frame, text=f"Top {len(tags)} de {total_count} tags",
                    bg="#1A1A1A", fg="#666666", font=("Arial", 9),
                    anchor="w", padx=15, pady=3).pack(fill="x")
        
        # Tag buttons
        for tag, count in tags:
            btn = tk.Button(self.tags_frame, text=f"{tag} ({count})",
                          bg="#1A1A1A", fg="#CCCCCC", font=("Arial", 10),
                          relief="flat", cursor="hand2", anchor="w", 
                          padx=15, pady=6)
            btn.config(command=lambda t=tag, b=btn: self._on_tag_click(t, b))
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
        
        self._bind_scroll_recursive(self.tags_frame)
    
    def _on_origin_click(self, origin: str, btn: tk.Button):
        """Handle origin filter click."""
        self._set_active_button(btn)
        if self.on_origin_filter:
            self.on_origin_filter(origin)
    
    def _on_category_click(self, categories: List[str], btn: tk.Button):
        """Handle category filter click."""
        self._set_active_button(btn)
        if self.on_category_filter:
            self.on_category_filter(categories)
    
    def _on_tag_click(self, tag: str, btn: tk.Button):
        """Handle tag filter click."""
        self._set_active_button(btn)
        if self.on_tag_filter:
            self.on_tag_filter(tag)
    
    def _on_show_all_categories(self):
        """Handle show all categories click."""
        if self.on_show_all_categories:
            self.on_show_all_categories()
    
    def _set_active_button(self, btn: tk.Button):
        """Set active button and reset previous."""
        try:
            if self._active_btn is not None:
                self._active_btn.config(bg="#1A1A1A")
        except Exception:
            pass
        
        self._active_btn = btn
        try:
            if btn is not None:
                btn.config(bg="#E50914")
        except Exception:
            pass
    
    def clear_active_button(self):
        """Clear active button state."""
        self._set_active_button(None)
    
    def _on_hover(self, btn: tk.Button, is_enter: bool):
        """Handle button hover."""
        if btn is self._active_btn:
            return
        
        try:
            if is_enter:
                btn.config(bg="#2A2A2A")
            else:
                btn.config(bg="#1A1A1A")
        except Exception:
            pass
    
    def _bind_scroll_recursive(self, widget: tk.Widget):
        """Bind scroll event recursively to all children."""
        def scroll(e):
            self.sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        
        widget.bind("<MouseWheel>", scroll)
        for child in widget.winfo_children():
            self._bind_scroll_recursive(child)
