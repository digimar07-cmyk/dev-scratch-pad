"""
keyword_maps.py
Dicionários de mapeamento keyword → rótulo para análise SEM Ollama.

Este arquivo é SOMENTE DADOS — edite aqui para expandir a cobertura.
A lógica de uso fica em fallbacks.py.

ESTRUTURA DE CADA MAPA:
  lista de tuplas: (["keyword1", "keyword2", ...], "Rótulo PT-BR")
  - keywords: substrings buscadas no nome normalizado (lowercase, sem acento)
  - Rótulo: categoria/tag exibida ao usuário (sempre PT-BR)
  - Ordem importa: mais específico PRIMEIRO

CATEGORIAS OBRIGATÓRIAS (nesta ordem):
  [0] DATE_MAP   → Data comemorativa
  [1] FUNCTION_MAP → Função / tipo do produto
  [2] AMBIENTE_MAP → Ambiente / cômodo
CATEGORIAS OPCIONAIS:
  [3] THEME_MAP  → Tema visual
  [4] STYLE_MAP  → Estilo
  [5] PUBLIC_MAP → Público-alvo
"""

# ===========================================================================
# DATE_MAP — Data comemorativa (Cat 1 — OBRIGATÓRIA)
# ===========================================================================
DATE_MAP = [
    # --- Páscoa ---
    (["pascoa", "easter", "coelho", "coelha", "coelhinho", "ovos pascoa",
      "ovo pascoa", "galinha da pascoa", "pintinho", "pollito"], "Páscoa"),

    # --- Natal ---
    (["natal", "christmas", "noel", "papai noel", "rena", "rudolph",
      "snowman", "boneco de neve", "arvore natal", "pinheiro natal",
      "xmas", "jingle", "sleigh", "trenó", "trenô", "guirlanda natal",
      "meia natal", "sino natal", "vela natal", "bola natal",
      "enfeite natal", "decoracao natal", "papai noel", "mamae noel",
      "familia noel", "rena natal", "estrela natal"], "Natal"),

    # --- Ano Novo ---
    (["ano novo", "new year", "reveillon", "virada", "feliz ano novo",
      "fogos artificio", "champanhe"], "Ano Novo"),

    # --- Carnaval ---
    (["carnaval", "carnival", "mardi gras", "fantasia carnaval",
      "mascara carnaval", "confete", "serpentina"], "Carnaval"),

    # --- Festa Junina ---
    (["festa junina", "junina", "sao joao", "arraial", "bandeirinha",
      "bandeirinhas", "chapeu palha", "xadrez", "fogueira",
      "quadrilha", "milho", "foguete"], "Festa Junina"),

    # --- Dia das Mães ---
    (["dia das maes", "dia mae", "mothers day", "maezinha", "mainha",
      "para mae", "para maes", "presente mae", "amor mae",
      "melhor mae", "super mae", "rainha mae"], "Dia das Mães"),

    # --- Dia dos Pais ---
    (["dia dos pais", "dia pai", "fathers day", "paizinho", "painho",
      "para pai", "presente pai", "melhor pai", "super pai",
      "heroi pai", "papai"], "Dia dos Pais"),

    # --- Dia dos Namorados ---
    (["dia dos namorados", "namorado", "namorada", "valentines",
      "valentine", "love heart", "coracao apaixonado", "romance",
      "amor eterno", "te amo", "para voce", "apaixonados",
      "casal apaixonado"], "Dia dos Namorados"),

    # --- Casamento ---
    (["wedding", "casamento", "noiva", "noivo", "bride", "groom",
      "matrimonio", "bodas", "noivado", "alianca", "votos",
      "cerimonia", "recepcao casamento", "decoracao casamento",
      "convite casamento", "mesa casamento", "lembranc casamento"], "Casamento"),

    # --- Chá de Bebê / Chá Revelacao ---
    (["cha de bebe", "baby shower", "cha revelacao", "churrascinho bebe",
      "gender reveal", "maternidade", "gravida", "gestante",
      "chegada bebe", "boas vindas bebe"], "Chá de Bebê"),

    # --- Aniversário ---
    (["aniversario", "birthday", "bday", "happy birthday",
      "parabens pra voce", "festa aniversario", "boleira",
      "anos", "aninho", "aniversariante", "feliz aniversario"], "Aniversário"),

    # --- Dia das Crianças ---
    (["dia das criancas", "criancas", "children day", "kids day",
      "para criancas", "infantil"], "Dia das Crianças"),

    # --- Halloween ---
    (["halloween", "bruxa", "witch", "abobora", "pumpkin",
      "caveira halloween", "fantasma", "ghost", "aranha halloween",
      "morcego", "bat", "zumbi", "zombie", "frankenstein",
      "dracul", "vampiro"], "Halloween"),

    # --- Dia de Finados ---
    (["finados", "dia dos mortos", "dia de finados", "dia dos mortos",
      "calavera", "sugar skull", "catrina"], "Dia de Finados"),

    # --- Formatura ---
    (["formatura", "graduation", "formando", "formanda", "diploma",
      "colacao", "cap gown", "chapeu formatura", "turma formatura"], "Formatura"),

    # --- Dia do Professor ---
    (["dia do professor", "professor", "professora", "teacher",
      "docente", "mestre", "mestra", "escola", "educador"], "Dia do Professor"),

    # --- Dia do Trabalho ---
    (["dia do trabalho", "trabalhador", "labor day", "primeiro de maio",
      "1 de maio"], "Dia do Trabalho"),

    # --- Dia dos Avós ---
    (["dia dos avos", "avo", "vovo", "vovó", "vovô", "avo",
      "neto", "neta", "para avo", "para vovo"], "Dia dos Avós"),

    # --- Dia do Amigo ---
    (["dia do amigo", "amizade", "friendship", "melhor amigo",
      "melhor amiga", "bff", "para amiga", "para amigo"], "Dia do Amigo"),

    # --- Dia dos Namorados (extras) ---
    (["coracao", "heart", "amor", "love", "te amo", "eu te amo",
      "for you", "para voce"], "Dia dos Namorados"),

    # --- Corpus Christi / Religioso ---
    (["corpus christi", "primeira comunhao", "crisma", "batizado",
      "batismo", "eucaristia"], "Primeira Comunião"),

    # --- Dia das Bruxas BR ---
    (["dia das bruxas", "noite das bruxas"], "Halloween"),

    # --- Maternidade (gestão / nascimento) ---
    (["recem nascido", "newborn", "chegada bebe", "nascimento"], "Chá de Bebê"),

    # --- Chá Bar ---
    (["cha bar", "churrascao"], "Chá Bar"),

    # --- Dia das Mulheres ---
    (["dia da mulher", "dia internacional mulher", "8 de marco",
      "womens day", "girl power", "empoderamento feminino"], "Dia das Mulheres"),

    # --- Dia do Homem ---
    (["dia do homem", "mens day", "homem"], "Dia do Homem"),

    # --- Dia do Animal / Pet ---
    (["dia do animal", "dia dos pets", "dia do pet", "pet day"], "Dia do Animal"),

    # --- São Valentin ---
    (["sao valentim", "san valentin", "saint valentin"], "Dia dos Namorados"),

    # --- Festas de Final de Ano ---
    (["ferias", "recesso", "fim de ano"], "Natal"),

    # --- Aniversário de Empresa ---
    (["aniversario empresa", "corporativo", "empresa anos",
      "fundacao empresa"], "Aniversário Corporativo"),

    # --- Aposentadoria ---
    (["aposentadoria", "aposentado", "aposentada",
      "retirement", "parabens aposentado"], "Aposentadoria"),

    # --- Promoção / Colação ---
    (["promocao escolar", "formatura escolar", "fim de ano escolar",
      "conclusao curso"], "Formatura"),
]


