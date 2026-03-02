"""
keyword_maps.py  —  SOMENTE DADOS, sem lógica.
Edite aqui para expandir cobertura. A lógica fica em fallbacks.py.

ESTRUTURA: lista de tuplas (["kw1","kw2",...], "Rótulo PT-BR")
  - keywords: substrings buscadas no nome normalizado (sem acento, lowercase)
  - Rótulo: sempre PT-BR, nunca genérico
  - Ordem: mais específico PRIMEIRO

REGRAS ABSOLUTAS:
  1. NUNCA coloque "Diversos", "Data Especial", "Ambiente Doméstico" ou
     qualquer outro termo genérico como rótulo — isso é tratado em fallbacks.py
  2. Toda keyword deve ser lowercase e sem acento (a busca normaliza o texto)
  3. Cada entrada deve ter pelo menos 2 keywords diferentes
"""

# ===========================================================================
# DATE_MAP — Data comemorativa (Cat 1 — OBRIGATÓRIA)
# REGRA: o sistema NUNCA deve retornar "Data Especial" como rótulo final.
#        Se o nome não bater aqui, fallbacks.py usa THEME→FUNCTION→PUBLIC
#        para inferir a data mais provável antes de usar o fallback.
# ===========================================================================
DATE_MAP = [
    # ── Páscoa ──────────────────────────────────────────────────────────────
    (["pascoa", "easter", "coelho", "coelha", "coelhinho",
      "galinha pascoa", "pintinho", "bunny easter", "rabbit easter",
      "ovo pascoa", "ovos pascoa", "cesta pascoa"], "Páscoa"),

    # ── Natal ────────────────────────────────────────────────────────────────
    (["natal", "christmas", "xmas", "noel", "papai noel", "mamae noel",
      "rena", "rudolph", "snowman", "boneco neve", "pinheiro natal",
      "arvore natal", "jingle", "sleigh", "treno", "guirlanda natal",
      "meia natal", "sino natal", "bola natal", "enfeite natal",
      "estrela natal", "familia noel", "presepinho", "presepio",
      "anjo natal", "grinch"], "Natal"),

    # ── Ano Novo ─────────────────────────────────────────────────────────────
    (["ano novo", "new year", "reveillon", "virada ano",
      "fogos artificio", "champanhe", "feliz ano novo"], "Ano Novo"),

    # ── Carnaval ─────────────────────────────────────────────────────────────
    (["carnaval", "carnival", "mardi gras", "mascara carnaval",
      "fantasia carnaval", "confete", "serpentina", "bloco carnaval",
      "rei momo", "escola samba"], "Carnaval"),

    # ── Festa Junina ─────────────────────────────────────────────────────────
    (["festa junina", "junina", "sao joao", "arraial", "bandeirinha",
      "chapeu palha", "fogueira", "quadrilha", "milho",
      "caipira", "xadrez junino", "balao junino"], "Festa Junina"),

    # ── Dia das Mães ─────────────────────────────────────────────────────────
    (["dia das maes", "dia mae", "mothers day", "mother day",
      "maezinha", "mainha", "para mae", "presente mae",
      "amor mae", "melhor mae", "super mae", "rainha mae",
      "homenagem mae", "obrigado mae"], "Dia das Mães"),

    # ── Dia dos Pais ─────────────────────────────────────────────────────────
    (["dia dos pais", "dia pai", "fathers day", "father day",
      "paizinho", "painho", "para pai", "presente pai",
      "melhor pai", "super pai", "heroi pai", "meu pai",
      "homenagem pai", "obrigado pai"], "Dia dos Pais"),

    # ── Dia das Crianças ─────────────────────────────────────────────────────
    (["dia das criancas", "dia crianca", "children day", "kids day",
      "para criancas", "presente crianca", "homenagem crianca",
      "12 de outubro"], "Dia das Crianças"),

    # ── Dia dos Namorados / Valentine ────────────────────────────────────────
    (["dia dos namorados", "namorado", "namorada",
      "valentines", "valentine", "san valentin", "saint valentin",
      "amor eterno", "te amo", "eu te amo", "casal apaixonado",
      "apaixonados", "love heart", "coracao apaixonado",
      "para meu amor", "romance"], "Dia dos Namorados"),

    # ── Casamento ────────────────────────────────────────────────────────────
    (["wedding", "casamento", "noiva", "noivo",
      "bride", "groom", "matrimonio", "bodas", "noivado",
      "alianca casamento", "votos casamento", "cerimonia",
      "recepcao casamento", "decoracao casamento", "mesa casamento",
      "convite casamento", "lembranca casamento",
      "bodas prata", "bodas ouro"], "Casamento"),

    # ── Chá de Bebê / Revelação ───────────────────────────────────────────────
    (["cha de bebe", "baby shower", "cha revelacao",
      "gender reveal", "maternidade", "gravida", "gestante",
      "chegada bebe", "boas vindas bebe", "churrascinho bebe",
      "recem nascido", "newborn", "nascimento bebe"], "Chá de Bebê"),

    # ── Aniversário ──────────────────────────────────────────────────────────
    (["aniversario", "birthday", "bday", "happy birthday",
      "parabens pra voce", "parabens", "festa aniversario",
      "boleira", "aniversariante", "feliz aniversario",
      "anos", "aninho"], "Aniversário"),

    # ── Halloween ────────────────────────────────────────────────────────────
    (["halloween", "bruxa", "witch", "abobora", "pumpkin",
      "fantasma", "ghost", "aranha halloween", "morcego", "bat",
      "zumbi", "zombie", "frankenstein", "dracul", "vampiro",
      "caveira halloween", "dia bruxas", "noite bruxas",
      "trick treat", "trick or treat"], "Halloween"),

    # ── Dia de Finados ────────────────────────────────────────────────────────
    (["finados", "dia mortos", "dia dos mortos",
      "calavera", "sugar skull", "catrina", "dia finados"], "Dia de Finados"),

    # ── Formatura ────────────────────────────────────────────────────────────
    (["formatura", "graduation", "formando", "formanda", "diploma",
      "colacao grau", "chapeu formatura", "turma formatura",
      "conclusao curso", "formatura escolar"], "Formatura"),

    # ── Dia do Professor ─────────────────────────────────────────────────────
    (["dia do professor", "dia professor", "professor dia",
      "professora dia", "teacher day", "homenagem professor",
      "presente professor", "obrigado professor"], "Dia do Professor"),

    # ── Dia do Trabalho ──────────────────────────────────────────────────────
    (["dia do trabalho", "dia trabalho", "trabalhador",
      "labor day", "primeiro de maio", "1 maio"], "Dia do Trabalho"),

    # ── Dia dos Avós ─────────────────────────────────────────────────────────
    (["dia dos avos", "dia avos", "avo", "vovo",
      "vovó", "vovô", "neto", "neta",
      "para vovo", "para vovó", "para vovô",
      "grandma", "grandpa", "presente avo"], "Dia dos Avós"),

    # ── Dia do Amigo ─────────────────────────────────────────────────────────
    (["dia do amigo", "dia amigo", "amizade", "friendship",
      "melhor amigo", "melhor amiga", "bff",
      "para amiga", "para amigo",
      "presente amigo", "homenagem amigo"], "Dia do Amigo"),

    # ── Primeira Comunhão / Religioso litúrgico ───────────────────────────────
    (["primeira comunhao", "comunhao", "crisma",
      "batizado", "batismo", "eucaristia",
      "corpus christi"], "Primeira Comunhão"),

    # ── Chá Bar ──────────────────────────────────────────────────────────────
    (["cha bar", "churrascao", "churrasco noivos"], "Chá Bar"),

    # ── Dia das Mulheres ─────────────────────────────────────────────────────
    (["dia da mulher", "dia mulher", "dia internacional mulher",
      "8 marco", "womens day", "girl power",
      "empoderamento feminino", "homenagem mulher"], "Dia das Mulheres"),

    # ── Dia do Homem ─────────────────────────────────────────────────────────
    (["dia do homem", "dia homem", "mens day",
      "homenagem homem", "presente homem"], "Dia do Homem"),

    # ── Dia do Animal / Pet ───────────────────────────────────────────────────
    (["dia do animal", "dia animal", "dia dos pets",
      "dia pet", "pet day", "dia animais"], "Dia do Animal"),

    # ── Aposentadoria ─────────────────────────────────────────────────────────
    (["aposentadoria", "aposentado", "aposentada",
      "retirement", "parabens aposentado",
      "fim carreira", "nova fase"], "Aposentadoria"),

    # ── Aniversário Corporativo ───────────────────────────────────────────────
    (["aniversario empresa", "empresa anos",
      "fundacao empresa", "anos empresa",
      "parabens empresa"], "Aniversário Corporativo"),

    # ── Dia dos Namorados extras (coração solto) ──────────────────────────────
    # ATENÇÃO: estas keywords são genéricas, vêm POR ÚLTIMO
    (["coracao", "heart", "amor", "love",
      "para voce", "for you"], "Dia dos Namorados"),
]


