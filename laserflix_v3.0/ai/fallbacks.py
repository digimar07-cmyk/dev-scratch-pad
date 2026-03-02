"""
Geradores de fallback (sem IA)
Usado quando Ollama está indisponível — garante que análise e descrição
SEMPRE retornam um resultado válido.

REGRAS (espelham exatamente o prompt da TextGenerator.analyze_project):
  Cat 1 — Data comemorativa (OBRIGATÓRIA)
  Cat 2 — Função / tipo do item  (OBRIGATÓRIA)
  Cat 3 — Ambiente / cômodo       (OBRIGATÓRIA)
  Cat 4 — Estilo                   (opcional)
  Cat 5 — Público                  (opcional)
"""
import os
import re
from utils.logging_setup import LOGGER


# ---------------------------------------------------------------------------
# DICIONÁRIOS DE KEYWORDS  (chave = substring; valor = rótulo)
# Ordem importa: mais específico primeiro
# ---------------------------------------------------------------------------

_DATE_MAP = [
    # Páscoa
    (["pascoa", "easter", "coelho", "coelha", "coelhinho", "ovo pascoa",
      "ovos pascoa", "galinha", "pintinho"], "Páscoa"),
    # Natal
    (["natal", "christmas", "noel", "papai noel", "rena", "rudolph",
      "snowman", "boneco de neve", "arvore natal", "xmas", "jingle",
      "sleigh", "star natal", "pinheiro"], "Natal"),
    # Dia das Mães
    (["mae", "mãe", "mom", "mother", "mothers day", "dia das maes",
      "maes", "maezinha", "mainha"], "Dia das Mães"),
    # Dia dos Pais
    (["pai", "dad", "father", "fathers day", "dia dos pais",
      "paizinho", "papai"], "Dia dos Pais"),
    # Dia dos Namorados
    (["namorado", "namorada", "valentines", "valentine", "love heart",
      "coracao", "dia dos namorados", "amor", "romance"], "Dia dos Namorados"),
    # Casamento
    (["wedding", "casamento", "noiva", "noivo", "bride", "groom",
      "matrimonio", "bodas", "noivado"], "Casamento"),
    # Chá de Bebê
    (["bebe", "baby", "shower", "cha de bebe", "maternidade",
      "recem nascido", "newborn", "cha bar"], "Chá de Bebê"),
    # Aniversário
    (["aniversario", "birthday", "aniversary", "bday",
      "happy birthday", "festa aniversario", "boleira"], "Aniversário"),
    # Dia das Crianças
    (["crianca", "criança", "children", "kids day", "dia das criancas",
      "infantil"], "Dia das Crianças"),
    # Halloween
    (["halloween", "witch", "bruxa", "abobora", "pumpkin", "skull",
      "caveira", "ghost", "fantasma", "spider", "aranha"], "Halloween"),
    # Formatura
    (["formatura", "graduation", "formando", "diploma",
      "formandos", "colacion"], "Formatura"),
    # Ano Novo
    (["ano novo", "new year", "reveillon", "virada"], "Ano Novo"),
    # Dia das Crianças (extras)
    (["brinquedo", "toy", "puzzle", "quebra cabeca"], "Dia das Crianças"),
]

