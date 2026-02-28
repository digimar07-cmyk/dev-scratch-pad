"""Description Generator - gera descrições com IA"""
import os
import re
from datetime import datetime
from core.logging_setup import LOGGER


class DescriptionGenerator:
    def __init__(self, ollama_client, vision_analyzer, project_analyzer):
        self.ollama = ollama_client
        self.vision = vision_analyzer
        self.analyzer = project_analyzer
        self.logger = LOGGER

    def generate_ai_description(self, project_path: str, data: dict, database: dict):
        if self.ollama.stop_analysis:
            return None

        structure = None
        try:
            structure = (
                data.get("structure")
                or database.get(project_path, {}).get("structure")
            )
            if not structure:
                structure = self.analyzer.analyze_project_structure(project_path)
                if project_path in database:
                    database[project_path]["structure"] = structure
                else:
                    data["structure"] = structure

            raw_name = data.get("name", os.path.basename(project_path) or "Sem nome")
            clean_name = raw_name
            for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
                clean_name = clean_name.replace(ext, "")
            clean_name = re.sub(r"[-_]\d{5,}", "", clean_name)
            clean_name = clean_name.replace("-", " ").replace("_", " ").strip()

            vision_context = ""
            cover_img = self.analyzer._find_first_image_path(project_path)
            if cover_img:
                quality = self.vision._image_quality_score(cover_img)
                if quality["use_vision"]:
                    vision_desc = self.vision._ollama_describe_image(cover_img)
                    if vision_desc:
                        vision_context = "\n\nDETALHE VISUAL (use apenas para complementar, nunca contradizer o nome): " + vision_desc
                else:
                    self.logger.info(
                        "⚠️ Visão desativada para %s (brilho=%.1f sat=%.1f fundo~%.1f%%)",
                        os.path.basename(project_path),
                        quality["brightness"], quality["saturation"], quality["white_pct"]
                    )

            if self.ollama.stop_analysis:
                return None

            prompt = (
                "Você é especialista em peças físicas de corte a laser — placas, espelhos, "
                "porta-retratos, tabuletas, cabides, calendários, nomes decorativos e similares.\n\n"
                "NOME DA PEÇA (use isso como verdade absoluta sobre o que é o produto): " + clean_name
                + vision_context + "\n\n"
                "### REGRA FUNDAMENTAL:\n"
                "O NOME define o que é o produto. O detalhe visual apenas complementa.\n"
                "Nunca invente função ou formato que contradiga o nome.\n\n"
                "### RACIOCINE antes de escrever:\n"
                "1. O que exatamente é esta peça física, baseado no nome? (tipo de objeto)\n"
                "2. Para que serve na prática? (uso real no dia a dia)\n"
                "3. Que emoção ou momento ela representa? (conexão afetiva)\n\n"
                "### ESCREVA a descrição EXATAMENTE neste formato (sem nada além disso):\n\n"
                + clean_name + "\n\n"
                "\U0001f3a8 Por Que Este Produto é Especial:\n"
                "[2 a 3 frases afetivas e únicas. Fale sobre o que torna ESTA peça especial. "
                "Nunca use frases genéricas que servem para qualquer produto.]\n\n"
                "\U0001f496 Perfeito Para:\n"
                "[2 a 3 frases práticas com exemplos reais de uso e ocasião para ESTA peça específica.]\n\n"
                "### REGRAS OBRIGATÓRIAS:\n"
                "- Escreva em português brasileiro\n"
                "- Nunca use a palavra projeto — esta é uma PEÇA ou PRODUTO físico\n"
                "- Nunca mencione arquivos, SVG, PDF, formatos ou etapas de produção\n"
                "- Nunca repita frases que poderiam servir para qualquer outra peça\n"
                "- Máximo 120 palavras no total\n"
                "- Responda APENAS com o texto no formato acima, sem comentários adicionais"
            )

            response_text = self.ollama._ollama_generate_text(
                prompt,
                role="text_quality",
                temperature=0.78,
                num_predict=250,
            )

            if response_text:
                if not response_text.strip().startswith(clean_name[:15]):
                    response_text = clean_name + "\n\n" + response_text.strip()
                database.setdefault(project_path, {})
                database[project_path]["ai_description"]           = response_text.strip()
                database[project_path]["description_generated_at"] = datetime.now().isoformat()
                database[project_path]["description_model"]        = self.ollama._model_name("text_quality")
                database[project_path].setdefault("structure", structure)
                return response_text.strip()

            return self.generate_fallback_description(project_path, data, structure, database)

        except Exception as e:
            self.logger.error("Erro ao gerar descrição para %s: %s", project_path, e, exc_info=True)
            return self.generate_fallback_description(
                project_path, data,
                structure or self.analyzer.analyze_project_structure(project_path),
                database
            )

    def generate_fallback_description(self, project_path, data, structure, database):
        raw_name = data.get("name", "Sem nome")
        clean_name = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean_name = clean_name.replace(ext, "")
        clean_name = re.sub(r"[-_]\d{5,}", "", clean_name)
        clean_name = clean_name.replace("-", " ").replace("_", " ").strip()

        tags      = data.get("tags", [])
        tags_lower = " ".join(tags).lower()
        name_lower = clean_name.lower()

        if any(w in name_lower or w in tags_lower for w in ["hanger", "coat hanger", "cabide"]):
            especial = (
                "Um cabide infantil encantador que transforma o quarto da criança "
                "em um cantinho cheio de personalidade e organização."
            )
            perfeito = (
                "Perfeito para organizar roupinhas no quarto infantil com charme. "
                "Ótimo presente para bebês e crianças em aniversários ou chá de bebê."
            )
        elif any(w in name_lower or w in tags_lower for w in ["mirror", "espelho"]):
            especial = (
                "Um espelho decorativo único, cortado a laser com precisão, "
                "que combina funcionalidade e arte para o ambiente infantil."
            )
            perfeito = (
                "Ideal para decorar quarto de bebê ou quarto infantil com estilo. "
                "Um presente memorável para maternidades e enxovais."
            )
        elif any(w in name_lower or w in tags_lower for w in ["calendar", "calendário", "calendario"]):
            especial = (
                "Um calendário decorativo que une organização e arte, "
                "tornando cada dia especial com detalhes únicos e lúdicos."
            )
            perfeito = (
                "Perfeito para quartos infantis, escritórios ou como presente criativo. "
                "Ideal para datas especiais e presentes personalizados."
            )
        elif any(w in name_lower or w in tags_lower for w in ["frame", "quadro", "porta-retrato"]):
            especial = (
                "Um porta-retrato artesanal que transforma memórias em arte, "
                "criando um objeto único cheio de afeto e significado."
            )
            perfeito = (
                "Exaltar momentos especiais na decoração de qualquer ambiente. "
                "Presente ideal para aniversários, casamentos e datas comemorativas."
            )
        elif any(w in name_lower or w in tags_lower for w in ["bebe", "baby", "nursery", "maternidade"]):
            especial = (
                "Uma peça especial que marca os primeiros momentos da vida, "
                "cheia de carinho e significado para toda a família."
            )
            perfeito = (
                "Presente perfeito para chá de bebê, decoração de quarto de bebê "
                "ou como lembrança afetiva dos primeiros anos."
            )
        elif any(w in name_lower or w in tags_lower for w in ["wedding", "casamento", "noiva"]):
            especial = (
                "Uma peça elegante que celebra o amor e marca para sempre "
                "o dia mais especial do casal."
            )
            perfeito = (
                "Ideal para decoração de cerimônia, recepção de convidados "
                "ou como presente inesquecível para os noivos."
            )
        elif any(w in name_lower or w in tags_lower for w in ["natal", "christmas", "pascoa", "easter"]):
            especial = (
                "Uma peça que traz o espírito da data para o ambiente, "
                "criando memórias afetivas para toda a família."
            )
            perfeito = (
                "Ideal para decoração sazonal, presente personalizado "
                "ou lembrancinha especial da época."
            )
        else:
            categories  = data.get("categories", ["Diversos"])
            cat_display = " | ".join(categories[:3]) if categories else "Produto personalizado"
            especial = (
                f"Uma peça de corte a laser em {cat_display}, "
                "criada para ser única e transmitir afeto em cada detalhe."
            )
            perfeito = (
                "Ideal como presente personalizado, decoração de ambiente "
                "ou lembrança especial para quem você ama."
            )

        description = (
            clean_name + "\n\n"
            "\U0001f3a8 Por Que Este Produto é Especial:\n"
            + especial + "\n\n"
            "\U0001f496 Perfeito Para:\n"
            + perfeito
        )

        database.setdefault(project_path, {})
        database[project_path]["ai_description"]           = description
        database[project_path]["description_generated_at"] = datetime.now().isoformat()
        return description