# ===========================================================================
# FUNCTION_MAP — Tipo / Função do produto (Cat 2 — OBRIGATÓRIA)
# ===========================================================================
FUNCTION_MAP = [
    # ── Luminária ────────────────────────────────────────────────────────────
    (["luminaria", "lamp", "lampada", "abajur", "nightlight",
      "night light", "luz noturna", "led luminaria", "luminoso",
      "neon", "light box", "caixa luz", "painel luminoso",
      "luz ambiente", "iluminacao"], "Luminária"),

    # ── Porta-Retrato ────────────────────────────────────────────────────────
    (["porta retrato", "portaretrato", "photo frame", "picture frame",
      "frame foto", "moldura foto", "quadro foto", "porta foto",
      "album foto"], "Porta-Retrato"),

    # ── Topo de Bolo ─────────────────────────────────────────────────────────
    (["topo de bolo", "cake topper", "topper bolo", "topo bolo",
      "decoracao bolo", "enfeite bolo"], "Topo de Bolo"),

    # ── Centro de Mesa ───────────────────────────────────────────────────────
    (["centro de mesa", "centerpiece", "enfeite mesa",
      "decoracao mesa", "arranjo mesa"], "Centro de Mesa"),

    # ── Mandala ──────────────────────────────────────────────────────────────
    (["mandala", "mandara", "geometria sagrada",
      "mandala floral", "mandala parede", "geometria mandala"], "Mandala"),

    # ── Porta-Joias ──────────────────────────────────────────────────────────
    (["porta joias", "jewelry box", "jewellery box", "joias",
      "bijuteria", "porta anel", "porta pulseira",
      "porta colar", "porta brinco", "organizador joias"], "Porta-Joias"),

    # ── Porta-Chaves ─────────────────────────────────────────────────────────
    (["porta chave", "porta chaves", "key holder", "keyholder",
      "key rack", "chaveiro parede", "organizador chave",
      "suporte chave"], "Porta-Chaves"),

    # ── Porta-Copo ───────────────────────────────────────────────────────────
    (["porta copo", "coaster", "descanso copo", "suporte copo",
      "base copo", "porta xicara", "porta xicaras"], "Porta-Copo"),

    # ── Suporte para Celular ─────────────────────────────────────────────────
    (["porta celular", "suporte celular", "phone holder",
      "phone stand", "suporte tablet", "dock phone",
      "cell stand", "phone rack"], "Suporte para Celular"),

    # ── Porta-Óculos ─────────────────────────────────────────────────────────
    (["porta oculos", "suporte oculos", "glasses holder",
      "eyeglass holder", "oculos suporte"], "Porta-Óculos"),

    # ── Organizador de Mesa ──────────────────────────────────────────────────
    (["porta caneta", "pen holder", "organizador mesa escritorio",
      "porta lapis", "porta clips", "porta objeto",
      "organizador escritorio", "desk organizer"], "Organizador de Mesa"),

    # ── Porta-Vinho ──────────────────────────────────────────────────────────
    (["porta vinho", "wine rack", "adega", "suporte vinho",
      "taca vinho", "wine holder", "vinho decorativo",
      "porta taça"], "Porta-Vinho"),

    # ── Bandeja ──────────────────────────────────────────────────────────────
    (["bandeja", "tray", "bandeja decorativa",
      "bandeja madeira", "bandeja organizadora"], "Bandeja"),

    # ── Pote Decorativo ──────────────────────────────────────────────────────
    (["pote", "pot", "vasilha", "potinho", "pote madeira",
      "recipiente", "pote decorativo", "jarra madeira"], "Pote Decorativo"),

    # ── Relógio ──────────────────────────────────────────────────────────────
    (["relogio", "clock", "wall clock", "relogio parede",
      "relogio madeira", "relogio decorativo"], "Relógio"),

    # ── Espelho Decorativo ───────────────────────────────────────────────────
    (["espelho", "mirror", "espelho decorativo",
      "espelho parede", "espelho madeira"], "Espelho Decorativo"),

    # ── Cabide ───────────────────────────────────────────────────────────────
    (["cabide", "hanger", "coat hanger", "gancho", "hook",
      "pendurador", "porta bolsa", "porta casaco",
      "porta toalha", "porta chapeu"], "Cabide"),

    # ── Nome Decorativo ──────────────────────────────────────────────────────
    (["nome decorativo", "letra decorativa", "monogram",
      "initial", "letreiro", "nome parede", "nome madeira",
      "first name", "family name", "nome personalizado"], "Nome Decorativo"),

    # ── Plaquinha / Sinalização ───────────────────────────────────────────────
    (["placa", "plaquinha", "plaque", "door sign", "aviso parede",
      "welcome sign", "bem vindo", "sinalizacao",
      "painel sinal", "indicativo"], "Plaquinha"),

    # ── Caixa Organizadora ────────────────────────────────────────────────────
    (["caixa organiz", "caixinha", "storage box", "porta trecos",
      "organizador caixa", "caixa madeira", "cofre madeira",
      "armazenamento", "box madeira"], "Caixa Organizadora"),

    # ── Caixa Presente ────────────────────────────────────────────────────────
    (["caixa presente", "gift box", "caixa festa",
      "embalagem presente", "sacola madeira",
      "packaging madeira"], "Caixa Presente"),

    # ── Lembrancinha ─────────────────────────────────────────────────────────
    (["lembrancinha", "lembranca", "chaveiro lembranca", "keychain",
      "tag lembranca", "mini lembranca", "brinde",
      "souvenir", "recordacao"], "Lembrancinha"),

    # ── Quadro Decorativo ────────────────────────────────────────────────────
    (["quadro decorativo", "painel decorativo", "wall art",
      "arte parede", "decoracao parede", "wall decor",
      "framed art", "poster madeira"], "Quadro Decorativo"),

    # ── Brinquedo Educativo ──────────────────────────────────────────────────
    (["brinquedo", "toy", "puzzle", "quebra cabeca", "educativo",
      "educacional", "montessori toy", "jogo infantil",
      "pedagogico", "aprendizado", "brinquedo madeira"], "Brinquedo Educativo"),

    # ── Jogo de Mesa ─────────────────────────────────────────────────────────
    (["jogo de mesa", "board game", "xadrez", "dama", "domino",
      "jogo madeira", "passa tempo", "tabuleiro",
      "jogo estrategia"], "Jogo de Mesa"),

    # ── Organizador de Banheiro ───────────────────────────────────────────────
    (["organizador banheiro", "porta sabonete", "suporte banheiro",
      "porta shampoo", "porta escova", "porta dental",
      "banheiro organizer"], "Organizador de Banheiro"),

    # ── Totem / Display ──────────────────────────────────────────────────────
    (["totem", "display madeira", "expositor", "suporte display",
      "totem decorativo", "expositor produto"], "Totem"),

    # ── Organizador de Cozinha ────────────────────────────────────────────────
    (["porta tempero", "spice rack", "organizador cozinha",
      "porta condimento", "suporte tempero",
      "porta sal", "porta azeite"], "Organizador de Cozinha"),

    # ── Fruteira ─────────────────────────────────────────────────────────────
    (["fruteira", "fruteiro", "bowl madeira", "bacia madeira",
      "bandeja cozinha", "cesta frutas"], "Fruteira"),

    # ── Escultura Decorativa ──────────────────────────────────────────────────
    (["escultura", "sculpture", "decor 3d", "arte 3d",
      "painel 3d", "decoracao 3d"], "Escultura Decorativa"),

    # ── Suporte para Plantas ──────────────────────────────────────────────────
    (["suporte planta", "plant stand", "vaso suporte",
      "suporte vaso", "cachepot", "jardim vertical",
      "suporte cacto"], "Suporte para Plantas"),

    # ── Porta-Livro ──────────────────────────────────────────────────────────
    (["porta livro", "bookend", "organizador livro",
      "suporte livro", "estante madeira"], "Porta-Livro"),

    # ── Etiqueta Decorativa ───────────────────────────────────────────────────
    (["etiqueta decorativa", "tag madeira", "etiqueta madeira",
      "etiqueta produto", "tag presente",
      "label madeira"], "Etiqueta Decorativa"),

    # ── Porta-Controle ────────────────────────────────────────────────────────
    (["porta controle", "suporte controle remoto",
      "porta controle remoto", "remote holder"], "Porta-Controle"),

    # ── Calendário Decorativo ─────────────────────────────────────────────────
    (["calendario decorativo", "calendario perpetuo",
      "calendar madeira", "planner madeira"], "Calendário Decorativo"),

    # ── Mapa Decorativo ───────────────────────────────────────────────────────
    (["mapa decorativo", "mapa brasil", "mapa mundi",
      "mapa cidade", "mapa estado", "map decor",
      "recorte mapa"], "Mapa Decorativo"),

    # ── Painel Vazado ────────────────────────────────────────────────────────
    (["painel vazado", "painel trelica", "painel mdf",
      "grade decorativa", "biombo", "painel corte laser"], "Painel Vazado"),

    # ── Suporte Leitura ───────────────────────────────────────────────────────
    (["suporte tablet", "suporte livro leitura",
      "suporte receita", "book stand",
      "suporte leitura"], "Suporte Leitura"),

    # ── Aplique Decorativo ────────────────────────────────────────────────────
    (["aplique", "recorte decorativo", "silhueta",
      "silhouette", "recorte mdf", "aplique parede"], "Aplique Decorativo"),

    # ── Porta-Fone ────────────────────────────────────────────────────────────
    (["porta fone", "headphone stand", "suporte headphone",
      "fone ouvido suporte", "headset holder"], "Porta-Fone"),

    # ── Decoração Gamer ───────────────────────────────────────────────────────
    (["setup gamer", "desk gamer", "gamer decor",
      "rgb decor", "gaming room"], "Decoração Gamer"),

    # ── Brinde Corporativo ────────────────────────────────────────────────────
    (["brinde corporativo", "presente empresa", "logo empresa",
      "brinde empresa", "corporativo laser"], "Brinde Corporativo"),
]


