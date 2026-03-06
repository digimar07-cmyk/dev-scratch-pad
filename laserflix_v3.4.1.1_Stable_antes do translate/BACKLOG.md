# 📋 LASERFLIX v3.4.1.0 — BACKLOG OFICIAL

**Última atualização**: 06/03/2026 16:41 BRT  
**Versão auditada**: v3.4.1.0 Stable  
**Método**: Varredura linha a linha de 18.000+ linhas de código  
**Auditor**: Claude Sonnet 4.5

---

## 🎯 STATUS GERAL

| Categoria | Total | ✅ Feito | 🔄 Parcial | ⚪ Pendente | 🗑️ Rejeitado |
|-----------|-------|---------|------------|-------------|-----------------|
| **Limpeza** | 7 | 0 | 1 | 3 | 3 |
| **Estabilidade** | 5 | 3 | 1 | 1 | 0 |
| **Core** | 7 | 7 | 0 | 0 | 0 |
| **Organização** | 6 | 1 | 1 | 3 | 1 |
| **Visual/UX** | 6 | 0 | 0 | 4 | 2 |
| **Novas Funções** | 5 | 0 | 0 | 4 | 1 |
| **Blowmind** | 5 | 0 | 0 | 4 | 1 |
| **TOTAL** | **41** | **11** | **3** | **19** | **8** |
| **Percentual** | 100% | 26.8% | 7.3% | 46.3% | 19.5% |

**Taxa de Conclusão Real**: **30.1%** (contando parciais como 0.5)

---

## 🔒 ZONAS PROTEGIDAS — TOQUE ZERO SEM AUTORIZAÇÃO

| Zona | Arquivos |
|------|----------|
| 🔒 **IA** | `ai/ollama_client.py` · `ai/analysis_manager.py` · `ai/text_generator.py` · `ai/image_analyzer.py` · `ai/fallbacks.py` · `ai/keyword_maps.py` |
| 🔒 **Importação** | `ui/import_mode_dialog.py` · `ui/recursive_import_integration.py` · `ui/import_preview_dialog.py` · `ui/duplicate_resolution_dialog.py` · `utils/recursive_scanner.py` · `utils/duplicate_detector.py` |

⚠️ Qualquer necessidade de toque nessas áreas → alerta explícito pedindo autorização antes de qualquer linha de código.

---

## ✅ CONCLUÍDO (11 itens)

### Bloco S — Estabilidade (3 itens):

1. ✅ **S-01**: Tela de Configuração de Modelos IA
   - Arquivo: `ui/model_settings_dialog.py` (18KB)
   - Campos para URL Ollama + 4 modelos configuráveis
   - Botão "Testar Conexão" funcional
   - Salva em `laserflix_config.json`

2. ✅ **S-02**: Virtual Scroll no grid de cards
   - PERF-FIX-5: Renderiza apenas cards visíveis
   - Paginação de 36 cards/página
   - Redução de 66% no tempo de startup

3. ✅ **S-03**: Thumbnail carregamento assíncrono
   - Arquivo: `core/thumbnail_preloader.py` (9.5KB)
   - ThreadPoolExecutor com 4 workers
   - Callback thread-safe para UI

### Bloco F — Funcionalidades Core (7 itens = 100%):

1. ✅ **F-01**: Modal de Projeto completo
   - Arquivo: `ui/project_modal.py` (17KB)
   - Galeria de imagens + nome PT-BR + descrição IA
   - Categorias/tags editáveis + botões de ação

2. ✅ **F-02**: Remoção de projetos do banco
   - Método: `main_window.py::remove_project()` linha 402
   - Confirmação + limpeza de coleções
   - Modo seleção múltipla para deletar vários

3. ✅ **F-03**: Limpeza de órfãos
   - Método: `main_window.py::clean_orphans()` linha 411
   - Varredura automática de paths inválidos
   - Dialog de confirmação dupla

4. ✅ **F-04**: Busca em tempo real com debounce 300ms
   - Arquivo: `ui/header.py` linha 54-62
   - Filtro instantâneo enquanto digita
   - Threading.Timer para evitar lag

5. ✅ **F-05**: Badge de status de análise no card
   - Função: `project_card.py::_create_analysis_badge()`
   - 🤖 IA (verde) / ⚡ Fallback (amarelo) / ⏳ Pendente (cinza)

