# 🎬 LASERFLIX v7.4.0

**Netflix-style project manager for laser cutting designs**

Gerenciador inteligente de projetos de corte a laser com interface inspirada no Netflix, análise por IA (Ollama + Moondream) e organização automática por categorias, tags e origem.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## ✨ Features

- 🎨 **Interface Netflix-style** — Grid visual com thumbnails 220x200px
- 🤖 **Análise com IA** — Categorização automática usando Ollama (Qwen2.5 + Moondream)
- 🖼️ **Visão computacional** — Análise de imagens de capa com filtro de qualidade
- 🏷️ **Tags inteligentes** — Extração automática de palavras-chave
- 🔍 **Busca e filtros** — Por status, origem, categoria, tag
- ⭐ **Gestão de estados** — Favorito, Feito, Bom, Ruim
- 💾 **Backup automático** — A cada 30 minutos + manual
- 📊 **Sidebar dinâmica** — Estatísticas em tempo real
- 🚀 **Performance** — Cache LRU para thumbnails, atomic saves

---

## 📦 Instalação

### Requisitos

- **Python 3.8+**
- **Ollama** instalado e rodando localmente
- **Modelos Ollama** baixados:
  ```bash
  ollama pull qwen2.5:7b-instruct-q4_K_M
  ollama pull qwen2.5:3b-instruct-q4_K_M
  ollama pull moondream:latest
  ollama pull nomic-embed-text:latest
  ```

### Dependências Python

```bash
pip install pillow requests
```

### Clone e Execute

```bash
git clone https://github.com/digimar07-cmyk/dev-scratch-pad.git
cd dev-scratch-pad
python laserflix_tkinter/main.py
```

---

## 🚀 Uso

### Primeira Execução

1. **Adicione pastas** — Clique em "➕ Pastas" e selecione pastas com projetos
2. **Análise com IA** — Menu "🤖 Analisar" → "Analisar apenas novos"
3. **Explore** — Use filtros, busca e sidebar para navegar

### Atalhos de Navegação

- **🏠 Home** — Todos os projetos
- **⭐ Favoritos** — Projetos marcados como favoritos
- **✓ Já Feitos** — Projetos concluídos
- **👍 Bons** — Projetos de alta qualidade
- **👎 Ruins** — Projetos descartados

### Ações nos Cards

- **📂** — Abrir pasta no explorador
- **⭐** — Marcar/desmarcar favorito
- **✓** — Marcar como feito
- **👍** — Marcar como bom
- **👎** — Marcar como ruim
- **🤖** — Analisar projeto individual

### Menu Principal

- **📊 Dashboard** — Estatísticas gerais (em desenvolvimento)
- **📝 Edição em Lote** — Editar múltiplos projetos (em desenvolvimento)
- **🤖 Configurar Modelos IA** — Trocar modelos Ollama
- **💾 Exportar/Importar Banco** — Backup e restore
- **🔄 Backup Manual** — Criar backup imediato

---

## 🏗️ Arquitetura

### Estrutura Modular (Fowler/Beck Refactoring)

```
laserflix_tkinter/
├── __init__.py              # Setup logging, version
├── main.py                  # Entry point
├── app.py                   # LaserflixApp (orchestrator)
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Centralized configuration
│
├── models/
│   ├── __init__.py
│   ├── project.py           # Project dataclass
│   └── database.py          # DatabaseManager (atomic saves)
│
├── services/
│   ├── __init__.py
│   ├── ollama_service.py    # OllamaService (AI)
│   ├── image_service.py     # ImageService (thumbnails + quality)
│   └── analysis_service.py  # AnalysisService (structure + tags)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # MainWindow (header + navigation)
│   ├── sidebar.py           # Sidebar (filters)
│   └── project_grid.py      # ProjectGrid (cards)
│
└── utils/
    ├── __init__.py
    └── file_utils.py        # File/path helpers
```

### Padrões Aplicados

- **Extract Module** — Separação em camadas (config, models, services, ui, utils)
- **Extract Class** — 12 classes com responsabilidade única
- **Single Responsibility** — Cada classe tem um propósito claro
- **Dependency Injection** — Services são injetados no app
- **Observer Pattern** — Callbacks conectam UI à lógica de negócio
- **LRU Cache** — Thumbnails com evicção automática
- **Atomic Writes** — Banco de dados salvo com transação atômica

### Fluxo de Dados