# ===========================================================================
# AMBIENTE_MAP — Ambiente / Cômodo (Cat 3 — OBRIGATÓRIA)
# ===========================================================================
AMBIENTE_MAP = [
    # ── Quarto de Bebê ───────────────────────────────────────────────────────
    (["quarto bebe", "cha de bebe", "baby shower", "maternidade",
      "newborn", "recem nascido", "chegada bebe",
      "decoracao bebe", "nursery", "quarto recem nascido"], "Quarto de Bebê"),

    # ── Quarto Infantil ───────────────────────────────────────────────────────
    (["quarto infantil", "kids room", "crianca quarto",
      "unicornio quarto", "dinossauro quarto", "fada quarto",
      "superheroi quarto", "menino quarto",
      "menina quarto", "princesa quarto"], "Quarto Infantil"),

    # ── Quarto Adulto ─────────────────────────────────────────────────────────
    (["quarto adulto", "bedroom", "quarto casal",
      "quarto solteiro", "dormitorio", "closet"], "Quarto"),

    # ── Cozinha ───────────────────────────────────────────────────────────────
    (["cozinha", "kitchen", "cafe decor", "coffee decor",
      "receita cozinha", "comida decor", "food decor",
      "chef cozinha", "utensilios", "tempero cozinha",
      "confeitaria", "padaria", "doces cozinha"], "Cozinha"),

    # ── Banheiro ──────────────────────────────────────────────────────────────
    (["banheiro", "bathroom", "lavabo", "bath decor",
      "sabonete", "toalha banheiro", "espelho banheiro",
      "organizador banheiro"], "Banheiro"),

    # ── Escritório / Home Office ──────────────────────────────────────────────
    (["escritorio", "home office", "office decor",
      "mesa trabalho", "organizer escritorio",
      "agenda escritorio", "planner escritorio",
      "calendario escritorio", "profissional"], "Escritório"),

    # ── Sala de Estar ─────────────────────────────────────────────────────────
    (["sala estar", "living room", "sofa",
      "sala jantar", "aparador", "rack sala",
      "parede sala", "sala visita"], "Sala"),

    # ── Área de Lazer / Varanda ───────────────────────────────────────────────
    (["varanda", "deck", "area lazer", "quintal",
      "terraco", "jardim", "area externa",
      "outdoor", "piscina area"], "Área de Lazer"),

    # ── Área Gourmet / Churrasco ──────────────────────────────────────────────
    (["churrasqueira", "churrasco", "area gourmet",
      "espaco gourmet", "parrilla", "grillmaster",
      "churrasqueiro"], "Área Gourmet"),

    # ── Sala de Jogos / Gamer ─────────────────────────────────────────────────
    (["sala jogos", "game room", "setup gamer",
      "games room", "playroom gamer", "sala gamer"], "Sala de Jogos"),

    # ── Academia / Gym ────────────────────────────────────────────────────────
    (["academia", "gym", "fitness", "crossfit",
      "musculacao", "treino", "personal trainer",
      "boxe", "luta"], "Academia"),

    # ── Espaço Religioso ──────────────────────────────────────────────────────
    (["igreja", "templo", "capela",
      "santuario", "altar", "oratorio",
      "espaco religioso", "cruzeiro"], "Espaço Religioso"),

    # ── Loja / Comercial ──────────────────────────────────────────────────────
    (["loja", "store", "comercio", "vitrine",
      "pdv", "ponto de venda", "showroom",
      "expositor loja"], "Loja"),

    # ── Pet Shop / Espaço Pet ─────────────────────────────────────────────────
    (["petshop", "pet shop", "veterinario",
      "clinica veterinaria", "espaco pet",
      "cachorro espaco", "gato espaco"], "Pet Shop"),

    # ── Garagem ───────────────────────────────────────────────────────────────
    (["garagem", "garage", "oficina",
      "workshop", "ferramentas", "mecanica"], "Garagem"),

    # ── Lavanderia ────────────────────────────────────────────────────────────
    (["lavanderia", "laundry", "lavadero",
      "area servico", "area de servico"], "Lavanderia"),

    # ── Festa / Evento ────────────────────────────────────────────────────────
    (["festa", "party", "evento", "celebracao",
      "decoracao festa", "mesa festa",
      "buffet", "salao festa", "espaco festas",
      "table decor festa"], "Festa"),

    # ── Sala de Aula / Escola ─────────────────────────────────────────────────
    (["sala aula", "escola", "colegio",
      "educacao", "pedagogico", "montessori sala",
      "sala montessori"], "Sala de Aula"),

    # ── Clínica ───────────────────────────────────────────────────────────────
    (["clinica", "consultorio", "medico decor",
      "fisioterapia", "psicologia", "nutricao",
      "odontologia", "dentista"], "Clínica"),

    # ── Salão de Beleza ───────────────────────────────────────────────────────
    (["barbearia", "salao beleza", "barbershop",
      "cabelereiro", "estetica", "spa",
      "nail art", "manicure"], "Salão de Beleza"),

    # ── Camping / Aventura ────────────────────────────────────────────────────
    (["camping", "aventura", "trilha",
      "acampamento", "natureza outdoor"], "Camping"),
]


