"""
LASERFLIX — Analysis Workers
Threading de análise em lote (categorias/tags/descrições)
"""

import threading
from tkinter import messagebox


class AnalysisWorker:
    """Gerencia análise em lote com threading"""

    def __init__(self, app):
        self.app = app
        self.db = app.database
        self.ollama = app.ollama
        self.ui = app.ui

    def analyze_only_new(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        unanalyzed = [p for p, d in self.db.data.items() if not d.get("analyzed")]
        if not unanalyzed:
            messagebox.showinfo("ℹ️", "Todos os projetos já foram analisados!")
            return
        model_name = self.ollama._model_name("text_fast" if len(unanalyzed) > 50 else "text_quality")
        if messagebox.askyesno("🆕 Analisar Novos", f"Analisar {len(unanalyzed)} projetos novos?\n\nModelo: {model_name}\nVocê poderá interromper a qualquer momento."):
            self._run_analysis(unanalyzed, "novos")

    def reanalyze_all(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.db.data.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Reanalisar Todos", f"Reanalisar TODOS os {len(all_projects)} projetos?\nCategorias e tags existentes serão SUBSTITUÍDAS.\n\nDeseja criar um backup antes?", icon="warning"):
            self.app.backup.manual_backup()
        if messagebox.askyesno("🔄 Confirmar Reanalise", f"Prosseguir com a reanálise de {len(all_projects)} projetos?"):
            self._run_analysis(all_projects, "todos")

    def analyze_current_filter(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.app.filter.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📊 Analisar Filtro", f"Analisar {len(filtered)} projetos?"):
            self._run_analysis(filtered, "filtro atual")

    def _run_analysis(self, projects_list, description):
        self.app.analyzing = True
        self.app.stop_analysis = False
        total = len(projects_list)
        role = "text_fast" if total > 50 else "text_quality"
        model_used = self.ollama._model_name(role)

        def analyze_batch():
            self.ui.root.after(0, self.ui.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.app.stop_analysis:
                    break
                project_name = self.db.data[path].get("name", "Sem nome")[:30]
                self.ui.root.after(0, lambda i=i, t=total, n=project_name: self.ui.update_progress(i, t, f"🤖 [{model_used[:15]}] {n}"))
                categories, tags = self.ollama.analyze_with_ai(path, batch_size=total)
                self.db.data[path]["categories"] = categories
                self.db.data[path]["tags"] = tags
                self.db.data[path]["analyzed"] = True
                self.db.data[path]["analyzed_model"] = model_used
                self.db.save()
                completed = i
            self.app.analyzing = False
            final_msg = f"✓ {completed} projetos analisados ({description}) [{model_used}]"
            if self.app.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} ({description})"
            self.ui.root.after(0, self.ui.update_sidebar)
            self.ui.root.after(0, self.ui.display_projects)
            self.ui.root.after(0, lambda: self.ui.status_bar.config(text=final_msg))
            self.ui.root.after(0, self.ui.hide_progress_ui)
            self.ui.root.after(0, lambda: messagebox.showinfo("✓ Concluído" if not self.app.stop_analysis else "⏹ Interrompido", final_msg))
            self.app.stop_analysis = False

        threading.Thread(target=analyze_batch, daemon=True).start()

    def generate_descriptions_for_new(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        projects = [p for p, d in self.db.data.items() if not (d.get("ai_description") or "").strip()]
        if not projects:
            messagebox.showinfo("ℹ️", "Todos os projetos já têm descrição!")
            return
        if messagebox.askyesno("📝 Gerar Descrições", f"Gerar descrições com IA para {len(projects)} projetos?\nModelo: {self.ollama._model_name('text_quality')}"):
            self._run_description_generation(projects, "projetos sem descrição")

    def generate_descriptions_for_all(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.db.data.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Gerar para Todos", f"Substituir descrições de TODOS os {len(all_projects)} projetos?\nDeseja backup antes?", icon="warning"):
            self.app.backup.manual_backup()
        if messagebox.askyesno("📝 Confirmar", f"Gerar {len(all_projects)} descrições?"):
            self._run_description_generation(all_projects, "todos os projetos")

    def generate_descriptions_for_filter(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.app.filter.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📝 Gerar Descrições do Filtro", f"Gerar descrições para {len(filtered)} projetos do filtro atual?"):
            self._run_description_generation(filtered, "filtro atual")

    def _run_description_generation(self, projects_list, description):
        self.app.analyzing = True
        self.app.stop_analysis = False
        total = len(projects_list)

        def generate_batch():
            self.ui.root.after(0, self.ui.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.app.stop_analysis:
                    break
                project_name = self.db.data[path].get("name", "Sem nome")[:30]
                self.ui.root.after(0, lambda i=i, t=total, n=project_name: self.ui.update_progress(i, t, f"📝 Gerando: {n}"))
                self.ollama.generate_ai_description(path, self.db.data[path])
                completed = i
            self.app.analyzing = False
            final_msg = f"✓ {completed} descrições geradas ({description})"
            if self.app.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} descrições ({description})"
            self.ui.root.after(0, lambda: self.ui.status_bar.config(text=final_msg))
            self.ui.root.after(0, self.ui.hide_progress_ui)
            self.ui.root.after(0, lambda: messagebox.showinfo("✓ Concluído" if not self.app.stop_analysis else "⏹ Interrompido", final_msg))
            self.app.stop_analysis = False

        threading.Thread(target=generate_batch, daemon=True).start()
