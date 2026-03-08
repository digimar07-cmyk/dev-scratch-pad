# 🎯 PLANO DE REFATORAÇÃO "TIDY FIRST" - LASERFLIX v3.4.2.6

**Criado em**: 07/03/2026 21:25 BRT  
**Última atualização**: 07/03/2026 21:25 BRT  
**Modelo usado**: Claude Sonnet 4.5  
**Baseado em**: Kent Beck "Tidy First", Simple Design, XP Refactoring

---

## 🚨 PROBLEMA ATUAL

```
Arquivo: ui/main_window.py
Linhas atuais: ~868 linhas
Limite: 200 linhas (FILE_SIZE_LIMIT_RULE.md)
Status: ❌ VIOLAÇÃO CRÍTICA
Excesso: ~668 linhas (434% acima do limite)
```

**Histórico**:
- Tentamos Fases 7C, 7D, 7E, 7F → **FALHARAM** (app quebrou)
- Motivo: Big Bang Refactoring sem incrementalidade
- Resultado: 2 dias de desenvolvimento parado

---

## ✅ FILOSOFIA KENT BECK APLICADA

### 4 Regras de Simple Design:
1. ✅ **Passa todos os testes** (manual OK por agora)
2. ✅ **Sem duplicação** (unificar código repetido)
3. ✅ **Expressa intenção** (nomes claros)
4. ✅ **Mínimo de elementos** (extrair só o necessário)

### Princípios "Tidy First":
- **Tidy First** = Arrumar ANTES de adicionar features
- **Micro-refactorings** = Mudanças de 5-15 minutos cada
- **Não cruzar os raios** = Nunca misturar refatoração + comportamento
- **Commits atômicos** = 1 mudança → 1 commit → 1 teste

---

## 📊 PLANO DEFINITIVO: 868 → 200 LINHAS

### META GERAL

| Fase | Tempo | Redução | Total Linhas | Status |
|------|-------|---------|--------------|--------|
| **Atual** | - | - | 868 | ❌ Violação |
| **Fase 1** | 60 min | -195 | 673 | ⚪ Pendente |
| **Fase 2** | 45 min | -80 | 593 | ⚪ Pendente |
| **Fase 3** | 30 min | -45 | 548 | ⚪ Pendente |
| **Fase 4** | 45 min | -100 | 448 | ⚪ Pendente |
| **Fase 5** | 30 min | -50 | 398 | ⚪ Pendente |
| **META** | - | - | **~400** | 🎯 Objetivo |

**TOTAL**: ~3h 30min para reduzir 470 linhas

---

## 🚀 FASE 1: EXTRAÇÃO CIRÚRGICA (60 MIN)

**Objetivo**: Extrair componentes UI autocontidos  
**Redução**: -195 linhas  
**Risco**: BAIXÍSSIMO

### 1A: Extrair `_update_chips_bar()` (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-chips-bar`

**Passos**:
1. Criar `ui/components/chips_bar.py`
2. Criar classe `ChipsBar` com método `build(parent, filters, callbacks)`
3. Mover lógica completa de `_update_chips_bar()` (50 linhas)
4. Atualizar `main_window.py` para usar componente

**Testar**:
- ✅ Filtros empilháveis funcionam
- ✅ Chips aparecem corretamente
- ✅ Botão "✕" remove filtros
- ✅ "Limpar tudo" funciona

**Commit**: `refactor: extract chips_bar to component (-50 lines)`

**Redução**: **-50 linhas**

---

### 1B: Extrair navegação de paginação (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-pagination`

**Passos**:
1. Criar `ui/components/pagination_controls.py`
2. Criar classe `PaginationControls` com método `build(parent, page_info, callbacks)`
3. Mover botões ⏮ ◀ ▶ ⏭ + combobox de ordenação (80 linhas)
4. Atualizar `main_window.py` para usar componente

**Testar**:
- ✅ Navegação entre páginas funciona
- ✅ Combobox de ordenação muda ordem
- ✅ Botões ficam disabled quando apropriado
- ✅ Label "Pág X/Y" atualiza corretamente

**Commit**: `refactor: extract pagination controls (-80 lines)`

**Redução**: **-80 linhas**

---

### 1C: Extrair barra de seleção múltipla (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-selection-bar`

**Passos**:
1. Criar `ui/components/selection_bar.py`
2. Criar classe `SelectionBar` com método `build(parent, controller)`
3. Mover UI da barra de seleção (40 linhas)
4. Atualizar `main_window.py` para usar componente

**Testar**:
- ✅ Modo seleção ativa/desativa barra
- ✅ Contador "X selecionado(s)" atualiza
- ✅ Botões de ação funcionam
- ✅ Barra aparece/desaparece corretamente

**Commit**: `refactor: extract selection bar UI (-40 lines)`

**Redução**: **-40 linhas**

---

### 1D: Simplificar `display_projects()` - Header (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-display-header`

**Passos**:
1. Criar método privado `_build_display_header(filtered_count, filters_active)`
2. Mover lógica de criação do header (25 linhas)
3. Chamar método no `display_projects()`