# ===========================================================================
# THEME_MAP — Tema visual (Cat 4 — opcional)
# ===========================================================================
THEME_MAP = [
    (["jesus", "cristo", "cruz", "religioso",
      "deus", "oracao", "biblia", "sagrado coracao",
      "nossa senhora", "anjo", "angel", "divino espirito",
      "fe", "pentecostal", "evangelico", "catolico",
      "batista"], "Religioso"),
    (["montessori", "waldorf", "estimulacao precoce",
      "desenvolvimento crianca", "pedagogia",
      "educacao natural"], "Montessori"),
    (["safari", "selva", "jungle", "leao", "tigre",
      "elefante", "girafa", "zebra", "macaco",
      "hipopotamo", "rinoceronte", "africa",
      "animais selvagens"], "Safari"),
    (["fazenda", "farm", "country", "vaca", "porco",
      "galinha", "cavalo", "ovelha", "cabra", "celeiro",
      "roca", "rural", "sitio", "rancho"], "Fazenda"),
    (["nautico", "mar", "sea", "ocean", "praia",
      "beach", "ancora", "leme", "barco", "navio",
      "sereia", "polvo", "golfinhos", "peixe",
      "concha", "onda"], "Náutico"),
    (["floresta", "forest", "natureza", "nature",
      "arvore", "folha", "botanico", "eco",
      "sustentavel", "planta"], "Natureza"),
    (["cachorro", "dog", "gato", "cat", "pet",
      "animal estimacao", "pata", "focinho",
      "labrador", "golden", "husky", "pitbull",
      "siames", "persa", "filhote pet"], "Pet"),
    (["unicornio", "unicorn", "fada", "fairy",
      "magia", "magico", "arco iris", "rainbow",
      "mermaid", "pegasus"], "Fantasia"),
    (["dinossauro", "dinosaur", "dino", "t rex", "trex",
      "jurassic", "pterossauro", "velocirraptor"], "Dinossauro"),
    (["superheroi", "superhero", "batman", "superman",
      "spiderman", "homem aranha", "homem ferro",
      "capitao america", "mulher maravilha",
      "marvel", "avengers", "liga justica"], "Super-Heróis"),
    (["princesa", "princess", "disney", "cinderela",
      "rapunzel", "frozen", "elsa", "anna",
      "moana", "ariel"], "Princesas"),
    (["anime", "manga", "naruto", "dragon ball",
      "one piece", "demon slayer", "kawaii",
      "chibi", "sakura"], "Anime"),
    (["futebol", "football", "basquete", "basketball",
      "volei", "tenis", "natacao", "ciclismo",
      "corrida", "atletismo"], "Esporte"),
    (["musica", "music", "violao", "guitarra",
      "piano", "bateria", "nota musical",
      "instrumento", "rock", "sertanejo", "samba"], "Música"),
    (["floral", "flores", "flower", "rosas",
      "girassol", "botanico", "botanical",
      "tulipa", "orquidea", "lavanda"], "Floral"),
    (["gamer", "gaming", "joystick", "controle jogo",
      "pixel", "arcade", "playstation", "xbox",
      "nintendo", "minecraft", "fortnite"], "Gamer"),
    (["espaco", "space", "galaxia", "galaxy",
      "planeta", "estrela", "lua", "sol",
      "astronauta", "foguete", "universo",
      "saturno", "marte"], "Espaço"),
    (["nordestino", "forro", "sertanejo",
      "nordeste", "lampiao", "maria bonita",
      "cordel", "xilografia", "caatinga"], "Cultura Nordestina"),
    (["brasil", "brazil", "verde amarelo",
      "selecao", "bandeira brasil",
      "independencia brasil"], "Brasil"),
    (["minimalista", "minimal", "clean design",
      "linha fina", "simples elegante"], "Minimalista"),
    (["tropical", "flamingo", "tucano", "arara",
      "folha tropical", "palmeira", "abacaxi"], "Tropical"),
]


