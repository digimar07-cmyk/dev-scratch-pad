#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laserflix_fallbacks.py
Análise inteligente por nome — usada quando Ollama está offline.
Patch 8 — substitui fallback_analysis / fallback_categories / fallback_description
         com lógica expandida por tokens, sem "Diversos" desnecessário.
"""

import os, re

# ---------------------------------------------------------------------------
# TABELAS DE LOOKUP  (pt-BR + en)
# ---------------------------------------------------------------------------

_DATE_TOKENS = {
    # Páscoa
    "pascoa":"Pascoa","easter":"Pascoa","coelho":"Pascoa","bunny":"Pascoa","ovos":"Pascoa","egg":"Pascoa",
    # Natal
    "natal":"Natal","christmas":"Natal","noel":"Natal","xmas":"Natal","rena":"Natal","reindeer":"Natal",
    "papai":"Natal","santa":"Natal","snowflake":"Natal","arvore":"Natal","tree":"Natal","snowman":"Natal",
    "boneco":"Natal","pinheiro":"Natal","pine":"Natal","ornament":"Natal","enfeite":"Natal",
    # Dia das Mães
    "mae":"Dia das Maes","mom":"Dia das Maes","mother":"Dia das Maes","mothers":"Dia das Maes",
    "mama":"Dia das Maes","mamae":"Dia das Maes",
    # Dia dos Pais
    "pai":"Dia dos Pais","dad":"Dia dos Pais","father":"Dia dos Pais","fathers":"Dia dos Pais",
    "papa":"Dia dos Pais","papai noel":None,  # evita falso positivo com Natal
    # Aniversário
    "aniversario":"Aniversario","birthday":"Aniversario","bday":"Aniversario","birth":"Aniversario",
    "happy":"Aniversario",
    # Casamento
    "casamento":"Casamento","wedding":"Casamento","noiva":"Casamento","bride":"Casamento",
    "noivo":"Casamento","groom":"Casamento","amor":"Casamento","love":"Casamento",
    # Chá de Bebê
    "bebe":"Cha de Bebe","baby":"Cha de Bebe","shower":"Cha de Bebe","nascimento":"Cha de Bebe",
    "recemnascido":"Cha de Bebe","newborn":"Cha de Bebe","maternidade":"Cha de Bebe",
    # Dia das Crianças
    "crianca":"Dia das Criancas","children":"Dia das Criancas","kids":"Dia das Criancas",
    "infantil":"Dia das Criancas","child":"Dia das Criancas",
    # Dia dos Namorados
    "namorados":"Dia dos Namorados","valentine":"Dia dos Namorados","valentines":"Dia dos Namorados",
    "coracao":"Dia dos Namorados","heart":"Dia dos Namorados","romance":"Dia dos Namorados",
    # Halloween
    "halloween":"Halloween","bruxa":"Halloween","witch":"Halloween","fantasma":"Halloween",
    "ghost":"Halloween","abobora":"Halloween","pumpkin":"Halloween","skull":"Halloween","caveira":"Halloween",
    # Formatura
    "formatura":"Formatura","graduation":"Formatura","formando":"Formatura","diploma":"Formatura",
    # Ano Novo
    "anonovo":"Ano Novo","newyear":"Ano Novo","reveillon":"Ano Novo","nye":"Ano Novo",
}

_FUNC_TOKENS = {
    # Porta-Retrato / Quadro
    "frame":"Porta-Retrato","quadro":"Quadro Decorativo","portaretrato":"Porta-Retrato",
    "porta retrato":"Porta-Retrato","picture":"Porta-Retrato","photo":"Porta-Retrato","foto":"Porta-Retrato",
    # Caixa
    "box":"Caixa Organizadora","caixa":"Caixa Organizadora","chest":"Caixa Organizadora",
    "storage":"Caixa Organizadora","organizer":"Caixa Organizadora","organizador":"Caixa Organizadora",
    # Luminária
    "lamp":"Luminaria","luminaria":"Luminaria","light":"Luminaria","luz":"Luminaria",
    "nightlight":"Luminaria","abajur":"Luminaria","lantern":"Luminaria","lanterna":"Luminaria",
    # Nome Decorativo / Letreiro
    "name":"Nome Decorativo","nome":"Nome Decorativo","letra":"Nome Decorativo","letter":"Nome Decorativo",
    "monogram":"Nome Decorativo","sign":"Letreiro","letreiro":"Letreiro","placa":"Plaquinha",
    "plaquinha":"Plaquinha","tag":"Plaquinha",
    # Painel / Mandala
    "painel":"Painel de Parede","panel":"Painel de Parede","wall":"Painel de Parede",
    "mandala":"Mandala","mural":"Painel de Parede",
    # Porta-Joias / Porta-Chaves
    "jewelry":"Porta-Joias","joia":"Porta-Joias","joias":"Porta-Joias","porta joias":"Porta-Joias",
    "keyholder":"Porta-Chaves","chaveiro":"Porta-Chaves","key":"Porta-Chaves","porta chaves":"Porta-Chaves",
    # Separador / Divisor
    "nook":"Separador de Livros","bookmark":"Separador de Livros","separador":"Separador de Livros",
    "divider":"Separador de Livros","shelf":"Separador de Livros","bookend":"Separador de Livros",
    # Suporte / Apoio
    "stand":"Suporte","suporte":"Suporte","holder":"Suporte","apoio":"Suporte","base":"Suporte",
    # Cabide
    "hanger":"Cabide","cabide":"Cabide","gancho":"Cabide","hook":"Cabide",
    # Espelho
    "mirror":"Espelho Decorativo","espelho":"Espelho Decorativo",
    # Calendário
    "calendar":"Calendario","calendario":"Calendario",
    # Topo de Bolo / Centro de Mesa
    "topper":"Topo de Bolo","topo":"Topo de Bolo","cake":"Topo de Bolo",
    "centerpiece":"Centro de Mesa","centro":"Centro de Mesa","mesa":"Centro de Mesa",
    # Lembrancinha / Chaveiro pequeno
    "lembran":"Lembrancinha","souvenir":"Lembrancinha","favor":"Lembrancinha",
    "mini":"Lembrancinha","miniatura":"Lembrancinha",
    # Brinquedo
    "toy":"Brinquedo Educativo","brinquedo":"Brinquedo Educativo","puzzle":"Brinquedo Educativo",
    "quebra":"Brinquedo Educativo","educational":"Brinquedo Educativo",
}

_AMB_TOKENS = {
    # Quarto de Bebê
    "nursery":"Quarto de Bebe","berco":"Quarto de Bebe","crib":"Quarto de Bebe",
    # Quarto Infantil
    "kids room":"Quarto Infantil","playroom":"Quarto Infantil",
    # Quarto (adulto)
    "bedroom":"Quarto","quarto":"Quarto","room":"Quarto",
    # Sala
    "living":"Sala","sala":"Sala","lounge":"Sala","home":"Sala",
    # Cozinha
    "kitchen":"Cozinha","cozinha":"Cozinha","cook":"Cozinha",
    # Banheiro
    "bathroom":"Banheiro","banheiro":"Banheiro","bath":"Banheiro",
    # Escritório
    "office":"Escritorio","escritorio":"Escritorio","desk":"Escritorio","work":"Escritorio",
    # Área Externa
    "garden":"Area Externa","jardim":"Area Externa","outdoor":"Area Externa","varanda":"Area Externa",
    # Festa
    "party":"Festa","festa":"Festa","event":"Festa","decoracao":"Festa","decor":"Festa",
}

# Descrições por tipo de produto (para fallback_description)
_DESC_BY_FUNC = {
    "Separador de Livros": (
        "Um separador de livros encantador, cortado a laser com detalhes precisos, que deixa sua estante cheia de personalidade.",
        "Ideal para organizar livros com charme e estilo. Presente criativo para leitores e amantes de decoracao."
    ),
    "Cabide": (
        "Um cabide decorativo que combina funcionalidade e arte, transformando qualquer cantinho em um espaco especial.",
        "Perfeito para organizar roupas e acessorios com elegancia. Otimo presente para quartos infantis e adultos."
    ),
    "Espelho Decorativo": (
        "Um espelho decorativo unico, cortado a laser com precisao, que une funcionalidade e beleza artesanal.",
        "Ideal para decorar quarto, sala ou corredor com personalidade e sofisticacao."
    ),
    "Calendario": (
        "Um calendario decorativo que transforma a organizacao do dia a dia em uma experiencia visual encantadora.",
        "Perfeito para quartos, escritorios e como presente criativo em datas especiais."
    ),
    "Porta-Retrato": (
        "Um porta-retrato artesanal que transforma memorias em arte, eternizando momentos especiais com delicadeza.",
        "Presente ideal para aniversarios, casamentos e qualquer data que merece ser lembrada."
    ),
    "Luminaria": (
        "Uma luminaria decorativa que cria uma atmosfera unica e acolhedora, com recortes precisos que projetam luz e sombra.",
        "Perfeita para quartos, salas e como presente em datas comemorativas."
    ),
    "Nome Decorativo": (
        "Uma peca personalizada com nome em corte a laser que traz identidade e afeto para qualquer ambiente.",
        "Ideal para quartos de criancas, bebes ou como presente unico e cheio de significado."
    ),
    "Caixa Organizadora": (
        "Uma caixa organizadora artesanal que combina beleza e praticidade, mantendo seus objetos com estilo.",
        "Perfeita para organizar joias, lembranças ou acessorios. Presente especial para qualquer ocasiao."
    ),
    "Mandala": (
        "Uma mandala decorativa com simetria e precisao impecaveis, trazendo harmonia e arte para qualquer parede.",
        "Ideal para sala, quarto ou escritorio. Presente sofisticado para quem aprecia arte e decoracao."
    ),
    "Painel de Parede": (
        "Um painel decorativo de parede que transforma qualquer ambiente com arte e elegancia em corte a laser.",
        "Perfeito para salas, quartos e escritorios. Presente marcante para datas especiais."
    ),
    "Topo de Bolo": (
        "Um topo de bolo artesanal e personalizado que torna qualquer celebracao ainda mais especial e memoravel.",
        "Perfeito para aniversarios, casamentos, formaturas e festas tematicas."
    ),
    "Porta-Chaves": (
        "Um porta-chaves decorativo e funcional, cortado a laser com precisao, que organiza com estilo.",
        "Ideal para entradas, corredores e como presente pratico e personalizado."
    ),
    "Porta-Joias": (
        "Uma porta-joias artesanal que guarda seus tesouros com delicadeza e muito charme.",
        "Presente ideal para ela em qualquer data especial."
    ),
    "Suporte": (
        "Um suporte artesanal em corte a laser que une funcionalidade e estetica de forma unica.",
        "Perfeito para organizar objetos do dia a dia com personalidade."
    ),
    "Letreiro": (
        "Um letreiro decorativo em corte a laser que da identidade e charme a qualquer espaco.",
        "Ideal para festas, eventos, comercios e como presente personalizado."
    ),
    "Plaquinha": (
        "Uma plaquinha decorativa e personalizada, criada em corte a laser com acabamento impecavel.",
        "Perfeita para identificar ambientes, presentear ou decorar com estilo."
    ),
    "Brinquedo Educativo": (
        "Um brinquedo educativo artesanal que estimula a criatividade e o aprendizado de forma ludica e encantadora.",
        "Ideal para criancas em fase escolar. Presente criativo e com proposito."
    ),
    "Lembrancinha": (
        "Uma lembrancinha artesanal em corte a laser, delicada e personalizada, que deixa qualquer festa mais especial.",
        "Perfeita para aniversarios, casamentos, chás e eventos comemorativos."
    ),
    "Centro de Mesa": (
        "Um centro de mesa elegante e personalizado que transforma qualquer celebracao em um momento inesquecivel.",
        "Perfeito para casamentos, aniversarios e festas de todos os estilos."
    ),
    "Quadro Decorativo": (
        "Um quadro decorativo unico, criado em corte a laser, que transforma paredes comuns em obras de arte.",
        "Ideal para sala, quarto ou escritorio. Presente sofisticado para qualquer ocasiao."
    ),
}

_DATE_DESC = {
    "Natal": (
        "Uma peca natalina encantadora que traz o espirito do Natal para o lar, criando memorias afetivas e aquecendo qualquer ambiente.",
        "Ideal para decoracao sazonal, presentes de fim de ano e lembrancas especiais de Natal."
    ),
    "Pascoa": (
        "Uma peca tematica de Pascoa cheia de charme e delicadeza, perfeita para celebrar essa data tao especial.",
        "Ideal como decoracao sazonol, lembrancinha de Pascoa ou presente criativo."
    ),
    "Dia das Maes": (
        "Uma peca afetiva e unica criada especialmente para homenagear a mae mais especial do mundo.",
        "O presente perfeito para o Dia das Maes — personalizado, artesanal e cheio de amor."
    ),
    "Dia dos Pais": (
        "Uma peca especial para celebrar e homenagear o pai com todo o carinho que ele merece.",
        "Presente ideal para o Dia dos Pais — unico, personalizado e cheio de significado."
    ),
    "Aniversario": (
        "Uma peca comemorativa que torna qualquer aniversario ainda mais especial e memoravel.",
        "Presente unico e personalizado para celebrar com quem voce ama."
    ),
    "Casamento": (
        "Uma peca romantica e elegante que celebra o amor e torna o dia mais especial e inesquecivel.",
        "Ideal como decoracao de casamento, lembrancinha para convidados ou presente aos noivos."
    ),
    "Cha de Bebe": (
        "Uma peca delicada e amorosa que celebra a chegada do novo membro da familia com toda a ternura.",
        "Perfeita para decoracao de cha de bebe ou como presente especial para os pais."
    ),
    "Halloween": (
        "Uma peca tematica de Halloween com visual marcante e personalidade, ideal para deixar a decoracao assustadoramente linda.",
        "Perfeita para decoracao sazonal, festas e colecoes tematicas de Halloween."
    ),
    "Dia dos Namorados": (
        "Uma peca romantica e personalizada que expressa amor com delicadeza e arte em corte a laser.",
        "O presente perfeito para o Dia dos Namorados — unico, afetivo e inesquecivel."
    ),
    "Formatura": (
        "Uma peca comemorativa que marca com elegancia e arte uma das conquistas mais importantes da vida.",
        "Presente ideal para homenagear formandos e celebrar essa etapa tao especial."
    ),
}


def _tokenize(name: str) -> list:
    """Quebra o nome em tokens normalizados (lowercase, sem extensao, sem codigos)."""
    clean = name
    for ext in [".zip",".rar",".7z",".svg",".pdf",".dxf",".cdr",".ai",".eps",".png",".jpg"]:
        clean = clean.replace(ext, "")
    clean = re.sub(r"[-_]\d{4,}", "", clean)
    clean = clean.replace("-"," ").replace("_"," ").lower()
    return clean.split()


def _match_tokens(tokens: list, lookup: dict) -> str | None:
    """
    Tenta match token a token e também bigrama (token[i]+token[i+1]).
    Retorna o primeiro valor encontrado ou None.
    """
    joined = " ".join(tokens)
    # Bigrama primeiro (mais específico)
    for i in range(len(tokens)-1):
        bigram = tokens[i] + " " + tokens[i+1]
        if bigram in lookup and lookup[bigram] is not None:
            return lookup[bigram]
    # Token simples
    for t in tokens:
        if t in lookup and lookup[t] is not None:
            return lookup[t]
    # Substring (cobre "aniversario" dentro de "meuaniversario")
    for key, val in lookup.items():
        if val and key in joined:
            return val
    return None


# ---------------------------------------------------------------------------
# FUNÇÕES PÚBLICAS
# ---------------------------------------------------------------------------

def smart_fallback_categories(project_path: str, existing: list) -> list:
    """
    Versão inteligente de fallback_categories.
    Garante 3 categorias obrigatórias sem retornar "Diversos" quando possível.
    Prioridade: existing > match por token > melhor chute > ultimo recurso com label descritivo.
    """
    name   = os.path.basename(project_path)
    tokens = _tokenize(name)

    result = list(existing)

    # ── CAT 1: Data comemorativa ──────────────────────────────────────────
    ALL_DATES = set(_DATE_TOKENS.values()) - {None}
    if not any(c in ALL_DATES for c in result):
        found = _match_tokens(tokens, _DATE_TOKENS)
        result.insert(0, found if found else "Uso Geral")

    # ── CAT 2: Função/Tipo ────────────────────────────────────────────────
    ALL_FUNCS = set(_FUNC_TOKENS.values())
    if not any(c in ALL_FUNCS for c in result):
        found = _match_tokens(tokens, _FUNC_TOKENS)
        if not found:
            # Chute inteligente: se tem imagem/foto no nome → porta-retrato
            if any(t in tokens for t in ["img","image","pic","png","jpg"]): found = "Quadro Decorativo"
            # Nomes curtos com 1-2 palavras provavelmente são nome decorativo
            elif len(tokens) <= 2: found = "Nome Decorativo"
            else: found = "Decoracao"
        result.append(found)

    # ── CAT 3: Ambiente ───────────────────────────────────────────────────
    ALL_AMB = set(_AMB_TOKENS.values())
    if not any(c in ALL_AMB for c in result):
        found = _match_tokens(tokens, _AMB_TOKENS)
        if not found:
            # Inferir ambiente pela data/função já encontrada
            cat1 = result[0] if result else ""
            cat2 = result[1] if len(result) > 1 else ""
            if "Bebe" in cat1 or "Bebe" in cat2:    found = "Quarto de Bebe"
            elif "Crianca" in cat1 or cat2 == "Brinquedo Educativo": found = "Quarto Infantil"
            elif cat2 in ("Topo de Bolo","Centro de Mesa","Lembrancinha"): found = "Festa"
            elif cat2 in ("Porta-Chaves","Porta-Joias","Organizador"):     found = "Quarto"
            elif cat2 in ("Luminaria","Mandala","Painel de Parede","Quadro Decorativo"): found = "Sala"
            elif cat2 == "Caixa Organizadora": found = "Escritorio"
            else: found = "Sala"
        result.append(found)

    return result


def smart_fallback_analysis(project_path: str) -> tuple:
    """
    Versão inteligente de fallback_analysis.
    Retorna (categories, tags) sem "Diversos".
    """
    name      = os.path.basename(project_path)
    raw_name  = name
    for ext in [".zip",".rar",".7z",".svg",".pdf",".dxf",".cdr",".ai"]: raw_name = raw_name.replace(ext,"")
    raw_name  = re.sub(r"[-_]\d{4,}","",raw_name).replace("-"," ").replace("_"," ").strip()
    tokens    = _tokenize(name)

    cats = smart_fallback_categories(project_path, [])

    # Tags inteligentes a partir do nome limpo
    stop = {"file","files","project","design","laser","cut","svg","pdf","vector",
            "bundle","pack","set","collection","digital","download","template"}
    words = [w for w in tokens if len(w)>=3 and not w.isdigit() and w.lower() not in stop]

    tags = []
    # Frase do nome (até 4 palavras)
    if len(words) >= 2:
        tags.append(" ".join(words[:4]).title())
    # Palavras individuais
    for w in words[:5]:
        tags.append(w.capitalize())
    # Tags contextuais baseadas nas categorias
    cat_tags = {
        "Natal":["natal","natalino","decoracao natal","presente natal"],
        "Pascoa":["pascoa","decoracao pascoa","presente pascoa"],
        "Dia das Maes":["dia das maes","presente mae","homenagem"],
        "Dia dos Pais":["dia dos pais","presente pai","homenagem"],
        "Aniversario":["aniversario","presente aniversario","celebracao"],
        "Casamento":["casamento","decoracao casamento","noivos"],
        "Cha de Bebe":["cha de bebe","maternidade","presente bebe"],
        "Dia dos Namorados":["dia dos namorados","presente romantico","amor"],
        "Halloween":["halloween","decoracao halloween","festa tematica"],
        "Formatura":["formatura","presente formando","celebracao"],
        "Separador de Livros":["separador de livros","organizacao","estante"],
        "Cabide":["cabide","organizacao","quarto"],
        "Luminaria":["luminaria","decoracao","iluminacao"],
        "Mandala":["mandala","arte","decoracao parede"],
        "Porta-Retrato":["porta-retrato","memorias","presente"],
        "Nome Decorativo":["personalizado","nome","decoracao"],
        "Topo de Bolo":["festa","celebracao","bolo personalizado"],
    }
    for cat in cats[:2]:
        for extra in cat_tags.get(cat, ["personalizado","artesanal","corte laser"])[:2]:
            tags.append(extra.capitalize())

    # Deduplica e limita
    seen, unique = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)

    # Garante pelo menos "Personalizado" e "Corte Laser" se ficou curto
    for fallback in ["Personalizado","Artesanal","Corte Laser"]:
        if len(unique) >= 8: break
        if fallback.lower() not in seen:
            unique.append(fallback)
            seen.add(fallback.lower())

    return cats, unique[:10]


def smart_fallback_description(project_path: str, data: dict, database: dict) -> str:
    """
    Versão inteligente de fallback_description.
    Constrói descrição real a partir do nome, sem frases genéricas.
    """
    raw  = data.get("name", os.path.basename(project_path)) or os.path.basename(project_path)
    clean = raw
    for ext in [".zip",".rar",".svg",".pdf",".dxf",".cdr",".ai"]: clean = clean.replace(ext,"")
    clean = re.sub(r"[-_]\d{4,}", "", clean).replace("-"," ").replace("_"," ").strip()

    tokens = _tokenize(raw)
    cats   = data.get("categories", [])
    tags_l = " ".join(data.get("tags", [])).lower()
    nl     = clean.lower()

    # ── Detecta função e data pelo nome ───────────────────────────────────
    func_cat = _match_tokens(tokens, _FUNC_TOKENS)
    date_cat = _match_tokens(tokens, _DATE_TOKENS)

    # Tenta pegar da lista de categorias se não achou pelo nome
    if not func_cat:
        all_funcs = set(_FUNC_TOKENS.values())
        func_cat = next((c for c in cats if c in all_funcs), None)
    if not date_cat:
        all_dates = set(v for v in _DATE_TOKENS.values() if v)
        date_cat = next((c for c in cats if c in all_dates), None)

    # ── Monta esp (especial) e prf (perfeito para) ────────────────────────
    esp, prf = None, None

    # 1) Prioridade: função específica
    if func_cat and func_cat in _DESC_BY_FUNC:
        esp, prf = _DESC_BY_FUNC[func_cat]

    # 2) Data comemorativa como contexto adicional/principal
    if date_cat and date_cat in _DATE_DESC:
        if esp is None:
            esp, prf = _DATE_DESC[date_cat]
        else:
            # Combina: função + contexto da data
            _, prf = _DATE_DESC[date_cat]

    # 3) Último recurso: constrói frase a partir do nome limpo
    if esp is None:
        words = [w for w in tokens if len(w) >= 3 and w not in
                 {"file","files","laser","cut","svg","pdf","vector","bundle","pack","set"}]
        produto = " ".join(words[:4]).title() if words else clean
        esp = (f"Uma peca decorativa de corte a laser inspirada em '{produto}', "
               f"criada com precisao e cuidado para ser unica e encantadora.")
        prf = ("Ideal como presente personalizado ou para decorar qualquer ambiente "
               "com arte e personalidade.")

    # ── Personaliza com o nome real quando possível ───────────────────────
    # Injeta o nome limpo na primeira frase se não estiver presente
    if clean.lower() not in esp.lower() and len(clean) < 60:
        esp = esp.replace("Uma peca", f"'{clean}' é uma peca", 1)

    desc = f"{clean}\n\nPor Que Este Produto e Especial:\n{esp}\n\nPerfeito Para:\n{prf}"

    # Persiste no banco
    database.setdefault(project_path, {})
    database[project_path]["ai_description"]           = desc
    database[project_path]["description_generated_at"] = __import__("datetime").datetime.now().isoformat()

    return desc
