# 🏛️ PLANO DE REFATORAÇÃO ARQUITETURAL

**Projeto**: Laserflix v3.4.1.1_Stable  
**Objetivo**: Reduzir main_window.py de 1248 linhas para < 200 linhas  
**Arquitetura Alvo**: MVC (Model-View-Controller)  
**Data Início**: 06/03/2026  
**Modelo responsável**: Claude Sonnet 4.5

---

## 🛑 REGRA ABSOLUTA

```
⚠️ NENHUM ARQUIVO UI PODE CRESCER ALÉM DOS LIMITES!

main_window.py           : 200 linhas (MÁXIMO ABSOLUTO)
project_card.py          : 150 linhas (MÁXIMO ABSOLUTO)
project_modal.py         : 250 linhas (MÁXIMO ABSOLUTO)
header.py / sidebar.py   : 200 linhas (MÁXIMO ABSOLUTO)
QUALQUER CONTROLLER      : 300 linhas (MÁXIMO ABSOLUTO)
QUALQUER COMPONENT       : 200 linhas (MÁXIMO ABSOLUTO)
```

**Consequência de violação**: PARAR TODO DESENVOLVIMENTO até extrair.

---

## 🎯 DIAGNÓSTICO DO PROBLEMA

### Estado Atual (main_window.py - 1248 linhas)

| Responsabilidade | Linhas | Deveria estar em |
|-----------------|--------|------------------|
| UI Layout (Header, Sidebar, Canvas, StatusBar, SelectionBar) | ~200 | `components/` |
| Filtros (Chips, add/remove/clear, origem/categoria/tag) | ~150 | `DisplayController` |
| Ordenação (date, name, origin, analyzed) | ~50 | `DisplayController` |
| Paginação (next, prev, first, last) | ~80 | `DisplayController` |
| Display (get_filtered, build_cards, render) | ~300 | `DisplayController` |
| Seleção (toggle, select all, remove selected) | ~80 | `SelectionController` |
| Análise IA (single, batch, new, all, callbacks) | ~150 | `AnalysisController` |
| Descrições (generate new, batch, callbacks) | ~80 | `AnalysisController` |
| Coleções (dialog, add/remove, filter) | ~100 | `CollectionController` |
| Modais (Project, Edit, PrepareFolders, ModelSettings) | ~100 | (já está separado) |
| Toggles (Favorite, Done, Good, Bad) | ~40 | (manter no main, é trivial) |
| Virtual Scroll | ~30 | (já está em virtual_scroll.py) |
| Cache/Display State | ~50 | `DisplayController` |

**Total**: 1248 linhas de RESPONSABILIDADES MISTURADAS.

---

## 🏛️ ARQUITETURA ALVO (MVC)

```
ui/
├── main_window.py              # 150-200 linhas - ORQUESTRADOR PURO
├── controllers/
│   ├── display_controller.py   # Filtros + Ordenação + Paginação
│   ├── analysis_controller.py  # Análise IA + Descrições
│   ├── collection_controller.py
│   └── selection_controller.py
├── components/
│   ├── chips_bar.py            # Barra de chips de filtros
│   ├── status_bar.py           # Barra de status inferior
│   ├── selection_bar.py        # Barra de seleção múltipla
│   └── pagination_controls.py  # Controles de página
├── header.py                   # (JÁ EXISTE)
├── sidebar.py                  # (JÁ EXISTE)
├── project_card.py             # (JÁ EXISTE)
└── project_modal.py            # (JÁ EXISTE)
```

### Fluxo de Dados (MVC)

```
UI (main_window.py)
  │
  ↓ (user input)
  │
Controllers (display, analysis, collection, selection)
  │
  ↓ (coordena operações)
  │
Core (database, collections_manager, analysis_manager)
  │
  ↓ (retorna dados)
  │
Controllers (processa)
  │
  ↓ (atualiza)
  │
UI Components (chips_bar, status_bar, cards)
```

---

## 📅 ROADMAP (8 FASES)

### ✅ FASE 1: CRIAR ESTRUTURA (1h) - **COMPLETA**

**Status**: ✅ CONCLUÍDA (06/03/2026 19:47 BRT)

**O que foi feito**:
1. ✅ Criado `ui/controllers/__init__.py`
2. ✅ Criado `ui/components/__init__.py`
3. ✅ Criado `display_controller.py` (base)
4. ✅ Criado `analysis_controller.py` (base)
5. ✅ Criado `collection_controller.py` (base)
6. ✅ Criado `selection_controller.py` (base)
7. ✅ Criado `chips_bar.py` (base)
8. ✅ Criado `status_bar.py` (base funcional)
9. ✅ Criado `selection_bar.py` (base funcional)
10. ✅ Criado `pagination_controls.py` (base funcional)

