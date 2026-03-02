"""
fallbacks.py
Lógica de análise e geração de descrições SEM Ollama.

Os dicionários de keywords vivem em keyword_maps.py.
Este arquivo só contém lógica pura.

GARANTIAS:
  - Sempre retorna 3 categorias obrigatórias (data, função, ambiente)
  - NUNCA retorna "Diversos" como categoria
  - Tags sempre em Português
  - name_pt sempre gerado (tradução por dicionário)
"""
import os
import re
from utils.logging_setup import LOGGER

from ai.keyword_maps import (
    DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
    THEME_MAP, STYLE_MAP, PUBLIC_MAP,
    TRANSLATION_MAP, GENERIC_FALLBACK_FUNCTION,
    FINAL_FALLBACK_FUNCTION, FINAL_FALLBACK_DATE, FINAL_FALLBACK_AMBIENTE,
)


def _match(name_lower, mapping):
    """Retorna rótulo do primeiro grupo de keywords que bater no nome."""
    for keywords, label in mapping:
        if any(k in name_lower for k in keywords):
            return label
    return None


class FallbackGenerator:
    """
    Gera análises e descrições sem IA usando regras de keyword_maps.py.

    Categorias retornadas (sempre nesta ordem):
      [0] Data comemorativa   (OBRIGATÓRIA — nunca "Diversos")
      [1] Função / tipo       (OBRIGATÓRIA — nunca "Diversos")
      [2] Ambiente / cômodo   (OBRIGATÓRIA — nunca "Diversos")
      [3] Tema visual          (opcional)
      [4] Estilo               (opcional)
      [5] Público-alvo         (opcional)
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
    # ANÁLISE PRINCIPAL (sem Ollama)
    # ------------------------------------------------------------------
    def fallback_analysis(self, project_path):
        """
        Retorna (categories: list[str], tags: list[str]).
        Chamado quando Ollama está offline ou retornou resposta vazia.
        """
        raw_name  = os.path.basename(project_path)
        name_tags = self.scanner.extract_tags_from_name(raw_name)
        name_low  = self._normalize(raw_name)

        cats = self._build_categories(name_low)
        tags = self._build_tags(name_low, name_tags)
        return cats, tags

    # ------------------------------------------------------------------
    # TRADUÇÃO DO NOME
    # ------------------------------------------------------------------
    def translate_name(self, raw_name):
        """
        Traduz palavras inglesas do nome do produto para PT-BR usando
        TRANSLATION_MAP. Palavras já em português ou não mapeadas
        são mantidas como estão.
        Retorna string ou None se não houver tradução relevante.
        """
        # Limpa o nome
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = re.sub(r"[\-_]", " ", clean).strip()

        words   = clean.split()
        translated_words = []
        changed = False

        for word in words:
            key = word.lower().strip(",.!?")
            if key in TRANSLATION_MAP:
                translated_words.append(TRANSLATION_MAP[key].title())
                changed = True
            else:
                translated_words.append(word)

        if not changed:
            return None  # Nome já parece ser PT-BR, não exibe dobrado

        result = " ".join(translated_words)
        return result if result.lower() != clean.lower() else None

    # ------------------------------------------------------------------
    # COMPLEMENTA categorias quando IA retornou < 3
    # ------------------------------------------------------------------
    def fallback_categories(self, project_path, existing_categories):
        """
        Garante as 3 categorias obrigatórias sem sobrescrever
        o que a IA já preencheu corretamente.
        """
        raw_name = os.path.basename(project_path)
        name_low = self._normalize(raw_name)
        full     = self._build_categories(name_low)

        result = list(existing_categories)

        DATE_OPTS = {v for _, v in DATE_MAP}
        FUNC_OPTS = {v for _, v in FUNCTION_MAP}
        ENV_OPTS  = {v for _, v in AMBIENTE_MAP}

        has_date = any(c in DATE_OPTS for c in result)
        has_func = any(c in FUNC_OPTS for c in result)
        has_env  = any(c in ENV_OPTS  for c in result)

        if not has_date:
            result.insert(0, full[0])
        if not has_func:
            result.insert(min(1, len(result)), full[1])
        if not has_env:
            result.append(full[2])

        return result[:8]

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------

    def _normalize(self, text):
        """Lowercase + remove extensões + separadores viram espaço."""
        t = text.lower()
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            t = t.replace(ext, "")
        t = re.sub(r"[\-_]",  " ", t)
        t = re.sub(r"\d{5,}", "",  t)
        t = re.sub(r"\s+",    " ",  t).strip()
        return t

    def _build_categories(self, name_low):
        """
        Monta lista de categorias.
        Garante que NENHUMA das 3 obrigatórias seja vazia ou 'Diversos'.
        """
        from ai.keyword_maps import GENERIC_FALLBACK_FUNCTION

        # --- Cat 1: Data comemorativa ---
        date_cat = _match(name_low, DATE_MAP)
        if not date_cat:
            date_cat = FINAL_FALLBACK_DATE          # "Data Especial"

        # --- Cat 2: Função ---
        func_cat = _match(name_low, FUNCTION_MAP)
        if not func_cat:
            # Segunda chance: GENERIC_FALLBACK_FUNCTION
            func_cat = _match(name_low, GENERIC_FALLBACK_FUNCTION)
        if not func_cat:
            func_cat = FINAL_FALLBACK_FUNCTION      # "Decoração Artesanal"

        # --- Cat 3: Ambiente ---
        env_cat = _match(name_low, AMBIENTE_MAP)
        if not env_cat:
            # Infere ambiente a partir da função detectada
            env_cat = self._infer_ambiente_from_function(func_cat)
        if not env_cat:
            env_cat = FINAL_FALLBACK_AMBIENTE       # "Ambiente Doméstico"

        cats = [date_cat, func_cat, env_cat]

        # --- Opcionais ---
        theme_cat  = _match(name_low, THEME_MAP)
        style_cat  = _match(name_low, STYLE_MAP)
        public_cat = _match(name_low, PUBLIC_MAP)

        for opt in (theme_cat, style_cat, public_cat):
            if opt and opt not in cats:
                cats.append(opt)

        return cats[:8]

    def _infer_ambiente_from_function(self, func_cat):
        """
        Infere ambiente mais provável baseado na função do produto.
        Evita retornar o fallback genérico quando possível.
        """
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
            "Porta-Óculos":           "Escritório",
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
            "Caixa Presente":          "Festa",
            "Suporte Leitura":         "Escritório",
            "Aplique Decorativo":      "Sala",
            "Porta-Fone":              "Escritório",
            "Decoração Gamer":        "Sala de Jogos",
            "Brinde Corporativo":      "Escritório",
        }
        return mapping.get(func_cat)

    def _build_tags(self, name_low, name_tags):
        """
        Constrói até 10 tags em Português:
          1. Keywords do nome traduzidas (via TRANSLATION_MAP)
          2. Rótulos detectados pelos mapas
          3. Tags genéricas de produto laser
        """
        extra = []

        # Traduz palavras do nome
        translated = []
        for w in name_low.split():
            pt = TRANSLATION_MAP.get(w.strip())
            if pt:
                translated.append(pt)

        # Rótulos detectados como tags contextuais
        for mapping in (DATE_MAP, FUNCTION_MAP, AMBIENTE_MAP,
                        THEME_MAP, STYLE_MAP, PUBLIC_MAP):
            hit = _match(name_low, mapping)
            if hit and hit not in (FINAL_FALLBACK_DATE,
                                   FINAL_FALLBACK_FUNCTION,
                                   FINAL_FALLBACK_AMBIENTE):
                extra.append(hit.lower())

        # Tags genéricas fixas de corte laser
        extra += ["corte a laser", "personalizado", "artesanal"]

        # Junta: nome_tags originais + traduções + extras
        all_tags = list(name_tags) + translated + extra

        # Deduplica preservando ordem, case-insensitive
        seen, unique = set(), []
        for t in all_tags:
            key = t.lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(t)

        return unique[:10]

    # ------------------------------------------------------------------
    # DESCRIÇÃO FALLBACK (sem IA)
    # ------------------------------------------------------------------
    def fallback_description(self, project_path, project_data, structure):
        """
        Gera descrição por template baseado em função + data detectadas.
        """
        raw_name   = project_data.get("name", "Sem nome")
        clean_name = self._clean_name(raw_name)
        name_low   = self._normalize(raw_name)

        tags     = project_data.get("tags", [])
        combined = name_low + " " + " ".join(tags).lower()

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
        }

        if func in templates:
            especial, perfeito = templates[func]
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
                "Decoração de quarto de bebê ou lembranca afetiva "
                "dos primeiros anos de vida."
            )
        else:
            cats = project_data.get("categories", [])
            cat_display = " | ".join(cats[:3]) if cats else "produto personalizado"
            especial = (
                f"Uma peça de corte a laser em {cat_display}, "
                "criada para ser única e transmitir afeto em cada detalhe."
            )
            perfeito = (
                "Presente personalizado, decoração de ambiente "
                "ou lembranca especial para quem você ama."
            )

        return (
            clean_name + "\n\n"
            "🎨 Por Que Este Produto é Especial:\n" + especial + "\n\n"
            "💖 Perfeito Para:\n" + perfeito
        )

    def _clean_name(self, raw_name):
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = clean.replace("-", " ").replace("_", " ").strip()
        return clean
