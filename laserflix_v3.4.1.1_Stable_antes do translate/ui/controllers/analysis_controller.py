"""
ui/controllers/analysis_controller.py

Controller responsável por:
- Análise IA (single, batch, new, all)
- Geração de descrições (single, batch, new, all)
- Coordenação com AnalysisManager
- UI de progresso (show/hide, update)

⚠️ LIMITE: 300 linhas MAX
"""

class AnalysisController:
    def __init__(self, analysis_manager, text_generator, database, callbacks):
        """
        Args:
            analysis_manager (AnalysisManager): Gerenciador de análises
            text_generator (TextGenerator): Gerador de descrições
            database (dict): Referência ao database
            callbacks (dict): Callbacks de UI (show_progress, hide_progress, update_progress, on_complete)
        """
        self.analysis_manager = analysis_manager
        self.text_generator = text_generator
        self.database = database
        self.callbacks = callbacks
    
    def analyze_single(self, path: str):
        """
        Analisa um projeto individualmente.
        TODO: Migrar de main_window.py na Fase 3
        """
        pass
    
    def analyze_batch(self, paths: list, mode: str):
        """
        Analisa múltiplos projetos (new ou all).
        TODO: Migrar de main_window.py na Fase 3
        """
        pass
    
    def generate_descriptions_batch(self, paths: list):
        """
        Gera descrições para múltiplos projetos.
        TODO: Migrar de main_window.py na Fase 3
        """
        pass
