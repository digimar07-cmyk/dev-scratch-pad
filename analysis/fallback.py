"""Fallback quando IA offline."""
import os
import re
from analysis.structure import analyze_project_structure, extract_tags_from_name


def fallback_categories(project_path: str, existing_categories: list = None) -> list:
    if existing_categories is None:
        existing_categories = []
    structure = analyze_project_structure(project_path)
    name_lower = os.path.basename(project_path).lower()
    
    # Data comemorativa
    if not any(c in ["Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", "Dia dos Namorados",
                     "Aniversário", "Casamento", "Chá de Bebê", "Halloween", "Dia das Crianças",
                     "Ano Novo", "Formatura"] for c in existing_categories):
        if "natal" in name_lower or "papai noel" in name_lower:
            existing_categories.append("Natal")
        elif "pascoa" in name_lower or "coelho" in name_lower:
            existing_categories.append("Páscoa")
        elif "mae" in name_lower or "maes" in name_lower:
            existing_categories.append("Dia das Mães")
        elif "pai" in name_lower or "pais" in name_lower:
            existing_categories.append("Dia dos Pais")
        elif "namorados" in name_lower or "amor" in name_lower:
            existing_categories.append("Dia dos Namorados")
        elif "aniversario" in name_lower or "festa" in name_lower:
            existing_categories.append("Aniversário")
        elif "casamento" in name_lower or "noivos" in name_lower:
            existing_categories.append("Casamento")
        elif "bebe" in name_lower or "baby" in name_lower:
            existing_categories.append("Chá de Bebê")
        elif "halloween" in name_lower:
            existing_categories.append("Halloween")
        elif "crianca" in name_lower:
            existing_categories.append("Dia das Crianças")
        elif "ano novo" in name_lower:
            existing_categories.append("Ano Novo")
        elif "formatura" in name_lower:
            existing_categories.append("Formatura")
        else:
            existing_categories.append("Diversos")
    
    # Função
    if "porta" in name_lower and "retrato" in name_lower:
        existing_categories.append("Porta-Retrato")
    elif "caixa" in name_lower:
        existing_categories.append("Caixa Organizadora")
    elif "luminaria" in name_lower or "luz" in name_lower:
        existing_categories.append("Luminária")
    elif "quadro" in name_lower:
        existing_categories.append("Quadro Decorativo")
    elif "mandala" in name_lower:
        existing_categories.append("Mandala")
    elif "nome" in name_lower:
        existing_categories.append("Nome Decorativo")
    elif "lembrancinha" in name_lower:
        existing_categories.append("Lembrancinha")
    elif "chaveiro" in name_lower:
        existing_categories.append("Chaveiro")
    elif "topo" in name_lower:
        existing_categories.append("Topo de Bolo")
    else:
        existing_categories.append("Diversos")
    
    # Ambiente
    if "quarto" in name_lower:
        existing_categories.append("Quarto")
    elif "sala" in name_lower:
        existing_categories.append("Sala")
    elif "cozinha" in name_lower:
        existing_categories.append("Cozinha")
    elif "banheiro" in name_lower:
        existing_categories.append("Banheiro")
    elif "escritorio" in name_lower:
        existing_categories.append("Escritório")
    else:
        existing_categories.append("Diversos")
    
    return existing_categories[:8]


def fallback_analysis(project_path: str):
    categories = fallback_categories(project_path)
    tags = extract_tags_from_name(os.path.basename(project_path))[:10]
    return categories, tags
