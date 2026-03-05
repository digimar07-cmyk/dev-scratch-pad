"""
Constantes de UI e configurações visuais do Laserflix.
Centraliza valores hardcoded para facilitar manutenção.
"""

# =========================================================================
# TRUNCAMENTO DE TEXTO NOS CARDS
# =========================================================================

# Nome do projeto no card
CARD_NAME_MAX_LENGTH = 27       # Máximo de caracteres antes de truncar
CARD_NAME_TRUNCATE_AT = 24      # Caracteres exibidos + "..."

# Tags no card
CARD_TAG_MAX_LENGTH = 11        # Máximo de caracteres antes de truncar
CARD_TAG_TRUNCATE_AT = 9        # Caracteres exibidos + "..."

# Categoria no card
CARD_CATEGORY_MAX_LENGTH = 11   # Máximo para botão de categoria

# =========================================================================
# LIMITES DE EXIBIÇÃO
# =========================================================================

# Sidebar
SIDEBAR_MAX_CATEGORIES = 8      # Máximo de categorias na sidebar
SIDEBAR_MAX_TAGS = 20           # Máximo de tags na sidebar

# Cards
CARD_MAX_CATEGORIES = 3         # Máximo de categorias exibidas no card
CARD_MAX_TAGS = 3               # Máximo de tags exibidas no card

# Modal de detalhes
MODAL_MAX_GRID_IMAGES = 30      # Máximo de imagens no grid do modal
MODAL_THUMBNAIL_SIZE = 200      # Tamanho das thumbnails no grid (px)
MODAL_GRID_COLUMNS = 2          # Colunas no grid de imagens

# =========================================================================
# CORES DO TEMA
# =========================================================================

# Backgrounds
BG_PRIMARY = "#141414"          # Fundo principal
BG_SECONDARY = "#1A1A1A"        # Sidebar
BG_CARD = "#2A2A2A"             # Cards de projeto
BG_HOVER = "#242424"            # Hover em elementos
BG_SEPARATOR = "#333333"        # Linhas separadoras

# Acentos
ACCENT_RED = "#E50914"          # Vermelho Netflix (primário)
ACCENT_GREEN = "#1DB954"        # Verde Spotify (sucesso/IA)
ACCENT_GOLD = "#FFD700"         # Dourado (favoritos)

# Texto
FG_PRIMARY = "#FFFFFF"          # Texto principal
FG_SECONDARY = "#AAAAAA"        # Texto secundário
FG_TERTIARY = "#666666"         # Texto terciário

# Origens (badges)
ORIGIN_COLORS = {
    "Creative Fabrica": "#FF6B35",
    "Etsy": "#F7931E",
    "Diversos": "#4ECDC4",
    "default": "#9B59B6"        # Fallback para origens desconhecidas
}

# Categorias (badges nos cards)
CATEGORY_COLORS = [
    "#FF6B6B",                   # Vermelho claro
    "#4ECDC4",                   # Turquesa
    "#95E1D3"                    # Verde água
]

# =========================================================================
# FONTES
# =========================================================================

FONT_FAMILY = "Arial"

# Tamanhos de fonte
FONT_SIZE_LOGO = 28
FONT_SIZE_VERSION = 10
FONT_SIZE_NAV = 12
FONT_SIZE_SEARCH = 12
FONT_SIZE_MENU = 11
FONT_SIZE_CARD_NAME = 10
FONT_SIZE_CARD_CATEGORY = 7
FONT_SIZE_CARD_TAG = 7
FONT_SIZE_CARD_ORIGIN = 7
FONT_SIZE_CARD_ACTION = 12
FONT_SIZE_SIDEBAR_TITLE = 14
FONT_SIZE_SIDEBAR_ITEM = 10
FONT_SIZE_STATUS = 10

# Estilos de fonte (combinações prontas)
FONT_LOGO = (FONT_FAMILY, FONT_SIZE_LOGO, "bold")
FONT_NAV = (FONT_FAMILY, FONT_SIZE_NAV)
FONT_CARD_NAME = (FONT_FAMILY, FONT_SIZE_CARD_NAME, "bold")
FONT_CARD_SMALL = (FONT_FAMILY, FONT_SIZE_CARD_TAG)
FONT_SIDEBAR_TITLE = (FONT_FAMILY, FONT_SIZE_SIDEBAR_TITLE, "bold")

# =========================================================================
# DIMENSÕES E ESPAÇAMENTO
# =========================================================================

# Header
HEADER_HEIGHT = 70              # Altura do header em pixels
HEADER_PADDING_X = 20           # Padding horizontal do header

# Sidebar
SIDEBAR_WIDTH = 250             # Largura da sidebar
SIDEBAR_PADDING = 15            # Padding interno da sidebar

# Status bar
STATUS_BAR_HEIGHT = 40          # Altura da barra de status

# Progressbar
PROGRESSBAR_WIDTH = 300         # Largura da barra de progresso

# Modal
MODAL_PADDING = 24              # Padding geral no modal
MODAL_SECTION_SPACING = 20      # Espaço entre seções

# =========================================================================
# COMPORTAMENTO DE SCROLL
# =========================================================================

SCROLL_SPEED = 120              # Delta do mousewheel (Windows padrão)

# =========================================================================
# STRINGS PROIBIDAS (NÃO EXIBIR NOS CARDS)
# =========================================================================

CARD_BANNED_STRINGS = {
    "diversos", 
    "data especial", 
    "ambiente doméstico",
    "ambiente domestico", 
    "sem categoria", 
    "general",
    "miscellaneous", 
    "uncategorized",
}

# =========================================================================
# CONFIGURAÇÕES DE SALVAMENTO
# =========================================================================

AUTO_SAVE_INTERVAL = 10         # Salvar database a cada N projetos analisados
