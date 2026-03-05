# 📋 LASERFLIX v3.4.0.0 — BACKLOG MASTER OFICIAL

> Lista única, canônica e definitiva de tarefas da v3.4.
> Atualizada a cada item concluído.
> Regra: **um item por vez**, confirma ✅ antes do próximo.

---

## 👉 PRÓXIMA TAREFA

### 🔴 **F-06: Ordenação Configurável**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Organização  

**Objetivo:**
Menu de ordenação no header (ao lado da busca) com 7 opções:

- 📅 **Recentes** → Data de importação (DESC)
- 📅 **Antigos** → Data de importação (ASC)
- 🔤 **A→Z** → Nome alfabético (ASC)
- 🔥 **Z→A** → Nome alfabético (DESC)
- 🏛️ **Origem** → Agrupa por origem + nome
- 🤖 **Analisados** → Projetos analisados primeiro
- ⏳ **Pendentes** → Projetos não analisados primeiro

**Implementação:**

1. Adicionar `ttk.Combobox` no header (após busca)
2. Criar `self.current_sort = "date_desc"` (padrão)
3. Criar método `_sort_projects(projects)` que retorna lista ordenada
4. Integrar em `display_projects()` ANTES da paginação
5. Bind `<<ComboboxSelected>>` para atualizar view

**Arquivos afetados:**
- `ui/main_window.py` (linhas ~100-150 + novo método)

**Critérios de aceitação:**
- ✅ Dropdown visível e responsivo
- ✅ Ordenação ANTES da paginação (não dentro da página)
- ✅ Estado persiste ao mudar de página
- ✅ Compatível com filtros ativos
- ✅ Performance: ordenação instantânea até 500 projetos

**Código de exemplo:**
```python
def _on_sort_change(self, event=None):
    label_to_key = {
        "📅 Recentes": "date_desc",
        "📅 Antigos": "date_asc",
        # ...
    }
    selected_label = self.sort_menu.get()
    self.current_sort = label_to_key.get(selected_label, "date_desc")
    self.current_page = 1
    self.display_projects()

def _sort_projects(self, projects):
    if self.current_sort == "date_desc":
        return sorted(projects, key=lambda p: p[1].get("added_date", ""), reverse=True)
    elif self.current_sort == "name_asc":
        return sorted(projects, key=lambda p: p[1].get("name", "").lower())
    # ...
    return projects

def display_projects(self):
    all_filtered = [(p, self.database[p]) for p in self.get_filtered_projects()]
    all_filtered = self._sort_projects(all_filtered)  # ← AQUI!
    # ... paginação ...
```

---

## 🟡 FILA DE ESPERA

### **S-03: Thumbnail Carregamento Assíncrono**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🟡 Médio  
**Impacto:** 🔴 Performance + UX  

**Problema:**
Thumbnails carregam sincronamente na thread principal, travando a UI.

**Solução:**
- Criar `core/thumbnail_preloader.py`
- `queue.Queue` + 4 threads workers
- Cache interno (`path → PhotoImage`)
- Callback assíncrono para atualizar card

**Arquivos afetados:**
- `core/thumbnail_preloader.py` (NOVO)
- `ui/project_card.py` (usar `preload_single()`)
- `ui/main_window.py` (instanciar `ThumbnailPreloader`)

**Critérios de aceitação:**
- ✅ UI não trava durante carregamento
- ✅ Cards renderizam com placeholder → atualizam quando thumbnail carrega
- ✅ Cache persiste durante sessão
- ✅ Performance: 100 cards em < 2s

---

### **F-01: Modal de Projeto Completo**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🔴 Alto  
**Impacto:** 🔴 Core do app  

**Objetivo:**
Expandir modal com:
- Galeria de imagens (thumbs clicáveis)
- Nome PT-BR editável (campo de texto)
- Descrição editável (textarea grande)
- Notas do usuário (campo livre)
- Botão "Salvar alterações"