**Testar**:
- ✅ Título dinâmico aparece correto
- ✅ Contadores funcionam
- ✅ Layout não quebrou

**Commit**: `refactor: extract display header builder (-25 lines)`

**Redução**: **-25 linhas**

---

### ✅ CHECKPOINT FASE 1

**Tempo total**: 60 minutos  
**Linhas removidas**: 195  
**Arquivo final**: 673 linhas (ainda acima, mas 22% de progresso)  
**Commits**: 4  
**Testes**: Manuais após cada commit

---

## 🔄 FASE 2: CONSOLIDAÇÃO DE CALLBACKS (45 MIN)

**Objetivo**: Reduzir duplicação e agrupar lógica similar  
**Redução**: -80 linhas  
**Risco**: BAIXO

### 2A: Agrupar callbacks de card em dict (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/consolidate-card-callbacks`

**Passos**:
1. Criar método `_build_card_callbacks() -> dict`
2. Mover criação do dict `card_cb` para método
3. Retornar dict completo

**Testar**:
- ✅ Cards renderizam normalmente
- ✅ Todos os callbacks funcionam
- ✅ Nenhum erro de KeyError

**Commit**: `refactor: consolidate card callbacks (-30 lines)`

**Redução**: **-30 linhas**

---

### 2B: Unificar métodos de toggle (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/unify-toggles`

**Passos**:
1. Criar método genérico `_toggle_flag(path, flag_name, btn=None, exclusive=[])`
2. Refatorar `toggle_favorite()`, `toggle_done()`, `toggle_good()`, `toggle_bad()`
3. Cada método agora chama `_toggle_flag()` com parâmetros específicos

**Exemplo**:
```python
def _toggle_flag(self, path, flag, btn=None, exclusive=[]):
    if path not in self.database:
        return
    nv = not self.database[path].get(flag, False)
    self.database[path][flag] = nv
    
    # Exclusividade (ex: good/bad)
    for ex_flag in exclusive:
        if nv:
            self.database[path][ex_flag] = False
    
    self.db_manager.save_database()
    self._invalidate_cache()
    
    if btn:
        # Atualizar UI do botão
        pass

def toggle_good(self, path, btn=None):
    self._toggle_flag(path, "good", btn, exclusive=["bad"])
```

**Testar**:
- ✅ Favoritos funcionam
- ✅ Já Feitos funcionam
- ✅ Bom/Ruim são mutuamente exclusivos
- ✅ Botões atualizam corretamente

**Commit**: `refactor: unify toggle methods (-30 lines)`

**Redução**: **-30 linhas**

---

### 2C: Extrair renderização de cards (15 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-cards-rendering`

**Passos**:
1. Criar método `_render_cards(page_items, callbacks)`
2. Mover loop `for i, (project_path, project_data) in enumerate(page_items)`
3. Chamar método no `display_projects()`

**Testar**:
- ✅ Cards renderizam normalmente
- ✅ Grid mantém layout correto
- ✅ Callbacks funcionam

**Commit**: `refactor: extract cards rendering (-20 lines)`

**Redução**: **-20 linhas**

---

### ✅ CHECKPOINT FASE 2

**Tempo total**: 45 minutos  
**Linhas removidas**: 80  
**Arquivo final**: 593 linhas (32% de progresso total)  
**Commits**: 3

---

## 🧹 FASE 3: LIMPEZA FINAL (30 MIN)

**Objetivo**: Remover código morto e simplificar  
**Redução**: -45 linhas  
**Risco**: MUITO BAIXO

### 3A: Deletar código comentado (10 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/remove-dead-code`

**Passos**:
1. Buscar comentários `# TODO` já resolvidos
2. Remover código comentado antigo
3. Limpar imports não usados (se houver)

**Commit**: `refactor: remove dead code and old comments (-15 lines)`

**Redução**: **-15 linhas**

---

### 3B: Simplificar imports (10 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/simplify-imports`

**Passos**:
1. Agrupar imports relacionados
2. Ordenar alfabeticamente dentro de grupos
3. Remover imports duplicados (se houver)

**Commit**: `refactor: organize and simplify imports (-10 lines)`

**Redução**: **-10 linhas**

---

### 3C: Extrair método `_refresh_ui()` (10 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-refresh-ui`

**Passos**:
1. Criar método `_refresh_ui()`
2. Consolidar padrão repetido:
   ```python
   self._invalidate_cache()
   self.display_projects()
   self.sidebar.refresh(self.database, self.collections_manager)
   ```
3. Substituir todas as ocorrências por `self._refresh_ui()`

**Commit**: `refactor: extract refresh_ui method (-20 lines)`

**Redução**: **-20 linhas**

---

### ✅ CHECKPOINT FASE 3

**Tempo total**: 30 minutos  
**Linhas removidas**: 45  
**Arquivo final**: 548 linhas (37% de progresso total)  
**Commits**: 3

---

## 🏗️ FASE 4: EXTRAÇÃO DE MODAIS (45 MIN)

