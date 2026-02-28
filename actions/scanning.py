"""Scanning de pastas e filtros."""
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from analysis.structure import get_origin_from_path
from data.persistence import save_database


def add_folders(app):
    folder = filedialog.askdirectory(title="Selecione uma pasta de projetos")
    if folder and folder not in app.folders:
        app.folders.append(folder)
        from data.persistence import save_config
        save_config(app)
        scan_projects(app)
        messagebox.showinfo("✓", f"Pasta adicionada!\n{folder}")


def scan_projects(app):
    new_count = 0
    for root_folder in app.folders:
        if not os.path.exists(root_folder):
            continue
        for item in os.listdir(root_folder):
            project_path = os.path.join(root_folder, item)
            if os.path.isdir(project_path) and project_path not in app.database:
                app.database[project_path] = {
                    "name": item,
                    "origin": get_origin_from_path(project_path),
                    "favorite": False, "done": False, "good": False, "bad": False,
                    "categories": [], "tags": [], "analyzed": False,
                    "ai_description": "", "added_date": datetime.now().isoformat(),
                }
                new_count += 1
    if new_count > 0:
        save_database(app)
        from ui.sidebar import update_sidebar
        from ui.project_grid import display_projects
        update_sidebar(app)
        display_projects(app)
        app.status_bar.config(text=f"✓ {new_count} novos projetos")


def get_filtered_projects(app):
    filtered = []
    for project_path, data in app.database.items():
        show = (
            app.current_filter == "all"
            or (app.current_filter == "favorite" and data.get("favorite"))
            or (app.current_filter == "done"     and data.get("done"))
            or (app.current_filter == "good"     and data.get("good"))
            or (app.current_filter == "bad"      and data.get("bad"))
        )
        if not show: continue
        if app.current_origin != "all" and data.get("origin") != app.current_origin: continue
        if app.current_categories and not any(c in data.get("categories", []) for c in app.current_categories): continue
        if app.current_tag and app.current_tag not in data.get("tags", []): continue
        if app.search_query and app.search_query not in data.get("name", "").lower(): continue
        filtered.append(project_path)
    return filtered