**Arquivos afetados:**
- `ui/project_modal.py` (expandir layout)

---

### **F-03: Limpeza de Órfãos**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Integridade dados  

**Objetivo:**
Botão "Limpar órfãos" que remove entradas do banco cujo `path` não existe mais em disco.

**Implementação:**
```python
def clean_orphans(self):
    orphans = [p for p in self.database if not os.path.isdir(p)]
    if not orphans:
        messagebox.showinfo("✅ Banco limpo", "Nenhum órfão encontrado!")
        return
    if messagebox.askyesno("🗑️ Limpar órfãos", f"Encontrados {len(orphans)} projeto(s).\n\nRemover?"):
        for p in orphans:
            self.database.pop(p)
        self.db_manager.save_database()
        self.display_projects()
```

**Arquivos afetados:**
- `ui/main_window.py` (método `clean_orphans()`)
- `ui/header.py` (botão no menu "Dashboard")

---

### **F-04: Busca em Tempo Real com Debounce**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 UX  

**Objetivo:**
Busca atualiza automaticamente após 300ms de inatividade (sem precisar apertar Enter).

**Implementação:**
```python
from threading import Timer

class LaserflixMainWindow:
    def __init__(self):
        self.search_timer = None
    
    def _on_search_keypress(self, event=None):
        if self.search_timer:
            self.search_timer.cancel()
        self.search_timer = Timer(0.3, self._execute_search)
        self.search_timer.start()
    
    def _execute_search(self):
        self.search_query = self.search_var.get().strip().lower()
        self.current_page = 1
        self.display_projects()
```

**Arquivos afetados:**
- `ui/main_window.py` (adicionar debounce)

---

### **F-05: Badge de Status de Análise**

**Prioridade:** 🟡 BAIXA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 UX/Info  

**Objetivo:**
Badge visual no card indicando:
- 🤖 **IA** → Analisado com Ollama
- ⚡ **Fallback** → Análise sem IA
- ⏳ **Pendente** → Não analisado

**Arquivos afetados:**
- `ui/project_card.py` (adicionar badge)

---

### **F-07: Filtro Multi-Critério Simultâneo**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟡 Médio  
**Impacto:** 🟠 Organização  

**Objetivo:**
Permitir múltiplos filtros ativos ao mesmo tempo (chips empilháveis com AND lógico).

Exemplo:
```
[Creative Fabrica ×] + [Natal ×] + [decorativo ×] = 15 projetos
```

**Arquivos afetados:**
- `ui/main_window.py` (lógica de filtros)
- `ui/header.py` (UI de chips)

---

## 🔵 BLOCO O — ORGANIZAÇÃO E PODER

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ☐ **O-01** | Sistema de Coleções/Playlists | 🔴 Game Changer | 🟡 Médio | Semana 3 |
| ☐ **O-02** | Export CSV/Excel | 🟠 Utilidade | 🟢 Baixo | Semana 3 |
| ☐ **O-03** | Atalhos de teclado (`Ctrl+F`, `Ctrl+A`, `F5`, `Espaço`, `Del`) | 🟠 UX/Power User | 🟢 Baixo | Semana 3 |
| ☐ **O-04** | Fila de análise com prioridade | 🟡 Workflow | 🟡 Médio | Semana 3 |

---

## 🎨 BLOCO V — EXPERIÊNCIA VISUAL

| # | O que fazer | Impacto | Esforço | Prioridade |
|---|---|---|---|---|
| ☐ **V-01** | Toast Notifications (não-bloqueantes) | 🟠 UX | 🟢 Baixo | Semana 3 |
| ☐ **V-02** | Animação hover nos cards | 🟠 Visual | 🟢 Baixo | Semana 3 |
| ☐ **V-03** | Modo Lista vs Modo Galeria | 🟠 UX | 🟡 Médio | Semana 3 |
| ☐ **V-04** | Score de qualidade no card | 🟡 Gamificação | 🟢 Baixo | Semana 4 |

---

