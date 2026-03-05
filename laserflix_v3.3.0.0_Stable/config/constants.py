"""
constants.py — Constantes globais do Laserflix.
Centraliza valores usados em múltiplos módulos para evitar duplicação.
"""

# =========================================================================
# STRINGS PROIBIDAS (NÃO EXIBIR/RETORNAR)
# =========================================================================

BANNED_STRINGS = {
    "diversos",
    "data especial",
    "ambiente doméstico",
    "ambiente domestico",
    "sem categoria",
    "general",
    "miscellaneous",
    "uncategorized",
}
"""
BANNED_STRINGS: Conjunto de strings que não devem ser:
  - Retornadas como categorias pela IA ou fallback
  - Exibidas nos cards da UI
  - Usadas em filtros ou listagens

Usado em:
  - ai/fallbacks.py: Filtrar categorias geradas
  - ui/project_card.py: Ocultar categorias nos cards
  - Qualquer validação de categorias/tags
"""
