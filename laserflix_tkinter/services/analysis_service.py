"""Project analysis service for structure and categorization."""
import os
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter

logger = logging.getLogger("Laserflix.Analysis")


class AnalysisService:
    """Analyzes project structure and provides categorization."""
    
    def analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze project folder structure.
        
        Returns dict with:
        - total_files: number of files
        - total_subfolders: number of subfolders
        - file_types: Counter of file extensions
        - subfolders: list of subfolder names
        - images: list of image filenames
        - documents: list of document filenames
        - has_svg, has_pdf, has_dxf, has_ai: format flags
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
                
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    
                    # Format flags
                    if ext == ".svg":
                        structure["has_svg"] = True
                    elif ext == ".pdf":
                        structure["has_pdf"] = True
                    elif ext == ".dxf":
                        structure["has_dxf"] = True
                    elif ext == ".ai":
                        structure["has_ai"] = True
                    
                    # Categorize files
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        
        except Exception as e:
            logger.error(f"Failed to analyze structure of {project_path}: {e}", exc_info=True)
        
        return structure
    
    def generate_fallback_categories(self, project_path: str, existing_categories: List[str] = None) -> List[str]:
        """
        Generate fallback categories based on keyword matching.
        
        Returns list with 3 categories:
        1. Commemorative date (Páscoa, Natal, etc.)
        2. Function/Type (Porta-Retrato, Caixa, etc.)
        3. Environment (Quarto, Sala, etc.)
        """
        if existing_categories is None:
            existing_categories = []
        
        name = os.path.basename(project_path).lower()
        result = list(existing_categories)
        
        # Date category mapping
        date_map = {
            "pascoa": "Páscoa", "easter": "Páscoa",
            "natal": "Natal", "christmas": "Natal",
            "mae": "Dia das Mães", "mother": "Dia das Mães",
            "pai": "Dia dos Pais", "father": "Dia dos Pais",
            "crianca": "Dia das Crianças", "children": "Dia das Crianças",
            "baby": "Chá de Bebê", "bebe": "Chá de Bebê",
            "wedding": "Casamento", "casamento": "Casamento",
            "birthday": "Aniversário", "aniversario": "Aniversário",
        }
        
        # Function category mapping
        function_map = {
            "frame": "Porta-Retrato", "foto": "Porta-Retrato",
            "box": "Caixa Organizadora", "caixa": "Caixa Organizadora",
            "name": "Nome Decorativo", "nome": "Nome Decorativo",
            "sign": "Plaquinha Divertida", "placa": "Plaquinha Divertida",
            "quadro": "Quadro Decorativo", "painel": "Painel de Parede",
        }
        
        # Environment category mapping
        ambiente_map = {
            "nursery": "Quarto de Bebê", "baby": "Quarto de Bebê",
            "bedroom": "Quarto", "quarto": "Quarto",
            "kitchen": "Cozinha", "cozinha": "Cozinha",
            "living": "Sala", "sala": "Sala",
            "kids": "Quarto Infantil", "infantil": "Quarto Infantil",
        }
        
        # Date categories
        date_cats = ["Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", 
                     "Casamento", "Chá de Bebê", "Aniversário", "Dia das Crianças"]
        
        if not any(c in date_cats for c in result):
            for key, val in date_map.items():
                if key in name:
                    result.insert(0, val)
                    break
            else:
                result.insert(0, "Diversos")
        
        # Function category
        if len(result) < 2:
            for key, val in function_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        
        # Environment category
        if len(result) < 3:
            for key, val in ambiente_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        
        return result
    
    def extract_context_tags(self, project_path: str) -> List[str]:
        """
        Extract context-aware tags from project name and path.
        
        Returns list of relevant tags based on detected keywords.
        """
        name = os.path.basename(project_path).lower()
        tags = []
        
        # Keyword checks
        checks = [
            (["pascoa", "easter", "coelho"], ["páscoa", "decoração", "festivo"]),
            (["natal", "christmas", "noel"], ["natal", "celebração", "festivo"]),
            (["mae", "mom", "mother"], ["dia das mães", "presente", "especial"]),
            (["pai", "dad", "father"], ["dia dos pais", "presente", "especial"]),
            (["baby", "bebe", "shower"], ["bebê", "chá de bebê", "maternidade"]),
            (["frame", "foto", "photo"], ["porta-retrato", "memória", "decoração"]),
            (["box", "caixa"], ["organização", "armazenamento", "prático"]),
            (["name", "nome", "sign"], ["personalizado", "nome", "decorativo"]),
            (["quadro", "painel"], ["arte", "parede", "decoração"]),
            (["nursery", "baby"], ["quarto de bebê", "infantil", "delicado"]),
        ]
        
        for words, context_tags in checks:
            if any(w in name for w in words):
                tags.extend(context_tags)
                break
        
        # Default tags if none matched
        if not tags:
            tags = ["personalizado", "artesanal", "decoração"]
        
        return tags[:5]
    
    def get_top_categories(self, all_projects: List[Dict[str, Any]], limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most common categories across all projects.
        Returns list of (category, count) tuples.
        """
        category_counter = Counter()
        for project_data in all_projects:
            categories = project_data.get("categories", [])
            category_counter.update(categories)
        
        return category_counter.most_common(limit)
    
    def get_top_tags(self, all_projects: List[Dict[str, Any]], limit: int = 20) -> List[Tuple[str, int]]:
        """
        Get most common tags across all projects.
        Returns list of (tag, count) tuples.
        """
        tag_counter = Counter()
        for project_data in all_projects:
            tags = project_data.get("tags", [])
            tag_counter.update(tags)
        
        return tag_counter.most_common(limit)
    
    def get_origin_stats(self, all_projects: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get project count by origin.
        Returns dict of {origin: count}.
        """
        origin_counter = Counter()
        for project_data in all_projects:
            origin = project_data.get("origin", "Desconhecido")
            origin_counter[origin] += 1
        
        return dict(origin_counter)
