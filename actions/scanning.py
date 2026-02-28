"""Scan de projetos e filtros."""
import os
from tkinter import filedialog, messagebox
from analysis.structure import analyze_project_structure, extract_tags_from_name
from data.persistence import save_database


def scan_folders(app):
    folder = filedialog.askdirectory(title="Selecione a pasta raiz dos projetos")
    if not folder:
        return
    
    new_count = 0
    try:
        for item in os.listdir(folder):
            project_path = os.path.join(folder, item)
            if os.path.isdir(project_path) and project_path not in app.database:
                structure = analyze_project_structure(project_path)
                tags = extract_tags_from_name(item)
                app.database[project_path] = {
                    "name": item,
                    "origin": os.path.basename(folder),
                    "categories": ["Diversos"],
                    "tags": tags,
                    "analyzed": False,
                    "favorite": False,
                    "done": False,
                    "good": False,
                    "bad": False,
                    "ai_description": "",
                }
                new_count += 1
        
        save_database(app)
        from ui.sidebar import update_sidebar
        update_sidebar(app)
        from ui.project_grid import display_projects
        display_projects(app)
        messagebox.showinfo("✅", f"{new_count} novos projetos adicionados!")
    
    except Exception as e:
        messagebox.showerror("❌ Erro", f"Erro ao escanear pastas: {e}")


def get_filtered_projects(app):
    filtered = list(app.database.keys())
    
    if app.current_origin and app.current_origin != "all":
        filtered = [p for p in filtered if app.database[p].get("origin") == app.current_origin]
    
    if app.current_categories:
        filtered = [p for p in filtered if any(c in app.database[p].get("categories", []) for c in app.current_categories)]
    
    if app.current_tag:
        filtered = [p for p in filtered if app.current_tag in app.database[p].get("tags", [])]
    
    if app.search_query:
        query = app.search_query.lower()
        filtered = [p for p in filtered if query in app.database[p].get("name", "").lower()]
    
    return filtered
