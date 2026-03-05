# 🎬 LASERFLIX v3.4.0.0 Stable

> **Gerenciador inteligente de projetos para corte a laser com IA local (Ollama)**

---

## 👨‍💻 PERSONA DE DESENVOLVIMENTO

🔴 **IMPORTANTE:** Este projeto segue a filosofia **Kent Beck** (Extreme Programming).

**Antes de contribuir, leia:**
- **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** → Filosofia de desenvolvimento OBRIGATÓRIA

**Princípios:**
- ✅ Simplicidade radical ("faça a coisa mais simples que funciona")
- ✅ Baby steps (um commit = uma mudança)
- ✅ Refatoração contínua (deixe melhor do que encontrou)
- ✅ Código autoexplicativo (comente o PORQUÊ, não o QUE)
- ❌ NUNCA antecipar requisitos futuros (YAGNI)
- ❌ NUNCA criar abstrações desnecessárias

> **Leia `DEVELOPER_PERSONA.md` ANTES de iniciar qualquer desenvolvimento!**

---

## 🔥 O QUE HÁ DE NOVO NA v3.4?

### 🆕 FEATURES EM DESENVOLVIMENTO:

#### 🔴 **F-06: Ordenação Configurável** (PRÓXIMA)
- Menu dropdown no header (ao lado da busca)
- 7 opções:
  - 📅 Recentes / Antigos
  - 🔤 A→Z / Z→A
  - 🏛️ Origem
  - 🤖 Analisados / Pendentes
- Ordena ANTES da paginação
- Estado persiste ao mudar de página

#### 🟡 **S-03: Thumbnail Assíncrono** (FILA)
- Carregamento em `queue.Queue`
- 4 threads workers
- Sem travar UI
- Cache inteligente

---

## ✅ FEATURES ESTABILIZADAS (herdadas da v3.3):

### 📊 **Paginação Simples (36 cards/página)**
- Grid 6×6 (6 linhas × 6 colunas)
- Navegação: ⏮ ◀ "Pág X/Y" ▶ ⏭
- Atalhos: `Home`, `End`, `←`, `→`
- Performance: suporta 1000+ projetos

### 🏷️ **Categorias/Tags Visíveis**
- 3 primeiras categorias (badges coloridos)
- 5 primeiras tags (clicáveis)
- Click em categoria/tag = aplica filtro

### ☑️ **Seleção em Massa**
- Botão `☑️ Selecionar` no header
- Barra flutuante com contadores
- Checkbox nos cards
- Remoção múltipla (confirmação dupla)

### 🤖 **Análise IA Sequencial**
- Após importação: pergunta se quer analisar
- Executa SEQUENCIALMENTE:
  1. Categorias + Tags (10+ categorias obrigatórias)
  2. Descrições detalhadas
- Apenas produtos recém-importados

### 📋 **Importação Recursiva Avançada**
- 3 modos:
  - **Hybrid:** `folder.jpg` + fallback
  - **Pure:** Apenas `folder.jpg`
  - **Simple:** 1 nível (qualquer subpasta)
- Detecção de duplicatas CONTRA database existente
- Dialog de resolução manual (skip/replace/merge)
- Preview antes de importar

### 🗑️ **Remoção de Projetos**
- Botão no modal individual
- Remoção em massa (seleção múltipla)
- Confirmação dupla
- NÃO apaga arquivos do disco

### ⚙️ **Configuração Modelos IA**
- Tela de seleção de modelos Ollama
- 3 papéis:
  - `image_vision` (Moondream)
  - `text_quality` (Qwen2.5 14B)
  - `text_fast` (Qwen2.5 3B)
- Salva em `laserflix_config.json`

---

## 📊 ESTRUTURA MODULAR