# ===========================================================================
# STYLE_MAP — Estilo visual (opcional)
# ===========================================================================
STYLE_MAP = [
    (["minimalista", "minimal", "clean", "simples moderno"],      "Minimalista"),
    (["rustico", "rustic", "madeira rustica", "estilo campo"],     "Rústico"),
    (["moderno", "modern", "contemporaneo", "design moderno"],      "Moderno"),
    (["vintage", "retro", "antigo", "anos 70", "anos 80"],         "Vintage"),
    (["romantico", "romantic", "delicado", "flores delicadas",
      "rendado"],                                                   "Romântico"),
    (["elegante", "elegant", "luxo", "luxury", "premium",
      "sofisticado", "requintado"],                                  "Elegante"),
    (["divertido", "fun", "fofo", "cute",
      "alegre", "vibrante"],                                        "Divertido"),
    (["geometrico", "geometric", "linhas geometricas",
      "angular", "triangulo", "hexagono"],                          "Geométrico"),
    (["boho", "bohemian", "macrame", "etnico",
      "hippie", "tribal"],                                          "Boho"),
    (["industrial", "metal decor", "estilo industrial"],           "Industrial"),
    (["escandinavo", "scandinavian", "nordico",
      "nordic", "hygge"],                                          "Escandinavo"),
    (["classico", "classic", "tradicional", "barroco"],            "Clássico"),
    (["oriental", "japones", "chines", "asiatico",
      "zen", "feng shui", "sakura", "torii"],                       "Oriental"),
    (["shabby chic", "shabby", "provencal",
      "patina", "desgastado"],                                      "Shabby Chic"),
    (["art deco", "deco", "gatsby", "anos 20"],                     "Art Déco"),
]


