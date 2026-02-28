"""Sidebar com filtros e categorias."""
import tkinter as tk
from tkinter import ttk
from collections import Counter


def create_sidebar(app, parent):
    app.sidebar = tk.Frame(parent, bg="#1A1A1A", width=240)
    app.sidebar.pack(side="left", fill="y")
    app.sidebar.pack_propagate(False)
    
    tk.Label(app.sidebar, text="🏛️ FILTROS", font=("Arial", 14, "bold"),
             bg="#1A1A1A", fg="#E50914").pack(pady=15)
    
    # Origins
    tk.Label(app.sidebar, text="🌐 Origem", font=("Arial", 11, "bold"),
             bg="#1A1A1A", fg="#CCCCCC").pack(pady=(10, 5), anchor="w", padx=15)
    app.origins_listbox = tk.Listbox(app.sidebar, bg="#2A2A2A", fg="#FFFFFF",
                                      font=("Arial", 10), relief="flat",
                                      selectbackground="#E50914", selectforeground="#FFFFFF",
                                      height=6, selectmode=tk.SINGLE)
    app.origins_listbox.pack(fill="x", padx=15, pady=5)
    app.origins_listbox.bind("<<ListboxSelect>>", lambda e: set_origin_filter(app))
    
    # Categories
    tk.Label(app.sidebar, text="🏷️ Categorias", font=("Arial", 11, "bold"),
             bg="#1A1A1A", fg="#CCCCCC").pack(pady=(15, 5), anchor="w", padx=15)
    cat_frame = tk.Frame(app.sidebar, bg="#1A1A1A")
    cat_frame.pack(fill="x", padx=15)
    app.active_categories_label = tk.Label(cat_frame, text="Todas", bg="#2A2A2A",
                                           fg="#FFFFFF", font=("Arial", 9), anchor="w",
                                           relief="flat", padx=8, pady=6)
    app.active_categories_label.pack(side="left", fill="x", expand=True)
    tk.Button(cat_frame, text="✎", command=lambda: open_categories_picker(app),
              bg="#E50914", fg="#FFFFFF", font=("Arial", 10, "bold"),
              relief="flat", cursor="hand2", width=3).pack(side="right")
    
    # Tags
    tk.Label(app.sidebar, text="🏷️ Tags", font=("Arial", 11, "bold"),
             bg="#1A1A1A", fg="#CCCCCC").pack(pady=(15, 5), anchor="w", padx=15)
    app.tags_listbox = tk.Listbox(app.sidebar, bg="#2A2A2A", fg="#FFFFFF",
                                   font=("Arial", 10), relief="flat",
                                   selectbackground="#E50914", selectforeground="#FFFFFF",
                                   height=12, selectmode=tk.SINGLE)
    app.tags_listbox.pack(fill="both", expand=True, padx=15, pady=5)
    app.tags_listbox.bind("<<ListboxSelect>>", lambda e: set_tag_filter(app))
    
    app.sidebar_buttons = {}
    update_sidebar(app)


def update_sidebar(app):
    update_origins_list(app)
    update_categories_list(app)
    update_tags_list(app)


def update_origins_list(app):
    app.origins_listbox.delete(0, tk.END)
    origins = Counter(d.get("origin", "Diversos") for d in app.database.values())
    total = sum(origins.values())
    app.origins_listbox.insert(tk.END, f"🌍 Todas ({total})")
    for origin in sorted(origins.keys()):
        app.origins_listbox.insert(tk.END, f"{origin} ({origins[origin]})")


def update_categories_list(app):
    if not app.current_categories:
        app.active_categories_label.config(text="Todas")
    else:
        display = ", ".join(app.current_categories[:3])
        if len(app.current_categories) > 3:
            display += f" +{len(app.current_categories)-3}"
        app.active_categories_label.config(text=display)


def update_tags_list(app):
    app.tags_listbox.delete(0, tk.END)
    all_tags = []
    for d in app.database.values():
        all_tags.extend(d.get("tags", []))
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(50)
    for tag, count in top_tags:
        app.tags_listbox.insert(tk.END, f"{tag} ({count})")


def open_categories_picker(app):
    from collections import Counter
    win = tk.Toplevel(app.root)
    win.title("🎯 Selecionar Categorias")
    win.configure(bg="#141414")
    win.geometry("700x600")
    win.transient(app.root)
    win.grab_set()
    
    tk.Label(win, text="🎯 Filtrar por Categorias", font=("Arial", 16, "bold"),
             bg="#141414", fg="#E50914").pack(pady=15)
    tk.Label(win, text="Selecione uma ou mais categorias (Ctrl/Cmd clique):",
             font=("Arial", 10), bg="#141414", fg="#CCCCCC").pack(pady=5)
    
    list_frame = tk.Frame(win, bg="#2A2A2A")
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    listbox = tk.Listbox(list_frame, bg="#2A2A2A", fg="#FFFFFF",
                         font=("Arial", 11), selectmode=tk.MULTIPLE,
                         yscrollcommand=scrollbar.set, relief="flat",
                         selectbackground="#E50914", selectforeground="#FFFFFF")
    listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scrollbar.config(command=listbox.yview)
    
    all_cats = Counter()
    for d in app.database.values():
        all_cats.update(d.get("categories", []))
    categories = sorted([c for c in all_cats.keys() if c and c != "Sem Categoria"])
    for cat in categories:
        listbox.insert(tk.END, f"{cat} ({all_cats[cat]})")
    for i, cat in enumerate(categories):
        if cat in app.current_categories:
            listbox.selection_set(i)
    
    def apply_filter():
        indices = listbox.curselection()
        app.current_categories = [categories[i] for i in indices]
        update_categories_list(app)
        from ui.project_grid import display_projects
        display_projects(app)
        win.destroy()
    
    def clear_filter():
        app.current_categories = []
        update_categories_list(app)
        from ui.project_grid import display_projects
        display_projects(app)
        win.destroy()
    
    btn_frame = tk.Frame(win, bg="#141414")
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="✓ Aplicar", command=apply_filter,
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🗑️ Limpar", command=clear_filter,
              bg="#FF6B6B", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✕ Cancelar", command=win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)


def set_origin_filter(app):
    selection = app.origins_listbox.curselection()
    if not selection: return
    selected_text = app.origins_listbox.get(selection[0])
    if selected_text.startswith("🌍 Todas"):
        app.current_origin = "all"
    else:
        app.current_origin = selected_text.split(" (")[0].strip()
    from ui.project_grid import display_projects
    display_projects(app)


def set_category_filter(app, category):
    if category in app.current_categories:
        app.current_categories.remove(category)
    else:
        app.current_categories.append(category)
    update_categories_list(app)
    from ui.project_grid import display_projects
    display_projects(app)


def set_tag_filter(app):
    selection = app.tags_listbox.curselection()
    if not selection: return
    selected_text = app.tags_listbox.get(selection[0])
    app.current_tag = selected_text.split(" (")[0].strip()
    from ui.project_grid import display_projects
    display_projects(app)


def _set_active_sidebar_btn(app, button_id):
    for btn_id, btn in app.sidebar_buttons.items():
        if btn_id == button_id:
            btn.config(bg="#E50914")
        else:
            btn.config(bg="#2A2A2A")
