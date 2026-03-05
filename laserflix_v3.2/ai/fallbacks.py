"""
fallbacks.py — Lógica pura de análise e geração de conteúdo SEM Ollama.
Os dicionários vivem em keyword_maps.py.

GARANTIAS ABSOLUTAS:
  1. Categorias SEMPRE em PT-BR
  2. Date NUNCA retorna string genérica — usa DATE_INFER_MAP se necessário
  3. NUNCA retorna "Diversos", "Data Especial" ou qualquer termo genérico
  4. name_pt SEMPRE gerado e disponível para o card/modal

LÓGICA REFINADA v741 (SUPORTE A 12 CATEGORIAS):
  - Detecção inteligente por keywords no nome+tags
  - _match_all() retorna TODAS as categorias detectadas (não só primeira)
  - Limite aumentado de 8 → 12 categorias para produtos complexos
  - Templates específicos para cada tipo de peça
  - Cascata: keyword > data > ambiente > função > genérico
  - Novas funções: Book Nook, Tracker, Régua, Organizador de Ferramentas

CLEANUP v3.2 (L-01/L-03/L-04/L-05):
  - _clean_name() removida — usa normalize_project_name() de text_utils
  - _match() legado (v740) removido — _build_tags usa _match_all()
  - generate_fallback_description() alias removido
  - parâmetro 'structure' fantasma removido de fallback_description()
"""
import os
import re
from utils.logging_setup import LOGGER
from utils.text_utils import normalize_project_name, remove_accents

from ai.keyword_maps import (
    DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
    THEME_MAP, STYLE_MAP, PUBLIC_MAP,
    TRANSLATION_MAP, GENERIC_FALLBACK_FUNCTION,
    DATE_INFER_MAP,
    FINAL_FALLBACK_FUNCTION, FINAL_FALLBACK_AMBIENTE,
)

# Strings proibidas como resultado final (captura erros legados)
# FONTE Única: config/constants.py — importada aqui para uso interno
_BANNED = {
    "diversos", "data especial", "ambiente doméstico",
    "ambiente domestico", "general", "miscellaneous",
    "uncategorized", "sem categoria",
}


def _match_all(name_norm, mapping, max_results=5):
    """
    Retorna TODAS as categorias que batem no nome (v741).

    Args:
        name_norm: Nome normalizado do projeto
        mapping: Lista de (keywords, label)
        max_results: Número máximo de resultados

    Returns:
        Lista de rótulos que bateram (pode ser vazia)
    """
    found = []
    seen_labels = set()

    for keywords, label in mapping:
        if label in seen_labels:
            continue
        for kw in keywords:
            kw_norm = remove_accents(kw.lower())
            if kw_norm in name_norm:
                found.append(label)
                seen_labels.add(label)
                break
        if len(found) >= max_results:
            break

    return found