# ===========================================================================
# FUNCTION_MAP — Função / Tipo do produto (Cat 2 — OBRIGATÓRIA)
# ===========================================================================
FUNCTION_MAP = [
    # --- Luminária ---
    (["luminaria", "lamp", "lampada", "abajur", "nightlight",
      "night light", "luz noturna", "led", "luminoso", "neon",
      "light box", "caixa de luz", "painel luminoso",
      "luminaria mesa", "luminaria parede", "luz ambiente"], "Luminária"),

    # --- Porta-Retrato / Quadro de Foto ---
    (["porta retrato", "portaretrato", "photo frame", "picture frame",
      "frame foto", "moldura", "quadro foto", "porta foto",
      "album foto", "memoria foto"], "Porta-Retrato"),

    # --- Topo de Bolo ---
    (["topo de bolo", "cake topper", "topper bolo", "topo bolo",
      "decoracao bolo", "enfeite bolo"], "Topo de Bolo"),

    # --- Centro de Mesa ---
    (["centro de mesa", "centerpiece", "enfeite mesa",
      "decoracao mesa", "centro mesa", "arranjo mesa"], "Centro de Mesa"),

    # --- Mandala ---
    (["mandala", "mandara", "geometria sagrada",
      "mandala floral", "mandala parede"], "Mandala"),

    # --- Porta-Joias ---
    (["porta joias", "jewelry box", "jewellery", "joias",
      "bijuteria", "porta anel", "porta pulseira",
      "porta colar", "porta brinco", "organizador joias"], "Porta-Joias"),

    # --- Porta-Chaves ---
    (["porta chave", "porta chaves", "key holder", "keyholder",
      "key rack", "chaveiro parede", "organizador chave",
      "suporte chave"], "Porta-Chaves"),

    # --- Porta-Copo / Descanso ---
    (["porta copo", "coaster", "descanso copo", "suporte copo",
      "base copo", "porta xicara"], "Porta-Copo"),

    # --- Porta-Celular / Suporte ---
    (["porta celular", "suporte celular", "phone holder",
      "phone stand", "suporte tablet", "dock phone"], "Suporte para Celular"),

    # --- Porta-Óculos ---
    (["porta oculos", "suporte oculos", "glasses holder",
      "eyeglass holder"], "Porta-Óculos"),

    # --- Porta-Caneta / Organizador de Mesa ---
    (["porta caneta", "pen holder", "organizador mesa escritorio",
      "porta lapis", "porta clips", "porta objeto",
      "organizador escritorio"], "Organizador de Mesa"),

    # --- Porta-Vinho / Adega ---
    (["porta vinho", "wine rack", "adega", "suporte vinho",
      "vinho", "taça vinho", "taca vinho", "wine holder"], "Porta-Vinho"),

    # --- Bandeja ---
    (["bandeja", "tray", "bandeja decorativa", "bandeja madeira",
      "bandeja organizadora"], "Bandeja"),

    # --- Pote / Recipiente ---
    (["pote", "pot", "vasilha", "potinho", "pote madeira",
      "recipiente", "pote decorativo"], "Pote Decorativo"),

    # --- Relógio ---
    (["relogio", "clock", "wall clock", "relogio parede",
      "relogio madeira", "relogio decorativo"], "Relógio"),

    # --- Espelho ---
    (["espelho", "mirror", "espelho decorativo",
      "espelho parede", "espelho madeira"], "Espelho Decorativo"),

    # --- Cabide / Gancho ---
    (["cabide", "hanger", "coat hanger", "gancho", "hook",
      "pendurador", "porta bolsa", "porta casaco",
      "porta toalha", "porta chapeu"], "Cabide"),

    # --- Nome Decorativo ---
    (["nome decorativo", "letra decorativa", "monogram",
      "initial", "letreiro", "sign nome", "placa nome",
      "nome parede", "nome madeira", "first name"], "Nome Decorativo"),

    # --- Plaquinha / Sinalização ---
    (["placa", "plaquinha", "plaque", "door sign", "aviso",
      "indicativo", "welcome sign", "bem vindo", "sinaliza",
      "sinalizacao", "totem", "painel sinal"], "Plaquinha"),

    # --- Caixa Organizadora ---
    (["caixa", "box", "organizador", "porta treco", "porta trecos",
      "armazenamento", "storage", "cofre", "caixa madeira",
      "caixa decorativa", "caixinha", "caixa organizadora",
      "caixa presente", "gift box"], "Caixa Organizadora"),

    # --- Lembrancinha / Chaveiro ---
    (["lembrancinha", "lembranca", "chaveiro", "keychain",
      "tag lembranca", "mini lembranca", "brinde",
      "souvenir", "recordacao"], "Lembrancinha"),

    # --- Quadro Decorativo / Arte Parede ---
    (["quadro decorativo", "painel decorativo", "wall art",
      "arte parede", "decoracao parede", "wall decor",
      "framed art", "poster madeira"], "Quadro Decorativo"),

    # --- Brinquedo Educativo ---
    (["brinquedo", "toy", "puzzle", "quebra cabeca", "educativo",
      "educacional", "montessori", "jogo infantil", "atividade",
      "pedagogico", "aprendizado", "brinquedo madeira"], "Brinquedo Educativo"),

    # --- Jogo de Mesa ---
    (["jogo de mesa", "board game", "xadrez", "dama", "domino",
      "jogo madeira", "game", "passa tempo",
      "jogo estrategia", "tabuleiro"], "Jogo de Mesa"),

    # --- Penteadeira / Organizador Banheiro ---
    (["organizador banheiro", "porta sabonete", "suporte banheiro",
      "porta shampoo", "porta escova", "porta dental"], "Organizador de Banheiro"),

    # --- Totem / Display ---
    (["totem", "display", "expositor", "suporte display",
      "display madeira", "totem decorativo"], "Totem"),

    # --- Porta-Tempero / Cozinha ---
    (["porta tempero", "spice rack", "organizador cozinha",
      "porta condimento", "porta sal", "porta azeite",
      "suporte tempero"], "Organizador de Cozinha"),

    # --- Fruteira / Bandeja Cozinha ---
    (["fruteira", "bowl", "fruteiro", "bacia madeira",
      "bandeja cozinha"], "Fruteira"),

    # --- Escultura / Decoração 3D ---
    (["escultura", "sculpture", "3d", "decor 3d",
      "decoracao 3d", "arte 3d", "painel 3d"], "Escultura Decorativa"),

    # --- Suporte para Plantas ---
    (["suporte planta", "plant stand", "vaso suporte",
      "suporte vaso", "cachepot", "jardim vertical",
      "suporte cacto"], "Suporte para Plantas"),

    # --- Porta-Livro / Organizador Livro ---
    (["porta livro", "bookend", "organizador livro",
      "suporte livro", "estante madeira"], "Porta-Livro"),

    # --- Tag / Etiqueta ---
    (["tag", "etiqueta", "label", "tag madeira",
      "etiqueta madeira", "etiqueta produto",
      "tag presente"], "Etiqueta Decorativa"),

    # --- Porta-Controle Remoto ---
    (["porta controle", "suporte controle", "porta controle remoto",
      "remote holder"], "Porta-Controle"),

    # --- Calendário ---
    (["calendario", "calendar", "agenda", "planner",
      "calendario perpetuo", "data"], "Calendário Decorativo"),

    # --- Mapa Decorativo ---
    (["mapa", "map", "mapa decorativo", "mapa brasil",
      "mapa mundi", "mapa cidade", "mapa estado"], "Mapa Decorativo"),

    # --- Painel Vazado ---
    (["painel vazado", "painel treliça", "painel mdf",
      "painel laser", "grade decorativa", "biombo"], "Painel Vazado"),

    # --- Embalagem / Caixa Presente ---
    (["embalagem", "packaging", "caixa presente", "gift box",
      "sacola madeira", "caixa festa"], "Caixa Presente"),

    # --- Suporte Tablet / Livro ---
    (["suporte tablet", "suporte livro leitura",
      "suporte receita", "book stand"], "Suporte Leitura"),

    # --- Aplique / Recorte Decorativo ---
    (["aplique", "recorte decorativo", "silhueta",
      "silhouette", "recorte mdf", "aplique parede"], "Aplique Decorativo"),

    # --- Nomes de Estádo / País ---
    (["mapa estado", "recorte estado", "mapa regiao",
      "mapa brasil"], "Mapa Decorativo"),

    # --- Porta-Fone / Headphone Stand ---
    (["porta fone", "headphone stand", "suporte headphone",
      "fone ouvido"], "Porta-Fone"),

    # --- Gamer / Setup ---
    (["gamer", "setup gamer", "gaming", "game room",
      "desk gamer", "rgb"], "Decoração Gamer"),

    # --- Presente Corporativo ---
    (["corporativo", "empresa", "brinde corporativo",
      "presente empresa", "logo empresa", "cnpj"], "Brinde Corporativo"),
]


