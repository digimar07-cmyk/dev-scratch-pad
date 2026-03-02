"""
fallbacks.py — Lógica pura de análise e geração de conteúdo SEM Ollama.
Os dicionários vivem em keyword_maps.py.

GARANTIAS ABSOLUTAS:
  1. Categorias SEMPRE em PT-BR
  2. Date NUNCA retorna string genérica — usa DATE_INFER_MAP se necessário
  3. NUNCA retorna "Diversos", "Data Especial" ou qualquer termo genérico
  4. name_pt SEMPRE gerado e disponível para o card/modal
"""
import os
import re
import unicodedata
from utils.logging_setup import LOGGER

from ai.keyword_maps import (
    DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
    THEME_MAP, STYLE_MAP, PUBLIC_MAP,
    TRANSLATION_MAP, GENERIC_FALLBACK_FUNCTION,
    DATE_INFER_MAP,
    FINAL_FALLBACK_FUNCTION, FINAL_FALLBACK_AMBIENTE,
)

# Strings proibidas como resultado final (captura erros legados)
_BANNED = {
    "diversos", "data especial", "ambiente doméstico",
    "ambiente domestico", "general", "miscellaneous",
    "uncategorized", "sem categoria",
}


def _remove_accents(text):
    """Remove acentos para normalizar busca sem depender de locale."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def _normalize(text):
    """Lowercase + sem acento + sem extensões + separadores → espaço."""
    t = text.lower()
    for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai", ".eps"]:
        t = t.replace(ext, "")
    t = _remove_accents(t)
    t = re.sub(r"[\-_]",  " ", t)
    t = re.sub(r"\d{5,}", "",  t)   # remove códigos longos (IDs de produto)
    t = re.sub(r"\s+",    " ",  t).strip()
    return t


def _match(name_norm, mapping):
    """Retorna rótulo do primeiro grupo de keywords que bater. None se nenhuma."""
    for keywords, label in mapping:
        for kw in keywords:
            kw_norm = _remove_accents(kw.lower())
            if kw_norm in name_norm:
                return label
    return None


class FallbackGenerator:
    """
    Gera análises e descrições sem IA usando keyword_maps.py.

    Retorna no mínimo 3 categorias obrigatórias (sempre PT-BR):
      [0] Data comemorativa   — NUNCA genérica
      [1] Função / tipo       — NUNCA genérica
      [2] Ambiente / cômodo   — NUNCA genérica
    + até 3 opcionais: tema, estilo, público.
    """

    def __init__(self, project_scanner):
        self.scanner = project_scanner
        self.logger  = LOGGER

    # ------------------------------------------------------------------
    # Alias público para compatibilidade com main_window
    # ------------------------------------------------------------------
    def generate_fallback_description(self, project_path, project_data, structure):
        return self.fallback_description(project_path, project_data, structure)

    # ------------------------------------------------------------------
    # ANÁLISE PRINCIPAL
    # ------------------------------------------------------------------
    def fallback_analysis(self, project_path):
        """Retorna (categories: list[str], tags: list[str])."""
        raw_name  = os.path.basename(project_path)
        name_tags = self.scanner.extract_tags_from_name(raw_name)
        name_norm = _normalize(raw_name)

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
            key = _remove_accents(word.lower().strip(",.!?"))
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
        """Preenche categorias obrigatórias sem sobrescrever as da IA."""
        raw_name  = os.path.basename(project_path)
        name_norm = _normalize(raw_name)
        full      = self._build_categories(name_norm)

        result = list(existing_categories)

        DATE_VALS = {v for _, v in DATE_MAP}
        FUNC_VALS = {v for _, v in FUNCTION_MAP}
        ENV_VALS  = {v for _, v in AMBIENTE_MAP}

        has_date = any(c in DATE_VALS for c in result)
        has_func = any(c in FUNC_VALS for c in result)
        has_env  = any(c in ENV_VALS  for c in result)

        if not has_date:
            result.insert(0, full[0])
        if not has_func:
            result.insert(min(1, len(result)), full[1])
        if not has_env:
            result.append(full[2])

        # Remove termos banidos que possam ter vindo da IA
        result = [c for c in result if c.lower() not in _BANNED]

        return result[:8]

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------

    def _build_categories(self, name_norm):
        """
        Monta lista de categorias.
        Garante que nenhuma das 3 obrigatórias seja vazia ou genérica.
        """
        # --- Cat 2 e 3 primeiro (usadas para inferir data) ---
        func_cat = _match(name_norm, FUNCTION_MAP)
        if not func_cat:
            func_cat = _match(name_norm, GENERIC_FALLBACK_FUNCTION)
        if not func_cat:
            func_cat = FINAL_FALLBACK_FUNCTION

        env_cat = _match(name_norm, AMBIENTE_MAP)
        if not env_cat:
            env_cat = self._infer_ambiente_from_function(func_cat)
        if not env_cat:
            env_cat = FINAL_FALLBACK_AMBIENTE

        # Opcionais (detectar antes de inferir data — usados em DATE_INFER_MAP)
        theme_cat  = _match(name_norm, THEME_MAP)
        style_cat  = _match(name_norm, STYLE_MAP)
        public_cat = _match(name_norm, PUBLIC_MAP)

        # --- Cat 1: Data — NUNCA genérica ---
        date_cat = _match(name_norm, DATE_MAP)
        if not date_cat:
            # Tenta inferir pela ordem: tema → função → público
            for hint in (theme_cat, func_cat, public_cat):
                if hint and hint in DATE_INFER_MAP:
                    date_cat = DATE_INFER_MAP[hint]
                    break
        if not date_cat:
            # Último recurso: produto genérico → Aniversário (data mais universal)
            date_cat = "Aniversário"

        # Monta lista final (sem duplicatas)
        cats = [date_cat, func_cat, env_cat]
        for opt in (theme_cat, style_cat, public_cat):
            if opt and opt not in cats:
                cats.append(opt)

        # Remove banidos por garantia
        cats = [c for c in cats if c.lower() not in _BANNED]
        return cats[:8]

    def _infer_ambiente_from_function(self, func_cat):
        """Infere ambiente mais provável pelo tipo de produto."""
        mapping = {
            "Luminária":              "Quarto",
            "Porta-Retrato":           "Sala",
            "Topo de Bolo":            "Festa",
            "Centro de Mesa":          "Festa",
            "Mandala":                 "Sala",
            "Porta-Joias":             "Quarto",
            "Porta-Chaves":            "Sala",
            "Porta-Copo":              "Sala",
            "Suporte para Celular":    "Escritório",
            "Porta-Óculos":            "Escritório",
            "Organizador de Mesa":     "Escritório",
            "Porta-Vinho":             "Área Gourmet",
            "Bandeja":                 "Sala",
            "Pote Decorativo":         "Cozinha",
            "Relógio":                 "Sala",
            "Espelho Decorativo":      "Quarto",
            "Cabide":                  "Quarto",
            "Nome Decorativo":         "Quarto Infantil",
            "Plaquinha":               "Sala",
            "Caixa Organizadora":      "Escritório",
            "Caixa Presente":          "Festa",
            "Lembrancinha":            "Festa",
            "Quadro Decorativo":       "Sala",
            "Brinquedo Educativo":     "Quarto Infantil",
            "Jogo de Mesa":            "Sala de Jogos",
            "Organizador de Banheiro": "Banheiro",
            "Totem":                   "Festa",
            "Organizador de Cozinha":  "Cozinha",
            "Fruteira":                "Cozinha",
            "Escultura Decorativa":    "Sala",
            "Suporte para Plantas":    "Área de Lazer",
            "Porta-Livro":             "Escritório",
            "Etiqueta Decorativa":     "Escritório",
            "Porta-Controle":          "Sala",
            "Calendário Decorativo":   "Escritório",
            "Mapa Decorativo":         "Sala",
            "Painel Vazado":           "Sala",
            "Suporte Leitura":         "Escritório",
            "Aplique Decorativo":      "Sala",
            "Porta-Fone":              "Escritório",
            "Decoração Gamer":         "Sala de Jogos",
            "Brinde Corporativo":      "Escritório",
        }
        return mapping.get(func_cat)

    def _build_tags(self, name_norm, name_tags):
        """Constrói até 10 tags em PT-BR."""
        translated = []
        for w in name_norm.split():
            pt = TRANSLATION_MAP.get(w.strip())
            if pt:
                translated.append(pt)

        extra = []
        for mapping in (DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
                        THEME_MAP, STYLE_MAP, PUBLIC_MAP):
            hit = _match(name_norm, mapping)
            if hit and hit.lower() not in _BANNED:
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

    # ------------------------------------------------------------------
    # DESCRIÇÃO FALLBACK (template sem IA)
    # ------------------------------------------------------------------
    def fallback_description(self, project_path, project_data, structure):
        raw_name   = project_data.get("name", "Sem nome")
        clean_name = self._clean_name(raw_name)
        name_norm  = _normalize(raw_name)

        tags     = project_data.get("tags", [])
        combined = name_norm + " " + _normalize(" ".join(tags))

        func = _match(combined, FUNCTION_MAP) or FINAL_FALLBACK_FUNCTION
        date = _match(combined, DATE_MAP)
        env  = _match(combined, AMBIENTE_MAP)

        templates = {
            "Luminária": (
                "Uma luminária de corte laser que transforma qualquer ambiente com "
                "luz acolhedora e design exclusivo, tornando cada momento especial.",
                "Decorar quartos, salas e escritórios com estilo. "
                "Presente perfeito para quem aprecia um toque único."
            ),
            "Porta-Retrato": (
                "Uma peça artesanal que transforma memórias em arte, "
                "criando um objeto único cheio de afeto e significado.",
                "Exaltar momentos especiais em qualquer ambiente. "
                "Presente ideal para aniversários e datas comemorativas."
            ),
            "Caixa Organizadora": (
                "Uma caixa organizadora cortada a laser que une "
                "funcionalidade e beleza para manter seus objetos no lugar.",
                "Organizar escritórios, quartos e cozinhas com charme. "
                "Presente criativo e prático para qualquer ocasião."
            ),
            "Caixa Presente": (
                "Uma caixa presente artesanal que valoriza o gesto de presentear, "
                "tornando o momento da entrega tão especial quanto o presente.",
                "Empacotar presentes de aniversário, casamento ou qualquer "
                "data especial com elegância e personalidade."
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
                "como lembrança afetiva para os convidados."
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
            "Porta-Chaves": (
                "Um porta-chaves artesanal que organiza sua entrada com estilo, "
                "unindo praticidade e decoração em uma única peça exclusiva.",
                "Organizar a entrada de casas e apartamentos com charme. "
                "Presente funcional e diferenciado para qualquer ocasião."
            ),
            "Relógio": (
                "Um relógio artesanal de corte laser que dá personalidade única "
                "a qualquer parede, unindo design e funcionalidade.",
                "Presente sofisticado e decorativo para salas, escritórios "
                "ou qualquer ambiente que precise de um toque especial."
            ),
            "Brinquedo Educativo": (
                "Um brinquedo educativo de madeira cortado a laser que estimula "
                "o desenvolvimento cognitivo e a criatividade das crianças.",
                "Crianças de 1 a 10 anos que aprendem brincando. "
                "Presente perfeito que alia diversão e aprendizado."
            ),
            "Jogo de Mesa": (
                "Um jogo de mesa artesanal em madeira, feito com precisão laser, "
                "que proporciona momentos de diversão e união para toda a família.",
                "Famílias, amigos e gamers que valorizam jogos únicos e artesanais. "
                "Presente original para qualquer idade."
            ),
            "Porta-Joias": (
                "Uma porta-joias artesanal que organiza suas joias e bijuterias "
                "com charme e estilo, sendo peça decorativa ela mesma.",
                "Presente especial para o Dia das Mães, Dia dos Namorados "
                "ou qualquer mulher que merece um mimo exclusivo."
            ),
            "Porta-Vinho": (
                "Um porta-vinho artesanal em madeira que eleva qualquer ambiente "
                "com sofisticação, unindo funcionalidade e design exclusivo.",
                "Decorar áreas gourmet, salas de jantar e home bars. "
                "Presente premium para apreciadores de bons momentos."
            ),
        }

        if func in templates:
            especial, perfeito = templates[func]
        elif not date:
            # Infere data para usar no texto
            date = self._build_categories(name_norm)[0]
            especial = (
                f"Uma peça artesanal de corte a laser criada para tornar "
                f"{date} ainda mais especial e inesquecível."
            )
            perfeito = (
                f"Presentear ou decorar com muito carinho para {date}. "
                "Cada detalhe feito com precisão e afeto."
            )
        elif date == "Natal":
            especial = (
                "Uma peça natalina que traz o espírito do Natal para o ambiente, "
                "criando memórias afetivas para toda a família."
            )
            perfeito = (
                "Decorar a casa no Natal, presentear com afeto "
                "ou como lembrancinha da época festiva."
            )
        elif date == "Páscoa":
            especial = (
                "Uma decoração de Páscoa artesanal que enche o ambiente de alegria "
                "e aconchego, perfeita para celebrar com a família."
            )
            perfeito = (
                "Decorar mesas e ambientes na Páscoa ou presentear "
                "com uma lembrancinha exclusiva e cheia de carinho."
            )
        elif date == "Casamento":
            especial = (
                "Uma peça elegante que celebra o amor e marca para sempre "
                "o dia mais especial do casal."
            )
            perfeito = (
                "Decoração de cerimônia, recepção de convidados "
                "ou como presente inesquecível para os noivos."
            )
        elif env in ("Quarto de Bebê", "Quarto Infantil"):
            especial = (
                "Uma peça especial que marca os primeiros momentos da vida, "
                "cheia de carinho e significado para toda a família."
            )
            perfeito = (
                "Decoração de quarto de bebê ou lembrança afetiva "
                "dos primeiros anos de vida."
            )
        else:
            cats = project_data.get("categories", [])
            cat_display = " | ".join(cats[:3]) if cats else "produto personalizado"
            especial = (
                f"Uma peça de corte a laser — {cat_display} — "
                "criada para ser única e transmitir afeto em cada detalhe."
            )
            perfeito = (
                "Presente personalizado, decoração de ambiente "
                "ou lembrança especial para quem você ama."
            )

        return (
            clean_name + "\n\n"
            "🎨 Por Que Este Produto é Especial:\n" + especial + "\n\n"
            "💖 Perfeito Para:\n" + perfeito
        )

    def _clean_name(self, raw_name):
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai", ".eps"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = clean.replace("-", " ").replace("_", " ").strip()
        return clean
