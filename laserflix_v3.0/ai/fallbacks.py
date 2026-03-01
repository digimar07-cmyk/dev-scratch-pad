"""
Geradores de fallback (sem IA)
Usado quando Ollama está indisponível — garante que análise e descrição
SEMPRE retornam um resultado válido.
"""
import os
import re
from utils.logging_setup import LOGGER


class FallbackGenerator:
    """
    Gera análises e descrições sem IA usando regras baseadas em keywords.
    Usado quando Ollama está indisponível.
    """

    def __init__(self, project_scanner):
        self.scanner = project_scanner
        self.logger = LOGGER

    # ------------------------------------------------------------------
    # Alias público para compatibilidade com main_window
    # ------------------------------------------------------------------
    def generate_fallback_description(self, project_path, project_data, structure):
        """Alias de fallback_description (chamado por main_window)."""
        return self.fallback_description(project_path, project_data, structure)

    def fallback_analysis(self, project_path):
        """
        Gera categorias e tags baseadas em keywords no nome.
        Chamado quando Ollama está offline ou retornou resposta vazia.

        Returns:
            Tuple (categories: list, tags: list)
        """
        name = os.path.basename(project_path).lower()
        name_tags = self.scanner.extract_tags_from_name(os.path.basename(project_path))

        categories = ["Diversos", "Diversos", "Diversos"]
        context_tags = ["personalizado", "artesanal"]

        checks = [
            (["pascoa", "easter", "coelho"],    0, "Páscoa"),
            (["natal", "christmas", "noel"],      0, "Natal"),
            (["mae", "mom", "mother"],             0, "Dia das Mães"),
            (["pai", "dad", "father"],             0, "Dia dos Pais"),
            (["baby", "bebe", "shower"],           0, "Chá de Bebê"),
            (["frame", "foto", "photo"],           1, "Porta-Retrato"),
            (["box", "caixa"],                     1, "Caixa Organizadora"),
            (["name", "nome", "sign"],             1, "Nome Decorativo"),
            (["quadro", "painel"],                  1, "Quadro Decorativo"),
            (["nursery", "baby"],                  2, "Quarto de Bebê"),
            (["bedroom", "quarto"],                 2, "Quarto"),
            (["kitchen", "cozinha"],                2, "Cozinha"),
            (["sala", "living"],                    2, "Sala"),
        ]

        for words, idx, val in checks:
            if any(w in name for w in words):
                categories[idx] = val

        all_tags = name_tags + context_tags
        seen = set()
        unique_tags = []
        for tag in all_tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)

        return categories, unique_tags[:10]

    def fallback_categories(self, project_path, existing_categories):
        """
        Completa categorias faltantes baseadas em keywords.
        Chamado quando IA retornou menos de 3 categorias.
        """
        name = os.path.basename(project_path).lower()
        result = list(existing_categories)

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

    def fallback_description(self, project_path, project_data, structure):
        """
        Gera descrição baseada em templates (sem IA).
        Chamado quando Ollama está offline ou retornou resposta vazia.
        Respeita o mesmo formato da descrição gerada por IA:
            NOME\n\n🎨 Por Que Este Produto é Especial:\n...\n\n💖 Perfeito Para:\n...
        """
        raw_name = project_data.get("name", "Sem nome")
        clean_name = self._clean_name(raw_name)

        tags = project_data.get("tags", [])
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
            categories = project_data.get("categories", ["Diversos"])
            cat_display = " | ".join(categories[:3]) if categories else "Produto personalizado"
            especial = (
                f"Uma peça de corte a laser em {cat_display}, "
                "criada para ser única e transmitir afeto em cada detalhe."
            )
            perfeito = (
                "Ideal como presente personalizado, decoração de ambiente "
                "ou lembrança especial para quem você ama."
            )

        return (
            clean_name + "\n\n"
            "\U0001f3a8 Por Que Este Produto é Especial:\n"
            + especial + "\n\n"
            "\U0001f496 Perfeito Para:\n"
            + perfeito
        )

    def _clean_name(self, raw_name):
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = clean.replace("-", " ").replace("_", " ").strip()
        return clean