# ===========================================================================
# AMBIENTE_MAP — Ambiente / Cômodo (Cat 3 — OBRIGATÓRIA)
# ===========================================================================
AMBIENTE_MAP = [
    # --- Quarto de Bebê ---
    (["quarto bebe", "cha de bebe", "baby shower", "maternidade",
      "newborn", "recem nascido", "chegada bebe",
      "decoracao bebe", "nursery", "quarto recem nascido"], "Quarto de Bebê"),

    # --- Quarto Infantil ---
    (["quarto infantil", "infantil", "kids room", "crianca",
      "children room", "unicornio", "dinossauro", "princess",
      "prince", "fada", "superheroi", "cartoon", "personagem",
      "menino", "menina", "quarto crianca"], "Quarto Infantil"),

    # --- Quarto Adulto ---
    (["quarto", "bedroom", "cama", "closet",
      "dormitorio", "quarto casal", "quarto solteiro"], "Quarto"),

    # --- Cozinha ---
    (["cozinha", "kitchen", "cafe", "coffee", "cha xicara",
      "receita", "comida", "food", "cook", "chef",
      "utensilios", "tempero", "fruteira", "gastronomia",
      "cozinheiro", "padaria", "confeitaria", "doces"], "Cozinha"),

    # --- Banheiro ---
    (["banheiro", "bathroom", "banho", "bath", "lavabo",
      "sabonete", "toalha", "ducha", "espelho banheiro",
      "organizador banheiro"], "Banheiro"),

    # --- Escritório / Home Office ---
    (["escritorio", "office", "home office", "trabalho",
      "desk", "mesa trabalho", "organizer escritorio",
      "agenda", "planner", "calendario", "corporativo",
      "negocios", "profissional"], "Escritório"),

    # --- Sala de Estar ---
    (["sala", "living room", "sofa", "tv", "sala estar",
      "sala jantar", "jantar", "aparador", "rack",
      "parede sala", "sala visita"], "Sala"),

    # --- Área de Lazer / Varanda ---
    (["varanda", "balcao", "deck", "area lazer", "quintal",
      "terraço", "terraco", "jardim", "area externa",
      "outdoor", "externo", "piscina"], "Área de Lazer"),

    # --- Churrasqueira / Gourmet ---
    (["churrasqueira", "churrasco", "gourmet", "area gourmet",
      "espaco gourmet", "parrilla", "grillmaster"], "Área Gourmet"),

    # --- Sala de Jogos / Gamer ---
    (["sala jogos", "game room", "gamer", "setup gamer",
      "games", "playroom", "sala gamer"], "Sala de Jogos"),

    # --- Academia / Gym ---
    (["academia", "gym", "fitness", "crossfit", "musculacao",
      "treino", "personal trainer", "esporte",
      "boxe", "luta"], "Academia"),

    # --- Templo / Espaço Religioso ---
    (["igreja", "templo", "capela", "cruzeiro", "religioso",
      "santuario", "altar", "oratorio"], "Espaço Religioso"),

    # --- Loja / Comercial ---
    (["loja", "store", "comercio", "comercial", "vitrine",
      "pdv", "ponto de venda", "showroom", "expositor loja"], "Loja"),

    # --- Pet Shop / Espaço Pet ---
    (["petshop", "pet shop", "veterinario", "clinica veterinaria",
      "espaco pet", "caniche", "poodle", "bulldog",
      "gato espaco", "cachorro espaco"], "Pet Shop"),

    # --- Garagem ---
    (["garagem", "garage", "oficina", "workshop",
      "ferramentas", "mecanica"], "Garagem"),

    # --- Lavanderia ---
    (["lavanderia", "laundry", "lavadero",
      "area servico", "area de servico"], "Lavanderia"),

    # --- Festa / Evento ---
    (["festa", "party", "evento", "celebracao", "decoracao festa",
      "balao", "confete", "table decor", "mesa festa",
      "buffet", "salao festa", "espaco festas"], "Festa"),

    # --- Escola / Educacional ---
    (["escola", "colegio", "educacao", "sala aula",
      "educacional", "pedagogico", "montessori",
      "sala montessori"], "Sala de Aula"),

    # --- Clinica / Consultório ---
    (["clinica", "consultorio", "medico", "medica",
      "hospital", "saude", "fisioterapia", "psicologia",
      "nutricao", "odontologia", "dentista"], "Clínica"),

    # --- Barbearia / Salão ---
    (["barbearia", "salao beleza", "salao de beleza", "barbershop",
      "cabelereiro", "estetica", "spa", "nail art", "manicure"], "Salão de Beleza"),

    # --- Camping / Aventura ---
    (["camping", "aventura", "trilha", "outdoor adventure",
      "acampamento", "natureza"], "Camping"),
]


