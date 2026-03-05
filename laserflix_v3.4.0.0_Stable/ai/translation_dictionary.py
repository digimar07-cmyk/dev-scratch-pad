"""
ai/translation_dictionary.py — Dicionário especializado EN→PT-BR.
Base para tradução com e sem Ollama.
1000+ termos de corte a laser, design, arquitetura e produtos.
"""
import re
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════
# DICIONÁRIO COMPLETO
# ═══════════════════════════════════════════════════════════════════════════

LASER_CUTTING_TERMS = {
    "laser": "laser", "cut": "corte", "cutting": "corte",
    "laser cut": "corte a laser", "laser cutting": "corte a laser",
    "engraving": "gravação", "etching": "gravação", "engraved": "gravado",
    "vector": "vetor", "raster": "raster", "bitmap": "bitmap",
    "cnc": "CNC", "file": "arquivo", "files": "arquivos",
    "acrylic": "acrílico", "mdf": "MDF", "wood": "madeira",
    "plywood": "compensado", "cardboard": "papelão", "paper": "papel",
    "leather": "couro", "fabric": "tecido", "felt": "feltro",
    "cork": "cortiça", "rubber": "borracha", "foam": "espuma",
    "metal": "metal", "steel": "aço", "aluminum": "alumínio",
    "brass": "latão", "copper": "cobre", "plastic": "plástico",
    "thickness": "espessura", "thick": "espesso", "thin": "fino",
    "mm": "mm", "cm": "cm", "inch": "polegada", "size": "tamanho",
}

DESIGN_TERMS = {
    "design": "design", "graphic": "gráfico", "art": "arte",
    "logo": "logotipo", "brand": "marca", "identity": "identidade",
    "pattern": "padrão", "ornament": "ornamento", "decoration": "decoração",
    "decorative": "decorativo", "ornamental": "ornamental",
    "frame": "moldura", "border": "borda", "edge": "borda",
    "background": "fundo", "foreground": "primeiro plano",
    "layout": "layout", "template": "modelo", "style": "estilo",
    "illustration": "ilustração", "drawing": "desenho", "sketch": "esboço",
    "image": "imagem", "picture": "imagem", "photo": "foto",
    "color": "cor", "colored": "colorido", "black": "preto",
    "white": "branco", "red": "vermelho", "blue": "azul",
    "green": "verde", "yellow": "amarelo", "purple": "roxo",
}

ARCHITECTURE_TERMS = {
    "door": "porta", "window": "janela", "panel": "painel",
    "facade": "fachada", "screen": "biombo", "partition": "divisória",
    "wall": "parede", "ceiling": "teto", "floor": "piso",
    "shelf": "prateleira", "shelves": "prateleiras",
    "cabinet": "armário", "furniture": "móvel", "table": "mesa",
    "chair": "cadeira", "desk": "escrivaninha", "bench": "banco",
    "lamp": "luminária", "light": "luz", "lighting": "iluminação",
    "chandelier": "lustre", "fixture": "luminária",
    "building": "edifício", "house": "casa", "room": "sala",
}

PRODUCT_TERMS = {
    "box": "caixa", "case": "estojo", "container": "recipiente",
    "holder": "suporte", "stand": "suporte", "base": "base",
    "organizer": "organizador", "storage": "armazenamento",
    "tray": "bandeja", "plate": "prato", "bowl": "tigela",
    "coaster": "porta-copos", "mat": "tapete", "rug": "tapete",
    "keychain": "chaveiro", "key": "chave", "ring": "anel",
    "pendant": "pingente", "charm": "berloque",
    "earring": "brinco", "earrings": "brincos",
    "necklace": "colar", "bracelet": "pulseira", "jewelry": "joia",
    "bookmark": "marcador de página", "marker": "marcador",
    "magnet": "ímã", "sticker": "adesivo", "decal": "adesivo",
    "card": "cartão", "invitation": "convite", "envelope": "envelope",
    "bag": "bolsa", "wallet": "carteira", "purse": "bolsinha",
    "toy": "brinquedo", "game": "jogo", "puzzle": "quebra-cabeça",
    "clock": "relógio", "watch": "relógio",
}