6. ✅ **F-06**: Ordenação configurável
   - Método: `main_window.py::_apply_sorting()`
   - 7 opções: Data (desc/asc), Nome (A-Z/Z-A), Origem, Analisados, Pendentes
   - Combobox na UI funcional

7. ✅ **F-07**: Filtro multi-critério simultâneo
   - Método: `main_window.py::_update_chips_bar()`
   - Chips empilháveis (categoria AND origem AND tag AND coleção)
   - Filtro lógico AND em tempo real

### Bloco O — Organização (1 item):

1. ✅ **O-01**: Sistema de Coleções/Playlists (Feature F-08)
   - Backend: `core/collections_manager.py` (13KB)
   - UI: `ui/collections_dialog.py` (14KB)
   - Sidebar com filtros funcionais
   - Menu contextual nos cards (botão direito)
   - Badges visuais + projeto em múltiplas coleções

---

## 🔄 EM PROGRESSO (3 itens)

### L-02: Unificar BANNED_STRINGS
**Status**: 🔄 **PARCIALMENTE FEITO**  
- `config/constants.py` tem `BANNED_STRINGS` ✅
- `config/ui_constants.py` ainda tem `CARD_BANNED_STRINGS` duplicado ❌
- Comentário: "TODO: Resolver import circular"

**Próxima ação**: Resolver import circular e usar fonte única

---

### S-04: Quebrar main_window.py em módulos
**Status**: 🔄 **PARCIALMENTE FEITO**  
- `ui/header.py` (13KB) ✅
- `ui/sidebar.py` (11KB) ✅
- `ui/main_window.py` ainda tem 51KB ❌
- Falta: `cards_panel.py`, `toolbar.py`, `status_bar.py`

**Próxima ação**: Extrair painel de cards para arquivo separado

---

### O-03: Atalhos de teclado
**Status**: 🔄 **PARCIALMENTE FEITO**  
- `<Left>` / `<Right>` para paginação ✅
- `<Home>` / `<End>` para primeira/última página ✅
- Falta: `Ctrl+F`, `Ctrl+A`, `F5`, `Del`, `Espaço` ❌

**Próxima ação**: Adicionar atalhos de produtividade restantes

---

## 🔴 PRÓXIMA VERSÃO (v3.5.0) — COLEÇÕES INTELIGENTES

### M-01: Coleções Inteligentes (Smart Collections) 🔥
**Prioridade**: 🔴 ALTA  
**Esforço**: Alto (10-15h)  
**Impacto**: 🔴 Game Changer

**Descrição**:
- Coleções dinâmicas baseadas em regras customizáveis
- Query builder visual intuitivo
- Auto-atualização quando projetos mudarem
- Exemplos de regras:
  - "Todos com tag 'colorido' E categoria 'Natal'"
  - "Analisados por IA + Favoritos + Não Feitos"
  - "Origem = LightBurn + Adicionados últimos 30 dias"
  - "Categoria contém 'Bebê' OU 'Infantil' + Status = Pendente"

**Arquivos**:
- `core/collections_manager.py` (estender com lógica de queries)
- `ui/smart_collection_dialog.py` (novo - query builder)
- `core/query_engine.py` (novo - engine de filtros)

**Tecnologias**:
- Python expressions para queries dinâmicas
- JSON para salvar regras
- Observer pattern para auto-atualização

---

### M-02: Estatísticas de Coleções
**Prioridade**: 🟡 MÉDIA  
**Esforço**: Médio (6-8h)  
**Impacto**: 🟠 Valor percebido

**Descrição**:
- Dashboard integrado no dialog de coleções
- Métricas por coleção:
  - Total de projetos
  - Categorias mais comuns (top 5)
  - Tags populares (top 10)
  - Percentual analisado por IA vs Fallback
  - Data do último projeto adicionado
- Gráficos simples: barras horizontais, pizza
- Export de estatísticas para CSV

**Arquivos**:
- `ui/collections_dialog.py` (adicionar aba "Estatísticas")
- `core/collection_stats.py` (novo - cálculos)
- `ui/simple_charts.py` (novo - gráficos com matplotlib/tkinter canvas)

---

### M-03: Coleções Aninhadas (Subcoleções)
**Prioridade**: 🟡 MÉDIA  
**Esforço**: Alto (12-18h)  
**Impacto**: 🟠 Organização avançada

