"""Toggles de estado dos projetos."""
import threading
from data.persistence import save_database


def toggle_favorite(app, project_path, btn=None):
    if project_path in app.database:
        new_val = not app.database[project_path].get("favorite", False)
        app.database[project_path]["favorite"] = new_val
        save_database(app)
        if btn:
            btn.config(text="⭐" if new_val else "☆",
                       fg="#FFD700" if new_val else "#666666")
        else:
            from ui.project_grid import display_projects
            display_projects(app)


def toggle_done(app, project_path, btn=None):
    if project_path in app.database:
        new_val = not app.database[project_path].get("done", False)
        app.database[project_path]["done"] = new_val
        save_database(app)
        if btn:
            btn.config(text="✓" if new_val else "○",
                       fg="#00FF00" if new_val else "#666666")
        else:
            from ui.project_grid import display_projects
            display_projects(app)


def toggle_good(app, project_path, btn=None):
    if project_path in app.database:
        current = app.database[project_path].get("good", False)
        new_val = not current
        app.database[project_path]["good"] = new_val
        if new_val:
            app.database[project_path]["bad"] = False
        save_database(app)
        if btn:
            btn.config(fg="#00FF00" if new_val else "#666666")
        else:
            from ui.project_grid import display_projects
            display_projects(app)


def toggle_bad(app, project_path, btn=None):
    if project_path in app.database:
        current = app.database[project_path].get("bad", False)
        new_val = not current
        app.database[project_path]["bad"] = new_val
        if new_val:
            app.database[project_path]["good"] = False
        save_database(app)
        if btn:
            btn.config(fg="#FF0000" if new_val else "#666666")
        else:
            from ui.project_grid import display_projects
            display_projects(app)


def analyze_single_project(app, project_path):
    app.status_bar.config(text="🤖 Analisando com IA...")
    def analyze():
        from analysis.analyzer import analyze_with_ai
        from ollama.ollama_client import _model_name
        categories, tags = analyze_with_ai(app, project_path, batch_size=1)
        app.database[project_path]["categories"] = categories
        app.database[project_path]["tags"] = tags
        app.database[project_path]["analyzed"] = True
        app.database[project_path]["analyzed_model"] = _model_name(app, "text_quality")
        save_database(app)
        
        from ui.sidebar import update_sidebar
        from ui.project_grid import display_projects
        app.root.after(0, lambda: update_sidebar(app))
        app.root.after(0, lambda: display_projects(app))
        app.root.after(0, lambda: app.status_bar.config(text="✓ Análise concluída"))
    threading.Thread(target=analyze, daemon=True).start()
