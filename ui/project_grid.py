"""Grid de projetos estilo Netflix."""
import tkinter as tk
import os
from actions.scanning import get_filtered_projects
from images.image_handler import get_cover_image


def display_projects(app):
    for widget in app.scrollable_frame.winfo_children():
        widget.destroy()
    filtered = get_filtered_projects(app)
    if not filtered:
        tk.Label(app.scrollable_frame, text="🔍 Nenhum projeto encontrado",
                 font=("Arial", 18), bg="#141414", fg="#999999").pack(pady=100)
        return
    
    tk.Label(app.scrollable_frame, text=f"🎥 {len(filtered)} projetos",
             font=("Arial", 14, "bold"), bg="#141414", fg="#FFFFFF",
             anchor="w").pack(fill="x", pady=(0, 15))
    
    row_frame = None
    for i, project_path in enumerate(filtered):
        if i % 5 == 0:
            row_frame = tk.Frame(app.scrollable_frame, bg="#141414")
            row_frame.pack(fill="x", pady=5)
        create_project_card(app, row_frame, project_path)


def create_project_card(app, parent, project_path):
    data = app.database[project_path]
    card = tk.Frame(parent, bg="#2A2A2A", relief="flat", width=220, height=280)
    card.pack(side="left", padx=8, pady=8)
    card.pack_propagate(False)
    
    # Imagem
    img_label = tk.Label(card, bg="#000000")
    img_label.pack(fill="x")
    photo = get_cover_image(app, project_path)
    if photo:
        img_label.config(image=photo)
        img_label.image = photo
    else:
        img_label.config(text="🖼️", font=("Arial", 40), fg="#666666")
    
    # Info
    info_frame = tk.Frame(card, bg="#2A2A2A")
    info_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    name = data.get("name", "Sem nome")[:25]
    tk.Label(info_frame, text=name, font=("Arial", 10, "bold"),
             bg="#2A2A2A", fg="#FFFFFF", anchor="w", wraplength=200).pack(fill="x")
    
    categories = data.get("categories", [])
    cat_text = " | ".join(categories[:2]) if categories else "Sem categoria"
    tk.Label(info_frame, text=cat_text[:30], font=("Arial", 8),
             bg="#2A2A2A", fg="#999999", anchor="w").pack(fill="x")
    
    # Ícones
    icons_frame = tk.Frame(info_frame, bg="#2A2A2A")
    icons_frame.pack(fill="x", pady=(5, 0))
    
    fav_icon = "⭐" if data.get("favorite") else "☆"
    done_icon = "✓" if data.get("done") else "○"
    good_icon = "👍" if data.get("good") else ""
    bad_icon = "👎" if data.get("bad") else ""
    
    icons = f"{fav_icon} {done_icon} {good_icon}{bad_icon}"
    tk.Label(icons_frame, text=icons, font=("Arial", 10),
             bg="#2A2A2A", fg="#FFD700").pack(side="left")
    
    # Click para abrir modal
    def open_modal(e=None):
        from ui.project_modal import open_project_modal
        open_project_modal(app, project_path)
    
    for widget in [card, img_label, info_frame]:
        widget.bind("<Button-1>", open_modal)
        widget.config(cursor="hand2")
    
    # Hover
    def on_enter(e):
        card.config(bg="#3A3A3A")
        info_frame.config(bg="#3A3A3A")
        for w in info_frame.winfo_children():
            if isinstance(w, (tk.Label, tk.Frame)):
                w.config(bg="#3A3A3A")
    
    def on_leave(e):
        card.config(bg="#2A2A2A")
        info_frame.config(bg="#2A2A2A")
        for w in info_frame.winfo_children():
            if isinstance(w, (tk.Label, tk.Frame)):
                w.config(bg="#2A2A2A")
    
    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)