# ===========================================================================
# THEME_MAP — Tema visual (Cat 4 — opcional)
# ===========================================================================
THEME_MAP = [
    # --- Religioso ---
    (["jesus", "cristo", "cruzeiro", "cruz", "religioso",
      "deus", "oracao", "biblia", "sagrado coracao",
      "nossa senhora", "maria", "jose", "anjo", "angel",
      "divino espirito", "fe", "esperanca", "pentecostal",
      "evangelico", "catolico", "batista"], "Religioso"),

    # --- Montessori ---
    (["montessori", "waldorf", "aprendizado natural",
      "estimulacao precoce", "desenvolvimento crianca",
      "pedagogia", "educacao natural"], "Montessori"),

    # --- Safari / Selva ---
    (["safari", "selva", "jungle", "leao", "tigre", "elefante",
      "girafa", "zebra", "macaco", "hipopotamo",
      "rinoceronte", "africa", "wild", "animais selvagens"], "Safari"),

    # --- Fazenda / Country ---
    (["fazenda", "farm", "country", "vaca", "porco", "galinha",
      "cavalo", "ovelha", "cabra", "celeiro", "roça",
      "campo", "rural", "sitio", "rancho"], "Fazenda"),

    # --- Náutico / Mar ---
    (["nautico", "nautica", "mar", "sea", "ocean", "praia",
      "beach", "ancora", "leme", "barco", "vela", "navio",
      "sereia", "polvo", "golfinhos", "peixe", "coral",
      "concha", "onda"], "Náutico"),

    # --- Floresta / Natureza ---
    (["floresta", "forest", "natureza", "nature", "arvore",
      "folha", "planta", "flor", "jardim", "botanico",
      "organico", "eco", "sustentavel"], "Natureza"),

    # --- Animais Domesticos / Pet ---
    (["cachorro", "dog", "gato", "cat", "pet", "bicho",
      "animal estimacao", "pata", "focinho", "rabo",
      "labrador", "golden", "husky", "pitbull", "dachshund",
      "siames", "persa", "filhote"], "Pet"),

    # --- Unicornio / Fantasia ---
    (["unicornio", "unicorn", "fada", "fairy", "magia",
      "fantasia", "magico", "arco iris", "rainbow",
      "sereia", "mermaid", "pegasus"], "Fantasia"),

    # --- Dinóssauro ---
    (["dinossauro", "dinosaur", "dino", "t-rex", "trex",
      "jurassic", "pterossauro", "velocirraptor"], "Dinóssauro"),

    # --- Super-Heróis ---
    (["superheroi", "superhero", "batman", "superman", "spiderman",
      "homem aranha", "homem ferro", "capitao america",
      "mulher maravilha", "marvel", "dc comics",
      "vingadores", "avengers", "liga justica"], "Super-Heróis"),

    # --- Princesas / Disney ---
    (["princesa", "princess", "disney", "cinderela", "rapunzel",
      "bela adormecida", "branca de neve", "frozen", "elsa",
      "anna", "moana", "ariel", "bela"], "Princesas"),

    # --- Anime / Mangá ---
    (["anime", "manga", "naruto", "dragon ball", "one piece",
      "demon slayer", "kimetsu", "my hero academia",
      "kawaii", "chibi", "sakura"], "Anime"),

    # --- Esporte ---
    (["futebol", "football", "basquete", "basketball", "volei",
      "volleyball", "tenis", "natacao", "ciclismo",
      "corrida", "atletismo", "esporte", "sport"], "Esporte"),

    # --- Música ---
    (["musica", "music", "violao", "guitarra", "piano",
      "bateria", "nota musical", "musica parede",
      "instrumento", "rock", "sertanejo", "forro", "samba"], "Música"),

    # --- Floral / Botânico ---
    (["floral", "flores", "flower", "rosas", "girassol",
      "botanico", "botanical", "tulipa", "orquidea",
      "lavanda", "camomila", "coroa flores"], "Floral"),

    # --- Gamer ---
    (["gamer", "gaming", "joystick", "controle jogo",
      "pixel", "arcade", "playstation", "xbox", "nintendo",
      "minecraft", "among us", "fortnite"], "Gamer"),

    # --- Astros / Espaço ---
    (["espaco", "space", "galaxia", "galaxy", "planeta",
      "estrela", "lua", "sol", "astronauta", "foguete",
      "universo", "cosmo", "saturno", "marte"], "Espaço"),

    # --- Nordestino / Forró ---
    (["nordestino", "forro", "forró", "sertanejo",
      "nordeste", "cangacu", "lampiao", "maria bonita",
      "cordel", "xilografia", "caatinga"], "Cultura Nordestina"),

    # --- Brasil / Patriótico ---
    (["brasil", "brazil", "verde amarelo", "selecao",
      "cbf", "pais brasil", "bandeira brasil",
      "independencia brasil"], "Brasil"),

    # --- Minimalismo ---
    (["minimalista", "minimal", "clean design",
      "linha fina", "simples elegante"], "Minimalista"),

    # --- Tropical ---
    (["tropical", "flamingo", "tucano", "arara",
      "folha tropical", "palmeira", "abacaxi",
      "frutas tropicais"], "Tropical"),
]


