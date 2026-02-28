"""
LASERFLIX — Project Analyzer
Análise de categorias e tags com IA
"""

import os
import re
import logging

LOGGER = logging.getLogger("Laserflix")
FAST_MODEL_THRESHOLD = 50


class ProjectAnalyzer:
    """Analisa projetos e gera categorias + tags"""

    def __init__(self, client, vision):
        self.client = client
        self.vision = vision

    def analyze(self, project_path: str, batch_size: int, model_fn):
        """Analisa projeto e retorna (categories, tags)"""
        try:
            from media.files import FileAnalyzer
            file_analyzer = FileAnalyzer()
            name = os.path.basename(project_path)
            structure = file_analyzer.analyze_structure(project_path)
            role = "text_fast" if batch_size > FAST_MODEL_THRESHOLD else "text_quality"
            model = model_fn(role)

            # Contexto técnico
            tech_context = []
            if structure["has_svg"]: tech_context.append("SVG vetorial")
            if structure["has_pdf"]: tech_context.append("PDF")
            if structure["has_dxf"]: tech_context.append("DXF/CAD")
            tech_str = ", ".join(tech_context) if tech_context else "formatos variados"

            # Visão (se disponível)
            vision_line = ""
            cover_img = file_analyzer.find_first_image(project_path)
            if cover_img:
                quality = self.vision.quality_score(cover_img)
                if quality["use_vision"]:
                    vision_desc = self.vision.describe_image(cover_img, model_fn("vision"))
                    if vision_desc:
                        vision_line = f"\n🖼️ DESCRIÇÃO VISUAL: {vision_desc}"

            prompt = f"""Analise este produto de corte laser.

📁 NOME: {name}
🔧 FORMATOS: {tech_str}{vision_line}

### TAREFA 1 — CATEGORIAS (3 a 5)
1. Data Comemorativa: Páscoa, Natal, Dia das Mães, Dia dos Pais, etc
2. Função/Tipo: Porta-Retrato, Caixa, Luminária, Quadro, etc
3. Ambiente: Quarto, Sala, Cozinha, etc
4. Estilo (opcional): Minimalista, Rústico, Moderno, etc
5. Público (opcional): Bebê, Criança, Adulto, etc

### TAREFA 2 — TAGS (exatas 8)
- Primeiras 3: palavras-chave do nome
- Demais 5: emoção, ocasião, público, estilo, uso

### FORMATO:
Categorias: [cat1], [cat2], [cat3], [cat4], [cat5]
Tags: [tag1], [tag2], [tag3], [tag4], [tag5], [tag6], [tag7], [tag8]"""

            text = self.client.generate_text(prompt, model, role=role, temperature=0.65, num_predict=200)
            categories, tags = [], []
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("Categorias:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        categories = [c.strip().strip('"') for c in raw.split(",") if c.strip()]
                    elif line.startswith("Tags:"):
                        raw = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
                        tags = [t.strip().strip('"') for t in raw.split(",") if t.strip()]
                name_tags = self._extract_tags_from_name(name)
                for tag in name_tags:
                    if tag not in tags:
                        tags.insert(0, tag)
                tags = list(dict.fromkeys(tags))[:10]
                if len(categories) < 3:
                    categories = self._fallback_categories(name, categories)
                return categories[:8], tags
        except Exception as e:
            LOGGER.exception(f"Erro em analyze: {e}")
        return self._fallback_analysis(project_path)

    def _extract_tags_from_name(self, name):
        """Extrai tags do nome do projeto"""
        clean = name
        for ext in [".zip", ".rar", ".svg", ".pdf"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"\d+", "", clean)
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", clean)
        words = [w.strip().capitalize() for w in clean.split() if len(w.strip()) > 2]
        return words[:5]

    def _fallback_categories(self, name, existing):
        """Fallback de categorias"""
        result = list(existing)
        if len(result) < 3:
            result.extend(["Diversos"] * (3 - len(result)))
        return result

    def _fallback_analysis(self, project_path):
        """Fallback sem IA"""
        name = os.path.basename(project_path)
        tags = self._extract_tags_from_name(name)
        return ["Diversos", "Diversos", "Diversos"], tags[:10]
