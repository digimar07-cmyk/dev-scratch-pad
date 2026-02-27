"""
LASERFLIX — File Analyzer
Análise de estrutura de arquivos de projetos
"""

import os
import logging

LOGGER = logging.getLogger("Laserflix")


class FileAnalyzer:
    """Analisa estrutura de projetos"""

    def analyze_structure(self, project_path):
        """Retorna dict com estrutura do projeto"""
        structure = {
            "total_files": 0,
            "total_subfolders": 0,
            "file_types": {},
            "subfolders": [],
            "images": [],
            "documents": [],
            "has_svg": False,
            "has_pdf": False,
            "has_dxf": False,
            "has_ai": False,
        }
        try:
            for root, dirs, files in os.walk(project_path):
                structure["total_files"] += len(files)
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    if ext == ".svg":
                        structure["has_svg"] = True
                    elif ext == ".pdf":
                        structure["has_pdf"] = True
                    elif ext == ".dxf":
                        structure["has_dxf"] = True
                    elif ext == ".ai":
                        structure["has_ai"] = True
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        except Exception as e:
            LOGGER.exception(f"Falha ao analisar estrutura: {e}")
        return structure

    def find_first_image(self, project_path):
        """Retorna caminho da primeira imagem do projeto"""
        image_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        try:
            for root, _, files in os.walk(project_path):
                for file in files:
                    if file.lower().endswith(image_exts):
                        return os.path.join(root, file)
        except Exception:
            pass
        return None

    def get_all_images(self, project_path):
        """Retorna lista de todas as imagens do projeto"""
        images = []
        image_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        try:
            for root, _, files in os.walk(project_path):
                for file in files:
                    if file.lower().endswith(image_exts):
                        images.append(os.path.join(root, file))
        except Exception:
            pass
        return images
