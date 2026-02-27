"""
LASERFLIX — Description Generator
Gera descrições comerciais com hierarquia nome > visão
"""

import os
import re
import logging
from datetime import datetime

LOGGER = logging.getLogger("Laserflix")


class DescriptionGenerator:
    """Gera descrições comerciais personalizadas"""

    def __init__(self, client, vision):
        self.client = client
        self.vision = vision

    def generate(self, project_path: str, data: dict, model_fn):
        """Gera descrição comercial"""
        try:
            from ..media.files import FileAnalyzer
            file_analyzer = FileAnalyzer()
            raw_name = data.get("name", os.path.basename(project_path))
            clean_name = self._clean_name(raw_name)

            # Visão (só se imagem passa filtro)
            vision_context = ""
            cover_img = file_analyzer.find_first_image(project_path)
            if cover_img:
                quality = self.vision.quality_score(cover_img)
                if quality["use_vision"]:
                    vision_desc = self.vision.describe_image(cover_img, model_fn("vision"))
                    if vision_desc:
                        vision_context = "\n\nDETALHE VISUAL (complemento): " + vision_desc

            model = model_fn("text_quality")
            prompt = (
                "Você é especialista em peças de corte a laser.\n\n"
                "NOME DA PEÇA (verdade absoluta): " + clean_name + vision_context + "\n\n"
                "### REGRA: Nome define o que é. Visual apenas complementa.\n\n"
                "### ESCREVA exatamente neste formato:\n\n"
                + clean_name + "\n\n"
                "🎨 Por Que Este Produto é Especial:\n"
                "[2-3 frases afetivas e únicas sobre ESTA peça]\n\n"
                "💖 Perfeito Para:\n"
                "[2-3 frases práticas com exemplos reais]\n\n"
                "REGRAS: português brasileiro, sem mencionar arquivos/formatos, máx 120 palavras."
            )

            response = self.client.generate_text(prompt, model, role="text_quality", temperature=0.78, num_predict=250)
            if response:
                if not response.strip().startswith(clean_name[:15]):
                    response = clean_name + "\n\n" + response.strip()
                LOGGER.info(f"✅ Descrição gerada para {clean_name[:30]}")
                return response.strip()
            return self._fallback_description(clean_name, data)
        except Exception as e:
            LOGGER.error(f"Erro ao gerar descrição: {e}")
            return self._fallback_description(data.get("name", "Sem nome"), data)

    def _clean_name(self, raw_name):
        """Remove extensões e códigos numéricos"""
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        return clean.replace("-", " ").replace("_", " ").strip()

    def _fallback_description(self, name, data):
        """Fallback sem IA"""
        categories = data.get("categories", ["Diversos"])
        cat_display = " | ".join(categories[:3]) if categories else "Produto personalizado"
        return (
            name + "\n\n"
            "🎨 Por Que Este Produto é Especial:\n"
            f"Uma peça de corte a laser em {cat_display}, criada para ser única.\n\n"
            "💖 Perfeito Para:\n"
            "Presente personalizado, decoração ou lembrança especial."
        )
