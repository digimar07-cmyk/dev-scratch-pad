"""
Gerenciador de análises IA de projetos.
Encapsula toda a lógica de análise, progresso e callbacks.

S-05: Thread watchdog para timeout automático (120s)
"""
import os
import threading
import time
from typing import Callable, Optional, List, Dict, Any

from config.settings import FAST_MODEL_THRESHOLD
from utils.logging_setup import LOGGER


class AnalysisManager:
    """
    Gerencia análises de projetos com IA.
    Separa lógica de análise da UI.
    
    S-05: Watchdog protege contra travamentos (timeout 120s).
    """
    
    # S-05: Timeout para análise de projeto individual
    ANALYSIS_TIMEOUT = 120  # segundos
    
    def __init__(self, text_generator, db_manager, ollama_client):
        """
        Inicializa o gerenciador de análises.
        
        Args:
            text_generator: Gerador de texto IA
            db_manager: Gerenciador de banco de dados
            ollama_client: Cliente Ollama
        """
        self.text_generator = text_generator
        self.db_manager = db_manager
        self.ollama = ollama_client
        self.logger = LOGGER
        
        # Estado
        self.is_analyzing = False
        self.should_stop = False
        
        # S-05: Watchdog state
        self._current_project_start: Optional[float] = None
        self._current_project_path: Optional[str] = None
        self._watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_active = False
        
        # Callbacks (conecta com UI)
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_start: Optional[Callable[[], None]] = None
        self.on_complete: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def _start_watchdog(self, project_path: str) -> None:
        """
        S-05: Inicia watchdog para projeto atual.
        Monitora timeout e cancela se necessário.
        """
        self._current_project_path = project_path
        self._current_project_start = time.time()
        
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            return  # Já ativo
        
        self._watchdog_active = True
        
        def _watchdog():
            while self._watchdog_active:
                time.sleep(5)  # Verifica a cada 5s
                
                if not self._current_project_start:
                    continue
                
                elapsed = time.time() - self._current_project_start
                
                if elapsed > self.ANALYSIS_TIMEOUT:
                    name = os.path.basename(self._current_project_path or "unknown")
                    self.logger.warning(
                        "⏰ TIMEOUT: Análise de '%s' travou após %.0fs. Cancelando...",
                        name, elapsed
                    )
                    self.stop()
                    self._stop_watchdog()
                    break
        
        self._watchdog_thread = threading.Thread(target=_watchdog, daemon=True)
        self._watchdog_thread.start()
    
    def _stop_watchdog(self) -> None:
        """
        S-05: Para watchdog após análise concluir/cancelar.
        """
        self._watchdog_active = False
        self._current_project_start = None
        self._current_project_path = None
    
    def analyze_single(self, project_path: str, database: Dict[str, Any]) -> None:
        """
        Analisa um único projeto.
        
        Args:
            project_path: Caminho do projeto
            database: Referência ao banco de dados
        """
        if self.is_analyzing:
            if self.on_error:
                self.on_error("Análise já em andamento")
            return
        
        self.is_analyzing = True
        self.should_stop = False
        self.ollama.stop_flag = False
        
        if self.on_start:
            self.on_start()
        
        name = database.get(project_path, {}).get("name", os.path.basename(project_path))
        
        def _worker():
            try:
                # S-05: Inicia watchdog
                self._start_watchdog(project_path)
                
                cats, tags = self.text_generator.analyze_project(project_path, batch_size=1)
                
                # S-05: Para watchdog após sucesso
                self._stop_watchdog()
                
                if project_path in database:
                    database[project_path]["categories"] = cats
                    database[project_path]["tags"] = tags
                    database[project_path]["analyzed"] = True
                    database[project_path]["analyzed_model"] = (
                        self.ollama.active_models.get("text_quality", "fallback"))
                    self.db_manager.save_database()
                
                if self.on_complete:
                    self.on_complete(1, 0)
                    
            except Exception as e:
                self._stop_watchdog()  # S-05: Para watchdog em erro
                self.logger.exception("Erro em analyze_single: %s", e)
                if self.on_error:
                    self.on_error(f"Erro ao analisar {name}: {str(e)}")
            finally:
                self.is_analyzing = False
        
        threading.Thread(target=_worker, daemon=True).start()
    
    def analyze_batch(
        self, 
        targets: List[str], 
        database: Dict[str, Any],
        filter_analyzed: bool = False
    ) -> None:
        """
        Analisa múltiplos projetos em lote.
        
        Args:
            targets: Lista de caminhos dos projetos
            database: Referência ao banco de dados
            filter_analyzed: Se True, pula projetos já analisados
        """
        if self.is_analyzing:
            if self.on_error:
                self.on_error("Análise já em andamento")
            return
        
        if filter_analyzed:
            targets = [p for p in targets if not database.get(p, {}).get("analyzed")]
        
        if not targets:
            if self.on_error:
                self.on_error("Nenhum projeto para analisar")
            return
        
        self.is_analyzing = True
        self.should_stop = False
        self.ollama.stop_flag = False
        
        if self.on_start:
            self.on_start()
        
        total = len(targets)
        batch_size = total
        
        def _worker():
            done = 0
            skipped = 0
            
            for project_path in targets:
                # Verifica se deve parar
                if self.should_stop or self.ollama.stop_flag:
                    self.logger.info("Análise interrompida pelo usuário")
                    break
                
                # Valida projeto
                if not os.path.isdir(project_path):
                    skipped += 1
                    continue
                
                # Notifica progresso
                name = database.get(project_path, {}).get(
                    "name", os.path.basename(project_path))
                
                if self.on_progress:
                    self.on_progress(done, total, f"🤖 {name}")
                
                # Analisa
                try:
                    # S-05: Inicia watchdog para este projeto
                    self._start_watchdog(project_path)
                    
                    cats, tags = self.text_generator.analyze_project(
                        project_path, batch_size=batch_size)
                    
                    # S-05: Para watchdog após sucesso
                    self._stop_watchdog()
                    
                    if project_path in database:
                        # Determina modelo usado
                        role = "text_fast" if batch_size > FAST_MODEL_THRESHOLD else "text_quality"
                        
                        database[project_path]["categories"] = cats
                        database[project_path]["tags"] = tags
                        database[project_path]["analyzed"] = True
                        database[project_path]["analyzed_model"] = \
                            self.ollama.active_models.get(role, "fallback")
                    
                    done += 1
                    
                    # Auto-save a cada 10 projetos
                    if done % 10 == 0:
                        self.db_manager.save_database()
                        self.logger.info("Auto-save: %d/%d projetos", done, total)
                
                except Exception as e:
                    self._stop_watchdog()  # S-05: Para watchdog em erro
                    self.logger.exception("Erro ao analisar %s: %s", project_path, e)
                    skipped += 1
            
            # S-05: Garante que watchdog está parado
            self._stop_watchdog()
            
            # Save final
            self.db_manager.save_database()
            
            # Notifica conclusão
            if self.on_complete:
                self.on_complete(done, skipped)
            
            self.is_analyzing = False
            self.should_stop = False
            self.ollama.stop_flag = False
        
        threading.Thread(target=_worker, daemon=True).start()
    
    def stop(self) -> None:
        """Para a análise em andamento."""
        self.should_stop = True
        self.ollama.stop_flag = True
        self._stop_watchdog()  # S-05: Para watchdog também
        self.logger.info("Solicitado parada da análise")
    
    def get_unanalyzed_projects(self, database: Dict[str, Any]) -> List[str]:
        """
        Retorna lista de projetos não analisados.
        
        Args:
            database: Banco de dados de projetos
            
        Returns:
            Lista de caminhos de projetos não analisados
        """
        return [
            p for p, d in database.items()
            if not d.get("analyzed") and os.path.isdir(p)
        ]
    
    def get_all_projects(self, database: Dict[str, Any]) -> List[str]:
        """
        Retorna lista de todos os projetos válidos.
        
        Args:
            database: Banco de dados de projetos
            
        Returns:
            Lista de caminhos de projetos
        """
        return [p for p in database if os.path.isdir(p)]