**Commits**:
- [003d087](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/003d087) - Fase 1.1: controllers/__init__.py
- [6fe3946](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/6fe3946) - Fase 1.2: components/__init__.py
- [ead652f](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/ead652f) - Fase 1.3: 4 controllers base
- [f1b3738](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/f1b3738) - Fase 1.4: 4 components base

**Arquivos criados**: 10  
**Linhas adicionadas**: ~400  
**App quebrado?**: ❌ NÃO (arquivos novos, nada alterado)

---

### 🔴 FASE 2: EXTRAIR DISPLAY CONTROLLER (2-3h)

**Status**: ⚪ PENDENTE

**Objetivo**: Migrar lógica de filtros/ordenação/paginação para `DisplayController`.

**Métodos a migrar de main_window.py**:
1. `_apply_filters()` → `DisplayController.apply_filters()`
2. `_get_filtered_projects()` → `DisplayController.get_filtered_projects()`
3. `_apply_sorting()` → `DisplayController.apply_sorting()`
4. `_paginate()` → `DisplayController.paginate()`
5. `on_next_page()` → `DisplayController.next_page()`
6. `on_prev_page()` → `DisplayController.prev_page()`
7. `on_first_page()` → `DisplayController.first_page()`
8. `on_last_page()` → `DisplayController.last_page()`
9. `add_active_filter()` → `DisplayController.add_filter()`
10. `remove_active_filter()` → `DisplayController.remove_filter()`
11. `clear_all_filters()` → `DisplayController.clear_filters()`

**Checklist**:
- [ ] Implementar `DisplayController.get_filtered_projects()`
- [ ] Implementar `DisplayController.apply_sorting()`
- [ ] Implementar `DisplayController.paginate()`
- [ ] Implementar navegação (next, prev, first, last)
- [ ] Implementar gestão de filtros (add, remove, clear)
- [ ] Instanciar `DisplayController` no `main_window.__init__()`
- [ ] Substituir chamadas no `main_window.py` para usar controller
- [ ] Testar manualmente: filtros, ordenação, paginação
- [ ] Remover métodos antigos de `main_window.py`
- [ ] Commit: `refactor: Fase 2 - Extrai DisplayController`

**Redução esperada**: -300 linhas no main_window.py

---

### 🔴 FASE 3: EXTRAIR ANALYSIS CONTROLLER (2-3h)

**Status**: ⚪ PENDENTE (aguarda Fase 2)

**Objetivo**: Migrar lógica de análise IA + descrições para `AnalysisController`.

**Métodos a migrar de main_window.py**:
1. `analyze_single_project()` → `AnalysisController.analyze_single()`
2. `analyze_new_projects()` → `AnalysisController.analyze_batch(mode='new')`
3. `analyze_all_projects()` → `AnalysisController.analyze_batch(mode='all')`
4. `_on_analysis_complete()` → `AnalysisController._handle_complete()`
5. `_on_analysis_progress()` → `AnalysisController._handle_progress()`
6. `generate_description_for()` → `AnalysisController.generate_description()`
7. `generate_descriptions_new()` → `AnalysisController.generate_descriptions_batch(mode='new')`
8. `generate_descriptions_all()` → `AnalysisController.generate_descriptions_batch(mode='all')`

**Checklist**:
- [ ] Implementar `AnalysisController.analyze_single()`
- [ ] Implementar `AnalysisController.analyze_batch()`
- [ ] Implementar callbacks de progresso/complete
- [ ] Implementar `AnalysisController.generate_descriptions_batch()`
- [ ] Instanciar `AnalysisController` no `main_window.__init__()`
- [ ] Substituir chamadas no `main_window.py` para usar controller
- [ ] Testar manualmente: análise single, batch (new, all)
- [ ] Testar descrições batch
- [ ] Remover métodos antigos de `main_window.py`
- [ ] Commit: `refactor: Fase 3 - Extrai AnalysisController`

**Redução esperada**: -230 linhas no main_window.py

---

### 🔴 FASE 4: EXTRAIR COLLECTION CONTROLLER (1-2h)

**Status**: ⚪ PENDENTE (aguarda Fase 3)

**Objetivo**: Migrar lógica de coleções para `CollectionController`.

