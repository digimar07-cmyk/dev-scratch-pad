"""LASERFLIX v7.4.0 — File Handler
Gerencia operações de arquivos e estrutura de projetos
"""

import os
import re
from typing import Dict, List, Any
from collections import Counter
from PIL import Image, ImageTk
from collections import OrderedDict
import logging

LOGGER = logging.getLogger("Laserflix")


class FileHandler:
    """Gerencia operações de sistema de arquivos"""
    
    def __init__(self, thumbnail_cache_limit: int = 300):
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = thumbnail_cache_limit
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analisa estrutura de um projeto"""
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
                    
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        except Exception:
            LOGGER.exception("Falha ao analisar estrutura de %s", project_path)
        
        return structure
    
    def extract_tags_from_name(self, name: str) -> List[str]:
        """Extrai tags do nome do projeto"""
        name_clean = name
        for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
            name_clean = name_clean.replace(ext, "")
        
        name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
        name_clean = name_clean.replace("-", " ").replace("_", " ")
        
        stop_words = {
            "file", "files", "project", "design", "laser", "cut", "svg",
            "pdf", "vector", "bundle", "pack", "set", "collection"
        }
        
        words = [
            w for w in name_clean.split()
            if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words
        ]
        
        tags = []
        if len(words) >= 2:
            phrase = " ".join(words[:4])
            if len(phrase) > 3:
                tags.append(phrase.title())
        
        for w in words[:5]:
            if len(w) >= 3:
                tags.append(w.capitalize())
        
        seen, unique = set(), []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        
        return unique[:5]
    
    def get_origin_from_path(self, project_path: str) -> str:
        """Detecta origem do projeto pelo caminho"""
        try:
            parent_folder = os.path.basename(os.path.dirname(project_path))
            parent_upper = parent_folder.upper()
            
            if "CREATIVE" in parent_upper or "FABRICA" in parent_upper:
                return "Creative Fabrica"
            elif "ETSY" in parent_upper:
                return "Etsy"
            else:
                return parent_folder
        except Exception:
            return "Diversos"
    
    def find_first_image(self, project_path: str) -> str:
        """Encontra primeira imagem na pasta"""
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        
        return ""
    
    def get_all_images(self, project_path: str) -> List[str]:
        """Retorna lista de todas as imagens do projeto"""
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        images = []
        
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    images.append(os.path.join(project_path, item))
        except Exception:
            LOGGER.exception("Falha ao listar imagens de %s", project_path)
        
        return sorted(images)
    
    def load_thumbnail(self, img_path: str, size=(220, 200)) -> ImageTk.PhotoImage:
        """Carrega thumbnail com cache"""
        try:
            mtime = os.path.getmtime(img_path)
        except Exception:
            return None
        
        try:
            cached = self.thumbnail_cache.get(img_path)
            if cached:
                cached_mtime, cached_photo = cached
                if cached_mtime == mtime:
                    self.thumbnail_cache.move_to_end(img_path)
                    return cached_photo
            
            img = Image.open(img_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_cache[img_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(img_path)
            
            while len(self.thumbnail_cache) > self.thumbnail_cache_limit:
                self.thumbnail_cache.popitem(last=False)
            
            return photo
        except Exception:
            LOGGER.exception("Erro ao gerar thumbnail de %s", img_path)
            return None
    
    def load_hero_image(self, project_path: str, max_width=800) -> ImageTk.PhotoImage:
        """Carrega imagem hero (grande) da capa"""
        try:
            valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
            
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    img_path = os.path.join(project_path, item)
                    img = Image.open(img_path)
                    
                    if img.width > max_width:
                        ratio = max_width / img.width
                        img = img.resize(
                            (max_width, int(img.height * ratio)),
                            Image.Resampling.LANCZOS
                        )
                    
                    return ImageTk.PhotoImage(img)
        except Exception:
            LOGGER.exception("Falha ao carregar hero image de %s", project_path)
        
        return None