## 🚀 BLOCO N — NOVAS FUNÇÕES

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ☐ **N-01** | Dashboard de Estatísticas | 🟠 Valor percebido | 🟡 Médio | v3.5 |
| ☐ **N-02** | Modo Etsy — Gerador de Listing | 🔴 Negócio | 🟡 Médio | v3.5 |
| ☐ **N-03** | Gerador de Ficha Técnica PDF | 🟠 Utilidade | 🟡 Médio | v3.5 |

---

## 🌌 BLOCO BM — BLOWMIND

| # | O que fazer | Impacto | Esforço | Versão alvo |
|---|---|---|---|---|
| ☐ **BM-01** | Recomendações "Para Você" via embeddings | 🔴 Diferencial IA | 🔴 Alto | v3.6 |
| ☐ **BM-02** | Modo Vitrine/Slideshow | 🟠 Valor comercial | 🟢 Baixo | v3.5 |
| ☐ **BM-03** | Linha do Tempo (calendário anual) | 🟡 Visual/Motivação | 🟡 Médio | v3.6 |

---

## 🏆 FINALIZADO NA v3.4

| # | Item | Descrição | Commit |
|---|---|---|---|
| ✅ **DOC** | Documentação inicial | Criado `VERSION_HISTORY.md`, `MIGRATION_v3.3_to_v3.4.md`, atualizado `README.md` e `BACKLOG.md` | (pendente) |

---

## 🏆 HERDADO DA v3.3 (JÁ COMPLETO)

### BLOCO HOT (Correções Críticas):
- ✅ HOT-01 a HOT-13 (modal, duplicatas, paginação, categorias, scrollbar, etc)

### BLOCO L (Limpeza):
- ✅ L-02, L-04, L-07 (BANNED_STRINGS, aliases, VERSION)

### BLOCO S (Estabilidade):
- ✅ S-01 (Configuração Modelos IA)
- ✅ S-02 (Virtual Scroll → depois substituído por paginação)
- ✅ S-04 (Refatoração main_window)

### BLOCO F (Funcionalidades):
- ✅ F-02 (Remoção individual)
- ✅ SEL-01 (Seleção em massa)

### FEATURES:
- ✅ Análise IA Sequencial (categorias+tags → descrições)
- ✅ Importação Recursiva (3 modos + dedup + preview)

---

## 🔒 ZONAS PROTEGIDAS

| Zona | Arquivos |
|---|---|
| 🔒 **IA** | `ai/ollama_client.py` · `ai/analysis_manager.py` · `ai/text_generator.py` · `ai/image_analyzer.py` · `ai/fallbacks.py` · `ai/keyword_maps.py` |
| 🔒 **Importação** | `ui/import_mode_dialog.py` · `ui/recursive_import_integration.py` · `ui/import_preview_dialog.py` · `ui/duplicate_resolution_dialog.py` · `utils/recursive_scanner.py` · `utils/duplicate_detector.py` |

> **Regra inviolável:** Qualquer toque em zona protegida requer alerta + autorização expressa antes de escrever.

---

## 🎯 REGRAS DO JOGO

1. Esta lista é **a única lista**. Qualquer nova sessão começa aqui.
2. **Um item por vez** — confirma ✅ antes do próximo.
3. Prefixo de versão nos commits: `Laserflix_v3.4.0.0_F-06`, `_S-03` etc.
4. **Leitura antes de escrever** — sempre lemos o arquivo atual antes de gerar código.
5. Nenhum item é pulado sem instrução expressa.
6. **ANÁLISE DE IMPACTO OBRIGATÓRIA** para zonas protegidas.
7. **RISCO vs BENEFÍCIO**: Tarefas teóricas em zonas críticas são canceladas se sistema funciona perfeitamente.
8. **ATUALIZAR BACKLOG**: Toda task concluída com sucesso é registrada na seção 🏆 FINALIZADO.

---

**Última atualização:** 05/03/2026 19:06 BRT
