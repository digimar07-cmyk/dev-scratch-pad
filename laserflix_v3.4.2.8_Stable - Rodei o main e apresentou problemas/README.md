# ⚠️⚠️⚠️ REGRA ABSOLUTA E INATACÁVEL - LEIA PRIMEIRO ⚠️⚠️⚠️

## 🚨 LIMITES MÁXIMOS DE ARQUIVO (INVIOLÁVEIS)

```
main_window.py           : 200 linhas (MÁXIMO ABSOLUTO)
project_card.py          : 150 linhas (MÁXIMO ABSOLUTO)
project_modal.py         : 250 linhas (MÁXIMO ABSOLUTO)
header.py / sidebar.py   : 200 linhas (MÁXIMO ABSOLUTO)
QUALQUER OUTRO ARQUIVO UI: 300 linhas (MÁXIMO ABSOLUTO)
```

### ❌ PROIBIDO:
- Adicionar lógica diretamente ao `main_window.py`
- Métodos com > 20 linhas no main_window.py
- Features sem criar controller ANTES
- Arquivo > 80% do limite sem refatorar

### ✅ OBRIGATÓRIO:
- Lógica SEMPRE em `ui/controllers/`
- UI reutilizável em `ui/components/`
- main_window.py = APENAS orquestrador
- Extrair código ANTES de adicionar feature

### 🚨 ARQUIVO > LIMITE?
1. **PARAR TODO DESENVOLVIMENTO**
2. **EXTRAIR** para controllers/components
3. **REDUZIR** para 70% do limite
4. **SÓ ENTÃO** continuar

**Detalhes completos**: [FILE_SIZE_LIMIT_RULE.md](./FILE_SIZE_LIMIT_RULE.md)

---

# 🎉 LASERFLIX v3.4.0.7 Stable

**“Organize a criatividade. Libere o potencial.”**

---

## 📝 ÍNDICE

