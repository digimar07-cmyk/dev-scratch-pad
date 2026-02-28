"""Análise em lote de projetos."""
import threading
from tkinter import messagebox
from core.config import FAST_MODEL_THRESHOLD
from analysis.analyzer import analyze_with_ai, _choose_text_role
from ollama.ollama_client import _model_name
from data.persistence import save_database, manual_backup
from ui.progress_ui import show_progress_ui, hide_progress_ui, update_progress


def analyze_only_new(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    unanalyzed = [p for p, d in app.database.items() if not d.get("analyzed")]
    if not unanalyzed:
        messagebox.showinfo("ℹ️", "Todos os projetos já foram analisados!")
        return
    model_info = _model_name(app, "text_fast") if len(unanalyzed) > FAST_MODEL_THRESHOLD else _model_name(app, "text_quality")
    if messagebox.askyesno("🆕 Analisar Novos",
                           f"Analisar {len(unanalyzed)} projetos novos?\n\n"
                           f"Modelo: {model_info}\n"
                           f"Você poderá interromper a qualquer momento."):
        run_analysis(app, unanalyzed, "novos")


def reanalyze_all(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    all_projects = list(app.database.keys())
    if not all_projects:
        messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
        return
    if messagebox.askyesno("⚠️ Reanalisar Todos",
                           f"Reanalisar TODOS os {len(all_projects)} projetos?\n"
                           f"Categorias e tags existentes serão SUBSTITUÍDAS.\n\n"
                           f"Deseja criar um backup antes?", icon="warning"):
        manual_backup(app)
    if messagebox.askyesno("🔄 Confirmar Reanalise",
                           f"Prosseguir com a reanálise de {len(all_projects)} projetos?"):
        run_analysis(app, all_projects, "todos")


def analyze_current_filter(app):
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    from actions.scanning import get_filtered_projects
    filtered = get_filtered_projects(app)
    if not filtered:
        messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
        return
    if messagebox.askyesno("📊 Analisar Filtro", f"Analisar {len(filtered)} projetos?"):
        run_analysis(app, filtered, "filtro atual")


def reanalyze_specific_category(app):
    import tkinter as tk
    from tkinter import ttk
    from collections import Counter
    
    if app.analyzing:
        messagebox.showinfo("ℹ️", "Análise em andamento!")
        return
    all_cats = set()
    for d in app.database.values():
        all_cats.update(d.get("categories", []))
    categories = sorted([c for c in all_cats if c and c != "Sem Categoria"])
    if not categories:
        messagebox.showinfo("ℹ️", "Nenhuma categoria encontrada!")
        return
    cat_win = tk.Toplevel(app.root)
    cat_win.title("🎯 Selecionar Categoria")
    cat_win.state("zoomed")
    cat_win.configure(bg="#141414")
    cat_win.transient(app.root)
    cat_win.grab_set()
    tk.Label(cat_win, text="🎯 Reanalisar Categoria", font=("Arial", 18, "bold"),
             bg="#141414", fg="#E50914").pack(pady=15)
    tk.Label(cat_win, text="Selecione a categoria:", font=("Arial", 11),
             bg="#141414", fg="#FFFFFF").pack(pady=(0, 10))
    list_frame = tk.Frame(cat_win, bg="#2A2A2A")
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    listbox = tk.Listbox(list_frame, bg="#2A2A2A", fg="#FFFFFF", font=("Arial", 11),
                         selectmode=tk.SINGLE, yscrollcommand=scrollbar.set,
                         relief="flat", selectbackground="#E50914", selectforeground="#FFFFFF")
    listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scrollbar.config(command=listbox.yview)
    for cat in categories:
        count = sum(1 for d in app.database.values() if cat in d.get("categories", []))
        listbox.insert(tk.END, f"{cat} ({count} projetos)")
    selected_category = [None]
    def on_select():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma categoria!")
            return
        selected_category[0] = categories[selection[0]]
        cat_win.destroy()
    btn_frame = tk.Frame(cat_win, bg="#141414")
    btn_frame.pack(fill="x", padx=20, pady=15)
    tk.Button(btn_frame, text="✓ Confirmar", command=on_select,
              bg="#1DB954", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✕ Cancelar", command=cat_win.destroy,
              bg="#666666", fg="#FFFFFF", font=("Arial", 12, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=10).pack(side="right", padx=5)
    cat_win.wait_window()
    if not selected_category[0]:
        return
    projects = [p for p, d in app.database.items() if selected_category[0] in d.get("categories", [])]
    if messagebox.askyesno("🎯 Confirmar",
                           f"Reanalisar {len(projects)} projetos da categoria '{selected_category[0]}'?"):
        run_analysis(app, projects, f"categoria '{selected_category[0]}'")


def run_analysis(app, projects_list, description):
    app.analyzing = True
    app.stop_analysis = False
    total = len(projects_list)
    role = _choose_text_role(total)
    model_used = _model_name(app, role)

    def analyze_batch():
        app.root.after(0, lambda: show_progress_ui(app))
        completed = 0
        for i, path in enumerate(projects_list, 1):
            if app.stop_analysis:
                break
            project_name = app.database[path].get("name", "Sem nome")[:30]
            app.root.after(0, lambda i=i, t=total, n=project_name:
                            update_progress(app, i, t, f"🤖 [{model_used[:15]}] {n}"))
            categories, tags = analyze_with_ai(app, path, batch_size=total)
            app.database[path]["categories"] = categories
            app.database[path]["tags"] = tags
            app.database[path]["analyzed"] = True
            app.database[path]["analyzed_model"] = model_used
            save_database(app)
            completed = i
        app.analyzing = False
        final_msg = f"✓ {completed} projetos analisados ({description}) [{model_used}]"
        if app.stop_analysis and completed < total:
            final_msg = f"⏹ Parado: {completed}/{total} ({description})"
        
        from ui.sidebar import update_sidebar
        from ui.project_grid import display_projects
        
        app.root.after(0, lambda: update_sidebar(app))
        app.root.after(0, lambda: display_projects(app))
        app.root.after(0, lambda: app.status_bar.config(text=final_msg))
        app.root.after(0, lambda: hide_progress_ui(app))
        app.root.after(0, lambda: messagebox.showinfo(
            "✓ Concluído" if not app.stop_analysis else "⏹ Interrompido", final_msg))
        app.stop_analysis = False

    threading.Thread(target=analyze_batch, daemon=True).start()
