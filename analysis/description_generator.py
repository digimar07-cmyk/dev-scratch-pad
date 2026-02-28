"""Gerador de descrições comerciais."""
import os
from ollama.ollama_client import _ollama_generate_text
from ollama.vision import _image_quality_score, _ollama_describe_image
from analysis.structure import analyze_project_structure
from data.persistence import save_database


def _find_first_image_path(project_path):
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                return os.path.join(project_path, item)
    except Exception:
        pass
    return None


def generate_ai_description(app, project_path: str, data: dict) -> str:
    try:
        name = data.get("name", os.path.basename(project_path))
        categories = data.get("categories", [])
        tags = data.get("tags", [])
        structure = analyze_project_structure(project_path)
        
        cat_str = ", ".join(categories[:5]) if categories else "produto decorativo"
        tag_str = ", ".join(tags[:8]) if tags else "personalizado"
        
        vision_line = ""
        cover_img = _find_first_image_path(project_path)
        if cover_img:
            quality = _image_quality_score(app, cover_img)
            if quality["use_vision"]:
                vision_desc = _ollama_describe_image(app, cover_img)
                if vision_desc:
                    vision_line = f"\n🖼️ VISUAL: {vision_desc}"
        
        prompt = f"""Crie uma descrição comercial atraente para este produto de corte a laser.

📁 PRODUTO: {name}
🏷️ CATEGORIAS: {cat_str}
🎯 TAGS: {tag_str}
📊 ARQUIVOS: {structure['total_files']} arquivos | Formatos: {', '.join(structure['file_types'].keys())}{vision_line}

### TAREFA:
Escreva uma descrição comercial em 2-3 parágrafos (máximo 250 palavras):

1. PARÁGRAFO 1: Apresente o produto destacando sua utilidade e apelo visual
2. PARÁGRAFO 2: Mencione características técnicas (material, acabamento, montagem)
3. PARÁGRAFO 3 (opcional): Sugestões de uso ou ocasiões ideais

Tom: Persuasivo, profissional, focado em venda.
Evite: Frases genéricas, repetições, exageros.

DESCRIÇÃO:"""
        
        if app.stop_analysis:
            return ""
        
        description = _ollama_generate_text(
            app,
            prompt,
            role="text_quality",
            temperature=0.7,
            num_predict=300,
        )
        
        if description and len(description) > 50:
            app.database[project_path]["ai_description"] = description.strip()
            save_database(app)
            return description.strip()
    
    except Exception:
        app.logger.exception("Erro gerando descrição para %s", project_path)
    
    return ""
