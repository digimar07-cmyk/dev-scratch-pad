# LASERFLIX v3.0 🎬

**Arquitetura Modular** - Gestão de projetos de corte laser com IA

---

## 🎯 Visão Geral

O Laserflix v3.0 é uma refatoração completa do v7.4.0, transformando um monolito de 2500+ linhas em uma arquitetura modular, escalável e testável.

### ✨ Principais Mudanças

- **Modularização completa**: Código organizado em pacotes semânticos
- **Separação de responsabilidades**: Core, AI, UI em módulos independentes
- **Manutenção facilitada**: Cada classe tem uma responsabilidade única
- **Testes unitários viáveis**: Módulos desacoplados permitem testes isolados
- **Extensão simples**: Adicionar features sem modificar código existente

---

## 📁 Estrutura de Arquivos

```
laserflix_v3.0/
├── main.py                          # Entry point
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Configurações (modelos, paths, timeouts)
│   └── constants.py                 # Constantes de UI (cores, fontes)
├── core/
│   ├── __init__.py
│   ├── database.py                  # Persistência JSON com backup atômico
│   ├── project_scanner.py           # Scan de pastas + análise estrutural
│   └── thumbnail_cache.py           # Cache LRU de thumbnails
├── ai/
│   ├── __init__.py
│   ├── ollama_client.py             # Cliente HTTP Ollama (texto + visão)
│   ├── image_analyzer.py            # Qualidade de imagem + moondream
│   ├── text_generator.py            # Análise (categorias/tags) + descrições
│   └── fallbacks.py                 # Fallbacks sem IA
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Janela principal (orquestrador)
│   ├── sidebar.py                   # Sidebar de filtros
│   ├── project_card.py              # Card individual de projeto
│   ├── project_modal.py             # Modal de detalhes
│   ├── edit_modal.py                # Modal de edição
│   ├── dashboard.py                 # Dashboard de estatísticas
│   └── progress_ui.py               # Barra de progresso + stop button
└── utils/
    ├── __init__.py
    ├── logging_setup.py             # Sistema de logs com rotação
    └── platform_utils.py            # Abrir pasta/imagem (multiplataforma)
```

---

## 🔧 Instalação

### Pré-requisitos

```bash
python >= 3.8
Ollama (rodando localmente em http://localhost:11434)
```

### Dependências

```bash
pip install pillow requests
```

### Modelos Ollama Necessários

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M   # Análise de qualidade
ollama pull qwen2.5:3b-instruct-q4_K_M   # Análise rápida (lotes grandes)
ollama pull moondream:latest              # Visão (análise de imagens)
ollama pull nomic-embed-text:latest       # Embeddings (reservado)
```

---

## 🚀 Uso

```bash
cd laserflix_v3.0
python main.py
```

---

## 🧩 Arquitetura

### 📦 Pacote `config/`

**Responsabilidade**: Configurações centralizadas

- **`settings.py`**: Modelos Ollama, timeouts, paths, limites de cache
- **`constants.py`**: Paleta de cores, fontes, dimensões de UI

### 📦 Pacote `core/`

**Responsabilidade**: Lógica de negócio central (sem IA, sem UI)

- **`database.py`**: 
  - `DatabaseManager`: Persistência JSON com salvamento atômico
  - Auto-backup com limpeza de arquivos antigos
  - Migração de compatibilidade (v7.4.0 → v3.0)

- **`project_scanner.py`**:
  - `ProjectScanner`: Escaneia pastas, detecta novos projetos
  - Análise estrutural (tipos de arquivo, subpastas, estatísticas)
  - Extração de tags do nome (remove SKUs, stopwords)
  - Detecção de origem (Creative Fabrica, Etsy)

- **`thumbnail_cache.py`**:
  - `ThumbnailCache`: Cache LRU (Least Recently Used)
  - Valida mtime (detecta arquivos modificados)
  - Auto-limpeza quando excede limite (300 imagens)

### 🤖 Pacote `ai/`

**Responsabilidade**: Integração com Ollama e análise com IA

- **`ollama_client.py`**:
  - `OllamaClient`: Cliente HTTP robusto
  - Health check com cache de 5s
  - Retry automático com backoff
  - `generate_text()`: usa `/api/chat` (Qwen2.5-Instruct)
  - `describe_image()`: usa `/api/generate` com base64 (moondream)

- **`image_analyzer.py`**:
  - `ImageAnalyzer`: Avalia qualidade de imagens
  - Métricas: brilho, saturação, % pixels brancos
  - Filtro de qualidade evita alucinações do moondream
  - Critérios de rejeição:
    - Brilho > 210 (fundo branco dominante)
    - Saturação < 25 (quase monocromática)
    - Pixels brancos > 50% (mockup ambíguo)

- **`text_generator.py`**:
  - `TextGenerator`: Gera análises e descrições
  - `analyze_project()`: categorias + tags (com visão integrada)
  - `generate_description()`: descrições comerciais
  - Hierarquia: **NOME** (1°) → **VISÃO** (2°, complementar)
  - Seleção automática de modelo (fast/quality baseado em batch_size)

- **`fallbacks.py`**:
  - `FallbackGenerator`: Sistema sem IA
  - Baseado em keywords e templates
  - 7 cenários contextuais (cabide, espelho, calendário, etc)
  - Usado quando Ollama está indisponível

### 🖥️ Pacote `ui/`

**Responsabilidade**: Interface Tkinter modular

- **`main_window.py`**:
  - `LaserflixMainWindow`: Orquestrador da aplicação
  - Inicializa todos os módulos (core + ai + ui)
  - Header: logo, busca, botões de ação
  - Sidebar: filtros (categorias, tags, origens, status)
  - Content area: grid de projetos (5 colunas)
  - Análise em lote com threading
  - Auto-backup agendado (30 min)

- **`sidebar.py`** *(TODO)*: Componente de sidebar isolado
- **`project_card.py`** *(TODO)*: Card de projeto reutilizável
- **`project_modal.py`** *(TODO)*: Modal de detalhes full-screen
- **`edit_modal.py`** *(TODO)*: Modal de edição de metadados
- **`dashboard.py`** *(TODO)*: Dashboard de estatísticas
- **`progress_ui.py`** *(TODO)*: Barra de progresso + botão stop

### 🛠️ Pacote `utils/`

**Responsabilidade**: Utilitários gerais

- **`logging_setup.py`**: Logger global com RotatingFileHandler (5MB, 3 backups)
- **`platform_utils.py`**: Funções multiplataforma (Windows, macOS, Linux)
  - `open_folder()`: Abre pasta no gerenciador de arquivos
  - `open_image()`: Abre imagem no visualizador padrão

---

## 🧰 Fluxo de Dados

```
1. USER adiciona pastas
   ↓