# ===========================================================================
# PUBLIC_MAP — Público-alvo (opcional)
# ===========================================================================
PUBLIC_MAP = [
    (["bebe", "baby", "newborn", "recem nascido"],                  "Bebê"),
    (["crianca", "infantil", "kids", "children",
      "menino", "menina"],                                          "Criança"),
    (["adolescente", "teen", "teenager", "jovem"],                  "Adolescente"),
    (["mae", "mom", "mother", "maezinha"],                          "Mãe"),
    (["pai", "dad", "father", "paizinho"],                          "Pai"),
    (["avo", "vovo", "grandpa", "grandma", "neto"],                 "Avós"),
    (["casal", "couple", "noiva", "namorado", "namorada"],          "Casal"),
    (["familia", "family", "casa familia"],                         "Família"),
    (["professor", "professora", "teacher", "docente"],             "Professor"),
    (["medico", "medica", "enfermeiro",
      "doutor", "doutora"],                                         "Profissional da Saúde"),
    (["pet", "cachorro", "gato", "animal estimacao",
      "dono pet"],                                                  "Dono de Pet"),
    (["atleta", "esportista", "fitness", "gym",
      "corredor", "ciclista"],                                      "Atleta"),
    (["empresario", "empresa", "corporativo",
      "empreendedor", "negocio"],                                   "Empresas"),
    (["presente", "gift", "lembrancinha", "mimo"],                  "Presente"),
    (["artesao", "artesanato", "artista", "crafter"],               "Artesanato"),
    (["cozinheiro", "chef", "confeiteiro",
      "padeiro", "gastronomia"],                                    "Gastrônomo"),
    (["musico", "guitarrista", "pianista",
      "baterista", "cantor"],                                       "Músico"),
    (["gamer", "jogador", "streamer"],                              "Gamer"),
]


