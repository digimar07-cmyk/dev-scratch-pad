"""
LASERFLIX Media — Gerenciamento de Mídia
"""

from .thumbnails import ThumbnailCache
from .files import FileAnalyzer


class MediaManager:
    """Gerenciador unificado de mídia"""

    def __init__(self):
        self.thumbnail_cache = ThumbnailCache()
        self.file_analyzer = FileAnalyzer()

    def get_cover_image(self, project_path):
        """Retorna thumbnail do projeto"""
        return self.thumbnail_cache.get_thumbnail(project_path, self.file_analyzer)

    def get_all_project_images(self, project_path):
        """Retorna todas as imagens do projeto"""
        return self.file_analyzer.get_all_images(project_path)

    def open_folder(self, folder_path):
        """Abre pasta no explorer"""
        import subprocess
        import platform
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception:
            pass

    def open_image(self, image_path):
        """Abre imagem no visualizador padrão"""
        import subprocess
        import platform
        try:
            if platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", image_path])
            else:
                subprocess.Popen(["xdg-open", image_path])
        except Exception:
            pass


__all__ = ["MediaManager", "ThumbnailCache", "FileAnalyzer"]
