"""
Funções utilitárias para normalização e processamento de texto.
Centraliza lógica de sanitização de nomes de projetos.
"""
import re
import unicodedata


def remove_accents(text: str) -> str:
    """
    Remove acentuação de texto usando unicodedata.
    
    Args:
        text: Texto com possíveis acentos
        
    Returns:
        Texto sem acentos (NFD decomposition)
        
    Example:
        >>> remove_accents("José")
        'Jose'
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def normalize_project_name(text: str) -> str:
    """
    Normaliza nome de projeto para matching consistente.
    
    Operações aplicadas:
    - Converte para lowercase
    - Remove extensões de arquivo (.zip, .svg, .pdf, etc)
    - Remove acentuação
    - Substitui separadores (-, _) por espaços
    - Remove códigos numéricos longos (IDs de produto)
    - Normaliza espaços múltiplos
    
    Args:
        text: Nome bruto do projeto
        
    Returns:
        Nome normalizado para matching
        
    Example:
        >>> normalize_project_name("Natal_2024_Árvore-12345.zip")
        'natal arvore'
    """
    t = text.lower()
    
    # Remove extensões comuns
    for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai", ".eps"]:
        t = t.replace(ext, "")
    
    # Remove acentos
    t = remove_accents(t)
    
    # Substitui separadores por espaço
    t = re.sub(r"[\-_]", " ", t)
    
    # Remove códigos numéricos longos (5+ dígitos)
    t = re.sub(r"\d{5,}", "", t)
    
    # Normaliza espaços múltiplos
    t = re.sub(r"\s+", " ", t).strip()
    
    return t
