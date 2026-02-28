"""Análise em lote."""
import threading
from analysis.analyzer import analyze_with_ai, _choose_text_role
from data.persistence import save_database
from ui.progress_ui import create_progress_window


def analyze_only_new(app):
    to_analyze = [p for p, d in app.database.items() if not d.get("analyzed")]
    if not to_analyze:
        from tkinter import messagebox
        messagebox.showinfo("✅", "Todos os projetos já foram analisados!")
        return
    _run_analysis(app, to_analyze, "Analisando novos projetos")


def reanalyze_all(app):
    _run_analysis(app, list(app.database.keys()), "Reanalisando todos")


def analyze_current_filter(app):
    from actions.scanning import get_filtered_projects
    filtered = get_filtered_projects(app)
    if not filtered:
        from tkinter import messagebox
        messagebox.showinfo("⚠️", "Nenhum projeto no filtro atual!")
        return
    _run_analysis(app, filtered, "Analisando filtro atual")


def reanalyze_specific_category(app, category):
    projects = [p for p, d in app.database.items() if category in d.get("categories", [])]
    if not projects:
        from tkinter import messagebox
        messagebox.showinfo("⚠️", f"Nenhum projeto na categoria '{category}'!")
        return
    _run_analysis(app, projects, f"Reanalisando '{category}'")


def _run_analysis(app, projects, title):
    app.stop_analysis = False
    progress_win, progress_label, progress_bar, stop_btn = create_progress_window(app, title, len(projects))
    
    def analyze_batch():
        total = len(projects)
        role = _choose_text_role(total)
        model_name = app.current_models.get(role, "qwen2.5:3b-instruct-q4_K_M" if role == "text_fast" else "qwen2.5:7b-instruct-q4_K_M")
        
        for i, project_path in enumerate(projects, 1):
            if app.stop_analysis:
                progress_label.config(text="⛔ Parado pelo usuário")
                break
            
            progress_label.config(text=f"[{i}/{total}] {app.database[project_path].get('name', 'Projeto')}")
            progress_bar["value"] = (i / total) * 100
            progress_win.update_idletasks()
            
            categories, tags = analyze_with_ai(app, project_path, batch_size=total)
            app.database[project_path]["categories"] = categories
            app.database[project_path]["tags"] = tags
            app.database[project_path]["analyzed"] = True
            app.database[project_path]["analyzed_model"] = model_name
            
            if i % 10 == 0:
                save_database(app)
        
        save_database(app)
        progress_label.config(text="✅ Concluído!")
        stop_btn.config(text="✖ Fechar", command=progress_win.destroy)
    
    thread = threading.Thread(target=analyze_batch, daemon=True)
    thread.start()