# ===========================================================================
# STYLE_MAP — Estilo visual (opcional)
# ===========================================================================
STYLE_MAP = [
    (["minimalista", "minimal", "clean", "simples moderno"],          "Minimalista"),
    (["rustico", "rustic", "madeira rustica", "estilo campo"],         "Rústico"),
    (["moderno", "modern", "contemporaneo", "design moderno"],          "Moderno"),
    (["vintage", "retro", "antigo", "anos 70", "anos 80"],             "Vintage"),
    (["romantico", "romantic", "delicado", "suave",
      "flores delicadas", "rendado"],                                   "Romântico"),
    (["elegante", "elegant", "luxo", "luxury", "premium",
      "sofisticado", "requintado"],                                      "Elegante"),
    (["divertido", "fun", "colorido", "fofo", "cute",
      "alegre", "vibrante"],                                            "Divertido"),
    (["geometrico", "geometric", "linhas", "abstract",
      "angular", "triangulo", "hexagono"],                              "Geométrico"),
    (["boho", "bohemian", "macrame", "etnico",
      "hippie", "tribal"],                                              "Boho"),
    (["industrial", "metal", "aco", "ferro",
      "tubulacao", "estilo industrial"],                                 "Industrial"),
    (["escandinavo", "scandinavian", "nordico", "nordic",
      "hygge"],                                                         "Escandinavo"),
    (["classico", "classic", "tradicional",
      "antigo", "barroco"],                                             "Clássico"),
    (["oriental", "japones", "chines", "asiatico",
      "zen", "feng shui", "sakura", "torii"],                           "Oriental"),
    (["shabby chic", "shabby", "provençal", "provencal",
      "patina", "desgastado"],                                          "Shabby Chic"),
    (["art deco", "deco", "gatsby", "anos 20"],                         "Art Déco"),
]


