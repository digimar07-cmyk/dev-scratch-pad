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

### 🔴 **F-01.3: Modal - Descrição Editável**

**Prioridade:** 🔴 ALTA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 UX  
**Estilo Kent Beck:** ✅ Um campo por vez, testar entre cada  

**Objetivo:**
Permitir edição da descrição gerada pela IA diretamente no modal.

**Implementação Kent Beck (simples):**

```python
class ProjectModal:
    def _build_editable_description(self, parent_frame):
        # Frame container
        desc_frame = tk.Frame(parent_frame, bg=BG_PRIMARY)
        desc_frame.pack(fill="both", expand=True, pady=10)
        
        # Label "Descrição"
        tk.Label(desc_frame, text="📝 Descrição do Projeto",
                 font=("Arial", 12, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY
                 ).pack(anchor="w", pady=(0, 5))
        
        # Textarea grande (500px altura) com scrollbar
        desc_text = tk.Text(desc_frame, height=20, width=60,
                           bg=BG_CARD, fg=FG_PRIMARY,
                           font=("Arial", 10), wrap="word")
        scrollbar = tk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.config(yscrollcommand=scrollbar.set)
        
        # Carrega texto existente
        current_desc = self.database[self.path].get("ai_description", "")
        desc_text.insert("1.0", current_desc)
        
        desc_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão Salvar
        def save_description():
            new_desc = desc_text.get("1.0", "end-1c").strip()
            self.database[self.path]["ai_description"] = new_desc
            self.db_manager.save_database()
            messagebox.showinfo("✅ Salvo", "Descrição atualizada com sucesso!")
        
        tk.Button(desc_frame, text="💾 Salvar Descrição",
                  command=save_description,
                  bg=ACCENT_GREEN, fg=FG_PRIMARY,
                  font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2",
                  padx=14, pady=8
                  ).pack(pady=(10, 0))
```

**Arquivos afetados:**
- `ui/project_modal.py` (adicionar textarea editável)

**Critérios de aceitação:**
- ✅ Textarea mostra descrição atual
- ✅ Permite edição de texto
- ✅ Botão salva no banco de dados
- ✅ Feedback visual após salvar
- ✅ Layout não quebra com texto longo

---

## 🟡 FILA DE ESPERA (alta prioridade)

### **F-01.4: Modal - Notas do Usuário**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Workflow  

**Kent Beck:**
```python
def _add_user_notes(self, parent_frame):
    # Campo livre "Minhas Notas"
    notes_frame = tk.Frame(parent_frame, bg=BG_PRIMARY)
    notes_frame.pack(fill="both", pady=10)
    
    tk.Label(notes_frame, text="📋 Minhas Notas",
             font=("Arial", 11, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY
             ).pack(anchor="w", pady=(0, 5))
    
    notes_text = tk.Text(notes_frame, height=10, width=60,
                        bg=BG_CARD, fg=FG_PRIMARY,
                        font=("Arial", 9), wrap="word")
    notes_text.insert("1.0", self.database[self.path].get("notes", ""))
    notes_text.pack(fill="both", expand=True)
    
    # Salvar
    def save_notes():
        self.database[self.path]["notes"] = notes_text.get("1.0", "end-1c").strip()
        self.db_manager.save_database()
        messagebox.showinfo("✅ Salvo", "Notas salvas!")
    
    tk.Button(notes_frame, text="💾 Salvar Notas",
              command=save_notes, bg=ACCENT_GREEN, fg=FG_PRIMARY,
              relief="flat", cursor="hand2", padx=12, pady=6
              ).pack(pady=(5, 0))
```

**Arquivos afetados:**
- `ui/project_modal.py` (adicionar notas)

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

## 📌 BLOCO PENDURICALHOS (baixa prioridade)

### **F-01.2: Modal - Nome PT-BR Editável**

**Prioridade:** 🟢 MUITO BAIXA (📌 PENDURICALHO)  
**Esforço:** 🟡 Médio  
**Impacto:** 🟡 Nice-to-have  

**STATUS:** ⚠️ **Implementação anterior FALHOU**
- Tentativa de implementar tradução automática (EN → PT-BR)
- Problema: ImportError (módulos `Translator` não funcionaram)
- **REVERTIDO** para v3.4.0.0 estável
- **Decisão:** Adiar para depois de todas features principais

**Objetivo (para refazer no futuro):**
Campo editável para nome traduzido em PT-BR:

```python
class ProjectModal:
    def _build_editable_name(self, parent_frame):
        # Entry + botão Editar/Salvar
        name_entry = tk.Entry(parent_frame, width=50)
        name_entry.insert(0, self.database[path].get("name_ptbr", ""))
        
        def save_name():
            new_name = name_entry.get().strip()
            self.database[path]["name_ptbr"] = new_name
            self.db_manager.save_database()
        
        tk.Button(parent_frame, text="💾 Salvar", command=save_name).pack()
```

**Decisão Kent Beck:**
> "Não é prioridade. Modal funciona bem sem isso. Deixa pro final quando tudo mais estiver pronto."

**Arquivos afetados (quando refazer):**
- `ui/project_modal.py` (adicionar campo editável)
- `ai/text_generator.py` (SE decidir adicionar tradução automática via Ollama)

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
Laserflix_v3.4.0.0_F-01.3: Modal - Descrição editável

- Textarea 500px altura com scrollbar
- Botão salvar atualiza banco de dados
- Feedback visual após salvar
- Testado com 5000+ caracteres: OK
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
3. **[REJECTED_IDEAS.md](REJECTED_IDEAS.md)** → Ideias descartadas (NÃO implementar!)

### Complementares:
4. **[VERSION_HISTORY.md](VERSION_HISTORY.md)** → Histórico
5. **[MIGRATION_v3.3_to_v3.4.md](MIGRATION_v3.3_to_v3.4.md)** → Migração
6. **[README.md](README.md)** → Visão geral

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
**Última atualização:** 05/03/2026 21:27 BRT
