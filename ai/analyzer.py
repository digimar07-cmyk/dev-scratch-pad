"""Analyzer - análise de projetos com IA"""
import os
from core.config import FAST_MODEL_THRESHOLD
from core.helpers import extract_tags_from_name
from core.logging_setup import LOGGER


class ProjectAnalyzer:
    def __init__(self, ollama_client, vision_analyzer):
        self.ollama = ollama_client
        self.vision = vision_analyzer
        self.logger = LOGGER

    def analyze_project_structure(self, project_path):
        structure = {
            "total_files": 0, "total_subfolders": 0,
            "file_types": {}, "subfolders": [],
            "images": [], "documents": [],
            "has_svg": False, "has_pdf": False, "has_dxf": False, "has_ai": False,
        }
        try:
            for root, dirs, files in os.walk(project_path):
                structure["total_files"] += len(files)
                if root == project_path:
                    structure["subfolders"] = dirs
                    structure["total_subfolders"] = len(dirs)
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    if ext == ".svg": structure["has_svg"] = True
                    elif ext == ".pdf": structure["has_pdf"] = True
                    elif ext == ".dxf": structure["has_dxf"] = True
                    elif ext == ".ai":  structure["has_ai"]  = True
                    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"):
                        structure["images"].append(file)
                    elif ext in (".pdf", ".txt", ".doc", ".docx"):
                        structure["documents"].append(file)
        except Exception:
            LOGGER.exception("Falha ao analisar estrutura de %s", project_path)
        return structure

    def _find_first_image_path(self, project_path):
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        return None

    def _choose_text_role(self, batch_size: int = 1) -> str:
        if batch_size > FAST_MODEL_THRESHOLD:
            return "text_fast"
        return "text_quality"

    def analyze_with_ai(self, project_path: str, batch_size: int = 1):
        try:
            name = os.path.basename(project_path)
            structure = self.analyze_project_structure(project_path)

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
            cover_img = self._find_first_image_path(project_path)
            if cover_img:
                vision_desc = self.vision._ollama_describe_image(cover_img)
                if vision_desc:
                    vision_line = f"\n🖼️ DESCRIÇÃO VISUAL DA CAPA: {vision_desc}"

            role = self._choose_text_role(batch_size)

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

            if self.ollama.stop_analysis:
                return self.fallback_analysis(project_path)

            text = self.ollama._ollama_generate_text(
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
                    categories = self.fallback_categories(project_path, categories)

                return categories[:8], tags

        except Exception:
            LOGGER.exception("Erro em analyze_with_ai para %s", project_path)

        return self.fallback_analysis(project_path)

    def fallback_categories(self, project_path, existing_categories):
        name = os.path.basename(project_path).lower()
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
        date_cats = ["Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", "Casamento", "Chá de Bebê", "Aniversário", "Dia das Crianças"]
        if not any(c in date_cats for c in result):
            for key, val in date_map.items():
                if key in name:
                    result.insert(0, val)
                    break
            else:
                result.insert(0, "Diversos")
        if len(result) < 2:
            for key, val in function_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        if len(result) < 3:
            for key, val in ambiente_map.items():
                if key in name:
                    result.append(val)
                    break
            else:
                result.append("Diversos")
        return result

    def fallback_analysis(self, project_path):
        name = os.path.basename(project_path).lower()
        name_tags = extract_tags_from_name(os.path.basename(project_path))
        categories = ["Diversos", "Diversos", "Diversos"]
        context_tags = ["personalizado", "artesanal"]
        checks = [
            (["pascoa","easter","coelho"], 0, "Páscoa"),
            (["natal","christmas","noel"], 0, "Natal"),
            (["mae","mom","mother"],       0, "Dia das Mães"),
            (["pai","dad","father"],       0, "Dia dos Pais"),
            (["baby","bebe","shower"],     0, "Chá de Bebê"),
            (["frame","foto","photo"],     1, "Porta-Retrato"),
            (["box","caixa"],              1, "Caixa Organizadora"),
            (["name","nome","sign"],       1, "Nome Decorativo"),
            (["quadro","painel"],          1, "Quadro Decorativo"),
            (["nursery","baby"],           2, "Quarto de Bebê"),
            (["bedroom","quarto"],         2, "Quarto"),
            (["kitchen","cozinha"],        2, "Cozinha"),
            (["sala","living"],            2, "Sala"),
        ]
        for words, idx, val in checks:
            if any(w in name for w in words):
                categories[idx] = val
        all_tags = name_tags + context_tags
        seen, unique_tags = set(), []
        for tag in all_tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        return categories, unique_tags[:10]
