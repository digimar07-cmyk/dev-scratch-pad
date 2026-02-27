"""File and path utilities."""
import os
import re
from typing import List


def get_origin_from_path(project_path: str) -> str:
    """Extract origin from parent folder name."""
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


def clean_project_name(raw_name: str) -> str:
    """Clean project name for display."""
    clean = raw_name
    for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
        clean = clean.replace(ext, "")
    clean = re.sub(r"[-_]\d{5,}", "", clean)
    clean = clean.replace("-", " ").replace("_", " ").strip()
    return clean


def extract_tags_from_name(name: str) -> List[str]:
    """Extract meaningful tags from project name."""
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
    
    # Deduplicate
    seen, unique = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    
    return unique[:5]


def find_first_image(project_path: str) -> str:
    """Find first image in project folder."""
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                return os.path.join(project_path, item)
    except Exception:
        pass
    return ""


def get_all_images(project_path: str) -> List[str]:
    """Get all images in project folder."""
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
    images = []
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                images.append(os.path.join(project_path, item))
    except Exception:
        pass
    return sorted(images)
