#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laserflix_fallbacks.py
Patch 8 — Fallbacks inteligentes sem Ollama
Substitui fallback_analysis, fallback_categories e fallback_description
com logica expandida baseada em tokens do nome do produto.
NAO alterar as assinaturas das funcoes — sao chamadas diretamente pelo Engine.
"""

import os
import re

# ---------------------------------------------------------------------------
# TABELAS DE CONHECIMENTO
# ---------------------------------------------------------------------------

# 1. DATA COMEMORATIVA — tokens EN + PT, ordem de prioridade
_DATE_TOKENS = [
    ("Pascoa",         ["pascoa","easter","coelho","bunny","bunny","ovinho","ovo de pascoa","coelhinho"]),
    ("Natal",          ["natal","christmas","xmas","noel","papai noel","rena","arvore de natal","jingle","snowflake","snowman","boneco de neve","natalino","natalina","santa"]),
    ("Dia das Maes",   ["mae","maes","mom","mother","mothers","mamae","mama"]),
    ("Dia dos Pais",   ["pai","pais","dad","father","fathers","papai","papa"]),
    ("Dia dos Namorados",["namorado","namorada","namorados","valentines","valentine","amor","love","coracao","heart","couple"]),
    ("Aniversario",    ["aniversario","birthday","bday","parabens","feliz aniversario","festa","party"]),
    ("Casamento",      ["casamento","wedding","noiva","noivo","bride","groom","matrimonio","casando"]),
    ("Cha de Bebe",    ["cha de bebe","baby shower","shower","nascimento","bebe","baby","newborn","recem nascido","gestante","gravidez","maternidade"]),
    ("Dia das Criancas",["dia das criancas","crianca","criancas","children","kids","infantil","infancia"]),
    ("Halloween",      ["halloween","bruxas","bruxa","witch","fantasma","ghost","abobora","pumpkin","horror","terror","vampiro","vampire","caveira","skull"]),
    ("Formatura",      ["formatura","formando","diploma","graduacao","graduation","colacao","turma"]),
    ("Ano Novo",       ["ano novo","new year","reveillon","virada","champagne","countdown"]),
]

# 2. TIPO / FUNCAO — tokens EN + PT
_TYPE_TOKENS = [
    ("Separador de Livros", ["bookmark","bookend","book end","nook","nook book","book nook","shelf sitter","separador de livro","separador de estante","porta livro","portalivre"]),
    ("Porta-Retrato",       ["frame","photo frame","picture frame","porta retrato","porta-retrato","porta foto","portafoto","moldura","quadro de foto"]),
    ("Caixa Organizadora",  ["box","caixa","organizer","organizador","storage","porta treco","portabilidade","case","cofre","chest"]),
    ("Luminaria",           ["lamp","light","luz","luminaria","lanterna","lantern","night light","luz noturna","abajur","nightlight","led"]),
    ("Nome Decorativo",     ["name","nome","first name","word","palavra","letra","letras","monogram","monograma","initial","iniciais"]),
    ("Quadro Decorativo",   ["quadro","wall art","wall decor","decorativo","art","artwork","parede","arte","picture","poster","sign board"]),
    ("Painel de Parede",    ["painel","panel","wall panel","banner","mural"]),
    ("Mandala",             ["mandala","mandalas","floral","geometrico","geometric","circular"]),
    ("Plaquinha",           ["sign","placa","plaquinha","plaque","tag","etiqueta","label","aviso","welcome","bem vindo"]),
    ("Porta-Joias",         ["jewelry","jewellery","porta joias","porta-joias","anel","brinco","colar","joia","jóia","bijuteria","jewel box"]),
    ("Porta-Chaves",        ["key","chave","porta chave","porta-chave","keychain","chaveiro","gancho de chave"]),
    ("Suporte",             ["stand","suporte","holder","apoio","base","dock","rack","display"]),
    ("Cabide",              ["hanger","cabide","gancho","hook","clothes","roupa","roupinha"]),
    ("Espelho",             ["mirror","espelho","reflexo"]),
    ("Calendario",          ["calendar","calendario","agenda","planner","data","mes","month"]),
    ("Lembrancinha",        ["lembrancinha","souvenir","favor","lembrete","recordacao","gift tag","lembranca"]),
    ("Brinquedo Educativo", ["puzzle","quebra cabeca","educational","educativo","brinquedo","toy","aprendizado","alfabeto","numero","letter block"]),
    ("Topo de Bolo",        ["cake topper","topo de bolo","topo bolo","topper","bolo"]),
    ("Centro de Mesa",      ["centerpiece","centro de mesa","centro mesa","table decor","mesa decorada"]),
    ("Chaveiro",            ["chaveiro","keychain","key ring","key fob"]),
]

# 3. AMBIENTE — tokens EN + PT
_ROOM_TOKENS = [
    ("Quarto de Bebe",  ["nursery","quarto de bebe","bebe","baby room","baby","newborn","recem nascido","berco","crib"]),
    ("Quarto Infantil", ["kids room","kids","children room","quarto infantil","quarto de crianca","playroom","infantil","crianca"]),
    ("Quarto",          ["bedroom","quarto","dormitorio","suite","master"]),
    ("Cozinha",         ["kitchen","cozinha","copa","pantry"]),
    ("Sala",            ["living","sala","sala de estar","living room","lounge","sala de jantar","dining"]),
    ("Banheiro",        ["bathroom","banheiro","lavabo","toilet","bath"]),
    ("Escritorio",      ["office","escritorio","home office","estudio","studio","desk","mesa de trabalho"]),
    ("Estante",         ["shelf","estante","bookshelf","biblioteca","livros","livraria","book"]),
    ("Festa",           ["party","festa","evento","event","celebration","celebracao","decoracao de festa"]),
    ("Area Externa",    ["garden","jardim","outdoor","externo","varanda","patio","quintal","porta de entrada","entrada"]),
]

# Estilos inferidos por tokens
_STYLE_TOKENS = [
    ("Rustico",     ["rustic","rustico","wood","madeira","natural","farmhouse","barn"]),
    ("Minimalista", ["minimal","minimalista","clean","simples","simple","modern","moderno"]),
    ("Romantico",   ["romantic","romantico","floral","flowers","flores","laco","bow","lace","rendado"]),
    ("Vintage",     ["vintage","retro","antigo","classic","classico","old"]),
    ("Infantil",    ["kids","infantil","cute","fofo","cartoon","animado","colorido"]),
    ("Elegante",    ["elegant","elegante","luxury","luxo","gold","dourado","prata","silver","premium"]),
]

# Publico inferido
_PUBLIC_TOKENS = [
    ("Para Bebe",   ["baby","bebe","newborn","recem nascido","nursery","berco"]),
    ("Para Crianca",["kids","crianca","infantil","child","children","menino","menina","boy","girl"]),
    ("Para Casal",  ["casal","couple","wedding","casamento","noiva","namorado","namorada","love"]),
    ("Presente",    ["gift","presente","lembranca","souvenir","favor","surprise","surpresa"]),
]

# Palavras a ignorar ao extrair tags do nome
_STOP_WORDS = {
    "file","files","project","design","laser","cut","svg","pdf","vector",
    "bundle","pack","set","collection","digital","download","template",
    "com","para","com","de","da","do","das","dos","em","um","uma","e","o","a",
}

# ---------------------------------------------------------------------------
# HELPERS INTERNOS
# ---------------------------------------------------------------------------

def _clean_name(raw_name: str) -> str:
    """Remove extensoes, codigos numericos longos e normaliza espacos."""
    c = raw_name
    for ext in [".zip",".rar",".7z",".svg",".pdf",".dxf",".cdr",".ai",".eps",".png",".jpg"]:
        c = c.replace(ext, "")
    c = re.sub(r"[-_]\d{5,}", "", c)
    c = c.replace("-", " ").replace("_", " ")
    c = re.sub(r"\s+", " ", c).strip()
    return c


def _tokens(name: str) -> list:
    """Retorna lista de tokens (palavras + bigramas + trigramas) em lowercase."""
    words = name.lower().split()
    result = list(words)
    for i in range(len(words)-1):
        result.append(words[i] + " " + words[i+1])
    for i in range(len(words)-2):
        result.append(words[i] + " " + words[i+1] + " " + words[i+2])
    return result


def _match(tokens: list, keyword_list: list) -> bool:
    """Retorna True se qualquer keyword bater em qualquer token."""
    for kw in keyword_list:
        for tok in tokens:
            if kw in tok or tok in kw:
                return True
    return False


def _best_match(tokens: list, table: list, default: str) -> str:
    """Retorna o primeiro item da tabela que bater, ou o default."""
    for label, keywords in table:
        if _match(tokens, keywords):
            return label
    return default


# ---------------------------------------------------------------------------
# FUNCAO PUBLICA 1 — fallback_categories
# ---------------------------------------------------------------------------

def smart_fallback_categories(project_path: str, existing: list) -> list:
    """
    Retorna lista de categorias inteligentes a partir do nome da pasta.
    Garante sempre 3 categorias obrigatorias (Data, Tipo, Ambiente)
    sem nunca retornar 'Diversos' quando ha informacao no nome.
    """
    name  = _clean_name(os.path.basename(project_path))
    toks  = _tokens(name)
    result = list(existing)

    # --- Posicao 0: Data comemorativa ---
    all_date_values = [v for v, _ in _DATE_TOKENS]
    if not any(c in all_date_values for c in result):
        date_cat = _best_match(toks, _DATE_TOKENS, "")
        result.insert(0, date_cat if date_cat else "Ocasiao Especial")

    # --- Posicao 1: Tipo/Funcao ---
    all_type_values = [v for v, _ in _TYPE_TOKENS]
    if len(result) < 2 or not any(c in all_type_values for c in result):
        type_cat = _best_match(toks, _TYPE_TOKENS, "")
        if not type_cat:
            # Tenta inferir pelo contexto: se tem "book" no nome -> Separador
            nl = name.lower()
            if "book" in nl or "shelf" in nl:  type_cat = "Separador de Livros"
            elif "wall" in nl:                  type_cat = "Quadro Decorativo"
            elif "name" in nl or "nome" in nl:  type_cat = "Nome Decorativo"
            else:                               type_cat = "Decoracao Artesanal"
        result.append(type_cat)

    # --- Posicao 2: Ambiente ---
    all_room_values = [v for v, _ in _ROOM_TOKENS]
    if len(result) < 3 or not any(c in all_room_values for c in result):
        room_cat = _best_match(toks, _ROOM_TOKENS, "")
        if not room_cat:
            # Inferencia contextual de ambiente
            nl = name.lower()
            if any(w in nl for w in ["baby","bebe","nursery","berco"]):
                room_cat = "Quarto de Bebe"
            elif any(w in nl for w in ["kids","infantil","crianca","child"]):
                room_cat = "Quarto Infantil"
            elif any(w in nl for w in ["book","shelf","estante","library"]):
                room_cat = "Estante"
            elif any(w in nl for w in ["party","festa","birthday","aniversario"]):
                room_cat = "Festa"
            else:
                room_cat = "Sala"
        result.append(room_cat)

    # --- Opcional: Estilo ---
    if len(result) < 5:
        style = _best_match(toks, _STYLE_TOKENS, "")
        if style:
            result.append(style)

    # --- Opcional: Publico ---
    if len(result) < 6:
        public = _best_match(toks, _PUBLIC_TOKENS, "")
        if public and public not in result:
            result.append(public)

    # Deduplica mantendo ordem
    seen, unique = set(), []
    for c in result:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique.append(c)

    return unique[:8]


# ---------------------------------------------------------------------------
# FUNCAO PUBLICA 2 — fallback_analysis
# ---------------------------------------------------------------------------

def smart_fallback_analysis(project_path: str, extract_tags_fn) -> tuple:
    """
    Retorna (categories, tags) sem Ollama.
    extract_tags_fn = engine.extract_tags (reusa a funcao ja existente no engine).
    """
    name      = os.path.basename(project_path)
    clean     = _clean_name(name)
    toks      = _tokens(clean)
    name_tags = extract_tags_fn(name)

    categories = smart_fallback_categories(project_path, [])

    # Tags adicionais baseadas em tokens semanticos
    extra_tags = []
    if _match(toks, ["personalized","personalizado","custom","customizado"]):
        extra_tags.append("Personalizado")
    if _match(toks, ["handmade","artesanal","artesanato","handcrafted"]):
        extra_tags.append("Artesanal")
    if _match(toks, ["gift","presente","presente especial"]):
        extra_tags.append("Presente")
    if _match(toks, ["wood","madeira","wooden","mdf"]):
        extra_tags.append("Madeira")
    if _match(toks, ["decor","decoracao","decorativo","decoration"]):
        extra_tags.append("Decoracao")

    # Fallback minimo se nao gerou nada
    if not extra_tags:
        extra_tags = ["Personalizado", "Artesanal"]

    tags = name_tags + extra_tags
    seen, unique = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)

    return categories, unique[:10]


# ---------------------------------------------------------------------------
# FUNCAO PUBLICA 3 — fallback_description
# ---------------------------------------------------------------------------

def smart_fallback_description(project_path: str, data: dict, structure: dict, save_fn) -> str:
    """
    Gera descricao comercial inteligente sem Ollama, baseada apenas no nome.
    save_fn = callable que recebe (project_path, description_text) e persiste no banco.
    """
    raw   = data.get("name", os.path.basename(project_path)) or os.path.basename(project_path)
    clean = _clean_name(raw)
    toks  = _tokens(clean)
    nl    = clean.lower()

    # Detecta tipo principal para montar descricao especifica
    tipo = _best_match(toks, _TYPE_TOKENS, "")

    # Detecta data/ocasiao para enriquecer o contexto
    data_cat = _best_match(toks, _DATE_TOKENS, "")

    # Prefixo de tema sazonal
    tema = ""
    if data_cat and data_cat not in ("Ocasiao Especial",):
        tema = f" com tema de {data_cat}"

    # ---- Descricoes por tipo ----
    if tipo == "Separador de Livros":
        esp = (f"{clean} e um separador de livros decorativo em madeira{tema}, "
               "feito para deixar sua estante com toda a personalidade que ela merece. "
               "Cada detalhe e cortado a laser com precisao, criando uma peca unica e cheia de charme.")
        prf = ("Perfeito para quem ama livros e quer transformar a estante em um cantinho especial. "
               "Otimo presente para leitores, amantes de decoracao ou para dar um toque personalizado ao escritorio ou sala.")

    elif tipo == "Porta-Retrato":
        esp = (f"{clean} e um porta-retrato artesanal em madeira{tema}, "
               "que transforma suas memorias favoritas em arte de parede. "
               "O corte a laser garante acabamento impecavel e detalhes que encantam.")
        prf = ("Ideal para eternizar momentos especiais em qualquer ambiente da casa. "
               "Presente perfeito para aniversarios, casamentos, chAs de bebe e datas comemorativas.")

    elif tipo == "Cabide":
        esp = (f"{clean} e um cabide decorativo em madeira{tema}, "
               "que organiza roupinhas e acessorios enquanto decora o ambiente com muito estilo. "
               "Um toque de personalidade para o quarto da crianca ou do bebe.")
        prf = ("Perfeito para quartos infantis e de bebe. "
               "Excelente opcao de presente para chAs de bebe, aniversarios e nascimentos.")

    elif tipo == "Espelho":
        esp = (f"{clean} e um espelho decorativo com moldura em madeira{tema}, "
               "onde funcionalidade e arte se encontram em uma peca unica. "
               "O corte a laser cria detalhes delicados que valorizam qualquer ambiente.")
        prf = ("Ideal para quartos, banheiros e salas que precisam de um toque especial. "
               "Otimo presente para diversas ocasioes.")

    elif tipo == "Calendario":
        esp = (f"{clean} e um calendario decorativo em madeira{tema}, "
               "que organiza seus dias com muito estilo e personalidade. "
               "Uma peca funcional e bonita que combina com qualquer ambiente.")
        prf = ("Perfeito para escritorios, quartos e salas. "
               "Presente criativo e util para aniversarios, datas comemorativas e inicio de ano.")

    elif tipo == "Luminaria":
        esp = (f"{clean} e uma luminaria decorativa em madeira{tema}, "
               "que projeta uma luz aconchegante e cria uma atmosfera magica no ambiente. "
               "Os recortes a laser criam efeitos de luz unicos e encantadores.")
        prf = ("Ideal para quartos, sala e decor de festas. "
               "Presente especial para aniversarios, Natal e datas romanticas.")

    elif tipo == "Nome Decorativo":
        esp = (f"{clean} e uma peca de nome decorativo em madeira{tema}, "
               "perfeita para personalizar qualquer ambiente com identidade unica. "
               "O corte a laser garante letras precisas e acabamento de qualidade.")
        prf = ("Ideal para quartos de bebe, quartos infantis e home offices. "
               "Presente muito especial para nascimentos, aniversarios e casamentos.")

    elif tipo == "Quadro Decorativo":
        esp = (f"{clean} e um quadro decorativo em madeira{tema}, "
               "com design exclusivo criado com corte a laser de alta precisao. "
               "Uma obra de arte funcional que transforma paredes comuns em algo memoravel.")
        prf = ("Perfeito para sala, quarto e escritorio. "
               "Presente elegante para quem aprecia design e decoracao.")

    elif tipo == "Caixa Organizadora":
        esp = (f"{clean} e uma caixa organizadora artesanal em madeira{tema}, "
               "que combina praticidade e design em uma unica peca. "
               "Os detalhes em corte a laser dao um acabamento sofisticado e personalizado.")
        prf = ("Ideal para organizar joias, documentos, maquiagem ou qualquer acessorio. "
               "Presente pratico e bonito para diversas ocasioes.")

    elif tipo == "Topo de Bolo":
        esp = (f"{clean} e um topo de bolo exclusivo em madeira{tema}, "
               "que transforma qualquer bolo em uma peca central inesquecivel. "
               "Feito com corte a laser para garantir detalhes perfeitos.")
        prf = ("Perfeito para aniversarios, casamentos, chAs de bebe e festas tematicas. "
               "Deixa a mesa de doces ainda mais especial e memoravel.")

    elif tipo == "Lembrancinha":
        esp = (f"{clean} e uma lembrancinha artesanal em madeira{tema}, "
               "feita com carinho e precisao para marcar momentos especiais. "
               "Um presente pequeno com um significado enorme.")
        prf = ("Ideal para festas de aniversario, casamentos, chAs de bebe e eventos comemorativos. "
               "Os convidados vao adorar levar essa lembranca para casa.")

    elif tipo == "Mandala":
        esp = (f"{clean} e uma mandala decorativa em madeira{tema}, "
               "com geometria precisa criada pelo corte a laser. "
               "Uma peca meditativa e visualmente impactante para qualquer ambiente.")
        prf = ("Perfeita para sala, quarto ou escritorio. "
               "Presente especial para quem aprecia espiritualidade, meditacao e decoracao.")

    elif tipo == "Separador de Livros":
        esp = (f"{clean} e um separador de livros artesanal em madeira{tema}. "
               "Ideal para deixar sua estante com identidade propria.")
        prf = ("Perfeito para presentear leitores e amantes de livros.")

    else:
        # Fallback generico — mas ainda usa o nome e o tema
        cat_label = data.get("categories", ["decoracao"])[0] if data.get("categories") else "decoracao"
        esp = (f"{clean} e uma peca artesanal de corte a laser em madeira{tema}. "
               f"Com design exclusivo, e criada para ser unica, cheia de personalidade e transmitir afeto "
               f"em cada detalhe.")
        prf = (f"Ideal como presente personalizado ou para decorar o ambiente com estilo. "
               f"Uma peca que conta uma historia e cria memorias afetivas duradouras.")

    desc = f"{clean}\n\nPor Que Este Produto e Especial:\n{esp}\n\nPerfeito Para:\n{prf}"

    # Persiste no banco via callback do engine
    save_fn(project_path, desc)
    return desc
