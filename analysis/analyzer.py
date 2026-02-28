"""Análise principal com IA."""
import os
from core.config import FAST_MODEL_THRESHOLD
from ollama.ollama_client import _ollama_generate_text
from ollama.vision import _image_quality_score, _ollama_describe_image
from analysis.structure import analyze_project_structure, extract_tags_from_name
from analysis.fallback import fallback_categories, fallback_analysis


def _find_first_image_path(project_path):
    valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(valid_extensions):
                return os.path.join(project_path, item)
    except Exception:
        pass
    return None


def _choose_text_role(batch_size: int = 1) -> str:
    if batch_size > FAST_MODEL_THRESHOLD:
        return "text_fast"
    return "text_quality"


def analyze_with_ai(app, project_path: str, batch_size: int = 1):
    try:
        name = os.path.basename(project_path)
        structure = analyze_project_structure(project_path)

        file_types_str = ", ".join(
            f"{ext} ({count}x)" for ext, count in structure["file_types"].items()
        )
        subfolders_str = (
            ", ".join(structure["subfolders"][:5]) if structure["subfolders"] else "nenhuma"
        )

        tech_context = []
        if structure["has_svg"]: tech_context.append("SVG vetorial")
        if structure["has_pdf"]: tech_context.append("PDF")
        if structure["has_dxf"]: tech_context.append("DXF/CAD")
        if structure["has_ai"]:  tech_context.append("Adobe Illustrator")
        tech_str = ", ".join(tech_context) if tech_context else "formatos variados"

        vision_line = ""
        cover_img = _find_first_image_path(project_path)
        if cover_img:
            quality = _image_quality_score(app, cover_img)
            if quality["use_vision"]:
                vision_desc = _ollama_describe_image(app, cover_img)
                if vision_desc:
                    vision_line = f"\n🖼️ DESCRIÇÃO VISUAL DA CAPA: {vision_desc}"

        role = _choose_text_role(batch_size)

        prompt = f"""Analise este produto de corte laser e responda EXATAMENTE no formato solicitado.

📁 NOME: {name}
📊 ARQUIVOS: {structure['total_files']} arquivos | Subpastas: {subfolders_str}
🗂️ TIPOS: {file_types_str}
🔧 FORMATOS: {tech_str}{vision_line}

### TAREFA 1 — CATEGORIAS
Atribua de 3 a 5 categorias, OBRIGATORIAMENTE nesta ordem:
1. Data Comemorativa (escolha UMA): Páscoa, Natal, Dia das Mães, Dia dos Pais, Dia dos Namorados, Aniversário, Casamento, Chá de Bebê, Halloween, Dia das Crianças, Ano Novo, Formatura, Diversos
2. Função/Tipo (escolha UMA): Porta-Retrato, Caixa Organizadora, Luminária, Porta-Joias, Porta-Chaves, Suporte, Quadro Decorativo, Painel de Parede, Mandala, Nome Decorativo, Letreiro, Lembrancinha, Chaveiro, Topo de Bolo, Centro de Mesa, Plaquinha, Brinquedo Educativo, Diversos
3. Ambiente (escolha UM): Quarto, Sala, Cozinha, Banheiro, Escritório, Quarto Infantil, Quarto de Bebê, Área Externa, Festa, Diversos
4. Estilo OPCIONAL (ex: Minimalista, Rústico, Moderno, Vintage, Romântico, Elegante)
5. Público OPCIONAL (ex: Bebê, Criança, Adulto, Casal, Família, Presente)

### TAREFA 2 — TAGS
Crie exatamente 8 tags relevantes:
- Primeiras 3: palavras-chave extraídas do nome "{name}" (sem códigos numéricos)
- Demais 5: emoção, ocasião, público, estilo, uso

### FORMATO DE RESPOSTA (siga exatamente):
Categorias: [cat1], [cat2], [cat3], [cat4 opcional], [cat5 opcional]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8]"""

        if app.stop_analysis:
            return fallback_analysis(project_path)

        text = _ollama_generate_text(
            app,
            prompt,
            role=role,
            temperature=0.65,
            num_predict=200,
        )

        categories, tags = [], []

        if text:
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("Categorias:") or line.startswith("Categories:"):
                    raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                    categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]
                elif line.startswith("Tags:"):
                    raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                    tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]

            name_tags = extract_tags_from_name(name)
            for tag in name_tags:
                if tag not in tags:
                    tags.insert(0, tag)

            tags = list(dict.fromkeys(tags))[:10]

            if len(categories) < 3:
                categories = fallback_categories(project_path, categories)

            return categories[:8], tags

    except Exception:
        app.logger.exception("Erro em analyze_with_ai para %s", project_path)

    return fallback_analysis(project_path)