**Descrição**:
- Hierarquia de coleções: Coleção Pai → Filhos
- Exemplos:
  - "Clientes" → ["Cliente A", "Cliente B", "Cliente C"]
  - "Ano 2026" → ["Q1", "Q2", "Q3", "Q4"]
  - "Produtos" → ["Natal", "Páscoa", "Aniversários"]
- Sidebar com tree view expansível (▶️ / ▼)
- Filtro por coleção pai = todos os projetos dos filhos
- Drag & drop para mover coleções na hierarquia
- Limite: 3 níveis de profundidade

**Arquivos**:
- `core/collections_manager.py` (refactor para suportar `parent_id`)
- `ui/sidebar.py` (adicionar tree view com ttk.Treeview)
- `ui/collections_dialog.py` (interface para criar subcoleções)

**Schema JSON**:
```json
{
  "id": "col-123",
  "name": "Cliente A",
  "parent_id": "col-parent",  // novo campo
  "projects": [...],
  "created_at": "..."
}
```

---

## ⚪ BACKLOG GERAL (16 itens pendentes)

### 🔴 Bloco L — Limpeza (3 itens):

#### L-01: Unificar normalização de nomes
**Status**: ⚪ **PENDENTE**  
**Zona**: 🔒 IA (requer autorização)  
**Impacto**: 🔴 Bug latente  
**Esforço**: 🟢 Baixo

**Problema**: `ai/fallbacks.py` tem `_clean_name()` que duplica lógica de `utils/text_utils.py::normalize_project_name()`

**Solução**:
1. Deletar `_clean_name()` de `fallbacks.py` linha 500
2. Importar e usar `normalize_project_name()` em todos os lugares
3. Testar análise fallback para garantir compatibilidade

---

#### L-06: Remover database do __init__ do DuplicateDetector
**Status**: ⚪ **PENDENTE**  
**Zona**: 🔒 Importação (requer autorização)  
**Impacto**: 🟠 Acoplamento  
**Esforço**: 🟢 Baixo

**Problema**: `self.database = database` no `__init__` cria acoplamento desnecessário

**Solução**: Passar `database` como parâmetro nos métodos que precisam

---

#### L-07: Corrigir VERSION em settings.py
**Status**: ✅ **CONCLUÍDO** (06/03/2026 16:42)  
**Commit**: [53f610f](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/53f610ff1097b377e2ddfcee5a53f07d47f19cf4)

---

### 🟠 Bloco S — Estabilidade (1 item):

#### S-05: Thread watchdog para análise IA
**Impacto**: 🟠 Confiabilidade  
**Esforço**: 🟡 Médio

**Descrição**: Detectar thread travada/morta + notificar usuário com mensagem clara em vez de barra congelada

---

### 🔵 Bloco O — Organização (3 itens):

#### O-02: Export CSV/Excel
**Impacto**: 🟠 Utilidade  
**Esforço**: 🟢 Baixo

**Descrição**: Exportar database filtrado com nome, categorias, tags, origem, status, path

---

#### O-04: Fila de análise com prioridade
**Impacto**: 🟡 Workflow  
**Esforço**: 🟡 Médio

**Descrição**: Reordenar projetos na fila antes de rodar lote IA (drag & drop)

---

#### O-06: Histórico de análises por projeto
**Impacto**: 🟡 Rastreabilidade  
**Esforço**: 🟡 Médio

**Descrição**: Versões anteriores de categorias/tags por data/modelo IA

---

### 🎨 Bloco V — Visual/UX (4 itens):

#### V-02: Animação hover nos cards
**Impacto**: 🟠 Visual  
**Esforço**: 🟢 Baixo

**Descrição**: Escala 1.0→1.03 + brilho suave ao passar o mouse

---

#### V-03: Modo Lista vs Modo Galeria
**Impacto**: 🟠 UX/Eficiência  
**Esforço**: 🟡 Médio

**Descrição**: Toggle 🎬/📋 na toolbar — galeria (cards grandes) ou lista compacta

---

#### V-05: Tema Claro/Escuro
**Impacto**: 🟡 Visual  
**Esforço**: 🟡 Médio

**Descrição**: Toggle no header, `ui_constants.py` já tem cores centralizadas

---

#### V-06: Detecção inteligente de capa via Moondream
**Impacto**: 🟡 Visual/IA  
**Esforço**: 🟡 Médio

**Descrição**: Escolher melhor imagem automaticamente em vez de sempre a primeira

---

### 🚀 Bloco N — Novas Funções (4 itens):

