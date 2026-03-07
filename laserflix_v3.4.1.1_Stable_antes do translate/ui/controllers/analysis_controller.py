"""
ui/controllers/analysis_controller.py — Controller de Análise IA (Fase 3)

Responsabilidades:
- Gerenciar análise de projetos (single/batch)
- Gerenciar geração de descrições (single/batch)
- Coordenar com AnalysisManager (core)
- Gerenciar UI de progresso (show/hide/update)
- Callbacks de conclusão/erro
- Thread-safe operations

EXTRAÍDO DE: main_window.py (~150 linhas)
TAMANHO: ~250 linhas
LIMITE: 300 linhas
STATUS: ✅ OK
"""
import os
import threading
from typing import Optional, Callable
from tkinter import messagebox
from utils.logging_setup import LOGGER


class AnalysisController:
    """
    Controller de análise IA - gerencia análises e descrições.
    
    Princípio de Responsabilidade Única:
    - ANÁLISE: Coordena análise de projetos (categories + tags)
    - DESCRIÇÕES: Coordena geração de descrições AI
    - PROGRESSO: Gerencia UI de progresso (callbacks)
    - THREADS: Operações assíncronas seguras
    """
    
    def __init__(self, analysis_manager, text_generator, db_manager, ollama_client):
        """
        Args:
            analysis_manager: AnalysisManager (core)
            text_generator: TextGenerator (ai)
            db_manager: DatabaseManager (core)
            ollama_client: OllamaClient (ai)
        """
        self.analysis_manager = analysis_manager
        self.text_generator = text_generator
        self.db_manager = db_manager
        self.ollama = ollama_client
        self.logger = LOGGER
        
        # Callbacks de UI (conectados pelo main_window)
        self.on_show_progress: Optional[Callable] = None
        self.on_hide_progress: Optional[Callable] = None
        self.on_update_progress: Optional[Callable] = None
        self.on_analysis_complete: Optional[Callable] = None
        self.on_refresh_ui: Optional[Callable] = None  # Dispara display_projects()
    
    # ═══════════════════════════════════════════════════════════════════
    # ANÁLISE DE PROJETOS (categories + tags)
    # ═══════════════════════════════════════════════════════════════════
    
    def setup_callbacks(self) -> None:
        """
        Configura callbacks do AnalysisManager.
        Chamado pelo main_window no __init__.
        """
        self.analysis_manager.on_start = self._on_analysis_start
        self.analysis_manager.on_progress = self._on_analysis_progress
        self.analysis_manager.on_complete = self._on_analysis_done
        self.analysis_manager.on_error = self._on_analysis_error
    
    def analyze_single(self, path: str, database: dict) -> None:
        """
        Analisa um projeto individual (categories + tags).
        
        Args:
            path: Caminho do projeto
            database: Database reference
        """
        self.analysis_manager.analyze_single(path, database)
    
    def analyze_only_new(self, database: dict) -> None:
        """
        Analisa apenas projetos não analisados.
        
        Args:
            database: Database reference
        """
        targets = self.analysis_manager.get_unanalyzed_projects(database)
        
        if not targets:
            messagebox.showinfo("✅ Completo", "Todos os projetos já foram analisados!")
            return
        
        if messagebox.askyesno(
            "🤖 Analisar Novos",
            f"Analisar {len(targets)} projeto(s) não analisado(s)?\n\n"
            "Isso irá gerar categorias e tags automaticamente."
        ):
            self.analysis_manager.analyze_batch(targets, database)
    
    def reanalyze_all(self, database: dict) -> None:
        """
        Reanalisar TODOS os projetos (sobrescreve análises anteriores).
        
        Args:
            database: Database reference
        """
        targets = self.analysis_manager.get_all_projects(database)
        
        if not targets:
            messagebox.showinfo("Banco Vazio", "Nenhum projeto no banco.")
            return
        
        if messagebox.askyesno(
            "🔄 Reanalisar Tudo",
            f"Reanalisar {len(targets)} projeto(s)?\n\n"
            "⚠️ Isso irá SOBRESCREVER categorias e tags existentes.",
            icon="warning"
        ):
            self.analysis_manager.analyze_batch(targets, database)
    
    def stop_analysis(self) -> None:
        """
        Para análise em andamento.
        """
        self.analysis_manager.stop()
    
    # ═══════════════════════════════════════════════════════════════════
    # GERAÇÃO DE DESCRIÇÕES (AI)
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_description_single(self, path: str, database: dict, callbacks: dict) -> None:
        """
        Gera descrição para um projeto (usado no modal).
        
        Args:
            path: Caminho do projeto
            database: Database reference
            callbacks: Dict com {on_start, on_success, on_error}
        """
        if "on_start" in callbacks:
            callbacks["on_start"]()
        
        def _run():
            try:
                desc = self.text_generator.generate_description(path, database[path])
                database[path]["ai_description"] = desc
                self.db_manager.save_database()
                
                if "on_success" in callbacks:
                    callbacks["on_success"](desc)
            
            except Exception as e:
                self.logger.error("Erro ao gerar descrição: %s", e)
                if "on_error" in callbacks:
                    callbacks["on_error"](str(e))
        
        threading.Thread(target=_run, daemon=True).start()
    
    def generate_descriptions_for_new(self, database: dict) -> None:
        """
        Gera descrições apenas para projetos SEM descrição.
        
        Args:
            database: Database reference
        """
        targets = [
            p for p, d in database.items() 
            if not d.get("ai_description", "").strip()
        ]
        
        if not targets:
            messagebox.showinfo("✅ Completo", "Todos os projetos já têm descrição!")
            return
        
        if messagebox.askyesno(
            "📝 Gerar Descrições",
            f"Gerar descrição para {len(targets)} projeto(s)?\n\n"
            "Isso pode demorar alguns minutos."
        ):
            self._batch_generate_descriptions(targets, database)
    
    def generate_descriptions_for_all(self, database: dict) -> None:
        """
        Gera descrições para TODOS os projetos (sobrescreve existentes).
        
        Args:
            database: Database reference
        """
        targets = list(database.keys())
        
        if not targets:
            messagebox.showinfo("Banco Vazio", "Nenhum projeto no banco.")
            return
        
        if messagebox.askyesno(
            "📝 Regenerar Descrições",
            f"Gerar descrição para {len(targets)} projeto(s)?\n\n"
            "⚠️ Isso irá SOBRESCREVER descrições existentes.",
            icon="warning"
        ):
            self._batch_generate_descriptions(targets, database)
    
    def _batch_generate_descriptions(self, targets: list, database: dict) -> None:
        """
        Gera descrições em batch (thread separada).
        
        Args:
            targets: Lista de paths
            database: Database reference
        """
        if self.on_show_progress:
            self.on_show_progress()
        
        def _run():
            done = 0
            skipped = 0
            
            for i, path in enumerate(targets, 1):
                # Verifica stop flag
                if self.ollama.stop_flag:
                    break
                
                # Valida path
                if not os.path.isdir(path):
                    skipped += 1
                    continue
                
                try:
                    # Atualiza progresso
                    project_name = os.path.basename(path)
                    if self.on_update_progress:
                        self.on_update_progress(i, len(targets), f"📝 {project_name}")
                    
                    # Gera descrição
                    desc = self.text_generator.generate_description(path, database[path])
                    database[path]["ai_description"] = desc
                    done += 1
                    
                    # Salva a cada 5 descrições
                    if done % 5 == 0:
                        self.db_manager.save_database()
                
                except Exception as e:
                    self.logger.error("Erro ao gerar descrição para %s: %s", path, e)
                    skipped += 1
            
            # Salva final
            self.db_manager.save_database()
            
            # Esconde progresso
            if self.on_hide_progress:
                self.on_hide_progress()
            
            # Refresh UI
            if self.on_refresh_ui:
                self.on_refresh_ui()
            
            # Mensagem final
            msg = f"✅ {done} descrição(ões) gerada(s)"
            if skipped > 0:
                msg += f" ({skipped} pulada(s))"
            
            if self.on_analysis_complete:
                self.on_analysis_complete(msg)
        
        threading.Thread(target=_run, daemon=True).start()
    
    # ═══════════════════════════════════════════════════════════════════
    # CALLBACKS INTERNOS (chamados pelo AnalysisManager)
    # ═══════════════════════════════════════════════════════════════════
    
    def _on_analysis_start(self) -> None:
        """Chamado quando análise batch inicia."""
        if self.on_show_progress:
            self.on_show_progress()
    
    def _on_analysis_progress(self, current: int, total: int, message: str = "") -> None:
        """Chamado a cada projeto analisado."""
        if self.on_update_progress:
            self.on_update_progress(current, total, message)
    
    def _on_analysis_done(self, done: int, skipped: int) -> None:
        """Chamado quando análise batch termina."""
        if self.on_hide_progress:
            self.on_hide_progress()
        
        if self.on_refresh_ui:
            self.on_refresh_ui()
        
        msg = f"✅ Análise: {done} projeto(s)"
        if skipped > 0:
            msg += f" ({skipped} pulado(s))"
        
        if self.on_analysis_complete:
            self.on_analysis_complete(msg)
    
    def _on_analysis_error(self, error_msg: str) -> None:
        """Chamado quando ocorre erro crítico."""
        messagebox.showwarning("⚠️ Erro na Análise", error_msg)
