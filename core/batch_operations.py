"""Batch Operations - análises e gerações em lote"""
import threading
from tkinter import messagebox
from core.logging_setup import LOGGER


class BatchOperations:
    def __init__(self, app):
        self.app = app
        self.logger = LOGGER

    def analyze_only_new(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        unanalyzed = [p for p, d in self.app.database.items() if not d.get("analyzed")]
        if not unanalyzed:
            messagebox.showinfo("ℹ️", "Todos os projetos já foram analisados!")
            return
        from core.config import FAST_MODEL_THRESHOLD
        model_info = self.app.ollama._model_name("text_fast") if len(unanalyzed) > FAST_MODEL_THRESHOLD else self.app.ollama._model_name("text_quality")
        if messagebox.askyesno("🆕 Analisar Novos",
                               f"Analisar {len(unanalyzed)} projetos novos?\n\n"
                               f"Modelo: {model_info}\n"
                               f"Você poderá interromper a qualquer momento."):
            self.run_analysis(unanalyzed, "novos")

    def reanalyze_all(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.app.database.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Reanalisar Todos",
                               f"Reanalisar TODOS os {len(all_projects)} projetos?\n"
                               f"Categorias e tags existentes serão SUBSTITUÍDAS.\n\n"
                               f"Deseja criar um backup antes?", icon="warning"):
            self.app.manual_backup()
        if messagebox.askyesno("🔄 Confirmar Reanalise",
                               f"Prosseguir com a reanálise de {len(all_projects)} projetos?"):
            self.run_analysis(all_projects, "todos")

    def analyze_current_filter(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.app.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📊 Analisar Filtro", f"Analisar {len(filtered)} projetos?"):
            self.run_analysis(filtered, "filtro atual")

    def reanalyze_specific_category(self):
        import tkinter as tk
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_cats = set()
        for d in self.app.database.values():
            all_cats.update(d.get("categories", []))
        categories = sorted([c for c in all_cats if c and c != "Sem Categoria"])
        if not categories:
            messagebox.showinfo("ℹ️", "Nenhuma categoria encontrada!")
            return
        # UI simplificada - vai implementar depois se precisar
        messagebox.showinfo("ℹ️", "Função em desenvolvimento")

    def run_analysis(self, projects_list, description):
        self.app.analyzing = True
        self.app.stop_analysis = False
        self.app.ollama.stop_analysis = False
        total = len(projects_list)
        role = self.app.analyzer._choose_text_role(total)
        model_used = self.app.ollama._model_name(role)

        def analyze_batch():
            self.app.root.after(0, self.app.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.app.stop_analysis:
                    break
                project_name = self.app.database[path].get("name", "Sem nome")[:30]
                self.app.root.after(0, lambda i=i, t=total, n=project_name:
                                self.app.update_progress(i, t, f"🤖 [{model_used[:15]}] {n}"))
                categories, tags = self.app.analyzer.analyze_with_ai(path, batch_size=total)
                self.app.database[path]["categories"] = categories
                self.app.database[path]["tags"] = tags
                self.app.database[path]["analyzed"] = True
                self.app.database[path]["analyzed_model"] = model_used
                self.app.save_database()
                completed = i
            self.app.analyzing = False
            final_msg = f"✓ {completed} projetos analisados ({description}) [{model_used}]"
            if self.app.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} ({description})"
            self.app.root.after(0, self.app.update_sidebar)
            self.app.root.after(0, self.app.display_projects)
            self.app.root.after(0, lambda: self.app.status_bar.config(text=final_msg))
            self.app.root.after(0, self.app.hide_progress_ui)
            self.app.root.after(0, lambda: messagebox.showinfo(
                "✓ Concluído" if not self.app.stop_analysis else "⏹ Interrompido", final_msg))
            self.app.stop_analysis = False
            self.app.ollama.stop_analysis = False

        threading.Thread(target=analyze_batch, daemon=True).start()

    # -----------------------------------------------------------------------
    # GERAÇÃO DE DESCRIÇÕES EM LOTE
    # -----------------------------------------------------------------------
    def generate_descriptions_for_new(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        projects = [p for p, d in self.app.database.items()
                    if not (d.get("ai_description") or "").strip()]
        if not projects:
            messagebox.showinfo("ℹ️", "Todos os projetos já têm descrição!")
            return
        if messagebox.askyesno("📝 Gerar Descrições",
                               f"Gerar descrições com IA para {len(projects)} projetos?\n"
                               f"Modelo: {self.app.ollama._model_name('text_quality')}"):
            self.run_description_generation(projects, "projetos sem descrição")

    def generate_descriptions_for_all(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        all_projects = list(self.app.database.keys())
        if not all_projects:
            messagebox.showinfo("ℹ️", "Nenhum projeto encontrado!")
            return
        if messagebox.askyesno("⚠️ Gerar para Todos",
                               f"Substituir descrições de TODOS os {len(all_projects)} projetos?\n"
                               f"Deseja backup antes?", icon="warning"):
            self.app.manual_backup()
        if messagebox.askyesno("📝 Confirmar", f"Gerar {len(all_projects)} descrições?"):
            self.run_description_generation(all_projects, "todos os projetos")

    def generate_descriptions_for_filter(self):
        if self.app.analyzing:
            messagebox.showinfo("ℹ️", "Análise em andamento!")
            return
        filtered = self.app.get_filtered_projects()
        if not filtered:
            messagebox.showinfo("ℹ️", "Nenhum projeto no filtro atual!")
            return
        if messagebox.askyesno("📝 Gerar Descrições do Filtro",
                               f"Gerar descrições para {len(filtered)} projetos do filtro atual?"):
            self.run_description_generation(filtered, "filtro atual")

    def run_description_generation(self, projects_list, description):
        self.app.analyzing = True
        self.app.stop_analysis = False
        self.app.ollama.stop_analysis = False
        total = len(projects_list)

        def generate_batch():
            self.app.root.after(0, self.app.show_progress_ui)
            completed = 0
            for i, path in enumerate(projects_list, 1):
                if self.app.stop_analysis:
                    break
                project_name = self.app.database[path].get("name", "Sem nome")[:30]
                self.app.root.after(0, lambda i=i, t=total, n=project_name:
                                self.app.update_progress(i, t, f"📝 Gerando: {n}"))
                self.app.desc_generator.generate_ai_description(path, self.app.database[path], self.app.database)
                self.app.save_database()
                completed = i
            self.app.analyzing = False
            final_msg = f"✓ {completed} descrições geradas ({description})"
            if self.app.stop_analysis and completed < total:
                final_msg = f"⏹ Parado: {completed}/{total} descrições ({description})"
            self.app.root.after(0, lambda: self.app.status_bar.config(text=final_msg))
            self.app.root.after(0, self.app.hide_progress_ui)
            self.app.root.after(0, lambda: messagebox.showinfo(
                "✓ Concluído" if not self.app.stop_analysis else "⏹ Interrompido", final_msg))
            self.app.stop_analysis = False
            self.app.ollama.stop_analysis = False

        threading.Thread(target=generate_batch, daemon=True).start()