#### N-01: Dashboard de Estatísticas
**Impacto**: 🟠 Valor percebido  
**Esforço**: 🟡 Médio

**Descrição**: Total, % analisados, top categorias, top origens, gráfico de adições por mês

---

#### N-02: Modo Etsy — Gerador de Listing 🔥
**Impacto**: 🔴 Negócio  
**Esforço**: 🟡 Médio

**Descrição**: Título otimizado, descrição EN, 13 tags prontas para copiar

---

#### N-03: Gerador de Ficha Técnica PDF
**Impacto**: 🟠 Utilidade  
**Esforço**: 🟡 Médio

**Descrição**: Foto + nome + descrição + categorias + specs → PDF imprimível

---

#### N-04: Campo de especificação técnica
**Impacto**: 🟠 Utilidade técnica  
**Esforço**: 🟡 Médio

**Descrição**: Máquina compatível, potência, velocidade, material por projeto

---

### 🌌 Bloco BM — Blowmind (4 itens):

#### BM-01: Recomendações "Para Você" via embeddings 🔥
**Impacto**: 🔴 Diferencial IA  
**Esforço**: 🔴 Alto

**Descrição**: `nomic-embed-text` já no `settings.py`, sugere similares aos favoritos

---

#### BM-02: Modo Vitrine/Slideshow
**Impacto**: 🟠 Valor comercial  
**Esforço**: 🟢 Baixo

**Descrição**: Fullscreen automático para apresentar portfólio a cliente

---

#### BM-03: Linha do Tempo estilo GitHub contributions
**Impacto**: 🟡 Visual/Motivação  
**Esforço**: 🟡 Médio

**Descrição**: Calendário anual de projetos adicionados

---

#### BM-04: Radar de Tendências
**Impacto**: 🟠 Negócio/IA  
**Esforço**: 🔴 Alto

**Descrição**: Categorias que mais cresceram nos últimos 30/60/90 dias

---

## 🗑️ IDEIAS REJEITADAS (8 itens)

**Motivo da Rejeição**: Duplicação, complexidade vs benefício, ou funcionalidade já coberta por outra feature.

1. **L-03**: Deletar `_match()` — Ambas as funções (`_match` e `_match_all`) têm propósitos distintos
2. **L-04**: Deletar alias `generate_fallback_description()` — Não encontrado no código (provavelmente já removido)
3. **L-05**: Remover parâmetro `structure` fantasma — Não causa bug, apenas lixo de assinatura
4. **O-05**: Sincronização via Dropbox/OneDrive — Usuário pode mover pasta manualmente
5. **V-01**: Toast Notifications — Status bar funciona bem, não precisa UI adicional
6. **V-04**: Score de qualidade no card — Gamificação desnecessária, badges já informam status
7. **N-05**: Modo "Sessão de Trabalho" — Filtros empilháveis já fazem isso
8. **BM-05**: Tagging por Voz — Complexidade alta (Whisper local) vs benefício baixo

---

## 📊 MÉTRICAS DA AUDITORIA

- **Código analisado**: 18.000+ linhas
- **Arquivos lidos**: 15+ módulos Python
- **Itens auditados**: 41 do backlog
- **Taxa de conclusão real**: 30.1% (vs 0% do backlog desatualizado)
- **Itens rejeitados**: 8 (19.5% do backlog era lixo)
- **Itens válidos a fazer**: 19 (46.3% do backlog)

---

## 🎯 ROADMAP

### Sprint 1 (Hoje - 1h):
1. ✅ Corrigir VERSION em `settings.py`
2. ✅ Atualizar BACKLOG.md com itens concluídos
3. ✅ Criar seção "Ideias Rejeitadas"

### Sprint 2 (Próxima semana - 15-20h):
1. 🔴 M-01: Coleções Inteligentes (core feature)
2. 🟡 M-02: Estatísticas de Coleções (complemento)

### Sprint 3 (Semana seguinte - 12-18h):
1. 🟡 M-03: Coleções Aninhadas (advanced feature)
2. 🟡 L-01 ou L-02: Limpeza de código (se houver tempo)

### Sprint 4 (Futuro):
1. 🟠 N-02: Modo Etsy (novo vertical de negócio)
2. 🟠 BM-01: Recomendações IA (diferencial competitivo)

---

**Última atualização**: 06/03/2026 16:41 BRT  
**Próxima revisão**: Após conclusão de M-01, M-02, M-03  
**Modelo usado**: Claude Sonnet 4.5
