"""Geração de descrições em lote."""
import threading
from tkinter import messagebox
from analysis.description_generator import generate_ai_description
from ollama.ollama_client import _model_name
from data.persistence import manual_backup
from ui.progress_ui import show_progress_ui, hide_progress_ui, update_progress


def generate_descriptions_for_new(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    projects = [p for p, d in app.database.items()
                if not (d.get("ai_description") or "").strip()]
    if not projects:
        messagebox.showinfo("ℹ️", "Todos os projetos já têm descrição!")
        return
    if messagebox.askyesno("📝 Gerar Descrições",
                           f"Gerar descrições com IA para {len(projects)} projetos?\n"
                           f"Modelo: {_model_name(app, 'text_quality')}"):
        run_description_generation(app, projects, "projetos sem descrição")


def generate_descriptions_for_all(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    all_projects = list(app.database.keys())
    if not all_projects:
        messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
        return
    if messagebox.askyesno("⚠️ Gerar para Todos",
                           f"Substituir descrições de TODOS os {len(all_projects)} projetos?\n"
                           f"Deseja backup antes?", icon="warning"):
        manual_backup(app)
    if messagebox.askyesno("📝 Confirmar", f"Gerar {len(all_projects)} descrições?"):
        run_description_generation(app, all_projects, "todos os projetos")


def generate_descriptions_for_filter(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    from actions.scanning import get_filtered_projects
    filtered = get_filtered_projects(app)
    if not filtered:
        messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
        return
    if messagebox.askyesno("📝 Gerar Descrições do Filtro",
                           f"Gerar descrições para {len(filtered)} projetos do filtro atual?"):
        run_description_generation(app, filtered, "filtro atual")


def run_description_generation(app, projects_list, description):
    app.analyzing = True
    app.stop_analysis = False
    total = len(projects_list)

    def generate_batch():
        app.root.after(0, lambda: show_progress_ui(app))
        completed = 0
        for i, path in enumerate(projects_list, 1):
            if app.stop_analysis:
                break
            project_name = app.database[path].get("name", "Sem nome")[:30]
            app.root.after(0, lambda i=i, t=total, n=project_name:
                            update_progress(app, i, t, f"📝 Gerando: {n}"))
            generate_ai_description(app, path, app.database[path])
            completed = i
        app.analyzing = False
        final_msg = f"✓ {completed} descrições geradas ({description})"
        if app.stop_analysis and completed < total:
            final_msg = f"⏹ Parado: {completed}/{total} descrições ({description})"
        app.root.after(0, lambda: app.status_bar.config(text=final_msg))
        app.root.after(0, lambda: hide_progress_ui(app))
        app.root.after(0, lambda: messagebox.showinfo(
            "✓ Concluído" if not app.stop_analysis else "⏹ Interrompido", final_msg))
        app.stop_analysis = False

    threading.Thread(target=generate_batch, daemon=True).start()
