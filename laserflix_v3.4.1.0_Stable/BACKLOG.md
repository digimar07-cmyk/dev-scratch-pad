# 📋 BACKLOG - Laserflix v3.4.0.7

**Versão**: 3.4.0.7 Stable  
**Última atualização**: 06/03/2026 13:22 BRT  
**Status**: Sistema de Coleções COMPLETO ✅

---

## 🎯 MISSÃO DO SPRINT ATUAL

Sistema de Coleções/Playlists **CONCLUÍDO** e **100% INTEGRADO**.

---

## ✅ CONCLUÍDO (v3.4.0.7)

### Feature F-08: Sistema de Coleções - COMPLETO

#### Backend
- ✅ `core/collections_manager.py` criado
  - CRUD de coleções (criar/renomear/deletar)
  - Adicionar/remover projetos
  - Suporte a múltiplas coleções por projeto
  - Persistência em `collections.json`
  - Limpeza de órfãos
  - API limpa estilo Kent Beck
  - Commit: `a7b6553`

#### Interface
- ✅ `ui/collections_dialog.py` criado
  - Dialog modal com split view
  - Listagem de coleções com contador
  - Visualização de projetos por coleção
  - Operações CRUD na UI
  - Padrão visual consistente
  - Commit: `79a778a`

#### Integração (v3.4.0.7)
- ✅ `main_window.py`
  - Inicialização do `CollectionsManager`
  - Método `open_collections_dialog()` adicionado
  - Callback `get_project_collections` integrado
  - Limpeza de órfãos ao remover projeto
  - Commit: `c6aa257`

- ✅ `project_modal.py`
  - Seção "Coleções" com visualização de badges
  - Callback funcional para obter coleções do projeto
  - Scroll do painel esquerdo corrigido (mousewheel binding)
  - Espaçamento final de 150px para melhor UX
  - Commits: `6c2f725`, `4a9d0b0`

#### Bugs Corrigidos (v3.4.0.7)
- ✅ FIX: Coleções não apareciam no modal (callback faltando)
- ✅ FIX: Scroll do painel esquerdo não funcionava (binding duplo adicionado)
- ✅ UX: Botões finais muito próximos do fim da janela (espaço adicionado)

---

## 📝 BACKLOG PRIORIZADO

### 🔴 PRIORIDADE ALTA

#### H-01: Filtro de Coleções na Sidebar
**Status**: 📝 Planejado  
**Dependências**: Nenhuma (F-08 completo)  
**Descrição**: Adicionar seção de coleções na sidebar com:
- Listagem de coleções com contador
- Clique para filtrar projetos da coleção
- Chips de filtro ativo
- Refresh automático quando coleção muda

#### H-02: Menu de Contexto - Adicionar a Coleção
**Status**: 📝 Planejado  
**Descrição**: Adicionar opção "Adicionar a Coleção" no menu de contexto do card:
- Dialog de seleção de coleções (checkboxes)
- Suporte a múltiplas coleções
- Indicador visual se projeto já está em coleções

---

### 🟡 PRIORIDADE MÉDIA

#### M-01: Export/Import de Coleções
**Status**: 📝 Planejado  
**Descrição**: Permitir exportar coleções em formato JSON separado

#### M-02: Drag & Drop para Coleções
**Status**: 📝 Planejado  
**Descrição**: Arrastar projetos para coleções na sidebar

#### M-03: Coleções Inteligentes (Smart Collections)
**Status**: 💡 Ideia  
**Descrição**: Coleções baseadas em regras (ex: "Todos com tag 'colorido'")

---

### 🟢 PRIORIDADE BAIXA

#### L-01: Ordenação de Projetos dentro de Coleções
**Status**: 💡 Ideia  
**Descrição**: Permitir reordenar manualmente projetos dentro de coleção

#### L-02: Compartilhar Coleção como Playlist
**Status**: 💡 Ideia  
**Descrição**: Gerar link/arquivo para compartilhar coleção

---

## 🚫 ÁREAS RESTRITAS (NUNCA TOCAR SEM AUTORIZAÇÃO)

### 🔒 Módulos de IA
- `ai/ollama_client.py` - Cliente Ollama
- `ai/image_analyzer.py` - Análise de imagens
- `ai/text_generator.py` - Geração de texto
- `ai/fallbacks.py` - Fallbacks
- `ai/analysis_manager.py` - Orquestrador de análises

**Motivo**: Sistema de IA está funcional e estável. Qualquer mudança requer testes extensivos.

### 🔒 Core do Banco de Dados
- `core/database.py` - Gerenciador de persistência

**Motivo**: Sistema de backup/recovery atômico testado. Mudanças podem causar corrupção.

### 🔒 Sistema de Thumbnails
- `core/thumbnail_cache.py` - Cache de thumbnails
- `core/thumbnail_preloader.py` - Pré-carregamento assíncrono

**Motivo**: Performance crítica. Sistema otimizado com threading complexo.

### ⚠️ Modificações Permitidas (com cuidado)
- `core/project_scanner.py` - Pode adicionar novos detectores
- `utils/*` - Pode adicionar novos utilitários

---

## 🎓 DÍVIDAS TÉCNICAS

### DT-01: Testes Unitários
**Prioridade**: 🟡 Média  
**Descrição**: Sistema não possui testes automatizados. Criar suite de testes para:
- CollectionsManager
- DatabaseManager
- ProjectScanner

### DT-02: Logs Estruturados
**Prioridade**: 🟢 Baixa  
**Descrição**: Migrar de logging simples para estruturado (JSON)

### DT-03: Type Hints Completos
**Prioridade**: 🟢 Baixa  
**Descrição**: Adicionar type hints em todos os módulos legacy

---

## 📊 MÉTRICAS DO PROJETO

### Código
- **Linhas de código**: ~15.500
- **Arquivos Python**: 42
- **Módulos principais**: 8
- **Dialogs/UI**: 12

### Banco de Dados
- **Projetos típicos**: 50-500
- **Tamanho médio DB**: 200-500KB
- **Backup automático**: ✅ Sim

### Performance
- **Startup**: < 2s (sem análise)
- **Renderização de grid**: < 500ms (36 cards)
- **Análise IA por projeto**: 3-5s

---

## 🔄 WORKFLOW DE ATUALIZAÇÃO DESTE ARQUIVO

1. **Após cada tarefa concluída**:
   - Mover de "EM ANDAMENTO" para "CONCLUÍDO"
   - Adicionar commit SHA
   - Atualizar timestamp

2. **Início de nova tarefa**:
   - Adicionar em "EM ANDAMENTO"
   - Definir prioridade
   - Quebrar em subtarefas

3. **Revisão semanal**:
   - Repriorizar backlog
   - Arquivar itens obsoletos
   - Adicionar novas ideias

---

## 📞 CONTATO

**Desenvolvedor**: digimar07  
**GitHub**: https://github.com/digimar07-cmyk/dev-scratch-pad  
**Versão do App**: 3.4.0.7 Stable  
**Branch**: main

---

**Última revisão**: Claude Sonnet 4.5 - 06/03/2026 13:22 BRT
