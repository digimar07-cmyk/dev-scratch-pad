"""
utils/name_translator.py — Tradutor estático EN→PT para busca bilíngue.

Sem dependência de Ollama. Mapeia termos comuns de projetos laser cut.
Usado em HOT-14 (busca bilíngue) + F-07 (filtros empilháveis).
"""

# Dicionário estático EN → PT
TRANSLATIONS = {
    # Animais
    "dog": "cachorro",
    "cat": "gato",
    "bird": "pássaro",
    "fish": "peixe",
    "elephant": "elefante",
    "lion": "leão",
    "tiger": "tigre",
    "bear": "urso",
    "wolf": "lobo",
    "fox": "raposa",
    "rabbit": "coelho",
    "horse": "cavalo",
    "cow": "vaca",
    "pig": "porco",
    "sheep": "ovelha",
    "chicken": "galinha",
    "duck": "pato",
    "owl": "coruja",
    "eagle": "águia",
    "butterfly": "borboleta",
    "bee": "abelha",
    "ant": "formiga",
    "spider": "aranha",
    "snake": "cobra",
    "turtle": "tartaruga",
    "frog": "sapo",
    "dolphin": "golfinho",
    "whale": "baleia",
    "shark": "tubarão",
    "octopus": "polvo",
    "crab": "caranguejo",
    "penguin": "pinguim",
    "giraffe": "girafa",
    "zebra": "zebra",
    "monkey": "macaco",
    "panda": "panda",
    "koala": "coala",
    "kangaroo": "canguru",
    "deer": "veado",
    "moose": "alce",
    "squirrel": "esquilo",
    "mouse": "rato",
    "hamster": "hamster",
    
    # Objetos domésticos
    "mirror": "espelho",
    "clock": "relógio",
    "lamp": "lâmpada",
    "table": "mesa",
    "chair": "cadeira",
    "shelf": "prateleira",
    "door": "porta",
    "window": "janela",
    "frame": "moldura",
    "box": "caixa",
    "basket": "cesta",
    "holder": "suporte",
    "organizer": "organizador",
    "tray": "bandeja",
    "coaster": "porta-copos",
    "vase": "vaso",
    "pot": "vaso",
    "planter": "vaso",
    "cup": "xícara",
    "mug": "caneca",
    "plate": "prato",
    "bowl": "tigela",
    "spoon": "colher",
    "fork": "garfo",
    "knife": "faca",
    "bottle": "garrafa",
    "jar": "pote",
    "container": "recipiente",
    "stand": "suporte",
    "rack": "suporte",
    "hanger": "cabide",
    "hook": "gancho",
    "handle": "alça",
    "knob": "puxador",
    "key": "chave",
    "lock": "fechadura",
    "keychain": "chaveiro",
    "bookmark": "marcador",
    "pen": "caneta",
    "pencil": "lápis",
    "ruler": "régua",
    "scissors": "tesoura",
    "notebook": "caderno",
    "folder": "pasta",
    "envelope": "envelope",
    "card": "cartão",
    "tag": "etiqueta",
    "label": "etiqueta",
    "sticker": "adesivo",
    "magnet": "ímã",
    "button": "botão",
    "zipper": "zíper",
    "bag": "bolsa",
    "wallet": "carteira",
    "purse": "bolsa",
    "backpack": "mochila",
    
    # Decoração
    "decoration": "decoração",
    "ornament": "ornamento",
    "wall": "parede",
    "art": "arte",
    "sign": "placa",
    "banner": "faixa",
    "flag": "bandeira",
    "garland": "guirlanda",
    "wreath": "guirlanda",
    "star": "estrela",
    "moon": "lua",
    "sun": "sol",
    "cloud": "nuvem",
    "rainbow": "arco-íris",
    "heart": "coração",
    "flower": "flor",
    "tree": "árvore",
    "leaf": "folha",
    "branch": "galho",
    "plant": "planta",
    "garden": "jardim",
    "rose": "rosa",
    "tulip": "tulipa",
    "daisy": "margarida",
    "lily": "lírio",
    "sunflower": "girassol",
    "cactus": "cacto",
    "succulent": "suculenta",
    
    # Temas
    "christmas": "natal",
    "halloween": "halloween",
    "easter": "páscoa",
    "birthday": "aniversário",
    "wedding": "casamento",
    "baby": "bebê",
    "nursery": "infantil",
    "kids": "crianças",
    "children": "crianças",
    "boy": "menino",
    "girl": "menina",
    "family": "família",
    "home": "casa",
    "kitchen": "cozinha",
    "bathroom": "banheiro",
    "bedroom": "quarto",
    "living": "sala",
    "office": "escritório",
    "desk": "mesa",
    "study": "estudo",
    "school": "escola",
    "teacher": "professor",
    "student": "estudante",
    
    # Formas e estilos
    "round": "redondo",
    "square": "quadrado",
    "rectangle": "retângulo",
    "circle": "círculo",
    "triangle": "triângulo",
    "hexagon": "hexágono",
    "oval": "oval",
    "diamond": "diamante",
    "geometric": "geométrico",
    "mandala": "mandala",
    "pattern": "padrão",
    "design": "design",
    "modern": "moderno",
    "vintage": "vintage",
    "rustic": "rústico",
    "minimalist": "minimalista",
    "elegant": "elegante",
    "classic": "clássico",
    "simple": "simples",
    "complex": "complexo",
    "detailed": "detalhado",
    "ornate": "ornamentado",
    
    # Tamanhos
    "small": "pequeno",
    "medium": "médio",
    "large": "grande",
    "mini": "mini",
    "tiny": "minúsculo",
    "big": "grande",
    "huge": "enorme",
    "giant": "gigante",
    
    # Cores
    "red": "vermelho",
    "blue": "azul",
    "green": "verde",
    "yellow": "amarelo",
    "orange": "laranja",
    "purple": "roxo",
    "pink": "rosa",
    "brown": "marrom",
    "black": "preto",
    "white": "branco",
    "gray": "cinza",
    "grey": "cinza",
    "gold": "dourado",
    "silver": "prateado",
    "bronze": "bronze",
    "colorful": "colorido",
    "rainbow": "arco-íris",
    
    # Materiais
    "wood": "madeira",
    "wooden": "madeira",
    "mdf": "mdf",
    "plywood": "compensado",
    "acrylic": "acrílico",
    "metal": "metal",
    "plastic": "plástico",
    "glass": "vidro",
    "fabric": "tecido",
    "leather": "couro",
    "paper": "papel",
    "cardboard": "papelão",
    
    # Ações
    "cut": "cortado",
    "laser": "laser",
    "engraved": "gravado",
    "etched": "gravado",
    "carved": "entalhado",
    "painted": "pintado",
    "stained": "tingido",
    "polished": "polido",
    "assembled": "montado",
    "handmade": "artesanal",
    "custom": "personalizado",
    "personalized": "personalizado",
    
    # Funcionalidades
    "storage": "armazenamento",
    "display": "exposição",
    "hanging": "pendurado",
    "standing": "em pé",
    "mounted": "montado",
    "folding": "dobrável",
    "stackable": "empilhável",
    "portable": "portátil",
    "adjustable": "ajustável",
    "removable": "removível",
    
    # Números
    "one": "um",
    "two": "dois",
    "three": "três",
    "four": "quatro",
    "five": "cinco",
    "six": "seis",
    "seven": "sete",
    "eight": "oito",
    "nine": "nove",
    "ten": "dez",
    "first": "primeiro",
    "second": "segundo",
    "third": "terceiro",
    
    # Comuns
    "set": "conjunto",
    "kit": "kit",
    "pack": "pacote",
    "piece": "peça",
    "part": "parte",
    "item": "item",
    "product": "produto",
    "gift": "presente",
    "toy": "brinquedo",
    "game": "jogo",
    "puzzle": "quebra-cabeça",
    "model": "modelo",
    "template": "modelo",
    "file": "arquivo",
    "project": "projeto",
    "craft": "artesanato",
    "diy": "faça-você-mesmo",
    "maker": "criador",
    "designer": "designer",
    "artist": "artista",
    
    # Etsy/Vendas
    "digital": "digital",
    "download": "download",
    "instant": "instantâneo",
    "printable": "imprimível",
    "svg": "svg",
    "dxf": "dxf",
    "vector": "vetorial",
    "commercial": "comercial",
    "license": "licença",
    "unique": "único",
    "exclusive": "exclusivo",
    "original": "original",
    "new": "novo",
    "bestseller": "mais vendido",
    "popular": "popular",
    "trending": "em alta",
    
    # Adjetivos comuns
    "beautiful": "bonito",
    "pretty": "bonito",
    "cute": "fofo",
    "lovely": "adorável",
    "nice": "legal",
    "cool": "legal",
    "awesome": "incrível",
    "amazing": "incrível",
    "perfect": "perfeito",
    "best": "melhor",
    "good": "bom",
    "great": "ótimo",
    "excellent": "excelente",
    "quality": "qualidade",
    "premium": "premium",
    "deluxe": "luxo",
    "fancy": "chique",
    "fun": "divertido",
    "creative": "criativo",
    "unique": "único",
    "special": "especial",
    "easy": "fácil",
    "quick": "rápido",
    "fast": "rápido",
    "simple": "simples",
}