**Métodos a migrar de main_window.py**:
1. `add_to_collection()` → `CollectionController.add_to_collection()`
2. `remove_from_collection()` → `CollectionController.remove_from_collection()`
3. `create_new_collection_with()` → `CollectionController.create_new_with()`
4. `on_collection_filter()` → `CollectionController.filter_by_collection()`
5. `open_collections_manager()` → `CollectionController.open_manager()`

**Checklist**:
- [ ] Implementar `CollectionController.add_to_collection()`
- [ ] Implementar `CollectionController.remove_from_collection()`
- [ ] Implementar `CollectionController.create_new_with()`
- [ ] Implementar `CollectionController.filter_by_collection()`
- [ ] Instanciar `CollectionController` no `main_window.__init__()`
- [ ] Substituir chamadas no `main_window.py` para usar controller
- [ ] Testar manualmente: add, remove, create, filter
- [ ] Remover métodos antigos de `main_window.py`
- [ ] Commit: `refactor: Fase 4 - Extrai CollectionController`

**Redução esperada**: -100 linhas no main_window.py

---

### 🔴 FASE 5: EXTRAIR SELECTION CONTROLLER (1-2h)

**Status**: ⚪ PENDENTE (aguarda Fase 4)

**Objetivo**: Migrar lógica de seleção múltipla para `SelectionController`.

**Métodos a migrar de main_window.py**:
1. `toggle_selection_mode()` → `SelectionController.toggle_mode()`
2. `toggle_card_selection()` → `SelectionController.toggle_card()`
3. `select_all()` → `SelectionController.select_all()`
4. `deselect_all()` → `SelectionController.deselect_all()`
5. `remove_selected_projects()` → `SelectionController.remove_selected()`

**Checklist**:
- [ ] Implementar `SelectionController.toggle_mode()`
- [ ] Implementar `SelectionController.toggle_card()`
- [ ] Implementar `SelectionController.select_all()`
- [ ] Implementar `SelectionController.deselect_all()`
- [ ] Implementar `SelectionController.remove_selected()`
- [ ] Instanciar `SelectionController` no `main_window.__init__()`
- [ ] Substituir chamadas no `main_window.py` para usar controller
- [ ] Testar manualmente: toggle mode, select all, remove
- [ ] Remover métodos antigos de `main_window.py`
- [ ] Commit: `refactor: Fase 5 - Extrai SelectionController`

**Redução esperada**: -80 linhas no main_window.py

---

### 🔴 FASE 6: EXTRAIR UI COMPONENTS (2-3h)

**Status**: ⚪ PENDENTE (aguarda Fase 5)

**Objetivo**: Migrar construção de widgets para `components/`.

**Widgets a extrair de main_window.py**:
1. Barra de chips → `ChipsBar` (já criada, implementar update_chips)
2. Barra de status → `StatusBar` (já funcional)
3. Barra de seleção → `SelectionBar` (já funcional)
4. Controles de paginação → `PaginationControls` (já funcional)

**Checklist**:
- [ ] Implementar `ChipsBar.update_chips()` completamente
- [ ] Substituir construção inline de chips no main por `ChipsBar`
- [ ] Substituir construção inline de status bar no main por `StatusBar`
- [ ] Substituir construção inline de selection bar no main por `SelectionBar`
- [ ] Substituir construção inline de paginação no main por `PaginationControls`
- [ ] Testar manualmente: chips, status, seleção, paginação
- [ ] Remover código inline de `main_window.py`
- [ ] Commit: `refactor: Fase 6 - Extrai UI Components`

**Redução esperada**: -200 linhas no main_window.py

---

### 🔴 FASE 7: LIMPAR MAIN_WINDOW (1h)

**Status**: ⚪ PENDENTE (aguarda Fase 6)

**Objetivo**: Remover código morto + simplificar `main_window.py`.

**Ações**:
1. Remover imports não utilizados
2. Remover variáveis de instância duplicadas (ex: `current_filter` agora está no DisplayController)
3. Remover comentários obsoletos
4. Consolidar `__init__()` (instanciação de controllers)
5. Simplificar `display_projects()` (agora só chama controller + renderiza)
6. Adicionar docstrings nos métodos que sobraram

**Checklist**:
- [ ] Remover imports obsoletos
- [ ] Remover variáveis duplicadas
- [ ] Consolidar `__init__()` (< 50 linhas)
- [ ] Simplificar `display_projects()` (< 30 linhas)
- [ ] Adicionar docstrings
- [ ] Executar linter (flake8, pylint)
- [ ] Testar app completo manualmente
- [ ] Commit: `refactor: Fase 7 - Limpa main_window.py`

**Redução esperada**: -150 linhas no main_window.py

---

