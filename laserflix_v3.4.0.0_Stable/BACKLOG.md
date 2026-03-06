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

### 🟠 **F-03: Limpeza de Órfãos**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 Integridade dados  
**Estilo Kent Beck:** ✅ Simples e direto  

**Objetivo:**
Remover projetos do banco de dados cujas pastas não existem mais no disco.

**Implementação Kent Beck (simples):**

```python
class LaserflixMainWindow:
    def clean_orphans(self):
        """Remove projetos órfãos (pastas deletadas do disco)."""
        # 1. LISTA OS INVÁLIDOS
        orphans = [p for p in self.database if not os.path.isdir(p)]
        
        # 2. NENHUM? AVISAR E SAIR
        if not orphans:
            messagebox.showinfo(
                "✅ Banco limpo",
                "Nenhum projeto órfão encontrado!\n\nTodos os caminhos são válidos."
            )
            return
        
        # 3. TEM? PERGUNTAR E REMOVER
        if messagebox.askyesno(
            "🗑️ Limpeza de Órfãos",
            f"Encontrados {len(orphans)} projeto(s) com pastas deletadas.\n\n"
            f"Remover do banco de dados?\n\n"
            f"(Os arquivos no disco NÃO serão afetados)",
            icon="warning"
        ):
            # Remove do banco
            for path in orphans:
                self.database.pop(path)
            
            # Salva + atualiza UI
            self.db_manager.save_database()
            self.sidebar.refresh(self.database)
            self.display_projects()
            
            # Feedback
            self.status_bar.config(
                text=f"✅ {len(orphans)} projeto(s) órfão(s) removido(s)."
            )
            
            self.logger.info(f"🧹 Limpeza: {len(orphans)} órfãos removidos")
```

**Adicionar botão no menu:**
```python
# ui/header.py - No menu "Dashboard"
menu.add_command(
    label="🧹 Limpar Órfãos",
    command=callbacks["on_clean_orphans"]
)
```

**Arquivos afetados:**
- `ui/main_window.py` (adicionar método `clean_orphans()`)
- `ui/header.py` (adicionar botão no menu "Dashboard")

**Critérios de aceitação:**
- ✅ Detecta pastas deletadas
- ✅ Mostra contador de órfãos
- ✅ Pede confirmação antes de remover
- ✅ Atualiza UI após limpeza
- ✅ Feedback visual no status bar
- ✅ Funciona mesmo com 1000+ projetos

---

## 🟡 FILA DE ESPERA (alta prioridade)

### **F-04: Busca em Tempo Real com Debounce**

**Prioridade:** 🟠 MÉDIA  
**Esforço:** 🟢 Baixo  
**Impacto:** 🟠 UX  

**Kent Beck:**
```python
from threading import Timer

class LaserflixMainWindow:
    def __init__(self, root):
        # ...
        self.search_timer = None  # Timer para debounce
    
    def _on_search_keypress(self, event=None):
        # Cancela timer anterior (se existir)
        if self.search_timer:
            self.search_timer.cancel()
        
        # Novo timer: 300ms
        self.search_timer = Timer(0.3, self._execute_search)
        self.search_timer.start()
    
    def _execute_search(self):
        """Executa busca (chamado pelo timer)."""
        self.search_query = self.search_var.get().strip().lower()
        self.current_page = 1
        self.display_projects()
```

**Arquivos afetados:**
- `ui/main_window.py` (adicionar debounce)
- `ui/header.py` (bind `<KeyRelease>` ao invés de `<Return>`)

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

> Features "nice-to-have" que não são core do app.
> Implementar apenas se tempo/energia sobrarem.

### **F-01.2: Modal - Nome PT-BR Editável**

**Prioridade:** 🟢 MUITO BAIXA  
**STATUS:** ⚠️ Implementação anterior FALHOU (ImportError)  
**Decisão:** Modal funciona bem sem isso.  

---

### **F-01.3: Modal - Descrição Editável**

**Prioridade:** 🟢 MUITO BAIXA  
**Objetivo:** Textarea editável para `ai_description`  
**Decisão:** Usuário pode editar manualmente no JSON se precisar. Não é prioridade.  

---

### **F-01.4: Modal - Notas do Usuário**

**Prioridade:** 🟢 MUITO BAIXA  
**Objetivo:** Campo livre para notas pessoais  
**Decisão:** Não é core. Deixar para v3.5 se houver demanda real.  

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
Laserflix_v3.4.0.0_F-03: Limpeza de órfãos

- Método clean_orphans() em main_window.py
- Botão "🧹 Limpar Órfãos" no menu Dashboard
- Detecta pastas deletadas do disco
- Testado com 500 projetos: instantâneo
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
**Última atualização:** 05/03/2026 21:30 BRT