# Inverter dicionário para busca PT → EN também
REVERSE_TRANSLATIONS = {v: k for k, v in TRANSLATIONS.items()}


def translate_to_pt(text_en: str) -> str:
    """
    Traduz texto inglês para português usando dicionário estático.
    Processa palavra por palavra, mantém palavras desconhecidas.
    
    Args:
        text_en: Texto em inglês (ex: "Nursery Mirror")
    
    Returns:
        Texto traduzido (ex: "infantil espelho")
    """
    if not text_en:
        return ""
    
    words = text_en.lower().split()
    translated_words = []
    
    for word in words:
        # Remove pontuação
        clean_word = word.strip('.,!?;:"\'-_()')
        
        # Traduz se existir no dicionário
        if clean_word in TRANSLATIONS:
            translated_words.append(TRANSLATIONS[clean_word])
        else:
            # Mantém palavra original se não encontrar tradução
            translated_words.append(clean_word)
    
    return " ".join(translated_words)


def translate_to_en(text_pt: str) -> str:
    """
    Traduz texto português para inglês usando dicionário estático.
    Processa palavra por palavra, mantém palavras desconhecidas.
    
    Args:
        text_pt: Texto em português (ex: "espelho infantil")
    
    Returns:
        Texto traduzido (ex: "mirror nursery")
    """
    if not text_pt:
        return ""
    
    words = text_pt.lower().split()
    translated_words = []
    
    for word in words:
        # Remove pontuação
        clean_word = word.strip('.,!?;:"\'-_()')
        
        # Traduz se existir no dicionário reverso
        if clean_word in REVERSE_TRANSLATIONS:
            translated_words.append(REVERSE_TRANSLATIONS[clean_word])
        else:
            # Mantém palavra original se não encontrar tradução
            translated_words.append(clean_word)
    
    return " ".join(translated_words)


def search_bilingual(query: str, text_en: str) -> bool:
    """
    Busca bilíngue: verifica se query (EN ou PT) existe no texto EN.
    
    Args:
        query: Termo de busca (ex: "espelho" ou "mirror")
        text_en: Texto em inglês para buscar (ex: "Nursery Mirror")
    
    Returns:
        True se query encontrada (em qualquer idioma)
    
    Exemplos:
        >>> search_bilingual("mirror", "Nursery Mirror")
        True
        >>> search_bilingual("espelho", "Nursery Mirror")
        True
        >>> search_bilingual("infantil", "Nursery Mirror")
        True
    """
    if not query or not text_en:
        return False
    
    query_lower = query.lower()
    text_lower = text_en.lower()
    
    # 1. Busca direta (query em inglês no texto inglês)
    if query_lower in text_lower:
        return True
    
    # 2. Traduz texto EN → PT e busca
    text_pt = translate_to_pt(text_en)
    if query_lower in text_pt.lower():
        return True
    
    # 3. Traduz query PT → EN e busca no texto original
    query_en = translate_to_en(query)
    if query_en.lower() in text_lower:
        return True
    
    return False