# ===========================================================================
# PUBLIC_MAP — Público-alvo (opcional)
# ===========================================================================
PUBLIC_MAP = [
    (["bebe", "baby", "newborn", "recem nascido"],                         "Bebê"),
    (["crianca", "infantil", "kids", "children",
      "menino", "menina"],                                                "Criança"),
    (["adolescente", "teen", "teenager", "jovem"],                         "Adolescente"),
    (["mae", "mom", "mother", "maezinha"],                                 "Mãe"),
    (["pai", "dad", "father", "paizinho"],                                 "Pai"),
    (["avo", "vovo", "grandpa", "grandma", "neto"],                        "Avós"),
    (["casal", "couple", "noiva", "namorado", "namorada"],                 "Casal"),
    (["familia", "family", "casa familia"],                                "Família"),
    (["professor", "professora", "teacher", "docente"],                    "Professor"),
    (["medico", "medica", "enfermeiro", "saude",
      "doutor", "doutura"],                                               "Profissional da Saúde"),
    (["pet", "cachorro", "gato", "animal",
      "dono pet"],                                                        "Dono de Pet"),
    (["atleta", "esportista", "fitness", "gym",
      "corredor", "ciclista"],                                            "Atleta"),
    (["empresario", "empresa", "corporativo",
      "empreendedor", "negocio"],                                         "Empresas"),
    (["presente", "gift", "lembranca",
      "lembrancinha", "mimo"],                                            "Presente"),
    (["artesao", "artesanato", "artista",
      "crafter"],                                                         "Artesanato"),
    (["cozinheiro", "chef", "confeiteiro",
      "padeiro", "gastronomia"],                                          "Gastrônomo"),
    (["musico", "guitarrista", "pianista",
      "baterista", "cantor"],                                             "Músico"),
    (["gamer", "jogador", "streamer"],                                     "Gamer"),
]


