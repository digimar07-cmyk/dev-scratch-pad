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

### 🔴 **F-01: Modal de Projeto Completo**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🔴 Alto  
**Impacto:** 🔴 Core do app  
**Estilo Kent Beck:** ✅ Um campo por vez, testar entre cada  

**Objetivo:**
Expandir modal com recursos avançados:

1. **Galeria de imagens** (thumbs clicáveis)
   - Grid de thumbs na parte inferior
   - Click = abre imagem grande
   - Navegação ◀ / ▶

2. **Nome PT-BR editável**
   - Campo de texto acima da capa
   - Botão "✏️ Editar" → "Salvar"
   - Atualiza banco ao salvar

3. **Descrição editável**
   - Textarea grande (500px altura)
   - Scrollable
   - Salvar = atualiza `ai_description`

4. **Notas do usuário**
   - Campo livre "Minhas Notas"
   - Salva em `notes` (novo campo)
   - Textarea 300px altura

**Implementação Kent Beck:**

```python
# PASSO 1: Adicionar galeria (commit 1)
class ProjectModal:
    def _build_gallery(self):
        # Grid de thumbs (5 colunas)
        # Click = self._open_image_viewer(img_path)

# PASSO 2: Nome editável (commit 2)
def _add_editable_name(self):
    # Entry + botão Editar/Salvar
    # Salvar = self.database[path]["name_ptbr"] = new_name

# PASSO 3: Descrição editável (commit 3)
def _add_editable_description(self):
    # Text widget + scrollbar
    # Salvar = self.database[path]["ai_description"] = new_desc

# PASSO 4: Notas usuário (commit 4)
def _add_user_notes(self):
    # Text widget
    # Salvar = self.database[path]["notes"] = notes
```

**Arquivos afetados:**
- `ui/project_modal.py` (expandir layout)

**Critérios de aceitação:**
- ✅ Galeria mostra todas as imagens do projeto
- ✅ Nome PT-BR editável e salva
- ✅ Descrição editável e salva
- ✅ Notas do usuário persistem
- ✅ Layout não quebra com conteúdo longo

---

## 🟡 FILA DE ESPERA

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

**Arquivos afetados:**
- `ui/main_window.py` (método `clean_orphans()`)
- `ui/header.py` (botão no menu "Dashboard")

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

**Arquivos afetados:**
- `ui/main_window.py` (adicionar debounce)
- `ui/header.py` (bind keypress ao invés de Return)

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
| ✅ **DOC** | Documentação inicial | `VERSION_HISTORY.md`, `MIGRATION_v3.3_to_v3.4.md`, `README.md`, `BACKLOG.md` | `1006409` |
| ✅ **PERSONA** | Persona Kent Beck | `DEVELOPER_PERSONA.md` + instruções no README/BACKLOG | `95708c0` |
| ✅ **F-06** | Ordenação configurável | Menu dropdown com 7 opções (data, nome, origem, status). JÁ IMPLEMENTADO no código base! | (código base) |
| ✅ **S-03** | Thumbnail assíncrono | `ThreadPoolExecutor` + cache LRU (300 imgs) + 4 workers. Speedup 13.3x. JÁ IMPLEMENTADO! | (código base) |

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
Laserflix_v3.4.0.0_F-01: Modal completo - Galeria de imagens

- Adicionado grid de thumbs (5 colunas)
- Click = abre image viewer
- Navegação ◀ / ▶
- Testado com 20 imagens: instantâneo
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
**Última atualização:** 05/03/2026 19:52 BRT