```
main.py
  ↓
LaserflixApp (orquestrador)
  ├── Settings → configuração centralizada
  ├── DatabaseManager → persistência
  ├── OllamaService → análise com IA
  ├── ImageService → thumbnails + qualidade
  ├── AnalysisService → estrutura + categorias
  ├── MainWindow → header + status
  ├── Sidebar → filtros dinâmicos
  └── ProjectGrid → cards visuais
```

---

## 🤖 Análise com IA

### Modelos Usados

| Modelo | Uso | Threshold |
|--------|-----|----------|
| **qwen2.5:7b** | Análise individual (qualidade) | < 50 projetos |
| **qwen2.5:3b** | Análise em lote (velocidade) | ≥ 50 projetos |
| **moondream:latest** | Descrição visual de capas | Quando qualidade OK |
| **nomic-embed-text** | Embeddings (reservado) | — |

### Filtro de Qualidade de Imagem

Antes de enviar para o Moondream, o sistema avalia:

- ✅ **Brilho** — Rejeita > 210 (fundo branco dominante)
- ✅ **Saturação** — Rejeita < 25 (quase monocromático)
- ✅ **% Branco** — Rejeita > 50% (mockup vazio)

### Prompt Cirúrgico

O prompt é otimizado para:
1. **Data Comemorativa** (Páscoa, Natal, Dia das Mães...)
2. **Função/Tipo** (Porta-Retrato, Caixa, Luminária...)
3. **Ambiente** (Quarto, Sala, Cozinha...)
4. **Tags** — 8 palavras-chave relevantes

---

## 🧪 Desenvolvimento

### Estrutura de Classes Principais

```python
# app.py
class LaserflixApp:
    def __init__(self, root: tk.Tk)
    def _connect_callbacks(self)      # Liga UI aos métodos
    def _display_projects(self)       # Renderiza grid filtrado
    def _analyze_project_with_ai(self) # Análise com Ollama

# services/ollama_service.py
class OllamaService:
    def generate_text(self, prompt, model, timeout)
    def generate_with_vision(self, prompt, image_b64, model)
    def is_available(self) -> bool    # Health check com cache

# services/image_service.py
class ImageService:
    def get_thumbnail(self, path) -> ImageTk.PhotoImage  # LRU cache
    def assess_image_quality(self, path) -> dict
    def prepare_image_for_vision(self, path) -> str

# models/database.py
class DatabaseManager:
    def save(self)                    # Atomic write
    def auto_backup(self)             # Scheduled backup
```

### Extendendo Funcionalidades

**Adicionar novo filtro:**
```python
# 1. MainWindow: adicionar botão no header
# 2. LaserflixApp._connect_callbacks: conectar callback
# 3. LaserflixApp._on_novo_filtro: implementar lógica
# 4. LaserflixApp._get_filtered_projects: adicionar condição
```

**Adicionar novo service:**
```python
# 1. Criar laserflix_tkinter/services/novo_service.py
# 2. Exportar em services/__init__.py
# 3. Instanciar em LaserflixApp.__init__
# 4. Usar em métodos de negócio
```

---

## 📊 Performance

- **Thumbnail Cache** — LRU com limite de 300 items
- **Health Check Cache** — Ollama status cached por 5s
- **Atomic Saves** — Transação tmp → replace
- **Lazy Loading** — Thumbnails carregados sob demanda
- **Batch Analysis** — Progress bar com stop button

---

## 🐛 Troubleshooting

### Ollama não responde

```bash
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama
ollama serve
```

### Thumbnails não aparecem

- Verificar se as imagens existem na pasta do projeto
- Formatos suportados: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`

### Banco corrompido

```bash
# Restaurar do backup mais recente
cp laserflix_backups/auto_backup_YYYYMMDD_HHMMSS.json laserflix_database.json
```

---

## 📝 Changelog

### v7.4.0 (Refatoração Fowler)
- ✅ Arquitetura modular em 5 camadas
- ✅ 12 classes com responsabilidade única
- ✅ Atomic saves + auto backup
- ✅ LRU cache para thumbnails
- ✅ Filtro de qualidade para visão
- ✅ Sidebar dinâmica com estatísticas
- ✅ Grid responsivo 5 colunas

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Digimar07**
- GitHub: [@digimar07-cmyk](https://github.com/digimar07-cmyk)
- Email: digimar07@gmail.com

---

## 🙏 Agradecimentos

- **Martin Fowler** — Refactoring principles
- **Kent Beck** — Clean code patterns
- **Ollama Team** — Local AI inference
- **Moondream** — Vision model

---

**Made with ❤️ for the laser cutting community**