# ===========================================================================
# TRANSLATION_MAP — Inglês → Português (para gerar name_pt no card)
# ===========================================================================
TRANSLATION_MAP = {
    # A
    "abstract": "abstrato", "acorn": "bolota", "adorable": "adorável",
    "alphabet": "alfabeto", "anchor": "âncora", "angel": "anjo",
    "animal": "animal", "anniversary": "aniversário",
    "apple": "maçã", "art": "arte", "autumn": "outono",
    "award": "prêmio",
    # B
    "baby": "bebê", "balloon": "balão", "bat": "morcego",
    "bathroom": "banheiro", "bear": "urso", "beautiful": "lindo",
    "bedroom": "quarto", "bee": "abelha", "bird": "pássaro",
    "birthday": "aniversário", "board": "tabuleiro", "book": "livro",
    "bookend": "porta-livro", "border": "borda", "box": "caixa",
    "branch": "galho", "brave": "corajoso", "bride": "noiva",
    "bunny": "coelhinho", "butterfly": "borboleta",
    # C
    "cabin": "cabana", "cake": "bolo", "calendar": "calendário",
    "candle": "vela", "card": "cartão", "cardinal": "cardeal",
    "carousel": "carrossel", "castle": "castelo",
    "cat": "gato", "celebration": "celebração", "centerpiece": "centro de mesa",
    "chalkboard": "quadro negro", "christmas": "natal",
    "circus": "circo", "city": "cidade", "clock": "relógio",
    "cloud": "nuvem", "coat": "casaco", "coaster": "porta-copo",
    "coffee": "café", "collection": "coleção", "color": "cor",
    "comet": "cometa", "compass": "bússola", "corner": "canto",
    "couple": "casal", "cow": "vaca", "craft": "artesanato",
    "crown": "coroa", "cute": "fofo",
    # D
    "dad": "pai", "daisy": "margarida", "dance": "dança",
    "decor": "decoração", "decorative": "decorativo",
    "deer": "cervo", "desk": "escrivaninha", "diamond": "diamante",
    "dinosaur": "dinossauro", "dino": "dino", "display": "display",
    "dog": "cachorro", "door": "porta", "dragon": "dragão",
    "dream": "sonho", "duck": "pato",
    # E
    "eagle": "águia", "easter": "páscoa", "elephant": "elefante",
    "elegant": "elegante", "enchanted": "encantado",
    "eternal": "eterno", "event": "evento",
    # F
    "fairy": "fada", "fall": "outono", "family": "família",
    "farm": "fazenda", "father": "pai", "feather": "pena",
    "festive": "festivo", "fish": "peixe", "flame": "chama",
    "flamingo": "flamingo", "flower": "flor", "forest": "floresta",
    "fox": "raposa", "frame": "moldura", "friend": "amigo",
    "frog": "sapo", "fruit": "fruta",
    # G
    "galaxy": "galáxia", "game": "jogo", "garden": "jardim",
    "gift": "presente", "girl": "menina", "glitter": "glitter",
    "gnome": "gnomo", "goat": "cabra", "graduation": "formatura",
    "groom": "noivo",
    # H
    "halloween": "halloween", "hamster": "hamster",
    "hanger": "cabide", "happy": "feliz", "harvest": "colheita",
    "heart": "coração", "hedgehog": "ouriço", "hello": "olá",
    "hippo": "hipopótamo", "holder": "suporte", "home": "lar",
    "honey": "mel", "horse": "cavalo", "house": "casa",
    "hummingbird": "beija-flor",
    # I
    "initial": "inicial", "inspirational": "inspiracional",
    # J
    "jar": "pote", "jewelry": "joias", "jungle": "selva",
    # K
    "key": "chave", "keychain": "chaveiro", "kids": "crianças",
    "kitchen": "cozinha", "kitten": "gatinho",
    # L
    "label": "etiqueta", "lamp": "lâmpada", "lantern": "lanterna",
    "laser": "laser", "lavender": "lavanda", "leaf": "folha",
    "letter": "letra", "light": "luz", "lion": "leão",
    "living": "sala", "llama": "lhama", "love": "amor",
    "lucky": "sortudo",
    # M
    "magic": "mágico", "mama": "mamãe", "map": "mapa",
    "memorial": "memorial", "mermaid": "sereia",
    "mirror": "espelho", "mom": "mãe", "monkey": "macaco",
    "moon": "lua", "mother": "mãe", "mountain": "montanha",
    "music": "música",
    # N
    "name": "nome", "nature": "natureza", "newborn": "recém-nascido",
    "night": "noite", "nursery": "quarto de bebê",
    # O
    "ocean": "oceano", "office": "escritório", "ornament": "enfeite",
    "outdoor": "externo", "owl": "coruja",
    # P
    "panda": "panda", "party": "festa", "peace": "paz",
    "penguin": "pinguim", "personalized": "personalizado",
    "pet": "pet", "photo": "foto", "pig": "porco",
    "plaque": "placa", "plant": "planta", "polar": "polar",
    "porch": "varanda", "portrait": "retrato",
    "pumpkin": "abóbora", "puppy": "filhote", "puzzle": "quebra-cabeça",
    # Q
    "queen": "rainha",
    # R
    "rabbit": "coelho", "rack": "rack", "rainbow": "arco-íris",
    "reindeer": "rena", "religious": "religioso", "ring": "anel",
    "rocket": "foguete", "rose": "rosa", "rustic": "rústico",
    # S
    "safari": "safari", "santa": "papai noel", "school": "escola",
    "seasonal": "sazonal", "sheep": "ovelha", "shelf": "prateleira",
    "sign": "placa", "skeleton": "esqueleto", "skull": "caveira",
    "sloth": "preguiça", "snowflake": "floco de neve",
    "snowman": "boneco de neve", "space": "espaço",
    "special": "especial", "spring": "primavera",
    "star": "estrela", "storage": "armazenamento",
    "summer": "verão", "sunflower": "girassol",
    "superhero": "super-herói", "sweet": "doce",
    # T
    "tag": "etiqueta", "teacher": "professor", "topper": "topo",
    "toy": "brinquedo", "tree": "árvore", "tray": "bandeja",
    "tropical": "tropical", "turtle": "tartaruga",
    # U
    "unicorn": "unicórnio", "unique": "único",
    # V
    "valentine": "dia dos namorados", "vintage": "vintage",
    # W
    "wall": "parede", "wedding": "casamento", "welcome": "bem-vindo",
    "whale": "baleia", "wild": "selvagem", "winter": "inverno",
    "witch": "bruxa", "wolf": "lobo", "wood": "madeira",
    "woodland": "floresta", "wreath": "guirlanda",
    # Y / Z
    "year": "ano", "zebra": "zebra",
}


