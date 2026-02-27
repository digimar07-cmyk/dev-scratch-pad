"""
LASERFLIX Ollama — Integração com IA
"""

from .client import OllamaClient
from .vision import VisionAnalyzer
from .analyzer import ProjectAnalyzer
from .description import DescriptionGenerator


class OllamaManager:
    """Gerenciador unificado do Ollama"""

    def __init__(self, app):
        self.app = app
        self.client = OllamaClient()
        self.vision = VisionAnalyzer(self.client)
        self.analyzer = ProjectAnalyzer(self.client, self.vision)
        self.description = DescriptionGenerator(self.client, self.vision)

    def _model_name(self, role):
        """Retorna nome do modelo para o papel"""
        return self.app.config.models.get(role, "qwen2.5:7b-instruct-q4_K_M")

    def analyze_with_ai(self, project_path, batch_size=1):
        """Analisa projeto e retorna (categories, tags)"""
        return self.analyzer.analyze(project_path, batch_size, self._model_name)

    def generate_ai_description(self, project_path, data):
        """Gera descrição comercial"""
        return self.description.generate(project_path, data, self._model_name)

    def open_model_settings(self):
        """Abre modal de configuração de modelos"""
        from tkinter import messagebox
        messagebox.showinfo("Em Desenvolvimento", "Configuração de modelos em desenvolvimento...")


__all__ = ["OllamaManager", "OllamaClient", "VisionAnalyzer", "ProjectAnalyzer", "DescriptionGenerator"]
