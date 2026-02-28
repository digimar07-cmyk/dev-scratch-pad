"""Toggles de estado (favorite, done, good, bad)."""
from data.persistence import save_database
from analysis.analyzer import analyze_with_ai


def toggle_favorite(app, project_path, button=None):
    current = app.database[project_path].get("favorite", False)
    app.database[project_path]["favorite"] = not current
    save_database(app)
    if button:
        button.config(text="⭐" if not current else "☆",
                      fg="#FFD700" if not current else "#666666")
    from ui.project_grid import display_projects
    display_projects(app)


def toggle_done(app, project_path, button=None):
    current = app.database[project_path].get("done", False)
    app.database[project_path]["done"] = not current
    save_database(app)
    if button:
        button.config(text="✓" if not current else "○",
                      fg="#00FF00" if not current else "#666666")
    from ui.project_grid import display_projects
    display_projects(app)


def toggle_good(app, project_path, button=None):
    current = app.database[project_path].get("good", False)
    app.database[project_path]["good"] = not current
    if not current:
        app.database[project_path]["bad"] = False
    save_database(app)
    if button:
        button.config(fg="#00FF00" if not current else "#666666")
    from ui.project_grid import display_projects
    display_projects(app)


def toggle_bad(app, project_path, button=None):
    current = app.database[project_path].get("bad", False)
    app.database[project_path]["bad"] = not current
    if not current:
        app.database[project_path]["good"] = False
    save_database(app)
    if button:
        button.config(fg="#FF0000" if not current else "#666666")
    from ui.project_grid import display_projects
    display_projects(app)


def analyze_single_project(app, project_path):
    from tkinter import messagebox
    messagebox.showinfo("🤖", "Analisando projeto...")
    categories, tags = analyze_with_ai(app, project_path)
    app.database[project_path]["categories"] = categories
    app.database[project_path]["tags"] = tags
    app.database[project_path]["analyzed"] = True
    save_database(app)
    messagebox.showinfo("✅", "Análise concluída!")
    from ui.project_grid import display_projects
    display_projects(app)