# ===========================================================================
# DATE_INFER_MAP — Inferência de data pelo TEMA/FUNÇÃO/PÚBLICO
# Usado quando DATE_MAP não bateu: NUNCA retorna string genérica
# Chave: rótulo detectado em THEME_MAP / FUNCTION_MAP / PUBLIC_MAP
# Valor: data comemorativa mais provável para esse tipo de produto
# ===========================================================================
DATE_INFER_MAP = {
    # Por tema
    "Religioso":        "Primeira Comunhão",
    "Montessori":       "Dia das Crianças",
    "Safari":           "Dia das Crianças",
    "Fazenda":          "Aniversário",
    "Náutico":          "Aniversário",
    "Natureza":         "Aniversário",
    "Pet":              "Dia do Animal",
    "Fantasia":         "Dia das Crianças",
    "Dinossauro":       "Dia das Crianças",
    "Super-Heróis":     "Dia das Crianças",
    "Princesas":        "Dia das Crianças",
    "Anime":            "Aniversário",
    "Esporte":          "Aniversário",
    "Música":           "Aniversário",
    "Floral":           "Dia das Mães",
    "Gamer":            "Aniversário",
    "Espaço":           "Dia das Crianças",
    "Cultura Nordestina": "Festa Junina",
    "Brasil":           "Aniversário",
    "Minimalista":      "Aniversário",
    "Tropical":         "Aniversário",
    # Por função
    "Topo de Bolo":         "Aniversário",
    "Centro de Mesa":       "Casamento",
    "Lembrancinha":         "Aniversário",
    "Caixa Presente":       "Aniversário",
    "Nome Decorativo":      "Chá de Bebê",
    "Porta-Retrato":        "Aniversário",
    "Brinde Corporativo":   "Aniversário Corporativo",
    "Calendário Decorativo": "Aniversário",
    "Brinquedo Educativo":  "Dia das Crianças",
    "Jogo de Mesa":         "Aniversário",
    "Porta-Vinho":          "Aniversário",
    "Porta-Joias":          "Dia das Mães",
    # Por público
    "Bebê":             "Chá de Bebê",
    "Criança":          "Dia das Crianças",
    "Mãe":              "Dia das Mães",
    "Pai":              "Dia dos Pais",
    "Avós":             "Dia dos Avós",
    "Casal":            "Dia dos Namorados",
    "Professor":        "Dia do Professor",
    "Atleta":           "Aniversário",
    "Gastrônomo":       "Aniversário",
    "Músico":           "Aniversário",
    "Gamer":            "Aniversário",
    "Dono de Pet":      "Dia do Animal",
    "Empresas":         "Aniversário Corporativo",
}