**Objetivo**: Delegar lógica de modais para manager  
**Redução**: -100 linhas  
**Risco**: MÉDIO

### 4A: Expandir DialogManager com ModalManager (45 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/extract-modal-logic`

**Passos**:
1. Expandir `ui/managers/dialog_manager.py`
2. Adicionar métodos:
   - `open_project_modal(window, project_path, ...)`
   - `open_edit_modal(window, project_path, ...)`
   - `handle_modal_toggle(window, path, key, value)`
   - `handle_modal_generate_desc(window, path, ...)`
3. Refatorar `main_window.py` para delegar

**Testar**:
- ✅ Modal de projeto abre normalmente
- ✅ Modal de edição funciona
- ✅ Toggles no modal funcionam
- ✅ Geração de descrição funciona
- ✅ Navegação entre projetos funciona

**Commit**: `refactor: extract modal logic to ModalManager (-100 lines)`

**Redução**: **-100 linhas**

---

### ✅ CHECKPOINT FASE 4

**Tempo total**: 45 minutos  
**Linhas removidas**: 100  
**Arquivo final**: 448 linhas (48% de progresso total)  
**Commits**: 1

---

## 🤖 FASE 5: EXTRAÇÃO DE ANÁLISE (30 MIN)

**Objetivo**: Internalizar UI de análise no controller  
**Redução**: -50 linhas  
**Risco**: MÉDIO

### 5A: Mover UI de progresso para AnalysisController (30 min)

**Status**: ⚪ Pendente  
**Branch**: `refactor/internalize-progress-ui`

**Passos**:
1. Modificar `ui/controllers/analysis_controller.py`
2. Internalizar métodos:
   - `show_progress_ui()` → `_show_progress()`
   - `hide_progress_ui()` → `_hide_progress()`
   - `update_progress()` → `_update_progress()`
3. Controller gerencia própria UI de progresso
4. Remover callbacks de `main_window.py`

**Testar**:
- ✅ Progress bar aparece durante análise
- ✅ Percentual atualiza corretamente
- ✅ Botão "Parar" funciona
- ✅ Progress bar desaparece ao finalizar

**Commit**: `refactor: internalize progress UI in AnalysisController (-50 lines)`

**Redução**: **-50 linhas**

---

### ✅ CHECKPOINT FASE 5

**Tempo total**: 30 minutos  
**Linhas removidas**: 50  
**Arquivo final**: 398 linhas (54% de progresso total)  
**Commits**: 1

---

## 📊 RESULTADO FINAL

### Resumo Geral:

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Linhas** | 868 | ~398 | **-54%** |
| **Tempo** | - | 3h 30min | Investimento |
| **Commits** | - | 12 | Incrementais |
| **Risco** | Alto | Controlado | Micro-steps |
| **Status** | ❌ Violação | ✅ Próximo limite | Progresso |

**OBS**: Meta de 200 linhas requer refatoração adicional (controllers, etc), mas 398 já é **ENORME progresso** e permite desenvolvimento seguro.

---

## 🔒 PROTOCOLO DE EXECUÇÃO

### Para CADA micro-refactoring:

```bash
# 1. Criar branch
git checkout -b refactor/nome-da-tarefa

# 2. Fazer UMA mudança pequena (10-15 min)
# ... código ...

# 3. Testar MANUALMENTE
python main.py
# Testar funcionalidade afetada

# 4. Se funciona:
git add .
git commit -m "refactor: descrição clara (-X lines)"
git push origin refactor/nome-da-tarefa

# 5. Se quebrou:
git reset --hard HEAD
# Tentar abordagem diferente

# 6. Merge e próxima
git checkout main
git merge refactor/nome-da-tarefa
```

---

## ⚠️ REGRAS ABSOLUTAS

### Durante refatoração:

1. ❌ **NÃO adicionar features** - Apenas mover código
2. ❌ **NÃO mudar comportamento** - Apenas estrutura
3. ❌ **NÃO fazer commits grandes** - Máximo 100 linhas por commit
4. ✅ **SEMPRE testar após cada commit** - Manual OK
5. ✅ **SEMPRE usar branches** - Facilita rollback
6. ✅ **SEMPRE commitar com mensagem clara** - Facilita git log

### Após cada fase:

1. ✅ Atualizar este arquivo com status
2. ✅ Registrar linhas reais removidas
3. ✅ Documentar problemas encontrados
4. ✅ Commit de checkpoint

---

## 📝 LOG DE PROGRESSO

### 07/03/2026 21:25 BRT
- ✅ Plano criado
- ✅ Documentação antiga arquivada
- ⚪ Aguardando início da execução

---

## 🎯 PRÓXIMO PASSO

**Começar FASE 1A** → Extrair `chips_bar.py`

**Comando**:
```bash
git checkout -b refactor/extract-chips-bar
```

---

**Modelo usado**: Claude Sonnet 4.5  
**Filosofia**: Kent Beck "Tidy First" + Simple Design  
**Garantia**: Micro-refactorings seguros e incrementais
