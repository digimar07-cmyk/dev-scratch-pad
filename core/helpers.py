"""Helper functions"""
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


def darken_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,int(r*0.8)):02x}{max(0,int(g*0.8)):02x}{max(0,int(b*0.8)):02x}"