# ===========================================================================
# TRANSLATION_MAP — Inglês → Português (para gerar name_pt no card)
# ===========================================================================
TRANSLATION_MAP = {
    "abstract": "abstrato", "acorn": "bolota", "adorable": "adorável",
    "alphabet": "alfabeto", "anchor": "âncora", "angel": "anjo",
    "animal": "animal", "anniversary": "aniversário",
    "apple": "maçã", "art": "arte", "autumn": "outono", "award": "prêmio",
    "baby": "bebê", "balloon": "balão", "bat": "morcego",
    "bathroom": "banheiro", "bear": "urso", "beautiful": "lindo",
    "bedroom": "quarto", "bee": "abelha", "bird": "pássaro",
    "birthday": "aniversário", "board": "tabuleiro", "book": "livro",
    "bookend": "porta-livro", "border": "borda", "box": "caixa",
    "branch": "galho", "brave": "corajoso", "bride": "noiva",
    "bunny": "coelhinho", "butterfly": "borboleta",
    "cabin": "cabana", "cake": "bolo", "calendar": "calendário",
    "candle": "vela", "card": "cartão", "cardinal": "cardeal",
    "carousel": "carrossel", "castle": "castelo",
    "cat": "gato", "celebration": "celebração",
    "centerpiece": "centro de mesa", "chalkboard": "quadro negro",
    "christmas": "natal", "circus": "circo", "city": "cidade",
    "clock": "relógio", "cloud": "nuvem", "coat": "casaco",
    "coaster": "porta-copo", "coffee": "café",
    "collection": "coleção", "color": "cor",
    "comet": "cometa", "compass": "bússola", "corner": "canto",
    "couple": "casal", "cow": "vaca", "craft": "artesanato",
    "crown": "coroa", "cute": "fofo",
    "dad": "pai", "daisy": "margarida", "dance": "dança",
    "decor": "decoração", "decorative": "decorativo",
    "deer": "cervo", "desk": "escrivaninha", "diamond": "diamante",
    "dinosaur": "dinossauro", "dino": "dino", "display": "display",
    "dog": "cachorro", "door": "porta", "dragon": "dragão",
    "dream": "sonho", "duck": "pato",
    "eagle": "águia", "easter": "páscoa", "elephant": "elefante",
    "elegant": "elegante", "enchanted": "encantado",
    "eternal": "eterno", "event": "evento",
    "fairy": "fada", "fall": "outono", "family": "família",
    "farm": "fazenda", "father": "pai", "feather": "pena",
    "festive": "festivo", "fish": "peixe", "flame": "chama",
    "flamingo": "flamingo", "flower": "flor", "forest": "floresta",
    "fox": "raposa", "frame": "moldura", "friend": "amigo",
    "frog": "sapo", "fruit": "fruta",
    "galaxy": "galáxia", "game": "jogo", "garden": "jardim",
    "gift": "presente", "girl": "menina", "glitter": "glitter",
    "gnome": "gnomo", "goat": "cabra", "graduation": "formatura",
    "groom": "noivo",
    "halloween": "halloween", "hamster": "hamster",
    "hanger": "cabide", "happy": "feliz", "harvest": "colheita",
    "heart": "coração", "hedgehog": "ouriço", "hello": "olá",
    "hippo": "hipopótamo", "holder": "suporte", "home": "lar",
    "honey": "mel", "horse": "cavalo", "house": "casa",
    "hummingbird": "beija-flor",
    "initial": "inicial", "inspirational": "inspiracional",
    "jar": "pote", "jewelry": "joias", "jungle": "selva",
    "key": "chave", "keychain": "chaveiro", "kids": "crianças",
    "kitchen": "cozinha", "kitten": "gatinho",
    "label": "etiqueta", "lamp": "lâmpada", "lantern": "lanterna",
    "laser": "laser", "lavender": "lavanda", "leaf": "folha",
    "letter": "letra", "light": "luz", "lion": "leão",
    "living": "sala", "llama": "lhama", "love": "amor",
    "lucky": "sortudo",
    "magic": "mágico", "mama": "mamãe", "map": "mapa",
    "memorial": "memorial", "mermaid": "sereia",
    "mirror": "espelho", "mom": "mãe", "monkey": "macaco",
    "moon": "lua", "mother": "mãe", "mountain": "montanha",
    "music": "música",
    "name": "nome", "nature": "natureza", "newborn": "recém-nascido",
    "night": "noite", "nursery": "quarto de bebê",
    "ocean": "oceano", "office": "escritório", "ornament": "enfeite",
    "outdoor": "externo", "owl": "coruja",
    "panda": "panda", "party": "festa", "peace": "paz",
    "penguin": "pinguim", "personalized": "personalizado",
    "pet": "pet", "photo": "foto", "pig": "porco",
    "plaque": "placa", "plant": "planta", "polar": "polar",
    "porch": "varanda", "portrait": "retrato",
    "pumpkin": "abóbora", "puppy": "filhote", "puzzle": "quebra-cabeça",
    "queen": "rainha",
    "rabbit": "coelho", "rack": "rack", "rainbow": "arco-íris",
    "reindeer": "rena", "religious": "religioso", "ring": "anel",
    "rocket": "foguete", "rose": "rosa", "rustic": "rústico",
    "safari": "safari", "santa": "papai noel", "school": "escola",
    "seasonal": "sazonal", "sheep": "ovelha", "shelf": "prateleira",
    "sign": "placa", "skeleton": "esqueleto", "skull": "caveira",
    "sloth": "preguiça", "snowflake": "floco de neve",
    "snowman": "boneco de neve", "space": "espaço",
    "special": "especial", "spring": "primavera",
    "star": "estrela", "storage": "armazenamento",
    "summer": "verão", "sunflower": "girassol",
    "superhero": "super-herói", "sweet": "doce",
    "tag": "etiqueta", "teacher": "professor", "topper": "topo",
    "toy": "brinquedo", "tree": "árvore", "tray": "bandeja",
    "tropical": "tropical", "turtle": "tartaruga",
    "unicorn": "unicórnio", "unique": "único",
    "valentine": "dia dos namorados", "vintage": "vintage",
    "wall": "parede", "wedding": "casamento", "welcome": "bem-vindo",
    "whale": "baleia", "wild": "selvagem", "winter": "inverno",
    "witch": "bruxa", "wolf": "lobo", "wood": "madeira",
    "woodland": "floresta", "wreath": "guirlanda",
    "year": "ano", "zebra": "zebra",
}


# ===========================================================================
# GENERIC_FALLBACK_FUNCTION — segunda chance quando FUNCTION_MAP não bateu
# ===========================================================================
GENERIC_FALLBACK_FUNCTION = [
    (["box", "caixa", "case", "chest"],             "Caixa Organizadora"),
    (["lamp", "light", "led", "luminaria", "neon"], "Luminária"),
    (["sign", "placa", "plaque", "welcome"],        "Plaquinha"),
    (["mirror", "espelho"],                         "Espelho Decorativo"),
    (["key", "chave"],                              "Porta-Chaves"),
    (["rack", "holder", "suporte", "stand"],        "Suporte"),
    (["tag", "etiqueta", "label"],                  "Etiqueta Decorativa"),
    (["tray", "bandeja"],                           "Bandeja"),
    (["frame", "moldura", "retrato"],               "Porta-Retrato"),
    (["clock", "relogio"],                          "Relógio"),
    (["topper", "topo"],                            "Topo de Bolo"),
    (["puzzle", "quebra"],                          "Brinquedo Educativo"),
    (["game", "jogo", "board"],                     "Jogo de Mesa"),
    (["wall", "parede", "decor"],                   "Quadro Decorativo"),
    (["bag", "sacola", "bolsa"],                    "Caixa Presente"),
    (["cup", "mug", "xicara", "copo"],              "Porta-Copo"),
]

# Fallback final ABSOLUTO — só entra se absolutamente nenhuma keyword bateu
# PROIBIDO usar para DATE: o sistema deve usar DATE_INFER_MAP antes
FINAL_FALLBACK_FUNCTION  = "Decoração Artesanal"
FINAL_FALLBACK_AMBIENTE  = "Ambiente Doméstico"
# FINAL_FALLBACK_DATE não existe mais: o sistema SEMPRE infere uma data real
