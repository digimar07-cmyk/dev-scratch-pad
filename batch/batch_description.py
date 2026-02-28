"""Geração de descrições em lote."""
import threading
from analysis.description_generator import generate_ai_description
from data.persistence import save_database
from ui.progress_ui import create_progress_window


def generate_descriptions_new(app):
    to_generate = [p for p, d in app.database.items() if not (d.get("ai_description") or "").strip()]
    if not to_generate:
        from tkinter import messagebox
        messagebox.showinfo("✅", "Todos os projetos já têm descrição!")
        return
    _run_description_generation(app, to_generate, "Gerando novas descrições")


def generate_descriptions_all(app):
    _run_description_generation(app, list(app.database.keys()), "Gerando todas as descrições")


def generate_descriptions_filter(app):
    from actions.scanning import get_filtered_projects
    filtered = get_filtered_projects(app)
    if not filtered:
        from tkinter import messagebox
        messagebox.showinfo("⚠️", "Nenhum projeto no filtro atual!")
        return
    _run_description_generation(app, filtered, "Gerando descrições do filtro")


def _run_description_generation(app, projects, title):
    app.stop_analysis = False
    progress_win, progress_label, progress_bar, stop_btn = create_progress_window(app, title, len(projects))
    
    def generate_batch():
        total = len(projects)
        for i, project_path in enumerate(projects, 1):
            if app.stop_analysis:
                progress_label.config(text="⛔ Parado pelo usuário")
                break
            
            data = app.database[project_path]
            progress_label.config(text=f"[{i}/{total}] {data.get('name', 'Projeto')}")
            progress_bar["value"] = (i / total) * 100
            progress_win.update_idletasks()
            
            generate_ai_description(app, project_path, data)
            
            if i % 5 == 0:
                save_database(app)
        
        save_database(app)
        progress_label.config(text="✅ Concluído!")
        stop_btn.config(text="✖ Fechar", command=progress_win.destroy)
    
    thread = threading.Thread(target=generate_batch, daemon=True)
    thread.start()
