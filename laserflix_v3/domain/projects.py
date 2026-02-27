"""
LASERFLIX v3.0 — Lógica de Domínio: Projetos
Funções puras extraídas da v7.4.0 (sem IO, sem Tkinter, sem rede).

Responsabilidades:
- Extração de tags de nomes de projetos
- Categorização automática por palavras-chave
- Detecção de origem baseada em path
"""

import os
import re
from typing import List


def extract_tags_from_name(name: str) -> List[str]:
    """
    Extrai tags relevantes do nome do projeto.
    
    Regras:
    - Remove extensões de arquivo (.zip, .rar, .svg, etc)
    - Remove códigos numéricos longos (5+ dígitos)
    - Filtra stop words genéricas ("laser", "cut", "file", etc)
    - Limita a 5 tags no máximo
    - Remove duplicatas (case-insensitive)
    
    Args:
        name: Nome do projeto (ex: "Easter Bunny Frame-123456.svg.zip")
    
    Returns:
        Lista de tags (ex: ["Easter Bunny Frame", "Easter", "Bunny", "Frame"])
    
    Exemplos:
        >>> extract_tags_from_name("Christmas Tree Ornament.svg")
        ['Christmas Tree Ornament', 'Christmas', 'Tree', 'Ornament']
        
        >>> extract_tags_from_name("laser cut file design-999999.zip")
        []  # Todas são stop words
    """
    name_clean = name
    
    # Remove extensões
    for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
        name_clean = name_clean.replace(ext, "")
    
    # Remove códigos numéricos longos (padrão: -123456 ou _123456)
    name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
    
    # Normaliza separadores
    name_clean = name_clean.replace("-", " ").replace("_", " ")
    
    # Filtra stop words
    stop_words = {
        "file", "files", "project", "design", "laser", "cut", "svg",
        "pdf", "vector", "bundle", "pack", "set", "collection"
    }
    
    words = [
        w for w in name_clean.split() 
        if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words
    ]
    
    tags = []
    
    # Primeira tag: frase completa (até 4 palavras)
    if len(words) >= 2:
        phrase = " ".join(words[:4])
        if len(phrase) > 3:
            tags.append(phrase.title())
    
    # Tags individuais (até 5 palavras)
    for w in words[:5]:
        if len(w) >= 3:
            tags.append(w.capitalize())
    
    # Remove duplicatas (preserva ordem, case-insensitive)
    seen = set()
    unique = []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    
    return unique[:5]


def fallback_categories(project_path: str, existing_categories: List[str]) -> List[str]:
    """
    Categorização automática por palavras-chave quando IA não está disponível.
    
    Hierarquia de categorias:
    1. Data Comemorativa (Páscoa, Natal, Dia das Mães, etc)
    2. Função/Tipo (Porta-Retrato, Caixa Organizadora, etc)
    3. Ambiente (Quarto, Sala, Cozinha, etc)
    
    Sempre retorna pelo menos 3 categorias.
    Preserva categorias existentes.
    
    Args:
        project_path: Caminho completo do projeto
        existing_categories: Categorias já atribuídas (podem estar incompletas)
    
    Returns:
        Lista com pelo menos 3 categorias
    
    Exemplos:
        >>> fallback_categories("/path/to/easter_bunny_frame", [])
        ['Páscoa', 'Porta-Retrato', 'Diversos']
        
        >>> fallback_categories("/path/to/christmas_tree", ['Natal'])
        ['Natal', 'Diversos', 'Diversos']
    """
    name = os.path.basename(project_path).lower()
    
    # Mapas de palavras-chave para categorias
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
    
    function_map = {
        "frame": "Porta-Retrato", "foto": "Porta-Retrato",
        "box": "Caixa Organizadora", "caixa": "Caixa Organizadora",
        "name": "Nome Decorativo", "nome": "Nome Decorativo",
        "sign": "Plaquinha Divertida", "placa": "Plaquinha Divertida",
        "quadro": "Quadro Decorativo", "painel": "Painel de Parede",
    }
    
    ambiente_map = {
        "nursery": "Quarto de Bebê", "baby": "Quarto de Bebê",
        "bedroom": "Quarto", "quarto": "Quarto",
        "kitchen": "Cozinha", "cozinha": "Cozinha",
        "living": "Sala", "sala": "Sala",
        "kids": "Quarto Infantil", "infantil": "Quarto Infantil",
    }
    
    result = list(existing_categories)
    
    # Nível 1: Data comemorativa
    date_cats = [
        "Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", 
        "Casamento", "Chá de Bebê", "Aniversário", "Dia das Crianças"
    ]
    if not any(c in date_cats for c in result):
        for key, val in date_map.items():
            if key in name:
                result.insert(0, val)
                break
        else:
            result.insert(0, "Diversos")
    
    # Nível 2: Função/Tipo
    if len(result) < 2:
        for key, val in function_map.items():
            if key in name:
                result.append(val)
                break
        else:
            result.append("Diversos")
    
    # Nível 3: Ambiente
    if len(result) < 3:
        for key, val in ambiente_map.items():
            if key in name:
                result.append(val)
                break
        else:
            result.append("Diversos")
    
    return result


def get_origin_from_path(project_path: str) -> str:
    """
    Detecta a origem do projeto baseado no caminho da pasta pai.
    
    Regras:
    - "CREATIVE" ou "FABRICA" no path → "Creative Fabrica"
    - "ETSY" no path → "Etsy"
    - Caso contrário → nome da pasta pai
    - Em caso de erro → "Diversos"
    
    Args:
        project_path: Caminho completo do projeto
    
    Returns:
        Nome da origem
    
    Exemplos:
        >>> get_origin_from_path("/storage/CREATIVE_FABRICA_2024/project1")
        'Creative Fabrica'
        
        >>> get_origin_from_path("/downloads/etsy_products/project2")
        'Etsy'
        
        >>> get_origin_from_path("/my_projects/custom_folder/project3")
        'custom_folder'
        
        >>> get_origin_from_path("")
        ''  # BUG: deveria retornar "Diversos" (TODO: corrigir)
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
