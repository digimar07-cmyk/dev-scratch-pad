# 📋 LASERFLIX v3.4.0.0 — BACKLOG MASTER OFICIAL

> Lista única, canônica e definitiva de tarefas da v3.4.
> Atualizada a cada item concluído.
> Regra: **um item por vez**, confirma ✅ antes do próximo.

---

## 🧑‍💻 PERSONA DE DESENVOLVIMENTO

🔴 **IMPORTANTE:** Este projeto segue a filosofia **Kent Beck** (Extreme Programming).

**ANTES de iniciar qualquer tarefa, leia:**
- **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** → Filosofia OBRIGATÓRIA

**Princípios Kent Beck aplicados:**
- ✅ **Simplicidade radical:** "Faça a coisa mais simples que funciona"
- ✅ **Baby steps:** Um commit = uma mudança
- ✅ **Refatoração contínua:** Deixe melhor do que encontrou
- ✅ **Testar sempre:** Manualmente após cada mudança
- ❌ **NUNCA antecipar:** YAGNI (You Aren't Gonna Need It)
- ❌ **NUNCA criar abstrações** desnecessárias

> **Workflow:** ENTENDER → PLANEJAR → IMPLEMENTAR → REFATORAR → DOCUMENTAR

---

## 👉 PRÓXIMA TAREFA

### 🔴 **F-06: Ordenação Configurável**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Organização  
**Estilo Kent Beck:** ✅ Simples, direto, funcional  

**Objetivo:**
Menu de ordenação no header (ao lado da busca) com 7 opções:

- 📅 **Recentes** → Data de importação (DESC)
- 📅 **Antigos** → Data de importação (ASC)
- 🔤 **A→Z** → Nome alfabético (ASC)
- 🔥 **Z→A** → Nome alfabético (DESC)
- 🏛️ **Origem** → Agrupa por origem + nome
- 🤖 **Analisados** → Projetos analisados primeiro
- ⏳ **Pendentes** → Projetos não analisados primeiro

**Implementação (Kent Beck style):**

1. **Ler código atual:** `ui/main_window.py`
2. **Adicionar menu:** `ttk.Combobox` no header (simples)
3. **Criar estado:** `self.current_sort = "date_desc"` (padrão)
4. **Método de ordenação:** `_sort_projects(projects)` (direto, sem abstração)
5. **Integrar:** Chamar ANTES da paginação
6. **Testar:** Todas as 7 opções manualmente

**Arquivos afetados:**
- `ui/main_window.py` (linhas ~100-150 + novo método)

**Critérios de aceitação:**
- ✅ Dropdown visível e responsivo
- ✅ Ordenação ANTES da paginação
- ✅ Estado persiste ao mudar de página
- ✅ Compatível com filtros ativos
- ✅ Performance: ordenação instantânea até 500 projetos

**Código exemplo (Kent Beck style):**
```python
# Simples, direto, funcional
def _sort_projects(self, projects):
    """Ordena lista de projetos. Simples assim."""
    if not projects:
        return projects
    
    # Dicionário mapeia comportamentos (Kent Beck gosta)
    if self.current_sort == "date_desc":
        return sorted(projects, key=lambda p: p[1].get("added_date", ""), reverse=True)
    elif self.current_sort == "name_asc":
        return sorted(projects, key=lambda p: p[1].get("name", "").lower())
    # ... outras opções ...
    return projects

# Na display_projects(), ANTES da paginação:
all_filtered = self._sort_projects(all_filtered)  # ← Uma linha. Perfeito.
```

**Código completo em:** `MIGRATION_v3.3_to_v3.4.md` (linhas 200-300)

---

## 🟡 FILA DE ESPERA

### **S-03: Thumbnail Carregamento Assíncrono**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🟡 Médio  
**Impacto:** 🔴 Performance + UX  
**Estilo Kent Beck:** ✅ `queue.Queue` é simples e funciona  

**Problema:**
Thumbnails carregam sincronamente na thread principal, travando a UI.

**Solução Kent Beck:**
```python
# Simples: fila + workers
import queue
import threading

class ThumbnailPreloader:
    def __init__(self, max_workers=4):
        self.queue = queue.Queue()  # Simples
        self.cache = {}  # Direto
        # 4 threads fazendo o trabalho
        for _ in range(max_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
    
    def preload_single(self, project_path, callback):
        # Já tem? Retorna. Não tem? Enfileira.
        if project_path in self.cache:
            callback(project_path, self.cache[project_path])
        else:
            self.queue.put((project_path, callback))
```

**Kent Beck diz:** "Funciona? Então funciona. Não precisa complicar."

**Arquivos afetados:**
- `core/thumbnail_preloader.py` (NOVO, ~80 linhas)
- `ui/project_card.py` (usar `preload_single()`)
- `ui/main_window.py` (instanciar `ThumbnailPreloader`)

---

### **F-01: Modal de Projeto Completo**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🔴 Alto  
**Impacto:** 🔴 Core do app  

**Objetivo:**
Expandir modal com:
- Galeria de imagens (thumbs clicáveis)
- Nome PT-BR editável
- Descrição editável
- Notas do usuário

**Kent Beck faria:** Um campo por vez. Testar entre cada.

---

### **F-03: Limpeza de Órfãos**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Integridade dados  

**Kent Beck style:**
```python
def clean_orphans(self):
    # Simples: lista os inválidos
    orphans = [p for p in self.database if not os.path.isdir(p)]
    
    # Nenhum? Avisar e sair.
    if not orphans:
        messagebox.showinfo("✅ Banco limpo", "Nenhum órfão!")
        return
    
    # Tem? Perguntar e remover.
    if messagebox.askyesno("🗑️ Limpar", f"{len(orphans)} órfão(s).\n\nRemover?"):
        for p in orphans:
            self.database.pop(p)
        self.db_manager.save_database()
        self.display_projects()
```

**Kent Beck:** "10 linhas. Funciona. Perfeito."

---

### **F-04: Busca em Tempo Real com Debounce**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 UX  

**Kent Beck:**
```python
from threading import Timer

class LaserflixMainWindow:
    def _on_search_keypress(self, event=None):
        # Cancela timer anterior (se existir)
        if self.search_timer:
            self.search_timer.cancel()
        
        # Novo timer: 300ms
        self.search_timer = Timer(0.3, self._execute_search)
        self.search_timer.start()
```

**Kent Beck:** "Timer + callback. Simples. Não precisa de biblioteca externa."

---

## 🏆 FINALIZADO NA v3.4

| # | Item | Descrição | Commit |
|---|---|---|---|
| ✅ **DOC** | Documentação inicial | `VERSION_HISTORY.md`, `MIGRATION_v3.3_to_v3.4.md`, `README.md`, `BACKLOG.md` | `1006409` |
| ✅ **PERSONA** | Persona Kent Beck | `DEVELOPER_PERSONA.md` + instruções no README/BACKLOG | (pendente) |

---

## 🏆 HERDADO DA v3.3 (JÁ COMPLETO)

### Estilo Kent Beck em ação:

- ✅ **HOT-08:** Paginação simples (ao invés de Virtual Scroll complexo)
- ✅ **HOT-10:** Normalização de nome (ao invés de algoritmo sofisticado)
- ✅ **HOT-13:** 36 cards (ao invés de cálculo dinâmico)
- ✅ **Análise sequencial:** Um depois do outro (ao invés de paralelo complexo)

**Kent Beck:** "Tudo funciona. Tudo simples. Tudo testado."

---

## 🔒 ZONAS PROTEGIDAS

| Zona | Arquivos |
|---|---|
| 🔒 **IA** | `ai/ollama_client.py` · `ai/analysis_manager.py` · `ai/text_generator.py` · `ai/image_analyzer.py` · `ai/fallbacks.py` · `ai/keyword_maps.py` |
| 🔒 **Importação** | `ui/import_mode_dialog.py` · `ui/recursive_import_integration.py` · `ui/import_preview_dialog.py` · `ui/duplicate_resolution_dialog.py` · `utils/recursive_scanner.py` · `utils/duplicate_detector.py` |

> **Kent Beck:** "Se funciona, NÃO mexa. Se precisar mexer, entenda COMPLETAMENTE antes."

---

## 🎯 REGRAS DO JOGO (Kent Beck Edition)

### ⚠️ NUNCA:
1. ❌ Modificar 5+ arquivos de uma vez
2. ❌ Criar abstração "para o futuro"
3. ❌ Commitar sem testar
4. ❌ Antecipar requisitos (YAGNI)
5. ❌ Fazer código "esperto" demais

### ✅ SEMPRE:
1. ✅ Ler código existente ANTES de modificar
2. ✅ Fazer a coisa mais simples que funciona
3. ✅ Testar manualmente após CADA mudança
4. ✅ Refatorar quando código cheira mal
5. ✅ Ler **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** no início de cada sessão

### 📝 Formato de commit:
```bash
Laserflix_v3.4.0.0_F-06: Ordenação configurável (7 opções)

- Adicionado ttk.Combobox no header
- Método _sort_projects() com 7 modos
- Integrado em display_projects()
- Testado com 200 projetos: instantâneo
```

### 📖 Antes de escrever código:
```
❓ Qual a coisa mais SIMPLES que resolve isso?
❓ Estou antecipando algo que não preciso agora?
❓ Posso fazer em menos linhas sem perder clareza?
❓ Os nomes expressam a intenção?
```

---

## 📚 DOCUMENTAÇÃO OBRIGATÓRIA

### 🔴 LEIA PRIMEIRO (sempre!):
1. **[DEVELOPER_PERSONA.md](DEVELOPER_PERSONA.md)** → Filosofia Kent Beck
2. **[BACKLOG.md](BACKLOG.md)** → Este arquivo (tarefas)

### Complementares:
3. **[VERSION_HISTORY.md](VERSION_HISTORY.md)** → Histórico
4. **[MIGRATION_v3.3_to_v3.4.md](MIGRATION_v3.3_to_v3.4.md)** → Migração
5. **[README.md](README.md)** → Visão geral

---

## 🗣️ FRASES KENT BECK PARA MEDITAR

> **"Make it work, make it right, make it fast."**  
> (Nessa ordem!)

> **"Do the simplest thing that could possibly work."**  
> (Sempre!)

> **"You aren't gonna need it."**  
> (YAGNI é real)

> **"When you feel pain, that's telling you something."**  
> (Dor no código = design problem)

---

**Persona ativa:** Kent Beck (Extreme Programming)  
**Mantra:** "Simplicidade radical. Baby steps. Refatoração contínua."  
**Última atualização:** 05/03/2026 19:20 BRT
