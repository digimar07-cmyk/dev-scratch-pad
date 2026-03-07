"""
ui/main_window.py — Orquestrador puro do Laserflix.
Teto: 350 linhas. Nunca constrói widgets diretamente.

HOT-08: Paginação simples (Kent Beck style):
  - HOT-13: 36 cards por página (6 linhas × 6 cols)
  - Navegação: Início/Anterior/Próxima/Final
  - Atalhos: Home/End/Arrows
  - SIMPLES, PREVISÍVEL, FUNCIONAL

HOT-12: Scrollbar vertical (cards com categorias ficaram mais altos)
HOT-14: Busca bilíngue (EN + PT-BR) — FUNCIONA SEM OLLAMA!
HOT-15: Tradutor estático (utils/name_translator.py)
F-07: Filtros empilháveis (chips AND) — CORRIGIDO!

FEATURE: Ordenação FUNCIONAL na linha de paginação
FEATURE: Análise SEQUENCIAL pós-importação (categorias+tags → descrições)
F-03: Limpeza de órfãos (entradas sem path válido)
F-08: Sistema de coleções/playlists (gerenciamento + filtros + menu contextual + badges)

PERF-FIX-1: Removido search_var.set("") de set_filter() (300ms debounce eliminado)
PERF-FIX-2: Indicadores visuais de filtro ativo no header (🏠⭐✓👍👎 ficam vermelhos)
PERF-FIX-3: Cache de estado + skip rebuild desnecessário (cliques repetidos)
PERF-FIX-4: Otimização de build_card() com bind compartilhado (~25% mais rápido)
PERF-FIX-5: Virtual scrolling - renderiza apenas cards visíveis (66% redução startup!)

REFACTOR-FASE-2: DisplayController extraído (filtros/ordenação/paginação) ✅
REFACTOR-FASE-3: AnalysisController extraído (análise IA + descrições) ✅
"""