"""
LASERFLIX — Project Modal (Netflix Style)
Modal detalhado para exibir/editar projetos individuais
"""

import tkinter as tk
from tkinter import ttk, messagebox, Text, Scrollbar
from PIL import Image, ImageTk
import os


class ProjectModal:
    """Modal Netflix-style para exibir detalhes do projeto"""

    def __init__(self, app, project_path):
        self.app = app
        self.project_path = project_path
        self.project_data = app.database.data.get(project_path, {})
        
        # Window
        self.window = tk.Toplevel(app.root)
        self.window.title(f"📁 {self.project_data.get('name', 'Projeto')}")
        self.window.geometry("1200x800")
        self.window.configure(bg="#141414")
        self.window.transient(app.root)
        
        # State
        self.current_image_index = 0
        self.images = []
        self.photo_refs = []
        
        self._create_ui()
        self._load_images()
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # UI CREATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def _create_ui(self):
        # Main container
        main_frame = tk.Frame(self.window, bg="#141414")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # Content (2 columns)
        content = tk.Frame(main_frame, bg="#141414")
        content.pack(fill="both", expand=True, pady=10)
        
        # Left: Images
        left = tk.Frame(content, bg="#141414")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._create_image_viewer(left)
        
        # Right: Details
        right = tk.Frame(content, bg="#1a1a1a", width=400)
        right.pack(side="right", fill="both", padx=(10, 0))
        right.pack_propagate(False)
        self._create_details_panel(right)
        
    def _create_header(self, parent):
        header = tk.Frame(parent, bg="#1a1a1a", height=80)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)
        
        # Title
        name = self.project_data.get("name", "Sem Nome")
        tk.Label(
            header,
            text=name,
            font=("Arial", 24, "bold"),
            fg="#E50914",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        # Path + Origin
        origin = self.project_data.get("origin", "Diversos")
        path_text = f"📂 {self.project_path}\n🏷️ Origem: {origin}"
        tk.Label(
            header,
            text=path_text,
            font=("Arial", 9),
            fg="#999999",
            bg="#1a1a1a",
            justify="left"
        ).pack(anchor="w", padx=20)
        
    def _create_image_viewer(self, parent):
        # Canvas for main image
        self.image_canvas = tk.Canvas(
            parent,
            bg="#000000",
            highlightthickness=0
        )
        self.image_canvas.pack(fill="both", expand=True)
        
        # Navigation buttons
        nav_frame = tk.Frame(parent, bg="#141414", height=50)
        nav_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(
            nav_frame,
            text="◀ Anterior",
            font=("Arial", 11, "bold"),
            bg="#E50914",
            fg="white",
            activebackground="#B20710",
            relief="flat",
            cursor="hand2",
            command=self._prev_image
        ).pack(side="left", padx=5)
        
        self.image_counter = tk.Label(
            nav_frame,
            text="0 / 0",
            font=("Arial", 11),
            fg="#999999",
            bg="#141414"
        )
        self.image_counter.pack(side="left", expand=True)
        
        tk.Button(
            nav_frame,
            text="Próxima ▶",
            font=("Arial", 11, "bold"),
            bg="#E50914",
            fg="white",
            activebackground="#B20710",
            relief="flat",
            cursor="hand2",
            command=self._next_image
        ).pack(side="right", padx=5)
        
    def _create_details_panel(self, parent):
        # Scrollable frame
        canvas = tk.Canvas(parent, bg="#1a1a1a", highlightthickness=0)
        scrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        self._create_action_buttons(scrollable)
        
        # AI Description
        self._create_description_section(scrollable)
        
        # Categories
        self._create_categories_section(scrollable)
        
        # Tags
        self._create_tags_section(scrollable)
        
        # Footer buttons
        self._create_footer_buttons(scrollable)
        
    def _create_action_buttons(self, parent):
        frame = tk.Frame(parent, bg="#1a1a1a")
        frame.pack(fill="x", padx=15, pady=10)
        
        # Row 1
        row1 = tk.Frame(frame, bg="#1a1a1a")
        row1.pack(fill="x", pady=(0, 5))
        
        is_fav = self.project_data.get("favorite", False)
        self.fav_btn = tk.Button(
            row1,
            text="⭐" if is_fav else "☆",
            font=("Arial", 18),
            fg="#FFD700" if is_fav else "#666666",
            bg="#2a2a2a",
            activebackground="#3a3a3a",
            width=3,
            relief="flat",
            cursor="hand2",
            command=self._toggle_favorite
        )
        self.fav_btn.pack(side="left", padx=2)
        
        is_done = self.project_data.get("done", False)
        self.done_btn = tk.Button(
            row1,
            text="✓" if is_done else "○",
            font=("Arial", 18),
            fg="#00FF00" if is_done else "#666666",
            bg="#2a2a2a",
            activebackground="#3a3a3a",
            width=3,
            relief="flat",
            cursor="hand2",
            command=self._toggle_done
        )
        self.done_btn.pack(side="left", padx=2)
        
        is_good = self.project_data.get("good", False)
        self.good_btn = tk.Button(
            row1,
            text="👍",
            font=("Arial", 16),
            fg="#00FF00" if is_good else "#666666",
            bg="#2a2a2a",
            activebackground="#3a3a3a",
            width=3,
            relief="flat",
            cursor="hand2",
            command=self._toggle_good
        )
        self.good_btn.pack(side="left", padx=2)
        
        is_bad = self.project_data.get("bad", False)
        self.bad_btn = tk.Button(
            row1,
            text="👎",
            font=("Arial", 16),
            fg="#FF0000" if is_bad else "#666666",
            bg="#2a2a2a",
            activebackground="#3a3a3a",
            width=3,
            relief="flat",
            cursor="hand2",
            command=self._toggle_bad
        )
        self.bad_btn.pack(side="left", padx=2)
        
        # Row 2
        tk.Button(
            frame,
            text="🤖 Analisar com IA",
            font=("Arial", 10, "bold"),
            bg="#E50914",
            fg="white",
            activebackground="#B20710",
            relief="flat",
            cursor="hand2",
            command=self._analyze_with_ai
        ).pack(fill="x", pady=(5, 0))
        
    def _create_description_section(self, parent):
        tk.Label(
            parent,
            text="📝 Descrição AI",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        desc_frame = tk.Frame(parent, bg="#2a2a2a")
        desc_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.desc_text = Text(
            desc_frame,
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="white",
            wrap="word",
            height=6,
            relief="flat",
            insertbackground="white"
        )
        self.desc_text.pack(fill="x", padx=5, pady=5)
        
        current_desc = self.project_data.get("ai_description", "Sem descrição ainda...")
        self.desc_text.insert("1.0", current_desc)
        
        tk.Button(
            desc_frame,
            text="💾 Salvar Descrição",
            font=("Arial", 9, "bold"),
            bg="#444444",
            fg="white",
            activebackground="#555555",
            relief="flat",
            cursor="hand2",
            command=self._save_description
        ).pack(pady=(0, 5))
        
    def _create_categories_section(self, parent):
        tk.Label(
            parent,
            text="📂 Categorias",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        cats = self.project_data.get("categories", [])
        cats_text = ", ".join(cats) if cats else "Nenhuma categoria"
        
        tk.Label(
            parent,
            text=cats_text,
            font=("Arial", 10),
            fg="#999999",
            bg="#1a1a1a",
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
    def _create_tags_section(self, parent):
        tk.Label(
            parent,
            text="🏷️ Tags",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        tags = self.project_data.get("tags", [])
        tags_text = ", ".join(tags) if tags else "Nenhuma tag"
        
        tk.Label(
            parent,
            text=tags_text,
            font=("Arial", 10),
            fg="#999999",
            bg="#1a1a1a",
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
    def _create_footer_buttons(self, parent):
        footer = tk.Frame(parent, bg="#1a1a1a")
        footer.pack(fill="x", padx=15, pady=20, side="bottom")
        
        tk.Button(
            footer,
            text="📂 Abrir Pasta",
            font=("Arial", 10, "bold"),
            bg="#444444",
            fg="white",
            activebackground="#555555",
            relief="flat",
            cursor="hand2",
            command=lambda: self.app.open_folder(self.project_path)
        ).pack(fill="x", pady=2)
        
        tk.Button(
            footer,
            text="❌ Fechar",
            font=("Arial", 10, "bold"),
            bg="#2a2a2a",
            fg="white",
            activebackground="#3a3a3a",
            relief="flat",
            cursor="hand2",
            command=self.window.destroy
        ).pack(fill="x", pady=2)
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # IMAGE HANDLING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def _load_images(self):
        self.images = self.app.get_all_project_images(self.project_path)
        if self.images:
            self._display_current_image()
        else:
            self.image_canvas.create_text(
                400, 300,
                text="Nenhuma imagem encontrada",
                font=("Arial", 14),
                fill="#666666"
            )
        self._update_counter()
        
    def _display_current_image(self):
        if not self.images:
            return
            
        self.image_canvas.delete("all")
        
        try:
            img_path = self.images[self.current_image_index]
            img = Image.open(img_path)
            
            # Resize to fit canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 700
                canvas_height = 600
                
            img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.photo_refs.append(photo)
            
            x = canvas_width // 2
            y = canvas_height // 2
            self.image_canvas.create_image(x, y, image=photo)
            
        except Exception as e:
            self.image_canvas.create_text(
                400, 300,
                text=f"Erro ao carregar imagem:\n{str(e)}",
                font=("Arial", 12),
                fill="#FF0000"
            )
            
    def _next_image(self):
        if self.images and self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self._display_current_image()
            self._update_counter()
            
    def _prev_image(self):
        if self.images and self.current_image_index > 0:
            self.current_image_index -= 1
            self._display_current_image()
            self._update_counter()
            
    def _update_counter(self):
        if self.images:
            self.image_counter.config(
                text=f"{self.current_image_index + 1} / {len(self.images)}"
            )
        else:
            self.image_counter.config(text="0 / 0")
            
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ACTIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def _toggle_favorite(self):
        self.app.toggle_favorite(self.project_path, self.fav_btn)
        self.project_data = self.app.database.data.get(self.project_path, {})
        
    def _toggle_done(self):
        self.app.toggle_done(self.project_path, self.done_btn)
        self.project_data = self.app.database.data.get(self.project_path, {})
        
    def _toggle_good(self):
        self.app.toggle_good(self.project_path, self.good_btn)
        self.project_data = self.app.database.data.get(self.project_path, {})
        # Update bad button
        is_bad = self.project_data.get("bad", False)
        self.bad_btn.config(fg="#FF0000" if is_bad else "#666666")
        
    def _toggle_bad(self):
        self.app.toggle_bad(self.project_path, self.bad_btn)
        self.project_data = self.app.database.data.get(self.project_path, {})
        # Update good button
        is_good = self.project_data.get("good", False)
        self.good_btn.config(fg="#00FF00" if is_good else "#666666")
        
    def _analyze_with_ai(self):
        self.app.analyze_single_project(self.project_path)
        messagebox.showinfo(
            "🤖 Análise Iniciada",
            "Análise com IA em andamento...\nAguarde alguns segundos."
        )
        
    def _save_description(self):
        new_desc = self.desc_text.get("1.0", "end-1c").strip()
        self.app.database.data[self.project_path]["ai_description"] = new_desc
        self.app.database.save()
        messagebox.showinfo("💾", "Descrição salva!")
