"""Modal de detalhes do projeto (estilo Netflix)."""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from images.image_handler import get_hero_image, get_all_project_images
from actions.toggles import toggle_favorite, toggle_done, toggle_good, toggle_bad, analyze_single_project
from actions.file_operations import open_folder, open_image, add_tag_to_listbox, remove_tag_from_listbox
from analysis.description_generator import generate_ai_description
from data.persistence import save_database


def open_project_modal(app, project_path):
    data = app.database.get(project_path, {})
    if not data:
        messagebox.showerror("Erro", "Projeto não encontrado no banco!")
        return
    
    modal = tk.Toplevel(app.root)
    modal.title(data.get("name", "Projeto"))
    modal.state("zoomed")
    modal.configure(bg="#141414")
    modal.transient(app.root)
    
    # Canvas scroll
    canvas = tk.Canvas(modal, bg="#141414", highlightthickness=0)
    scrollbar = ttk.Scrollbar(modal, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#141414")
    
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def _on_mw(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mw)
    modal.protocol("WM_DELETE_WINDOW", lambda: [canvas.unbind_all("<MouseWheel>"), modal.destroy()])
    
    # Hero image
    hero_frame = tk.Frame(scroll_frame, bg="#000000", height=450)
    hero_frame.pack(fill="x")
    hero_frame.pack_propagate(False)
    
    hero_photo = get_hero_image(project_path)
    if hero_photo:
        hero_label = tk.Label(hero_frame, image=hero_photo, bg="#000000")
        hero_label.image = hero_photo
        hero_label.pack(expand=True)
    else:
        tk.Label(hero_frame, text="🖼️ Sem Imagem", font=("Arial", 40),
                 bg="#000000", fg="#666666").pack(expand=True)
    
    # Info principal
    info_frame = tk.Frame(scroll_frame, bg="#141414")
    info_frame.pack(fill="x", padx=40, pady=20)
    
    tk.Label(info_frame, text=data.get("name", "Sem nome"), font=("Arial", 24, "bold"),
             bg="#141414", fg="#FFFFFF", anchor="w").pack(fill="x", pady=(0, 10))
    
    # Metadados
    meta_frame = tk.Frame(info_frame, bg="#141414")
    meta_frame.pack(fill="x", pady=5)
    
    origin = data.get("origin", "Desconhecida")
    tk.Label(meta_frame, text=f"🌐 {origin}", font=("Arial", 11),
             bg="#141414", fg="#999999").pack(side="left", padx=(0, 20))
    
    categories = data.get("categories", [])
    if categories:
        cat_text = " | ".join(categories[:3])
        tk.Label(meta_frame, text=f"🏷️ {cat_text}", font=("Arial", 11),
                 bg="#141414", fg="#999999").pack(side="left", padx=(0, 20))
    
    if data.get("analyzed"):
        model_used = data.get("analyzed_model", "IA")[:20]
        tk.Label(meta_frame, text=f"🤖 {model_used}", font=("Arial", 10),
                 bg="#141414", fg="#1DB954").pack(side="left")
    
    # Botões de ação
    actions_frame = tk.Frame(info_frame, bg="#141414")
    actions_frame.pack(fill="x", pady=15)
    
    fav_btn = tk.Button(actions_frame, text="⭐" if data.get("favorite") else "☆",
                        command=lambda: toggle_favorite(app, project_path, fav_btn),
                        bg="#2A2A2A", fg="#FFD700" if data.get("favorite") else "#666666",
                        font=("Arial", 18), relief="flat", cursor="hand2", width=3, height=1)
    fav_btn.pack(side="left", padx=5)
    
    done_btn = tk.Button(actions_frame, text="✓" if data.get("done") else "○",
                         command=lambda: toggle_done(app, project_path, done_btn),
                         bg="#2A2A2A", fg="#00FF00" if data.get("done") else "#666666",
                         font=("Arial", 18), relief="flat", cursor="hand2", width=3, height=1)
    done_btn.pack(side="left", padx=5)
    
    good_btn = tk.Button(actions_frame, text="👍",
                         command=lambda: toggle_good(app, project_path, good_btn),
                         bg="#2A2A2A", fg="#00FF00" if data.get("good") else "#666666",
                         font=("Arial", 16), relief="flat", cursor="hand2", width=3, height=1)
    good_btn.pack(side="left", padx=5)
    
    bad_btn = tk.Button(actions_frame, text="👎",
                        command=lambda: toggle_bad(app, project_path, bad_btn),
                        bg="#2A2A2A", fg="#FF0000" if data.get("bad") else "#666666",
                        font=("Arial", 16), relief="flat", cursor="hand2", width=3, height=1)
    bad_btn.pack(side="left", padx=5)
    
    tk.Button(actions_frame, text="📂 Abrir Pasta",
              command=lambda: open_folder(project_path),
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=10)
    
    tk.Button(actions_frame, text="✎ Editar",
              command=lambda: open_edit_mode(app, project_path, modal),
              bg="#E50914", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
    
    tk.Button(actions_frame, text="🤖 Analisar",
              command=lambda: analyze_single_project(app, project_path),
              bg="#9B59B6", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=15, pady=8).pack(side="left", padx=5)
    
    # Descrição
    desc_frame = tk.Frame(scroll_frame, bg="#141414")
    desc_frame.pack(fill="x", padx=40, pady=20)
    
    tk.Label(desc_frame, text="📝 Descrição", font=("Arial", 16, "bold"),
             bg="#141414", fg="#FFFFFF", anchor="w").pack(fill="x", pady=(0, 10))
    
    description = data.get("ai_description", "").strip()
    if description:
        desc_text = tk.Text(desc_frame, bg="#2A2A2A", fg="#CCCCCC",
                            font=("Arial", 11), wrap="word", relief="flat",
                            height=10, padx=15, pady=10)
        desc_text.insert("1.0", description)
        desc_text.config(state="disabled")
        desc_text.pack(fill="x")
    else:
        no_desc_frame = tk.Frame(desc_frame, bg="#2A2A2A")
        no_desc_frame.pack(fill="x", pady=10, padx=5, ipady=20)
        tk.Label(no_desc_frame, text="⚠️ Sem descrição", font=("Arial", 12),
                 bg="#2A2A2A", fg="#999999").pack()
        tk.Button(no_desc_frame, text="✨ Gerar com IA",
                  command=lambda: _generate_description_inline(app, project_path, desc_frame, modal),
                  bg="#1DB954", fg="#FFFFFF", font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", padx=15, pady=8).pack(pady=10)
    
    # Galeria de imagens
    gallery_frame = tk.Frame(scroll_frame, bg="#141414")
    gallery_frame.pack(fill="x", padx=40, pady=20)
    
    tk.Label(gallery_frame, text="🖼️ Galeria", font=("Arial", 16, "bold"),
             bg="#141414", fg="#FFFFFF", anchor="w").pack(fill="x", pady=(0, 10))
    
    images = get_all_project_images(project_path)
    if images:
        img_container = tk.Frame(gallery_frame, bg="#141414")
        img_container.pack(fill="x")
        for img_path in images[:10]:
            try:
                from PIL import Image, ImageTk
                img = Image.open(img_path)
                img.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(img)
                btn = tk.Button(img_container, image=photo, bg="#2A2A2A",
                                command=lambda p=img_path: open_image(p),
                                relief="flat", cursor="hand2")
                btn.image = photo
                btn.pack(side="left", padx=5, pady=5)
            except Exception:
                pass
    else:
        tk.Label(gallery_frame, text="Nenhuma imagem encontrada", font=("Arial", 11),
                 bg="#141414", fg="#666666").pack()
    
    # Botão fechar
    tk.Button(scroll_frame, text="✖ Fechar", command=modal.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 14, "bold"),
              relief="flat", cursor="hand2", padx=40, pady=12).pack(pady=30)


def _generate_description_inline(app, project_path, parent_frame, modal):
    for widget in parent_frame.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_children():
            first_child = widget.winfo_children()[0]
            if isinstance(first_child, tk.Label) and first_child.cget("text") == "⚠️ Sem descrição":
                widget.destroy()
    
    loading = tk.Label(parent_frame, text="🤖 Gerando descrição...", font=("Arial", 12),
                       bg="#2A2A2A", fg="#1DB954", pady=20)
    loading.pack(fill="x")
    modal.update_idletasks()
    
    import threading
    def generate():
        desc = generate_ai_description(app, project_path, app.database[project_path])
        modal.after(0, lambda: _update_description_display(parent_frame, loading, desc))
    threading.Thread(target=generate, daemon=True).start()


def _update_description_display(parent_frame, loading_label, description):
    loading_label.destroy()
    if description:
        desc_text = tk.Text(parent_frame, bg="#2A2A2A", fg="#CCCCCC",
                            font=("Arial", 11), wrap="word", relief="flat",
                            height=10, padx=15, pady=10)
        desc_text.insert("1.0", description)
        desc_text.config(state="disabled")
        desc_text.pack(fill="x")
    else:
        tk.Label(parent_frame, text="⚠️ Erro ao gerar descrição", font=("Arial", 12),
                 bg="#2A2A2A", fg="#FF6B6B", pady=20).pack(fill="x")


def open_edit_mode(app, project_path, parent_modal):
    data = app.database.get(project_path, {})
    edit_win = tk.Toplevel(parent_modal)
    edit_win.title(f"Editar: {data.get('name', 'Projeto')}")
    edit_win.configure(bg="#141414")
    edit_win.geometry("800x700")
    edit_win.transient(parent_modal)
    edit_win.grab_set()
    
    tk.Label(edit_win, text="✎ EDITAR PROJETO", font=("Arial", 18, "bold"),
             bg="#141414", fg="#E50914").pack(pady=20)
    
    # Categorias
    tk.Label(edit_win, text="🏷️ Categorias", font=("Arial", 12, "bold"),
             bg="#141414", fg="#FFFFFF").pack(pady=(10, 5))
    
    cat_frame = tk.Frame(edit_win, bg="#2A2A2A")
    cat_frame.pack(fill="both", expand=True, padx=40, pady=10)
    
    cat_listbox = tk.Listbox(cat_frame, bg="#2A2A2A", fg="#FFFFFF",
                             font=("Arial", 11), relief="flat",
                             selectbackground="#E50914", height=6)
    cat_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    for cat in data.get("categories", []):
        cat_listbox.insert(tk.END, cat)
    
    cat_btn_frame = tk.Frame(cat_frame, bg="#2A2A2A")
    cat_btn_frame.pack(side="right", fill="y", padx=5)
    tk.Button(cat_btn_frame, text="➕", command=lambda: add_tag_to_listbox(app, cat_listbox),
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 10, "bold"),
              relief="flat", cursor="hand2", width=3).pack(pady=2)
    tk.Button(cat_btn_frame, text="➖", command=lambda: remove_tag_from_listbox(cat_listbox),
              bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"),
              relief="flat", cursor="hand2", width=3).pack(pady=2)
    
    # Tags
    tk.Label(edit_win, text="🏷️ Tags", font=("Arial", 12, "bold"),
             bg="#141414", fg="#FFFFFF").pack(pady=(10, 5))
    
    tag_frame = tk.Frame(edit_win, bg="#2A2A2A")
    tag_frame.pack(fill="both", expand=True, padx=40, pady=10)
    
    tag_listbox = tk.Listbox(tag_frame, bg="#2A2A2A", fg="#FFFFFF",
                             font=("Arial", 11), relief="flat",
                             selectbackground="#E50914", height=8)
    tag_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    for tag in data.get("tags", []):
        tag_listbox.insert(tk.END, tag)
    
    tag_btn_frame = tk.Frame(tag_frame, bg="#2A2A2A")
    tag_btn_frame.pack(side="right", fill="y", padx=5)
    tk.Button(tag_btn_frame, text="➕", command=lambda: add_tag_to_listbox(app, tag_listbox),
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 10, "bold"),
              relief="flat", cursor="hand2", width=3).pack(pady=2)
    tk.Button(tag_btn_frame, text="➖", command=lambda: remove_tag_from_listbox(tag_listbox),
              bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"),
              relief="flat", cursor="hand2", width=3).pack(pady=2)
    
    # Botões
    btn_frame = tk.Frame(edit_win, bg="#141414")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="💾 Salvar",
              command=lambda: save_edit_modal(app, project_path, cat_listbox, tag_listbox, edit_win, parent_modal),
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=25, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✖ Cancelar", command=edit_win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=25, pady=10).pack(side="left", padx=5)


def save_edit_modal(app, project_path, cat_listbox, tag_listbox, edit_win, parent_modal):
    new_cats = list(cat_listbox.get(0, tk.END))
    new_tags = list(tag_listbox.get(0, tk.END))
    app.database[project_path]["categories"] = new_cats
    app.database[project_path]["tags"] = new_tags
    save_database(app)
    from ui.sidebar import update_sidebar
    update_sidebar(app)
    messagebox.showinfo("✓", "Alterações salvas!")
    edit_win.destroy()
    parent_modal.destroy()
    from ui.project_grid import display_projects
    display_projects(app)