2. ProjectScanner escaneia e detecta novos projetos
   ↓
3. DatabaseManager salva metadados básicos
   ↓
4. USER inicia análise em lote
   ↓
5. TextGenerator para cada projeto:
   a. ProjectScanner.analyze_project_structure()
   b. ImageAnalyzer.analyze_cover() (se imagem passa no filtro)
   c. OllamaClient.generate_text() (categorias + tags)
   d. FallbackGenerator (se Ollama falhar)
   ↓
6. DatabaseManager salva resultados
   ↓
7. MainWindow atualiza UI (grid + filtros)
```

---

## 🎯 Princípios de Design

### Single Responsibility Principle (SRP)

Cada classe tem **uma única responsabilidade**:

- `DatabaseManager`: Apenas persistência
- `OllamaClient`: Apenas comunicação HTTP com Ollama
- `ImageAnalyzer`: Apenas análise de qualidade de imagens
- `TextGenerator`: Apenas geração de texto com IA

### Dependency Injection

Módulos recebem dependências via construtor:

```python
image_analyzer = ImageAnalyzer(ollama_client)
text_generator = TextGenerator(ollama_client, image_analyzer, project_scanner)
```

Benefícios:
- **Testável**: Pode injetar mocks
- **Flexível**: Pode trocar implementações
- **Desacoplado**: Módulos não conhecem implementações concretas

### Separation of Concerns

- **Core**: Lógica de negócio pura (sem IA, sem UI)
- **AI**: Integração com Ollama isolada
- **UI**: Interface Tkinter separada da lógica

---

## ✅ Funcionalidades Implementadas

- [x] Scan automático de pastas
- [x] Análise estrutural de projetos
- [x] Análise com IA (Qwen2.5 + moondream)
- [x] Sistema de fallback (sem IA)
- [x] Cache LRU de thumbnails
- [x] Persistência JSON com backup atômico
- [x] Auto-backup agendado (30 min)
- [x] Filtros: categorias, tags, origens, status, busca
- [x] Detecção de origem (Creative Fabrica, Etsy)
- [x] Extração inteligente de tags
- [x] Sistema de logs com rotação
- [x] Suporte multiplataforma (Windows, macOS, Linux)
- [x] Análise em lote com threading
- [x] Health check do Ollama com cache
- [x] Filtro de qualidade para visão

---

## 🚧 TODO (Próximos Commits)

- [ ] `ui/sidebar.py`: Componente de sidebar isolado
- [ ] `ui/project_card.py`: Card de projeto reutilizável
- [ ] `ui/project_modal.py`: Modal de detalhes full-screen
- [ ] `ui/edit_modal.py`: Modal de edição
- [ ] `ui/dashboard.py`: Dashboard de estatísticas
- [ ] `ui/progress_ui.py`: Barra de progresso animada
- [ ] Testes unitários (pytest)
- [ ] Testes de integração
- [ ] Documentação de API (docstrings completos)

---

## 📝 Diferenças v7.4.0 → v3.0

| Aspecto | v7.4.0 | v3.0 |
|---------|--------|------|
| **Arquitetura** | Monolito (1 arquivo) | Modular (20 arquivos) |
| **Linhas de código** | 2500+ linhas | ~150-300 linhas/arquivo |
| **Testabilidade** | Impossível | Alta (módulos desacoplados) |
| **Manutenção** | Difícil (tudo acoplado) | Fácil (SRP, DI) |
| **Extensão** | Arriscada (side effects) | Segura (OCP) |
| **Dependências** | Globais implícitas | Injetadas explicitamente |
| **Configuração** | Hardcoded | Centralizada (settings.py) |
| **UI** | Acoplada à lógica | Separada (ui/) |

---

## 👨‍💻 Autor

Digimar07

---

## 📜 Licença

Uso pessoal
