# Arquitetura Modular v7.5.0

## Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────────┐
│                     laserflix_v750_modular.py                    │
│                         (Entry Point)                             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             v
              ┌──────────────────────────────┐
              │      LaserflixApp.__init__    │
              │  - Carrega config/database    │
              │  - Inicializa HTTP session    │
              │  - Cria UI                    │
              └──────────────┬───────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         v                   v                   v
  ┌──────────┐        ┌──────────┐       ┌──────────┐
  │   core   │        │  ollama  │       │   data   │
  └──────────┘        └──────────┘       └──────────┘
         │                   │                   │
         v                   v                   v
  config.py           ollama_client.py    persistence.py
  logging_setup.py    vision.py           (save/load)

                             │
         ┌───────────────────┼───────────────────┐
         v                   v                   v
  ┌──────────┐        ┌──────────┐       ┌──────────┐
  │ analysis │        │  batch   │       │  images  │
  └──────────┘        └──────────┘       └──────────┘
         │                   │                   │
         v                   v                   v
  analyzer.py         batch_analyzer.py   image_handler.py
  description_.py     batch_description.  (thumbnails)
  fallback.py
  structure.py

                             │
         ┌───────────────────┼───────────────────┐
         v                   v                   v
  ┌──────────┐        ┌──────────┐       ┌──────────┐
  │ actions  │        │    ui    │       │  (user)  │
  └──────────┘        └──────────┘       └──────────┘
         │                   │
         v                   v
  toggles.py          main_window.py
  file_operations.py  sidebar.py
  scanning.py         project_grid.py
                      project_modal.py
                      dashboard.py
                      progress_ui.py
```

## Dependências entre Módulos

### Nível 0 (Zero dependências)
- `core/config.py`
- `core/logging_setup.py`

### Nível 1 (Dependem apenas de core)
- `ollama/ollama_client.py` → `core/config`
- `data/persistence.py` → `core/config`
- `images/image_handler.py` → (sem dependências core)

### Nível 2
- `ollama/vision.py` → `ollama/ollama_client`
- `analysis/structure.py` → (standalone)
- `analysis/fallback.py` → `analysis/structure`

### Nível 3
- `analysis/analyzer.py` → `ollama/*`, `analysis/structure`, `analysis/fallback`, `images/image_handler`
- `analysis/description_generator.py` → `ollama/*`, `analysis/structure`, `analysis/fallback`, `images/image_handler`

### Nível 4
- `batch/batch_analyzer.py` → `analysis/analyzer`, `data/persistence`, `ui/progress_ui`
- `batch/batch_description.py` → `analysis/description_generator`, `data/persistence`, `ui/progress_ui`

### Nível 5 (UI)
- `ui/progress_ui.py` → (standalone)
- `ui/model_settings.py` → `data/persistence`
- `actions/toggles.py` → `data/persistence`
- `actions/file_operations.py` → (standalone)
- `actions/scanning.py` → `analysis/structure`, `data/persistence`

### Nível 6 (UI high-level)
- `ui/sidebar.py` → `actions/*`, `ui/project_grid`
- `ui/project_grid.py` → `actions/scanning`, `images/image_handler`, `ui/project_modal`
- `ui/dashboard.py` → (standalone UI)

### Nível 7 (Top-level UI)
- `ui/project_modal.py` → `images/*`, `actions/*`, `analysis/description_generator`, `data/persistence`
- `ui/main_window.py` → `ui/*`, `batch/*`, `actions/scanning`, `data/persistence`

### Nível 8 (Entry point)
- `laserflix_v750_modular.py` → `core/*`, `ollama/ollama_client`, `images/image_handler`, `data/persistence`, `ui/main_window`

## Princípios Arquiteturais

### 1. Separação de Responsabilidades
- **core**: Configuração e infraestrutura
- **ollama**: Comunicação com IA
- **analysis**: Lógica de análise
- **batch**: Processamento em lote
- **data**: Persistência
- **images**: Gerenciamento de imagens
- **actions**: Ações do usuário
- **ui**: Interface gráfica

### 2. Injeção de Dependências
Todos os módulos recebem `app` como parâmetro, permitindo acesso ao estado global sem acoplar.

### 3. Single Responsibility
Cada arquivo tem um propósito único e claro.

### 4. Open/Closed
Módulos abertos para extensão (novos analisadores), fechados para modificação (core estável).

## Padrões de Design Utilizados

### Factory Pattern
- `_choose_text_role()`: Seleciona modelo baseado em contexto

### Strategy Pattern  
- Múltiplos analisadores (IA vs fallback)
- Múltiplos modelos Ollama configuráveis

### Observer Pattern
- Callbacks de UI atualizam sidebar/grid após mudanças

### Cache Pattern
- LRU cache para thumbnails
- Health check cache para Ollama

### Template Method
- `run_analysis()` e `run_description_generation()` compartilham estrutura

## Performance

### Otimizações Implementadas
1. **HTTP Session Reutilizável**: Reduz overhead de conexão
2. **Cache de Thumbnails**: LRU com 300 itens
3. **Health Check Cache**: 5s de cache para Ollama availability
4. **Lazy Loading**: Módulos carregam sob demanda
5. **Threading**: Análises em batch não bloqueiam UI

### Métricas
- Tempo de inicialização: < 2s
- Renderização de grid (100 projetos): < 500ms
- Análise individual (modelo qualidade): ~8s
- Análise em lote (modelo rápido, 50 projetos): ~3min

## Segurança

1. **Salvamento Atômico**: Evita corrupção de dados
2. **Backups Automáticos**: Proteção contra perda
3. **Rotação de Backups**: Evita acumulação de arquivos
4. **Validação de Entrada**: Sanitização de paths e JSON

---

**Última atualização:** 2026-02-27