# ===========================================================================
# GENERIC_FALLBACK_FUNCTION — quando NENHUMA keyword de FUNCTION_MAP bateu
# Mapeamento por palavras genéricas de produtos laser
# ===========================================================================
GENERIC_FALLBACK_FUNCTION = [
    (["box", "caixa", "case", "chest"],                  "Caixa Organizadora"),
    (["lamp", "light", "led", "luminaria", "neon"],       "Luminária"),
    (["sign", "placa", "plaque", "welcome"],              "Plaquinha"),
    (["mirror", "espelho"],                               "Espelho Decorativo"),
    (["key", "chave"],                                    "Porta-Chaves"),
    (["rack", "holder", "suporte", "stand"],              "Suporte"),
    (["tag", "etiqueta", "label"],                        "Etiqueta Decorativa"),
    (["tray", "bandeja"],                                 "Bandeja"),
    (["frame", "moldura", "retrato"],                     "Porta-Retrato"),
    (["clock", "relogio"],                                "Relógio"),
    (["topper", "topo"],                                  "Topo de Bolo"),
    (["puzzle", "quebra"],                                "Brinquedo Educativo"),
    (["game", "jogo", "board"],                           "Jogo de Mesa"),
]

# Fallback final absoluto (quando absolutamente NADA bateu)
FINAL_FALLBACK_FUNCTION  = "Decoração Artesanal"
FINAL_FALLBACK_DATE      = "Data Especial"
FINAL_FALLBACK_AMBIENTE  = "Ambiente Doméstico"
