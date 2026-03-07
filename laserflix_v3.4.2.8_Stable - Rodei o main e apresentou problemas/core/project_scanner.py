"""
Scanner de projetos e análise estrutural
"""
import os
import re
from datetime import datetime
from config.constants import FILE_EXTENSIONS
from utils.logging_setup import LOGGER


class ProjectScanner:
    """
    Escaneia pastas de projetos e analisa estrutura de arquivos.
    """
    
    def __init__(self, database):
        self.database = database
        self.logger = LOGGER
    
    def scan_projects(self, folders):
        """
        Escaneia pastas e adiciona novos projetos ao database.
        Retorna quantidade de projetos novos encontrados.
        """
        new_count = 0
        
        for root_folder in folders:
            if not os.path.exists(root_folder):
                self.logger.warning("⚠️ Pasta não encontrada: %s", root_folder)
                continue
            
            try:
                for item in os.listdir(root_folder):
                    project_path = os.path.join(root_folder, item)
                    
                    # Apenas diretórios são considerados projetos
                    if not os.path.isdir(project_path):
                        continue
                    
                    # Ignora se já existe no database
                    if project_path in self.database:
                        continue
                    
                    # Adiciona novo projeto
                    self.database[project_path] = {
                        "name": item,
                        "origin": self.get_origin_from_path(project_path),
                        "favorite": False,
                        "done": False,
                        "good": False,
                        "bad": False,
                        "categories": [],
                        "tags": [],
                        "analyzed": False,
                        "ai_description": "",
                        "added_date": datetime.now().isoformat(),
                    }
                    new_count += 1
            
            except Exception as e:
                self.logger.error("Erro ao escanear %s: %s", root_folder, e, exc_info=True)
        
        if new_count > 0:
            self.logger.info("✅ %d novos projetos encontrados", new_count)
        
        return new_count
    
    def get_origin_from_path(self, project_path):
        """
        Detecta origem do projeto baseado no nome da pasta pai.
        """
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
    
    def analyze_project_structure(self, project_path):
        """
        Analisa estrutura de arquivos do projeto.
        Retorna dicionário com estatísticas completas.
        """
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
                
                # Captura subpastas apenas do nível raiz
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    
                    # Flags de formatos específicos
                    if ext == ".svg":
                        structure["has_svg"] = True
                    elif ext == ".pdf":
                        structure["has_pdf"] = True
                    elif ext == ".dxf":
                        structure["has_dxf"] = True
                    elif ext == ".ai":
                        structure["has_ai"] = True
                    
                    # Classificação de arquivos
                    if ext in FILE_EXTENSIONS["images"] or ext in FILE_EXTENSIONS["vectors"]:
                        structure["images"].append(file)
                    elif ext in FILE_EXTENSIONS["documents"]:
                        structure["documents"].append(file)
        
        except Exception:
            self.logger.exception("Falha ao analisar estrutura de %s", project_path)
        
        return structure
    
    def extract_tags_from_name(self, name):
        """
        Extrai tags relevantes do nome do projeto.
        Remove números de SKU, extensões e stopwords.
        """
        name_clean = name
        
        # Remove extensões comuns
        for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
            name_clean = name_clean.replace(ext, "")
        
        # Remove códigos numéricos longos (SKUs)
        name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
        
        # Substitui separadores por espaços
        name_clean = name_clean.replace("-", " ").replace("_", " ")
        
        # Stopwords (palavras genéricas a ignorar)
        stop_words = {
            "file", "files", "project", "design", "laser", "cut", "svg",
            "pdf", "vector", "bundle", "pack", "set", "collection"
        }
        
        # Extrai palavras relevantes
        words = [
            w for w in name_clean.split()
            if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words
        ]
        
        tags = []
        
        # Primeira tag: frase de 2-4 palavras (se disponível)
        if len(words) >= 2:
            phrase = " ".join(words[:4])
            if len(phrase) > 3:
                tags.append(phrase.title())
        
        # Tags individuais
        for w in words[:5]:
            if len(w) >= 3:
                tags.append(w.capitalize())
        
        # Remove duplicatas mantendo ordem
        seen = set()
        unique_tags = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique_tags.append(t)
        
        return unique_tags[:5]