_FUNCTION_MAP = [
    # Porta-Retrato / quadro de foto
    (["porta retrato", "portaretrato", "frame", "photo frame", "picture frame",
      "foto", "fotos", "photo"], "Porta-Retrato"),
    # Caixa Organizadora
    (["caixa", "box", "organizador", "porta treco", "porta trecos",
      "armazen", "storage", "cofre"], "Caixa Organizadora"),
    # Luminária
    (["luminaria", "luminaria", "lamp", "light", "led", "abajur",
      "nightlight", "night light", "luz noturna"], "Luminária"),
    # Porta-Joias
    (["porta joias", "jewelry", "jewellery", "joias", "bijuteria",
      "porta anel", "porta pulseira"], "Porta-Joias"),
    # Porta-Chaves
    (["porta chave", "porta chaves", "key holder", "keyholder",
      "key rack", "chaveiro parede"], "Porta-Chaves"),
    # Cabide
    (["cabide", "hanger", "coat hanger", "gancho", "hook",
      "pendurador", "porta bolsa"], "Suporte"),
    # Mandala
    (["mandala"], "Mandala"),
    # Nome Decorativo
    (["nome", "name", "letra", "letter", "initial", "monogram",
      "letreiro", "sign", "placa nome"], "Nome Decorativo"),
    # Quadro Decorativo / Painel
    (["quadro", "painel", "wall art", "arte parede", "decorative",
      "decoracao parede"], "Quadro Decorativo"),
    # Lembrancinha / Chaveiro (item pequeno)
    (["lembrancinha", "lembranca", "chaveiro", "keychain", "tag",
      "mini", "brinde"], "Lembrancinha"),
    # Topo de Bolo
    (["topo de bolo", "cake topper", "topper", "topo bolo"], "Topo de Bolo"),
    # Centro de Mesa
    (["centro de mesa", "centerpiece", "centro mesa", "enfeite mesa"], "Centro de Mesa"),
    # Plaquinha
    (["placa", "plaquinha", "plaque", "door sign", "aviso",
      "indicativo", "welcome", "bem vindo"], "Plaquinha"),
    # Brinquedo Educativo
    (["brinquedo", "toy", "puzzle", "quebra cabeca", "educativo",
      "educacional", "montessori"], "Brinquedo Educativo"),
    # Porta-Retrato (espelho)
    (["mirror", "espelho"], "Porta-Joias"),
    # Calendario
    (["calendar", "calendario", "agenda", "planner"], "Quadro Decorativo"),
]

_AMBIENTE_MAP = [
    # Quarto de Bebê
    (["bebe", "baby", "nursery", "maternidade", "newborn",
      "recem nascido", "cha de bebe"], "Quarto de Bebê"),
    # Quarto Infantil
    (["infantil", "kids", "crianca", "criança", "children",
      "unicornio", "dinossauro", "princess", "prince", "fada",
      "superheroi", "cartoon"], "Quarto Infantil"),
    # Quarto (adulto)
    (["bedroom", "quarto", "cama", "bed", "closet",
      "dormitorio", "travesseiro"], "Quarto"),
    # Cozinha
    (["kitchen", "cozinha", "cafe", "coffee", "cha", "receita",
      "comida", "food", "cook", "chef", "utensilios"], "Cozinha"),
    # Banheiro
    (["bathroom", "banheiro", "banho", "bath", "lavabo",
      "sabonete", "toalha"], "Banheiro"),
    # Escritório
    (["office", "escritorio", "trabalho", "desk", "mesa trabalho",
      "home office", "organizer", "agenda", "planner", "calendario"], "Escritório"),
    # Área Externa
    (["garden", "jardim", "outdoor", "externo", "varanda",
      "quintal", "piscina", "churrasqueira"], "Área Externa"),
    # Sala
    (["sala", "living", "sofa", "tv", "sala estar",
      "parede sala", "sala jantar", "jantar"], "Sala"),
    # Festa
    (["festa", "party", "evento", "celebracao", "decoracao festa",
      "balao", "balloon", "table decor"], "Festa"),
]

_STYLE_MAP = [
    (["minimalista", "minimal", "clean", "simples"],        "Minimalista"),
    (["rustico", "rustic", "madeira", "wood"],               "Rústico"),
    (["moderno", "modern", "contemporaneo"],                  "Moderno"),
    (["vintage", "retro", "antigo"],                          "Vintage"),
    (["romantico", "romantic", "flores", "floral", "flower"], "Romântico"),
    (["elegante", "elegant", "luxo", "luxury", "premium"],    "Elegante"),
    (["divertido", "fun", "colorido", "fofo", "cute"],        "Divertido"),
    (["geometrico", "geometric", "lines", "abstract"],        "Geométrico"),
    (["boho", "bohemian", "macrame", "etnico"],               "Boho"),
]