```
laserflix_v3.4.0.0_Stable/
├── main.py                    # Entry point
├── requirements.txt
├── README.md                  # Este arquivo
├── DEVELOPER_PERSONA.md       # 🔴 Filosofia Kent Beck (LEIA PRIMEIRO!)
├── VERSION_HISTORY.md         # Histórico de versões
├── MIGRATION_v3.3_to_v3.4.md  # Guia de migração
├── BACKLOG.md                 # Tarefas (fonte única)
├── BACKUP_GUIDE.md            # Sistema de backup
├── LAYOUT_CHECKLIST.md        # Checklist de layout
├───
├── config/                    # Configurações
│   ├── settings.py            # Constantes globais
│   ├── constants.py           # BANNED_STRINGS, etc
│   ├── ui_constants.py        # Cores, fontes
│   └── card_layout.py         # Dimensões dos cards
├───
├── core/                      # Lógica central
│   ├── database.py            # Persistência JSON
│   ├── project_scanner.py     # Escaneia pastas
│   └── thumbnail_cache.py     # Cache de imagens (será substituído)
├───
├── ai/                        # Inteligência Artificial
│   ├── ollama_client.py       # Cliente Ollama
│   ├── analysis_manager.py    # Gerencia análises
│   ├── image_analyzer.py      # Moondream (visão)
│   ├── text_generator.py      # Qwen2.5 (texto)
│   ├── fallbacks.py           # Análise sem IA
│   └── keyword_maps.py        # Mapas de categorias/tags
├───
├── ui/                        # Interface gráfica
│   ├── main_window.py         # Orquestrador principal
│   ├── header.py              # Barra superior
│   ├── sidebar.py             # Barra lateral
│   ├── project_card.py        # Card de projeto
│   ├── project_modal.py       # Modal de detalhes
│   ├── edit_modal.py          # Edição manual
│   ├── model_settings_dialog.py  # Configuração IA
│   ├── import_mode_dialog.py     # Seleção de modo de importação
│   ├── import_preview_dialog.py  # Preview antes de importar
│   ├── duplicate_resolution_dialog.py  # Resolução de duplicatas
│   ├── recursive_import_integration.py  # Orquestrador de importação
│   └── prepare_folders_dialog.py  # Preparação de pastas
├───
└── utils/                     # Utilitários
    ├── logging_setup.py       # Logger centralizado
    ├── platform_utils.py      # Funções cross-platform
    ├── recursive_scanner.py   # Escaneia pastas recursivamente
    └── duplicate_detector.py  # Detecta duplicatas
```

---

## 🚀 INSTALAÇÃO E USO

### 1. Pré-requisitos:

```bash
# Python 3.10+
python --version

# Ollama instalado e rodando
ollama --version

# Modelos baixados
ollama pull moondream
ollama pull qwen2.5:14b
ollama pull qwen2.5:3b
```

### 2. Instalar dependências:

```bash
cd laserflix_v3.4.0.0_Stable
pip install -r requirements.txt
```

### 3. Rodar o app:

```bash
python main.py
```

---

## 📚 DOCUMENTAÇÃO

### 🔴 Arquivos OBRIGATÓRIOS:

- **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** → 🔴 **LEIA PRIMEIRO!** Filosofia Kent Beck
- **[BACKLOG.md](BACKLOG.md)** → Tarefas pendentes (fonte única)

### Arquivos complementares:

- **[VERSION_HISTORY.md](VERSION_HISTORY.md)** → Histórico completo de versões
- **[MIGRATION_v3.3_to_v3.4.md](MIGRATION_v3.3_to_v3.4.md)** → Guia de migração
- **[BACKUP_GUIDE.md](BACKUP_GUIDE.md)** → Sistema de backup automático
- **[LAYOUT_CHECKLIST.md](LAYOUT_CHECKLIST.md)** → Checklist de layout

---

## 🧑‍💻 CONTRIBUINDO

### 🔴 ANTES DE CONTRIBUIR:

1. ✅ Ler **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** COMPLETAMENTE
2. ✅ Entender filosofia Kent Beck
3. ✅ Seguir workflow de 5 fases:
   - ENTENDER → PLANEJAR → IMPLEMENTAR → REFATORAR → DOCUMENTAR
4. ✅ Fazer baby steps (um commit por vez)
5. ✅ Testar manualmente após CADA mudança

### Checklist antes de commitar:

```
☐ Código funciona? (testei manualmente)
☐ Código é o mais simples possível?
☐ Nomes são claros?
☐ Funções têm < 20 linhas?
☐ Não há código duplicado?
☐ Commit message é descritiva?
☐ BACKLOG.md foi atualizado?
```

---

## 🔒 ZONAS PROTEGIDAS

Arquivos que NÃO devem ser modificados sem análise de impacto:

### 🔒 IA (Geração Criativa):
```
ai/ollama_client.py
ai/analysis_manager.py
ai/text_generator.py
ai/image_analyzer.py
ai/fallbacks.py
ai/keyword_maps.py
```

### 🔒 Importação (Fluxo Crítico):
```
ui/import_mode_dialog.py
ui/recursive_import_integration.py
ui/import_preview_dialog.py
ui/duplicate_resolution_dialog.py
utils/recursive_scanner.py
utils/duplicate_detector.py
```

> **Regra:** Qualquer toque em zona protegida requer alerta + autorização expressa antes de escrever.

---

## 👥 CRÉDITOS

- **v740:** Base visual (layout Netflix)
- **v3.x:** Refactoring modular + novas features
- **Persona:** Kent Beck (Extreme Programming)
- **Perplexity (Claude Sonnet 4.6):** Arquitetura e desenvolvimento

---

## 📦 VERSÃO

**v3.4.0.0 Stable**  
**Data:** 05/03/2026  
**Status:** 🔴 EM DESENVOLVIMENTO  
**Persona:** Kent Beck (XP)  

**Última feature:** Documentação inicial + Persona de desenvolvimento  
**Próxima feature:** F-06 - Ordenação configurável

---

**Última atualização:** 05/03/2026 19:20 BRT