### 🔴 FASE 8: VALIDAÇÃO FINAL (30min)

**Status**: ⚪ PENDENTE (aguarda Fase 7)

**Objetivo**: Confirmar que TODOS os arquivos estão abaixo dos limites.

**Checklist**:
- [ ] Contar linhas de `main_window.py` (deve ser < 200)
- [ ] Contar linhas de `display_controller.py` (deve ser < 300)
- [ ] Contar linhas de `analysis_controller.py` (deve ser < 300)
- [ ] Contar linhas de `collection_controller.py` (deve ser < 300)
- [ ] Contar linhas de `selection_controller.py` (deve ser < 300)
- [ ] Contar linhas de `chips_bar.py` (deve ser < 200)
- [ ] Contar linhas de `status_bar.py` (deve ser < 200)
- [ ] Contar linhas de `selection_bar.py` (deve ser < 200)
- [ ] Contar linhas de `pagination_controls.py` (deve ser < 200)
- [ ] Atualizar FILE_SIZE_LIMIT_RULE.md com novos arquivos
- [ ] Commit: `docs: Atualiza FILE_SIZE_LIMIT_RULE com novos módulos`
- [ ] Atualizar este documento (ARCHITECTURAL_REFACTORING_PLAN.md) com status final
- [ ] Commit: `docs: Marca refatoração arquitetural como completa`

---

## 📊 MÉTRICAS ESPERADAS

### Antes (v3.4.1.1_Stable):
```
main_window.py: 1248 linhas ❌
```

### Depois (v3.5.0_Refactored):
```
main_window.py              : ~180 linhas ✅
display_controller.py       : ~280 linhas ✅
analysis_controller.py      : ~250 linhas ✅
collection_controller.py    : ~120 linhas ✅
selection_controller.py     : ~100 linhas ✅
chips_bar.py                : ~80 linhas ✅
status_bar.py               : ~90 linhas ✅
selection_bar.py            : ~70 linhas ✅
pagination_controls.py      : ~80 linhas ✅

TOTAL: 1250 linhas DISTRIBUÍDAS em 9 arquivos
```

**Benefício**: Cada arquivo tem UMA responsabilidade clara e pode ser modificado/testado isoladamente.

---

## ✔️ CRITÉRIOS DE ACEITAÇÃO

### Por Fase:
- [ ] App roda sem erros
- [ ] Todas as funcionalidades testadas manualmente
- [ ] Nenhum arquivo > limite estabelecido
- [ ] Commit limpo com mensagem descritiva

### Final (Fase 8):
- [ ] `main_window.py` tem < 200 linhas
- [ ] Nenhum controller > 300 linhas
- [ ] Nenhum component > 200 linhas
- [ ] Todos os testes manuais passam:
  - [ ] Filtros (origem, categoria, tag, coleção, busca)
  - [ ] Ordenação (7 opções)
  - [ ] Paginação (next, prev, first, last)
  - [ ] Seleção múltipla (toggle, select all, remove)
  - [ ] Análise IA (single, batch new, batch all)
  - [ ] Descrições (generate new, all)
  - [ ] Coleções (add, remove, create, filter)
  - [ ] Toggles (favorite, done, good, bad)
  - [ ] Modais (project, edit, prepare folders, model settings)

---

## 🔥 SE ALGO QUEBRAR

### Plano de Rollback (por fase):

1. **Identificar último commit funcional** (antes da fase atual)
2. **Git revert** do commit problemático:
   ```bash
   git revert <commit_sha>
   ```
3. **Documentar o problema** neste arquivo (seção ISSUES)
4. **Reanalisar abordagem** antes de tentar novamente

### Commits de Segurança:
- Fase 1: [003d087, 6fe3946, ead652f, f1b3738]
- Fase 2: (aguardando)
- Fase 3: (aguardando)
- Fase 4: (aguardando)
- Fase 5: (aguardando)
- Fase 6: (aguardando)
- Fase 7: (aguardando)
- Fase 8: (aguardando)

---

## 📝 ISSUES ENCONTRADOS

_(Nenhum issue encontrado até o momento)_

---

## ✅ CONCLUSÃO

**Status Geral**: 🔴 EM ANDAMENTO  
**Fases Completas**: 1/8 (12.5%)  
**Linhas Reduzidas**: 0/1048 (0%)  
**Estimativa Total**: 10-15 horas de trabalho  
**Próxima Fase**: FASE 2 - Extrair DisplayController

---

**Última atualização**: 06/03/2026 19:50 BRT  
**Responsável**: Claude Sonnet 4.5