_PUBLIC_MAP = [
    (["bebe", "baby", "newborn"],                                   "Bebê"),
    (["crianca", "criança", "kids", "infantil", "children"],        "Criança"),
    (["mae", "mãe", "mom", "mother"],                               "Mãe"),
    (["pai", "dad", "father"],                                       "Pai"),
    (["casal", "couple", "wedding", "noiva", "namorado"],           "Casal"),
    (["familia", "família", "family"],                              "Família"),
    (["adulto", "adult", "grown"],                                   "Adulto"),
    (["presente", "gift", "lembranca", "lembrancinha"],              "Presente"),
]


def _match(name_lower, mapping):
    """Retorna rótulo do primeiro grupo de keywords que bater no nome."""
    for keywords, label in mapping:
        if any(k in name_lower for k in keywords):
            return label
    return None


class FallbackGenerator:
    """
    Gera análises e descrições sem IA usando regras baseadas em keywords.
    Usado quando Ollama está indisponível.

    GARANTE sempre 3 categorias obrigatórias:
      [0] Data comemorativa
      [1] Função / tipo
      [2] Ambiente / cômodo
    + até 2 opcionais (estilo, público)
    """

    def __init__(self, project_scanner):
        self.scanner = project_scanner
        self.logger = LOGGER

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
        Gera categorias (3 obrigatórias + opcionais) e tags a partir do nome.
        Chamado quando Ollama está offline ou retornou resposta vazia.
        """
        raw_name  = os.path.basename(project_path)
        name_tags = self.scanner.extract_tags_from_name(raw_name)
        name_low  = self._normalize(raw_name)

        cats = self._build_categories(name_low)
        tags = self._build_tags(name_low, name_tags)

        return cats, tags

    # ------------------------------------------------------------------
    # COMPLEMENTA categorias quando IA retornou < 3
    # ------------------------------------------------------------------
    def fallback_categories(self, project_path, existing_categories):
        """
        Completa categorias faltantes até garantir as 3 obrigatórias.
        Chamado quando IA retornou menos de 3 categorias.
        """
        raw_name = os.path.basename(project_path)
        name_low = self._normalize(raw_name)
        full     = self._build_categories(name_low)

        result = list(existing_categories)

        # Verifica quais obrigatórias já estão presentes por posição
        DATE_OPTS = {v for _, v in _DATE_MAP}
        FUNC_OPTS = {v for _, v in _FUNCTION_MAP}
        ENV_OPTS  = {v for _, v in _AMBIENTE_MAP}

        has_date = any(c in DATE_OPTS for c in result)
        has_func = any(c in FUNC_OPTS for c in result)
        has_env  = any(c in ENV_OPTS  for c in result)

        if not has_date:
            result.insert(0, full[0])   # date é sempre full[0]
        if not has_func:
            # insere após a data
            pos = 1 if len(result) >= 1 else 0
            result.insert(pos, full[1])
        if not has_env:
            result.append(full[2])

        return result[:8]

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------

    def _normalize(self, text):
        """Lowercase + remove extensões + substitui separadores."""
        t = text.lower()
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            t = t.replace(ext, "")
        t = re.sub(r"[\-_]", " ", t)       # hífen e underscore viram espaço
        t = re.sub(r"\d{5,}", "", t)        # remove códigos SKU longos
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _build_categories(self, name_low):
        """
        Monta lista de até 5 categorias respeitando a ordem obrigatória.
        Garante NUNCA retornar lista com 3 'Diversos' seguidos.
        """
        # --- Obrigatórias ---
        date_cat = _match(name_low, _DATE_MAP)     or "Diversos"
        func_cat = _match(name_low, _FUNCTION_MAP) or "Diversos"
        env_cat  = _match(name_low, _AMBIENTE_MAP) or "Diversos"

        cats = [date_cat, func_cat, env_cat]

        # --- Opcionais ---
        style_cat  = _match(name_low, _STYLE_MAP)
        public_cat = _match(name_low, _PUBLIC_MAP)

        if style_cat:
            cats.append(style_cat)
        if public_cat and public_cat not in cats:
            cats.append(public_cat)

        # --- Desambiguação inteligente ---
        # Se as 3 são Diversos, tenta heurísticas extras
        if cats[:3] == ["Diversos", "Diversos", "Diversos"]:
            cats = self._heuristic_fallback(name_low)

        return cats[:8]

    def _heuristic_fallback(self, name_low):
        """
        Último recurso quando nenhuma keyword bateu.
        Usa comprimento e padrões genéricos do nome.
        """
        words = name_low.split()

        # Tenta inferir função por palavras genéricas do corte laser
        func = "Quadro Decorativo"
        if any(w in words for w in ["box", "caixa", "case"]):
            func = "Caixa Organizadora"
        elif any(w in words for w in ["lamp", "light", "led", "luminaria"]):
            func = "Luminária"
        elif any(w in words for w in ["sign", "placa", "plaque"]):
            func = "Plaquinha"
        elif any(w in words for w in ["mirror", "espelho"]):
            func = "Porta-Joias"
        elif any(w in words for w in ["key", "chave"]):
            func = "Porta-Chaves"

        return ["Diversos", func, "Sala"]

    def _build_tags(self, name_low, name_tags):
        """
        Constrói lista de até 10 tags:
          - Primeiras: keywords extraídas do nome (extract_tags_from_name)
          - Depois: data, função, ambiente, estilo, público detectados
          - Final: tags contextuais genéricas do corte laser
        """
        extra = []

        # Adiciona rótulos detectados como tags contextuais
        for mapping in (_DATE_MAP, _FUNCTION_MAP, _AMBIENTE_MAP,
                        _STYLE_MAP, _PUBLIC_MAP):
            hit = _match(name_low, mapping)
            if hit and hit != "Diversos":
                # usa versão lowercase para tag
                extra.append(hit.lower())

        # Tags genéricas de produto laser sempre úteis
        extra += ["corte a laser", "personalizado", "artesanal"]

        all_tags = list(name_tags) + extra

        # Deduplica preservando ordem, case-insensitive
        seen    = set()
        unique  = []
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
        Gera descrição baseada em templates (sem IA).
        Respeita o mesmo formato da descrição gerada por IA:
            NOME\n\n🎨 Por Que Este Produto é Especial:\n...\n\n💖 Perfeito Para:\n...
        """
        raw_name   = project_data.get("name", "Sem nome")
        clean_name = self._clean_name(raw_name)
        name_low   = self._normalize(raw_name)

        tags       = project_data.get("tags", [])
        tags_low   = " ".join(tags).lower()
        combined   = name_low + " " + tags_low

        # — Seleciona template por função detectada —
        func = _match(combined, _FUNCTION_MAP) or "Diversos"
        date = _match(combined, _DATE_MAP)
        env  = _match(combined, _AMBIENTE_MAP)

        if func == "Luminária":
            especial = (
                "Uma luminária de corte laser que transforma qualquer ambiente com "
                "uma luz acolhedora e design exclusivo, tornando cada momento especial."
            )
            perfeito = (
                "Ideal para decorar quartos, salas e escritórios com estilo. "
                "Presente perfeito para quem aprecia um toque único na decoração."
            )
        elif func in ("Porta-Retrato", "Quadro Decorativo"):
            especial = (
                "Uma peça decorativa artesanal que transforma memórias em arte, "
                "criando um objeto único cheio de afeto e significado."
            )
            perfeito = (
                "Exaltar momentos especiais na decoração de qualquer ambiente. "
                "Presente ideal para aniversários, casamentos e datas comemorativas."
            )
        elif func == "Caixa Organizadora":
            especial = (
                "Uma caixa organizadora cuidadosamente cortada a laser, que une "
                "funcionalidade e beleza para manter seus objetos sempre no lugar."
            )
            perfeito = (
                "Organizar escritórios, quartos e cozinhas com charme. "
                "Presente criativo e prático para qualquer ocasião."
            )
        elif func == "Nome Decorativo":
            especial = (
                "Um nome decorativo único, cortado a laser com precisão millímetro a "
                "millímetro, que personaliza qualquer ambiente com identidade própria."
            )
            perfeito = (
                "Decorar quartos infantis, quarto de bebê ou salas com o nome da "
                "família. Lembrancinha especial para aniversários e chur de bebê."
            )
        elif func == "Luminária":
            especial = (
                "Uma luminária artesanal que cria atmosferas mágicas com recortes "
                "precisos, projetando sombras e luzes que encantam o ambiente."
            )
            perfeito = (
                "Ideal para quartos infantis, salas de estar ou como presente romântico. "
                "Combina estilo e funcionalidade em uma única peça."
            )
        elif func == "Topo de Bolo":
            especial = (
                "Um topo de bolo personalizado que transforma qualquer comemoração em "
                "um momento único e inesquecível para toda a família."
            )
            perfeito = (
                "Festas de aniversário, casamentos, formaturas e qualquer celebração "
                "que mereça um toque artesanal especial."
            )
        elif func == "Lembrancinha":
            especial = (
                "Uma lembrancinha delicada e personalizada, cortada a laser com "
                "atenção a cada detalhe, perfeita para guardar com carinho."
            )
            perfeito = (
                "Distribuir em festas, casamentos, formaturas e eventos especiais "
                "como lembrança afetiva para os convidados."
            )
        elif func == "Plaquinha":
            especial = (
                "Uma plaquinha exclusiva que combina design moderno e mensagem afetiva, "
                "criando identidade e personalidade para qualquer espaço."
            )
            perfeito = (
                "Sinalizar ambientes em casa, eventos ou comemções com estilo. "
                "Presente original e personalizado para quem você ama."
            )
        elif func == "Mandala":
            especial = (
                "Uma mandala cortada a laser com geometria precisa e rica em detalhes, "
                "trazendo equilíbrio visual e energia positiva para o ambiente."
            )
            perfeito = (
                "Decorar salas, quartos e escritórios com arte e simbolismo. "
                "Presente significativo para quem valoriza espiritualidade e design."
            )
        elif func == "Porta-Chaves":
            especial = (
                "Um porta-chaves artesanal que organiza sua entrada com estilo, "
                "unindo praticidade e decoração em uma única peça exclusiva."
            )
            perfeito = (
                "Organizar a entrada de casas e apartamentos com charme. "
                "Presente funcional e diferenciado para qualquer ocasião."
            )
        elif date == "Natal":
            especial = (
                "Uma peça natalina que traz o espírito do Natal para o ambiente, "
                "criando memórias afetivas para toda a família."
            )
            perfeito = (
                "Decorar a casa no Natal, presentear com afeto "
                "ou como lembrancinha especial da época festiva."
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
        elif date in ("Chá de Bebê", None) and env in ("Quarto de Bebê", "Quarto Infantil"):
            especial = (
                "Uma peça especial que marca os primeiros momentos da vida, "
                "cheia de carinho e significado para toda a família."
            )
            perfeito = (
                "Presente perfeito para chá de bebê, decoração de quarto de bebê "
                "ou como lembranca afetiva dos primeiros anos."
            )
        elif date == "Casamento":
            especial = (
                "Uma peça elegante que celebra o amor e marca para sempre "
                "o dia mais especial do casal."
            )
            perfeito = (
                "Ideal para decoração de cerimônia, recepção de convidados "
                "ou como presente inesquecível para os noivos."
            )
        else:
            cats = project_data.get("categories", [])
            cat_display = " | ".join(cats[:3]) if cats else "Produto personalizado"
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

    def _clean_name(self, raw_name):
        clean = raw_name
        for ext in [".zip", ".rar", ".svg", ".pdf", ".dxf", ".cdr", ".ai"]:
            clean = clean.replace(ext, "")
        clean = re.sub(r"[-_]\d{5,}", "", clean)
        clean = clean.replace("-", " ").replace("_", " ").strip()
        return clean