1. [O que é Laserflix?](#-o-que-é-laserflix)
2. [Recursos](#-recursos)
3. [Instalação](#-instalação)
4. [Uso Rápido](#-uso-rápido)
5. [Documentação Completa](#-documentação-completa)
6. [Desenvolvimento](#-desenvolvimento)
7. [FAQ](#-faq)
8. [Licença](#-licença)

---

## 🎯 O QUE É LASERFLIX?

Laserflix é um **organizador visual de projetos de design 3D** (LightBurn, LaserGRBL, etc.) com:

- 🖼️ **Grid estilo Netflix**: Thumbnails instantâneos de vetores
- 🤖 **IA Local**: Categorização e tags automáticas com Ollama
- 🔍 **Busca Inteligente**: Bilíngue (EN/PT-BR) sem dependência de IA
- 📁 **Coleções**: Organize projetos em playlists temáticas
- ⚡ **Performance**: Startup < 2s, busca instantânea
- 🔒 **Privacidade**: 100% local, zero telemetria

**Público**: Designers 3D, makers, pequenos negócios de corte a laser.

---

## ✨ RECURSOS

### Core
- ✅ Import recursivo de pastas (LightBurn, LaserGRBL, SVG, etc.)
- ✅ Thumbnails automáticos (vetores renderizados)
- ✅ Grid paginado (36 cards/página)
- ✅ Busca em tempo real
- ✅ Filtros empilháveis (categorias + tags + origem)
- ✅ Ordenação flexível (data, nome, origem, análise)

### IA Assistente (Opcional)
- ✅ Categorização automática
- ✅ Sugestão de tags
- ✅ Descrições geradas por visão (Moondream)
- ✅ Fallbacks inteligentes (funciona sem IA)

### Coleções (NEW v3.4)
- ✅ Criar coleções/playlists
- ✅ Projetos em múltiplas coleções
- ✅ Gerenciamento completo (CRUD)
- ✅ Filtro por coleção na sidebar
- ✅ Visualização no modal de projeto

### Produtividade
- ✅ Favoritos / Já Feitos / Bom/Ruim
- ✅ Seleção em massa
- ✅ Backup automático
- ✅ Export/import de banco
- ✅ Limpeza de órfãos

---

## 📦 INSTALAÇÃO

### Pré-requisitos

- **Python**: 3.9+
- **Sistema**: Windows / Linux / macOS
- **Ollama** (opcional): Para IA local

### Passo 1: Clonar Repositório

```bash
git clone https://github.com/digimar07-cmyk/dev-scratch-pad.git
cd dev-scratch-pad/laserflix_v3.4.0.7_Stable
```

### Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```txt
Pillow>=10.0.0
requests>=2.31.0
cairosvg>=2.7.0  # Linux/Mac (Windows: opcional)
```

### Passo 3: (Opcional) Configurar Ollama

#### Instalar Ollama
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Baixar de https://ollama.com/download
```

#### Baixar Modelos
```bash
ollama pull llama3.2:3b           # Texto rápido
ollama pull qwen2.5:7b            # Texto qualidade
ollama pull moondream:1.8b        # Visão (análise de imagem)
ollama pull nomic-embed-text:latest  # Embeddings
```

### Passo 4: Executar

```bash
python main.py
```

**Primeira execução**:
- Arquivos criados: `laserflix_database.json`, `laserflix_config.json`, `collections.json`
- Pasta `backups/` criada automaticamente

---

## 🚀 USO RÁPIDO

### 1. Importar Projetos

1. Clique em **“📂 Importar Pastas”**
2. Selecione pasta raiz dos projetos
3. Escolha modo:
   - **Rápido**: Apenas scan (sem IA)
   - **Completo**: Scan + análise IA
4. Aguarde import (progress bar)

### 2. Navegar

- **Filtros rápidos**: ⭐ Favoritos, ✓ Já Feitos, 👍 Bons, 👎 Ruins
- **Busca**: Digite nome do projeto (bilíngue EN/PT-BR)
- **Sidebar**: Filtrar por origem, categoria, tag, **coleção**
- **Ordenação**: Data, nome, origem, status de análise

### 3. Gerenciar Projeto

**Clique no card** para abrir modal:
- Ver detalhes completos
- Editar categorias/tags
- Gerar descrição IA
- Abrir pasta no explorador
- Marcar como favorito/feito/bom/ruim
- Ver coleções do projeto

### 4. Coleções

1. Menu **Tools → 📁 Coleções**
2. Criar coleção (ex: “Natal 2025”)
3. Adicionar projetos ao card ou modal
4. Filtrar por coleção na sidebar

---

## 📚 DOCUMENTAÇÃO COMPLETA

### Arquivos de Documentação

- **[FILE_SIZE_LIMIT_RULE.md](./FILE_SIZE_LIMIT_RULE.md)**: 🚨 **REGRA ABSOLUTA** (LEIA PRIMEIRO)
- **[BACKLOG.md](./BACKLOG.md)**: Status do projeto, próximas features, áreas restritas
- **[PERSONA_MASTER_CODER.md](./PERSONA_MASTER_CODER.md)**: Padrões de código Kent Beck, instruções absolutas
- **[APP_PHILOSOPHY.md](./APP_PHILOSOPHY.md)**: Missão, valores, razão de existir
- **[CHANGELOG_v3.4.0.7.md](./CHANGELOG_v3.4.0.7.md)**: Histórico detalhado de mudanças
- **[README.md](./README.md)**: Este arquivo (visão geral)

### Estrutura do Projeto

```
laserflix_v3.4.0.7_Stable/
├── ai/                      # 🚫 Módulos de IA (restrito)
│   ├── ollama_client.py
│   ├── image_analyzer.py
│   ├── text_generator.py
│   ├── fallbacks.py
│   └── analysis_manager.py
├── core/                    # Backend
│   ├── database.py          # 🚫 Gerenciador JSON (restrito)
│   ├── project_scanner.py   # Scanner de projetos
│   ├── thumbnail_cache.py   # 🚫 Cache (restrito)
│   ├── thumbnail_preloader.py # 🚫 Preload assíncrono (restrito)
│   └── collections_manager.py # ✨ Coleções
├── ui/                      # Interface
│   ├── main_window.py       # Orquestrador principal (🚨 MAX 200 linhas)
│   ├── header.py            # Barra superior
│   ├── sidebar.py           # Filtros laterais
│   ├── project_card.py      # Card de projeto
│   ├── project_modal.py     # Modal detalhado
│   ├── collections_dialog.py # ✨ UI de coleções
│   └── [outros dialogs]
├── utils/                   # Utilitários
│   ├── logging_setup.py
│   ├── platform_utils.py
│   └── name_translator.py   # Busca bilíngue
├── config/                  # Configurações
│   ├── settings.py
│   └── ui_constants.py
├── main.py                  # Entry point
├── *.md                     # Documentação
└── backups/                 # Backups automáticos
```

---

## 🛠️ DESENVOLVIMENTO

### Setup de Dev

```bash
# Clonar
git clone https://github.com/digimar07-cmyk/dev-scratch-pad.git
cd dev-scratch-pad/laserflix_v3.4.0.7_Stable

# Instalar deps
pip install -r requirements.txt

# Executar
python main.py
```

### Workflow

1. **Ler documentação obrigatória**:
   - **`FILE_SIZE_LIMIT_RULE.md`** (🚨 PRIMEIRA LEITURA)
   - `PERSONA_MASTER_CODER.md` (padrões Kent Beck)
   - `APP_PHILOSOPHY.md` (missão e valores)
   - `BACKLOG.md` (tarefas atuais)

2. **Desenvolvimento**:
   - Seguir Simple Design (4 regras)
   - **NUNCA** adicionar lógica ao `main_window.py`
   - **SEMPRE** criar controller/component ANTES
   - Commits semânticos
   - Logs claros
   - Nunca tocar áreas restritas sem autorização

3. **Após cada tarefa**:
   - **VERIFICAR** tamanho dos arquivos (`wc -l ui/*.py`)
   - Atualizar `BACKLOG.md`
   - Commit descritivo
   - Testar manualmente

4. **A cada 1h**: Reler documentação (recalibração)

### 🚫 Áreas Restritas (Não Tocar)

- `ai/*` - Sistema de IA funcional e estável
- `core/database.py` - Persistência crítica
- `core/thumbnail_cache.py` - Performance otimizada
- `core/thumbnail_preloader.py` - Threading complexo

### ✅ Áreas Abertas

- `ui/*` - Melhorias de interface (🚨 SEGUIR LIMITES)
- `utils/*` - Novos utilitários
- `core/project_scanner.py` - Novos detectores
- `core/collections_manager.py` - Novas features

---

## ❓ FAQ

### P: Preciso de Ollama?
**R**: Não! Laserflix funciona perfeitamente sem IA. Ollama é opcional para:
- Categorização automática
- Sugestão de tags
- Descrições geradas

Sem Ollama, use edição manual (igualmente poderosa).

### P: Funciona offline?
**R**: Sim! 100% local. Zero dependência de internet.

### P: Meus dados são privados?
**R**: Absolutamente. Nenhum dado sai da sua máquina. Zero telemetria.

### P: Suporta quais formatos?
**R**: LightBurn (.lbrn2), LaserGRBL (.nc, .gcode), SVG, DXF, e qualquer formato detectado por variáveis de ambiente.

### P: Como fazer backup?
**R**: Menu **Tools → Backup Manual**. Backups automáticos são criados em `backups/`.

### P: Posso contribuir?
**R**: Sim! Issues e PRs bem-vindos. Leia `FILE_SIZE_LIMIT_RULE.md` e `PERSONA_MASTER_CODER.md` antes.

---

## 🐛 TROUBLESHOOTING

### Problema: Thumbnails não aparecem
**Solução**:
1. Verifique se `Pillow` está instalado: `pip show Pillow`
2. Linux/Mac: Instale `cairosvg`: `pip install cairosvg`
3. Check logs em `laserflix.log`

### Problema: IA não funciona
**Solução**:
1. Verifique Ollama: `ollama list`
2. Teste conexão: Menu **Tools → Configurações de Modelo → Testar**
3. Modelos instalados: `ollama pull llama3.2:3b`

### Problema: Lento no import
**Solução**:
1. Use “Modo Rápido” (sem IA)
2. Analise depois: Menu **Tools → Analisar Novos**
3. Evite pastas com 1000+ projetos de uma vez

---

## 📊 PERFORMANCE

### Benchmarks

- **Startup**: < 2s (500 projetos)
- **Import**: ~10 projetos/s (modo rápido)
- **Busca**: < 50ms (1000 projetos)
- **Renderização**: < 500ms (36 cards)
- **Análise IA**: 3-5s/projeto (Ollama local)

### Otimizações

- Thumbnails pré-carregados assíncronos
- Paginação (36 cards/vez)
- Cache de metadados
- Persistência atômica (JSON)

---

## 🎓 CHANGELOG

### v3.4.0.7 (06/03/2026)
🔧 **Correções e Melhorias de UX**
- ✅ FIX F-08: Sistema de coleções totalmente integrado
- ✅ FIX: Callback `get_project_collections` adicionado ao modal
- ✅ FIX: Scroll do painel esquerdo do modal funcionando
- ✅ UX: Espaço vazio no final do modal para melhor acessibilidade dos botões
- ✅ DOCS: Documentação completa atualizada para v3.4.0.7

### v3.4.0.0 (06/03/2026)
- ✨ Sistema de Coleções/Playlists
- 📝 Documentação completa (4 arquivos .md)
- 🧹 Limpeza de órfãos
- 🔄 Recalibração periódica de dev

### v3.3.0.0
- 🔍 Busca bilíngue (EN/PT-BR)
- 🏇 Filtros empilháveis (chips AND)
- 📊 Ordenação flexível
- 🚦 Seleção em massa

### v3.2.0.0
- 🤖 Integração Ollama
- 👁️ Análise de imagem (Moondream)
- ⚡ Fallbacks inteligentes

### v3.1.0.0
- 📁 Import recursivo
- 🎨 Novo design de cards
- 💾 Backup automático

---

## 📜 LICENÇA

**Atual**: Proprietário (uso interno)  
**Planejado v4.0**: MIT (open-source)

---

## 📞 CONTATO

- **GitHub**: https://github.com/digimar07-cmyk/dev-scratch-pad
- **Versão**: 3.4.0.7 Stable
- **Branch**: main
- **Desenvolvedor**: digimar07

---

## ❤️ AGRADECIMENTOS

- **Kent Beck**: Filosofia XP
- **Ollama**: IA democrática
- **LightBurn**: Comunidade laser
- **Claude AI**: Parceiro de desenvolvimento
- **Você**: Por usar o Laserflix! 🎉

---

**“Organize a criatividade. Libere o potencial.”**

---

**Modelo usado**: Claude Sonnet 4.5
**Versão do Documento**: v3.4.0.7
