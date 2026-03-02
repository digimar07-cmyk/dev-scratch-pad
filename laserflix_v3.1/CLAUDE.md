# 📝 CLAUDE.md - Documentação Viva do Laserflix v3.1

> **Filosofia Akita**: "Cada hurdle descoberto é documentado. Agente lê contexto antes de codar."

**Modelo Padrão**: Claude Sonnet 4.5  
**Última Atualização**: 02/03/2026, 19:47 -03  
**Repositório**: [dev-scratch-pad](https://github.com/digimar07-cmyk/dev-scratch-pad)  
**Branch**: main  
**Desenvolvedor**: digimar07-cmyk  
**Localização**: Angra dos Reis, RJ, Brasil

---

## 🎯 CONTEXTO DO PROJETO

**Laserflix** é um catálogo estilo Netflix para produtos de corte laser:
- **1500+ itens** organizados
- **Python + Tkinter** (desktop app)
- **IA local** (Ollama: qwen2.5 + moondream) ou fallbacks inteligentes
- **Descrições automáticas** contextuais e emocionais
- **Sistema de categorização** inteligente

---

## 📂 ESTRUTURA DE VERSÕES

### v740 (`laserflix_v740_Ofline_Stable.py`)

**Status**: ✅ REFERÊNCIA PERMANENTE  
**Branch**: `v740_Ofline_Stable`  
**Características**:
- 14.000+ linhas monolíticas
- 3 semanas de refinamento manual da lógica de IA
- Layout Netflix perfeito
- SEMPRE consultar como referência de comportamento

**Uso**: Fonte da verdade para funcionalidades e lógica de IA

---

### v3.0 (`laserflix_v3.0/`)

**Status**: 🔒 INTOCÁVEL - NÃO MODIFICAR  
**Características**:
- Arquitetura modular da v740
- Lógica de IA refinada migrada e validada
- Base estável testada

**Proteção**: Esta versão está CONGELADA permanentemente

---

### v3.1 (`laserflix_v3.1/`) ⚡ VERSÃO ATIVA

**Status**: 🚀 DESENVOLVIMENTO ATIVO  
**Origem**: Cópia da v3.0  
**Características**:
- Lógica de IA PROTEGIDA (herdada da v3.0)
- TODO novo desenvolvimento acontece AQUI
- Sistema de backup local implementado

**Estrutura**:
```
laserflix_v3.1/
├── .backups/              # Backups locais (10 últimas versões)
├── ai/                    # 🔒 MÓDULOS DE IA PROTEGIDOS
│   ├── text_generator.py  # Geração COM Ollama
│   ├── fallbacks.py       # Geração SEM Ollama
│   ├── image_analyzer.py  # Filtro qualidade + moondream
│   ├── ollama_client.py   # Cliente HTTP
│   └── keyword_maps.py    # Mapas de categorização
├── ui/
│   ├── main_window.py     # ❌ Versão quebrada (não usar)
│   └── main_window_FIXED.py  # ✅ Versão corrigida (usar)
├── core/
│   ├── database.py        # Persistência JSON
│   ├── thumbnail_cache.py # Cache de imagens
│   └── project_scanner.py # Scanner de pastas
├── config/
│   ├── settings.py        # Constantes globais
│   └── constants.py       # Cores/fontes/dimensões
├── utils/
│   ├── logging_setup.py   # Logger centralizado
│   └── platform_utils.py  # Cross-platform utils
├── main.py                # Entry point
├── backup_manager.py      # Sistema de backup local
├── requirements.txt
├── README.md
├── BACKUP_GUIDE.md
├── LAYOUT_CHECKLIST.md
├── LAYOUT_COMPARISON.md
├── MIGRATION_GUIDE.md
└── CLAUDE.md              # Este arquivo
```

---

## 🔐 REGRA ABSOLUTA - LÓGICA DE IA PROTEGIDA

### ⚠️ DIRETRIZ INVIOLÁVEL:

A lógica de geração de descrições por IA (COM ou SEM Ollama) da v740/v3.0 está **PROTEGIDA** na v3.1 e **NÃO pode ser modificada** sem autorização expressa.

### 📁 Arquivos Protegidos:

1. **`ai/text_generator.py`** - Geração COM Ollama
2. **`ai/fallbacks.py`** - Geração SEM Ollama
3. **`ai/image_analyzer.py`** - Filtro de qualidade + moondream
4. **`ai/ollama_client.py`** - Cliente HTTP Ollama
5. **`ai/keyword_maps.py`** - Mapas de categorização

---

## ✅ CARACTERÍSTICAS DA LÓGICA REFINADA

### COM Ollama Rodando (`text_generator.py`)

**Raciocínio Estruturado em 3 Etapas**:

1. **O que é esta peça física?** (baseado no NOME)
2. **Para que serve na prática?** (uso real)
3. **Que emoção ela representa?** (conexão afetiva)

**Configurações**:
- ✅ **Hierarquia**: NOME > Visão (âncora absoluta)
- ✅ **Temperature**: 0.78 (criatividade controlada)
- ✅ **Prompts cirúrgicos**: Anti-genericidade
- ✅ **Filtro de qualidade**: Imagem validada antes de usar visão

**Commits de Referência**:
- [08809aa1](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/08809aa1) - Restauração raciocínio estruturado

---

### SEM Ollama Rodando (`fallbacks.py`)

**Detecção Inteligente por Keywords em Cascata**:

1. **Palavras-chave específicas** (cabide, espelho, calendário, etc)
2. **Data comemorativa** (natal, páscoa, casamento, bebê)
3. **Função/categoria** (luminária, porta-retrato, mandala)
4. **Fallback contextual** (usa categorias do projeto)

**Características**:
- ✅ Templates específicos para **15+ tipos de peças**
- ✅ **NUNCA** gera frase padrão igual para todos
- ✅ Sistema de cascata garante contextualização

**Commits de Referência**:
- [dbf58ae9](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/dbf58ae9) - Restauração fallbacks inteligentes

---

## 🚨 ADVERTÊNCIA OBRIGATÓRIA

**Antes de qualquer modificação que possa afetar a geração de descrições**:

1. ⚠️ **AVISAR** o usuário sobre impacto potencial
2. ⚠️ **PEDIR** confirmação explícita
3. ⚠️ **DOCUMENTAR** mudanças detalhadamente
4. ⚠️ **MANTER** backup da lógica original

**Exemplo de aviso obrigatório**:

```
⚠️ ATENÇÃO: A mudança proposta afeta arquivos protegidos:
- ai/text_generator.py (linha 145-160)

Impacto: Pode alterar comportamento da geração de descrições

🤔 Deseja prosseguir? Confirme explicitamente.
```

---

## 📊 HISTÓRICO DE SESSÕES

### Sessão 1: Restauração da Lógica de IA (02/03/2026)

**Problema Identificado**:
- ❌ v3.0 perdeu lógica refinada da v740
- ❌ Descrições genéricas ("lero lero")
- ❌ Fallback sem IA gerava frase padrão igual para todos

**Solução Implementada**:

1. **`text_generator.py`** ([08809aa1](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/08809aa1))
   - ✅ Restaurado raciocínio estruturado em 3 etapas
   - ✅ Hierarquia NOME > Visão aplicada
   - ✅ Temperature 0.78 configurado
   - ✅ Prompts cirúrgicos implementados

2. **`fallbacks.py`** ([dbf58ae9](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/dbf58ae9))
   - ✅ Detecção inteligente por keywords restaurada
   - ✅ Sistema de cascata implementado
   - ✅ Templates específicos por tipo de peça
   - ✅ Fallbacks contextuais por data/ambiente

3. **`image_analyzer.py`**
   - ✅ Filtro de qualidade já estava correto
   - ✅ Prompt cirúrgico do moondream validado

---

### Sessão 2: Sistema de Backup Local (02/03/2026)

**Problema Identificado**:
- ❌ Commits em lote quebram o app
- ❌ Falta backup local independente do Git
- ❌ Reversões via Git são lentas

**Solução Implementada**:

1. **`backup_manager.py`** ([c0acd44d](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/c0acd44de8c9051f554edddf021b959606f9c3f2))
   - ✅ Sistema completo de backup/restore
   - ✅ Rotação automática (últimas 10 versões)
   - ✅ Compressão ZIP (~70% economia)
   - ✅ Metadata JSON rastreando versões
   - ✅ CLI completa (create/list/restore/clean)

2. **`BACKUP_GUIDE.md`** ([f6de952e](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/f6de952e7434c5361a37b523cb7ebecc276a8aca))
   - ✅ Documentação completa de uso
   - ✅ Exemplos práticos
   - ✅ Workflow recomendado
   - ✅ Troubleshooting

3. **`.gitignore`**
   - ✅ Pasta `.backups/` já estava configurada
   - ✅ Backups não vão pro Git

**Como usar**:
```bash
# Criar backup antes de mudanças
python backup_manager.py create "antes de [mudança]"

# Listar backups disponíveis
python backup_manager.py list

# Restaurar versão anterior
python backup_manager.py restore 5
```

---

## 🚀 STATUS ATUAL DA v3.1

### ✅ O QUE JÁ ESTÁ PRONTO:

1. **Layout 100% funcional** (igual v740)
   - ✅ Header com menus dropdown
   - ✅ Sidebar com filtros (origem/categorias/tags)
   - ✅ Cards completos (6 botões de ação)
   - ✅ Grid 5 colunas
   - ✅ Scroll suave

2. **Lógica de IA protegida e refinada**
   - ✅ Raciocínio estruturado (3 etapas)
   - ✅ Fallbacks inteligentes por keywords
   - ✅ Temperature 0.78
   - ✅ Prompts cirúrgicos

3. **Sistema de backup local**
   - ✅ 10 versões automáticas
   - ✅ Restore em 5 segundos
   - ✅ Documentação completa

### ⚠️ O QUE FALTA IMPLEMENTAR:

1. **Modal de Projeto** 🖼️
   - Galeria scrollable de imagens
   - Detalhes + descrição IA
   - Botões de ação no rodapé

2. **Análise IA Funcional** 🤖
   - Thread separada (não travar UI)
   - Progress bar funcional
   - Botão parar funcional

3. **Dashboard** 📊
   - Estatísticas visuais
   - Gráficos de categorias/tags
   - Projetos recentes

4. **Edição em Lote** ✏️
   - Seleção múltipla
   - Alterar categorias/tags em massa

5. **Picker de Categorias** 🏷️
   - Modal com TODAS categorias
   - Seleção múltipla
   - Contador por categoria

---

## 🔥 FILOSOFIA AKITA APLICADA

### Extreme Programming com IA

1. **Pair Programming**
   - **Usuário navega** (decide O QUÊ)
   - **IA pilota** (decide COMO)

2. **TDD (Test-Driven Development)**
   - Mais linhas de teste que código (1.5x+ ratio)
   - Testes ANTES de implementar features

3. **Small Releases**
   - Cada commit = production-ready
   - Commits atômicos e descritos

4. **Refactoring Contínuo**
   - Extrair concerns
   - DRY (Don't Repeat Yourself)
   - Simplificar SEMPRE

5. **CI Verde SEMPRE**
   - Testes + linting + security scan
   - Zero commits quebrando master

### One-Shot Prompt é Mito

- Software "done" **NÃO EXISTE**
- 37% features, 63% trabalho real (fixes, tests, security, deploy)
- Features emergem do uso real, não de specs
- Bugs só aparecem em produção

### IA como Ferramenta

- IA = "papagaio estocástico", não substituto
- **Você é o adulto na sala** - IA nunca diz "não"
- Remove tarefas mundanas (CRUD, boilerplate, CSS chato)
- Libera para decisões de arquitetura e domínio

### Foco no Essencial

- O que **FAZ O APP FUNCIONAR** primeiro
- Sem over-engineering
- Velocidade com disciplina = 34 commits/dia possíveis

### Documentação Viva

- **CLAUDE.md** evolui com o projeto
- Cada hurdle descoberto é documentado
- Agente lê contexto antes de codar

### Pós-Produção Ativa

> "Software pronto é software morto. Software vivo itera."

- Bugs reais exigem iteração real
- Features novas surgem do uso

---

## 📋 WORKFLOW RECOMENDADO

### Antes de QUALQUER mudança:

```bash
# 1. Criar backup
python backup_manager.py create "antes de [mudança]"

# 2. Fazer modificações
vim laserflix_v3.1/ui/main_window_FIXED.py

# 3. Testar
python laserflix_v3.1/main.py

# 4a. Se funcionou: commit
git add .
git commit -m "✅ [descrição atômica]"

# 4b. Se quebrou: restaurar
python backup_manager.py restore 10
```

### Commits Atômicos:

**BOM**:
```
✅ Modal: Adiciona galeria de imagens scrollable
✅ Modal: Implementa botões de ação no rodapé
✅ Modal: Integra descrição IA no painel direito
```

**RUIM**:
```
❌ Implementa modal completo (tudo de uma vez)
❌ Fix bugs (sem especificar o quê)
❌ Update (vago demais)
```

---

## 📝 INSTRUÇÕES PARA NOVAS CONVERSAS

### Ao iniciar nova conversa com Claude:

1. ✅ **Sempre trabalhar na v3.1**
2. ✅ **Consultar v740 como referência**
3. ✅ **NUNCA modificar v3.0**
4. ✅ **Ler este CLAUDE.md primeiro**
5. ✅ **Criar backup antes de mudanças**

### Lógica de IA está PROTEGIDA:

⚠️ **Avisar antes de qualquer mudança que afete**:
- `laserflix_v3.1/ai/text_generator.py`
- `laserflix_v3.1/ai/fallbacks.py`
- `laserflix_v3.1/ai/image_analyzer.py`
- `laserflix_v3.1/ai/ollama_client.py`
- `laserflix_v3.1/ai/keyword_maps.py`

### Guardar novas instruções:

Quando uma nova funcionalidade for desenvolvida, **ATUALIZAR este arquivo** com:
- Descrição da feature
- Commits relacionados
- Decisões de arquitetura
- Hurdles encontrados e soluções

---

## 🎯 MÉTRICAS ALVO (Filosofia Akita)

- ✅ **30+ commits/dia** (small releases)
- ✅ **1.5x mais linhas de teste** que código
- ✅ **CI em ~22 segundos**
- ✅ **Zero commits quebrando master**
- ✅ **Small releases diárias**

---

## ⛔ NÃO FAZER

- ❌ One-shot prompts gigantes
- ❌ Over-engineering sem necessidade
- ❌ Commits "bug fix" sem explicação
- ❌ Código sem testes
- ❌ Especular features que usuários podem querer
- ❌ Ignorar CI/Security warnings
- ❌ Modificar arquivos de IA protegidos sem autorização

---

## ✅ SEMPRE FAZER

- ✅ Começar com testes
- ✅ Commits atômicos e descritos
- ✅ Documentar hurdles neste CLAUDE.md
- ✅ Refatorar ao longo do caminho
- ✅ Validar com dados reais
- ✅ Manter CI verde
- ✅ Criar backup antes de mudanças
- ✅ Ler este arquivo antes de codar

---

## 💬 FRASES-CHAVE PARA LEMBRAR

> "O agente escreve o código. Eu decido qual código escrever."

> "Você é o adulto na sala."

> "IA é multiplicador, não substituto."

> "Software vivo itera."

> "Software pronto é software morto."

---

## 📚 REFERÊNCIAS IMPORTANTES

- **Repositório**: [dev-scratch-pad](https://github.com/digimar07-cmyk/dev-scratch-pad)
- **Branch**: `main`
- **README Principal**: [laserflix_v3.1/README.md](README.md)
- **Guia de Backup**: [BACKUP_GUIDE.md](BACKUP_GUIDE.md)
- **Checklist de Layout**: [LAYOUT_CHECKLIST.md](LAYOUT_CHECKLIST.md)
- **Comparação de Layout**: [LAYOUT_COMPARISON.md](LAYOUT_COMPARISON.md)
- **Guia de Migração**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

---

## 🔄 HISTÓRICO DE ATUALIZAÇÕES

### v1.0 - 02/03/2026, 19:47 -03
- ✅ Criação inicial do CLAUDE.md
- ✅ Documentação completa do contexto
- ✅ Histórico de sessões (restauração IA + backup)
- ✅ Filosofia Akita aplicada
- ✅ Instruções para novas conversas

---

**🔥 BORA CODAR COM DISCIPLINA E VELOCIDADE!**