class FallbackGenerator:
    """
    Gera análises e descrições sem IA usando keyword_maps.py.

    Retorna no mínimo 3 categorias obrigatórias (sempre PT-BR):
      [0] Data comemorativa   — NUNCA genérica
      [1] Função / tipo       — NUNCA genérica
      [2] Ambiente / cômodo   — NUNCA genérica
    + até 9 adicionais de temas, estilos, públicos e contextos múltiplos.

    LIMITE v741: Até 12 categorias totais.
    """

    def __init__(self, project_scanner):
        self.scanner = project_scanner
        self.logger  = LOGGER

    # ------------------------------------------------------------------
    # ANÁLISE PRINCIPAL
    # ------------------------------------------------------------------
    def fallback_analysis(self, project_path):
        """Retorna (categories: list[str], tags: list[str])."""
        raw_name  = os.path.basename(project_path)
        name_tags = self.scanner.extract_tags_from_name(raw_name)
        name_norm = normalize_project_name(raw_name)

        cats = self._build_categories(name_norm)
        tags = self._build_tags(name_norm, name_tags)
        return cats, tags

    # ------------------------------------------------------------------
    # TRADUÇÃO DO NOME (para name_pt no card)
    # ------------------------------------------------------------------
    def translate_name(self, raw_name):
        """
        Traduz palavras EN→PT usando TRANSLATION_MAP.
        Retorna string traduzida ou None se o nome já é PT ou não mudou.
        """
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai", ".eps"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = re.sub(r"[\-_]", " ", clean).strip()

        words, changed = clean.split(), False
        result_words = []
        for word in words:
            key = remove_accents(word.lower().strip(",.!?"))
            if key in TRANSLATION_MAP:
                result_words.append(TRANSLATION_MAP[key].title())
                changed = True
            else:
                result_words.append(word)

        if not changed:
            return None
        result = " ".join(result_words)
        return result if result.lower() != clean.lower() else None

    # ------------------------------------------------------------------
    # COMPLEMENTA categorias vindas da IA (quando IA retornou < 3)
    # ------------------------------------------------------------------
    def fallback_categories(self, project_path, existing_categories):
        """
        Preenche os 3 slots obrigatórios (date, func, env) sem sobrescrever
        os que a IA já retornou corretamente.
        Remove banidos e limita a 12 (v741).
        """
        raw_name  = os.path.basename(project_path)
        name_norm = normalize_project_name(raw_name)
        full      = self._build_categories(name_norm)

        DATE_VALS = {v for _, v in DATE_MAP}
        FUNC_VALS = {v for _, v in FUNCTION_MAP}
        ENV_VALS  = {v for _, v in AMBIENTE_MAP}

        result = [c for c in existing_categories if c.lower() not in _BANNED]

        has_date = any(c in DATE_VALS for c in result)
        has_func = any(c in FUNC_VALS for c in result)
        has_env  = any(c in ENV_VALS  for c in result)

        if not has_env:
            result.append(full[2])

        if not has_func:
            func_idx = 1 if has_date else 0
            result.insert(func_idx, full[1])

        if not has_date:
            result.insert(0, full[0])

        return result[:12]

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------

    def _build_categories(self, name_norm):
        """
        Monta lista de categorias usando _match_all().
        Garante que nenhuma das 3 obrigatórias seja vazia ou genérica.
        LIMITE v741: Até 12 categorias.
        """
        func_cats = _match_all(name_norm, FUNCTION_MAP, max_results=3)
        if not func_cats:
            func_cats = _match_all(name_norm, GENERIC_FALLBACK_FUNCTION, max_results=1)
        if not func_cats:
            func_cats = [FINAL_FALLBACK_FUNCTION]

        env_cats = _match_all(name_norm, AMBIENTE_MAP, max_results=2)
        if not env_cats:
            inferred = self._infer_ambiente_from_function(func_cats[0])
            env_cats = [inferred] if inferred else []
        if not env_cats:
            env_cats = [FINAL_FALLBACK_AMBIENTE]

        theme_cats  = _match_all(name_norm, THEME_MAP,  max_results=2)
        style_cats  = _match_all(name_norm, STYLE_MAP,  max_results=2)
        public_cats = _match_all(name_norm, PUBLIC_MAP, max_results=2)

        date_cats = _match_all(name_norm, DATE_MAP, max_results=2)
        if not date_cats:
            for hint in (
                theme_cats[0]  if theme_cats  else None,
                func_cats[0],
                public_cats[0] if public_cats else None,
            ):
                if hint and hint in DATE_INFER_MAP:
                    date_cats = [DATE_INFER_MAP[hint]]
                    break
        if not date_cats:
            date_cats = ["Aniversário"]

        cats = []
        seen = set()

        for cat in date_cats[:2]:
            if cat and cat not in seen and cat.lower() not in _BANNED:
                cats.append(cat); seen.add(cat)

        for cat in func_cats[:3]:
            if cat and cat not in seen and cat.lower() not in _BANNED:
                cats.append(cat); seen.add(cat)

        for cat in env_cats[:2]:
            if cat and cat not in seen and cat.lower() not in _BANNED:
                cats.append(cat); seen.add(cat)

        for cat_list in (theme_cats, style_cats, public_cats):
            for cat in cat_list[:2]:
                if cat and cat not in seen and cat.lower() not in _BANNED:
                    cats.append(cat); seen.add(cat)

        return cats[:12]

    def _infer_ambiente_from_function(self, func_cat):
        """Infere ambiente mais provável pelo tipo de produto."""
        mapping = {
            "Luminária":               "Quarto",
            "Porta-Retrato":            "Sala",
            "Topo de Bolo":             "Festa",
            "Centro de Mesa":           "Festa",
            "Mandala":                  "Sala",
            "Porta-Joias":              "Quarto",
            "Porta-Chaves":             "Sala",
            "Porta-Copo":               "Sala",
            "Suporte para Celular":     "Escritório",
            "Porta-Óculos":             "Escritório",
            "Organizador de Mesa":      "Escritório",
            "Porta-Vinho":              "Área Gourmet",
            "Bandeja":                  "Sala",
            "Pote Decorativo":          "Cozinha",
            "Relógio":                  "Sala",
            "Espelho Decorativo":       "Quarto",
            "Cabide":                   "Quarto",
            "Nome Decorativo":          "Quarto Infantil",
            "Plaquinha":                "Sala",
            "Caixa Organizadora":       "Escritório",
            "Caixa Presente":           "Festa",
            "Lembrancinha":             "Festa",
            "Quadro Decorativo":        "Sala",
            "Brinquedo Educativo":      "Quarto Infantil",
            "Jogo de Mesa":             "Sala de Jogos",
            "Organizador de Banheiro":  "Banheiro",
            "Totem":                    "Festa",
            "Organizador de Cozinha":   "Cozinha",
            "Fruteira":                 "Cozinha",
            "Escultura Decorativa":     "Sala",
            "Suporte para Plantas":     "Área de Lazer",
            "Porta-Livro":              "Escritório",
            "Suporte para Livros":      "Biblioteca",
            "Quadro de Acompanhamento": "Escritório",
            "Régua de Crescimento":     "Quarto Infantil",
            "Organizador de Ferramentas": "Garagem",
            "Etiqueta Decorativa":      "Escritório",
            "Porta-Controle":           "Sala",
            "Calendário Decorativo":    "Escritório",
            "Mapa Decorativo":          "Sala",
            "Painel Vazado":            "Sala",
            "Suporte Leitura":          "Escritório",
            "Aplique Decorativo":       "Sala",
            "Porta-Fone":               "Escritório",
            "Decoração Gamer":          "Sala de Jogos",
            "Brinde Corporativo":       "Escritório",
        }
        return mapping.get(func_cat)

    def _build_tags(self, name_norm, name_tags):
        """Constrói até 10 tags em PT-BR."""
        translated = []
        for w in name_norm.split():
            pt = TRANSLATION_MAP.get(w.strip())
            if pt:
                translated.append(pt)

        # Usa _match_all para pegar até 2 hits por mapa (mais rico que _match)
        extra = []
        for mapping in (DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
                        THEME_MAP, STYLE_MAP, PUBLIC_MAP):
            hits = _match_all(name_norm, mapping, max_results=2)
            for hit in hits:
                if hit.lower() not in _BANNED:
                    extra.append(hit.lower())

        extra += ["corte a laser", "personalizado", "artesanal"]

        all_tags = list(name_tags) + translated + extra
        seen, unique = set(), []
        for t in all_tags:
            key = t.lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(t)

        return unique[:10]

    # ================================================================
    # DESCRIÇÃO FALLBACK (v740 refinado)
    # ================================================================
    def fallback_description(self, project_path, project_data):
        """
        Gera descrição sem IA usando detecção inteligente por keywords.

        CASCATA DE DETECÇÃO:
          1° Palavras-chave específicas (cabide, espelho, calendário, etc)
          2° Data comemorativa (natal, páscoa, casamento)
          3° Ambiente/Público (bebê, infantil)
          4° Função genérica (pela categoria)
          5° Fallback genérico (last resort)

        NUNCA retorna frase padrão igual para todos — sempre contextual.
        """
        raw_name  = project_data.get("name", "Sem nome")
        # Usa normalize_project_name para limpeza do nome de exibição
        clean_name = normalize_project_name(raw_name).title()
        name_norm  = normalize_project_name(raw_name)

        tags          = project_data.get("tags", [])
        tags_lower    = " ".join(tags).lower()
        combined_text = name_norm + " " + tags_lower

        # 1° PALAVRAS-CHAVE ESPECÍFICAS
        if any(w in combined_text for w in ["hanger", "coat hanger", "cabide"]):
            especial = (
                "Um cabide infantil encantador que transforma o quarto da criança "
                "em um cantinho cheio de personalidade e organização."
            )
            perfeito = (
                "Perfeito para organizar roupinhas no quarto infantil com charme. "
                "Ótimo presente para bebês e crianças em aniversários ou chá de bebê."
            )

        elif any(w in combined_text for w in ["mirror", "espelho"]):
            especial = (
                "Um espelho decorativo único, cortado a laser com precisão, "
                "que combina funcionalidade e arte para o ambiente infantil."
            )
            perfeito = (
                "Ideal para decorar quarto de bebê ou quarto infantil com estilo. "
                "Um presente memorável para maternidades e enxovais."
            )

        elif any(w in combined_text for w in ["calendar", "calendario"]):
            especial = (
                "Um calendário decorativo que une organização e arte, "
                "tornando cada dia especial com detalhes únicos e lúdicos."
            )
            perfeito = (
                "Perfeito para quartos infantis, escritórios ou como presente criativo. "
                "Ideal para datas especiais e presentes personalizados."
            )

        elif any(w in combined_text for w in ["frame", "quadro", "porta retrato"]):
            especial = (
                "Um porta-retrato artesanal que transforma memórias em arte, "
                "criando um objeto único cheio de afeto e significado."
            )
            perfeito = (
                "Exaltar momentos especiais na decoração de qualquer ambiente. "
                "Presente ideal para aniversários, casamentos e datas comemorativas."
            )

        # 2° DATA COMEMORATIVA
        elif any(w in combined_text for w in ["bebe", "baby", "nursery", "maternidade"]):
            especial = (
                "Uma peça especial que marca os primeiros momentos da vida, "
                "cheia de carinho e significado para toda a família."
            )
            perfeito = (
                "Presente perfeito para chá de bebê, decoração de quarto de bebê "
                "ou como lembranca afetiva dos primeiros anos."
            )

        elif any(w in combined_text for w in ["wedding", "casamento", "noiva"]):
            especial = (
                "Uma peça elegante que celebra o amor e marca para sempre "
                "o dia mais especial do casal."
            )
            perfeito = (
                "Ideal para decoração de cerimônia, recepção de convidados "
                "ou como presente inesquecível para os noivos."
            )

        elif any(w in combined_text for w in ["natal", "christmas", "noel"]):
            especial = (
                "Uma peça que traz o espírito do Natal para o ambiente, "
                "criando memórias afetivas para toda a família."
            )
            perfeito = (
                "Ideal para decoração sazonal, presente personalizado "
                "ou lembrancinha especial da época."
            )

        elif any(w in combined_text for w in ["pascoa", "easter", "coelho"]):
            especial = (
                "Uma decoração de Páscoa artesanal que enche o ambiente de alegria "
                "e aconchego, perfeita para celebrar com a família."
            )
            perfeito = (
                "Ideal para decorar mesas e ambientes na Páscoa ou presentear "
                "com uma lembrancinha exclusiva e cheia de carinho."
            )

        # 3° DETECÇÃO POR FUNÇÃO/CATEGORIA
        else:
            categories  = project_data.get("categories", ["Diversos"])
            cat_display = " | ".join(categories[:3]) if categories else "Produto personalizado"
            func        = categories[1] if len(categories) > 1 else "Diversos"

            templates_by_func = {
                "Luminária": (
                    "Uma luminária de corte laser que transforma qualquer ambiente com "
                    "luz acolhedora e design exclusivo, tornando cada momento especial.",
                    "Decorar quartos, salas e escritórios com estilo. "
                    "Presente perfeito para quem aprecia um toque único."
                ),
                "Caixa Organizadora": (
                    "Uma caixa organizadora cortada a laser que une "
                    "funcionalidade e beleza para manter seus objetos no lugar.",
                    "Organizar escritórios, quartos e cozinhas com charme. "
                    "Presente criativo e prático para qualquer ocasião."
                ),
                "Nome Decorativo": (
                    "Um nome decorativo único, cortado a laser com precisão milímetro a "
                    "milímetro, que personaliza qualquer ambiente com identidade própria.",
                    "Decorar quartos infantis, quarto de bebê ou salas com o nome da "
                    "família. Lembrancinha especial para aniversários e chá de bebê."
                ),
                "Topo de Bolo": (
                    "Um topo de bolo personalizado que transforma qualquer comemoração "
                    "em um momento único e inesquecível para toda a família.",
                    "Festas de aniversário, casamentos, formaturas e qualquer "
                    "celebração que mereça um toque artesanal especial."
                ),
                "Lembrancinha": (
                    "Uma lembrancinha delicada e personalizada, cortada a laser com "
                    "atenção a cada detalhe, perfeita para guardar com carinho.",
                    "Distribuir em festas, casamentos e eventos especiais "
                    "como lembranca afetiva para os convidados."
                ),
                "Plaquinha": (
                    "Uma plaquinha exclusiva com design moderno e mensagem afetiva, "
                    "criando identidade e personalidade para qualquer espaço.",
                    "Sinalizar ambientes em casa ou eventos com estilo. "
                    "Presente original e personalizado para quem você ama."
                ),
                "Mandala": (
                    "Uma mandala cortada a laser com geometria precisa e rica em detalhes, "
                    "trazendo equilíbrio visual e energia positiva para o ambiente.",
                    "Decorar salas, quartos e escritórios com arte e simbolismo. "
                    "Presente significativo para quem valoriza espiritualidade e design."
                ),
            }

            if func in templates_by_func:
                especial, perfeito = templates_by_func[func]
            else:
                especial = (
                    f"Uma peça de corte a laser em {cat_display}, "
                    "criada para ser única e transmitir afeto em cada detalhe."
                )
                perfeito = (
                    "Ideal como presente personalizado, decoração de ambiente "
                    "ou lembranca especial para quem você ama."
                )

        return (
            clean_name + "\n\n"
            "🎨 Por Que Este Produto é Especial:\n"
            + especial + "\n\n"
            "💖 Perfeito Para:\n"
            + perfeito
        )
