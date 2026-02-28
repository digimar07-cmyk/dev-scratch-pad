"""Análise de estrutura de projetos e extração de tags."""
import os
import re


def get_origin_from_path(project_path):
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


def analyze_project_structure(project_path):
    structure = {
        "total_files": 0, "total_subfolders": 0,
        "file_types": {}, "subfolders": [],
        "images": [], "documents": [],
        "has_svg": False, "has_pdf": False, "has_dxf": False, "has_ai": False,
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
                if ext == ".svg": structure["has_svg"] = True
                elif ext == ".pdf": structure["has_pdf"] = True
                elif ext == ".dxf": structure["has_dxf"] = True
                elif ext == ".ai":  structure["has_ai"]  = True
                if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                    structure["images"].append(file)
                elif ext in (".pdf", ".txt", ".doc", ".docx"):
                    structure["documents"].append(file)
    except Exception:
        pass
    return structure


def extract_tags_from_name(name):
    name_clean = name
    for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
        name_clean = name_clean.replace(ext, "")
    name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
    name_clean = name_clean.replace("-", " ").replace("_", " ")
    stop_words = {"file", "files", "project", "design", "laser", "cut", "svg",
                  "pdf", "vector", "bundle", "pack", "set", "collection"}
    words = [w for w in name_clean.split() if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words]
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