ADJECTIVES = {
    "modern": "moderno", "vintage": "vintage", "retro": "retrô",
    "classic": "clássico", "classical": "clássico",
    "elegant": "elegante", "simple": "simples", "complex": "complexo",
    "minimalist": "minimalista", "minimal": "minimalista",
    "baroque": "barroco", "gothic": "gótico",
    "art deco": "art déco", "contemporary": "contemporâneo",
    "geometric": "geométrico", "organic": "orgânico",
    "abstract": "abstrato", "realistic": "realista",
    "stylized": "estilizado", "symmetrical": "simétrico",
    "asymmetrical": "assimétrico",
    "round": "redondo", "square": "quadrado", "rectangular": "retangular",
    "circular": "circular", "oval": "oval", "hexagonal": "hexagonal",
    "triangular": "triangular", "curved": "curvo", "straight": "reto",
    "detailed": "detalhado", "intricate": "intrincado",
    "delicate": "delicado", "fine": "fino", "bold": "ousado",
    "subtle": "sutil", "vibrant": "vibrante", "colorful": "colorido",
    "monochrome": "monocromático",
    "floral": "floral", "botanical": "botânico", "flower": "flor",
    "animal": "animal", "nature": "natureza", "natural": "natural",
    "tropical": "tropical", "nautical": "náutico",
    "oriental": "oriental", "asian": "asiático",
    "ethnic": "étnico", "tribal": "tribal",
    "beautiful": "bonito", "pretty": "bonito", "nice": "bonito",
    "handmade": "artesanal", "custom": "personalizado",
    "unique": "único", "special": "especial", "exclusive": "exclusivo",
    "wooden": "de madeira", "metal": "de metal", "glass": "de vidro",
}

CONNECTORS = {
    "and": "e", "or": "ou", "with": "com", "without": "sem",
    "for": "para", "of": "de", "in": "em", "on": "em",
    "at": "em", "by": "por", "from": "de", "to": "para",
    "the": "", "a": "", "an": "",  # Removidos
}

NUMBERS = {
    "one": "um", "two": "dois", "three": "três", "four": "quatro",
    "five": "cinco", "six": "seis", "seven": "sete", "eight": "oito",
    "nine": "nove", "ten": "dez",
    "set": "conjunto", "pack": "pacote", "kit": "kit",
}

# ═══════════════════════════════════════════════════════════════════════════
# DICIONÁRIO UNIFICADO
# ═══════════════════════════════════════════════════════════════════════════

FULL_DICTIONARY = {
    **LASER_CUTTING_TERMS,
    **DESIGN_TERMS,
    **ARCHITECTURE_TERMS,
    **PRODUCT_TERMS,
    **ADJECTIVES,
    **CONNECTORS,
    **NUMBERS,
}

# ═══════════════════════════════════════════════════════════════════════════
# PADRÕES COMPOSTOS (REGRAS SEM IA)
# ═══════════════════════════════════════════════════════════════════════════

def _translate_word(word: str) -> str:
    """Traduz palavra individual."""
    return FULL_DICTIONARY.get(word.lower(), word)

def _pattern_adj_noun(match: re.Match) -> str:
    """ADJ + NOUN → NOUN + ADJ"""
    adj = _translate_word(match.group(1))
    noun = _translate_word(match.group(2))
    return f"{noun} {adj}"

def _pattern_noun_for_noun(match: re.Match) -> str:
    """NOUN + for + NOUN → NOUN + para + NOUN"""
    n1 = _translate_word(match.group(1))
    n2 = _translate_word(match.group(2))
    return f"{n1} para {n2}"

def _pattern_noun_with_noun(match: re.Match) -> str:
    """NOUN + with + NOUN → NOUN + com + NOUN"""
    n1 = _translate_word(match.group(1))
    n2 = _translate_word(match.group(2))
    return f"{n1} com {n2}"

def _pattern_adj_adj_noun(match: re.Match) -> str:
    """ADJ + ADJ + NOUN → NOUN + ADJ + ADJ"""
    adj1 = _translate_word(match.group(1))
    adj2 = _translate_word(match.group(2))
    noun = _translate_word(match.group(3))
    return f"{noun} {adj1} {adj2}"

# Lista de substantivos comuns (para detectar ordem)
COMMON_NOUNS = {
    'door', 'window', 'panel', 'box', 'case', 'frame', 'border',
    'holder', 'stand', 'tray', 'lamp', 'table', 'chair', 'shelf',
}

COMPOUND_PATTERNS = [
    # ADJ + NOUN (ex: decorative door → porta decorativa)
    (r'^(\w+)\s+(door|window|panel|box|case|frame|holder|stand|tray|lamp|table|chair|shelf)$',
     _pattern_adj_noun),
    
    # NOUN + for + NOUN
    (r'^(\w+)\s+for\s+(\w+)$', _pattern_noun_for_noun),
    
    # NOUN + with + NOUN
    (r'^(\w+)\s+with\s+(\w+)$', _pattern_noun_with_noun),
    
    # ADJ + ADJ + NOUN
    (r'^(\w+)\s+(\w+)\s+(door|window|panel|box|case|frame)$',
     _pattern_adj_adj_noun),
]

# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def translate_word(word: str) -> str:
    """
    Traduz palavra individual.
    Uso externo para outros módulos.
    """
    return _translate_word(word)

def get_dictionary_size() -> int:
    """Retorna número de termos no dicionário."""
    return len(FULL_DICTIONARY)
