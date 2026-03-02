"""
Constantes de UI - Cores e fontes

NOTA: Dimensões de card/grid ficam em config/card_layout.py
"""

# ============================================================================
# PALETA DE CORES (NETFLIX-STYLE)
# ============================================================================
COLORS = {
    # Backgrounds
    "bg_primary":   "#141414",  # Fundo principal
    "bg_secondary": "#1A1A1A",  # Sidebar
    "bg_card":      "#2A2A2A",  # Cards de projeto
    "bg_hover":     "#3A3A3A",  # Hover state
    "bg_header":    "#000000",  # Header
    "bg_modal":     "#0F0F0F",  # Modal overlay

    # Foregrounds
    "fg_primary":   "#FFFFFF",  # Texto principal
    "fg_secondary": "#CCCCCC",  # Texto secundário
    "fg_tertiary":  "#999999",  # Texto terciário
    "fg_disabled":  "#666666",  # Texto desabilitado

    # Accent colors
    "accent":       "#E50914",  # Vermelho Netflix (primary action)
    "accent_dark":  "#B20710",  # Vermelho escuro (hover)
    "success":      "#1DB954",  # Verde Spotify (success)
    "warning":      "#FF6B35",  # Laranja (warning)
    "info":         "#4ECDC4",  # Azul claro (info)

    # Status colors
    "favorite":     "#FFD700",  # Dourado (estrela)
    "good":         "#00FF00",  # Verde (thumb up)
    "bad":          "#FF0000",  # Vermelho (thumb down)
    "done":         "#1DB954",  # Verde (checkmark)

    # Origin colors
    "origin_cf":    "#FF6B35",  # Creative Fabrica
    "origin_etsy":  "#F7931E",  # Etsy
    "origin_other": "#4ECDC4",  # Outros

    # Separators
    "separator":    "#2A2A2A",  # Linhas de separação
}

# ============================================================================
# FONTES
# ============================================================================
FONTS = {
    "title":        ("Arial", 24, "bold"),
    "header":       ("Arial", 20, "bold"),
    "section":      ("Arial", 14, "bold"),
    "subsection":   ("Arial", 12, "bold"),
    "body":         ("Arial", 11),
    "body_bold":    ("Arial", 11, "bold"),
    "small":        ("Arial", 10),
    "small_bold":   ("Arial", 10, "bold"),
    "tiny":         ("Arial", 9),
    "tiny_bold":    ("Arial", 9, "bold"),
    "button":       ("Arial", 11, "bold"),
    "button_small": ("Arial", 10, "bold"),
    "logo":         ("Arial", 28, "bold"),
    "icon":         ("Arial", 14),
    "icon_large":   ("Arial", 60),
}

# ============================================================================
# EXTENSÕES DE ARQUIVO
# ============================================================================
FILE_EXTENSIONS = {
    "images":    (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"),
    "vectors":   (".svg", ".ai", ".eps"),
    "cad":       (".dxf", ".dwg"),
    "documents": (".pdf", ".txt", ".doc", ".docx"),
    "archives":  (".zip", ".rar", ".7z"),
}
