# 🚀 MIGRAÇÃO v3.3.0.0 → v3.4.0.0

---

## 📊 RESUMO EXECUTIVO

**Tipo de migração:** Cópia limpa (fresh copy)  
**Compat banco de dados:** ✅ 100% compatível  
**Ação necessária:** NENHUMA (zero breaking changes)  

---

## ✅ O QUE JÁ ESTÁ NA v3.4

### 📦 Features Herdadas da v3.3:

#### 1. **PAGINAÇÃO SIMPLES (HOT-08/HOT-13)**
- 36 cards por página (6 linhas × 6 colunas)
- Navegação: ⏮ ◀ "Pág X/Y" ▶ ⏭
- Atalhos: `Home`/`End`/`Arrows`

**Arquivos:**
- `ui/main_window.py` (linhas 150-250)
- `config/card_layout.py` (`COLS=6`, `items_per_page=36`)

---

#### 2. **CATEGORIAS/TAGS VISÍVEIS NOS CARDS (HOT-09)**
- 3 primeiras categorias (badges coloridos)
- 5 primeiras tags (clicáveis)
- Click = aplica filtro instantâneo

**Arquivos:**
- `ui/project_card.py` (linhas 80-150)

---

#### 3. **SELEÇÃO EM MASSA (SEL-01)**
- Botão `☑️ Selecionar` no header
- Barra flutuante com contadores
- Checkbox nos cards
- Remoção múltipla (confirmação dupla)

**Arquivos:**
- `ui/main_window.py` (linhas 300-400)
- `ui/header.py` (botão de seleção)

---

#### 4. **ANÁLISE IA SEQUENCIAL**
- Após importação: pergunta se quer analisar
- Executa SEQUENCIALMENTE:
  1. Categorias + Tags (`analysis_manager.analyze_batch()`)
  2. Aguarda conclusão (`_wait_for_analysis_manager()`)
  3. Descrições (`text_generator.generate_description()`)

**Arquivos:**
- `ui/recursive_import_integration.py` (linhas 250-350)

---

#### 5. **IMPORTAÇÃO RECURSIVA AVANÇADA**
- 3 modos: **hybrid**, **pure**, **simple**
- Detecção de duplicatas CONTRA database existente
- Dialog de resolução manual (skip/replace/merge)
- Preview antes de importar

**Arquivos:**
- `ui/recursive_import_integration.py`
- `ui/import_mode_dialog.py`
- `ui/duplicate_resolution_dialog.py`
- `utils/recursive_scanner.py`
- `utils/duplicate_detector.py`

---

#### 6. **SCROLLBAR VERTICAL (HOT-12)**
- Canvas scrollable para o grid
- MouseWheel funcional
- Responsível por cards mais altos

**Arquivos:**
- `ui/main_window.py` (linhas 100-130)

---

#### 7. **CONFIGURAÇÃO MODELOS IA (S-01)**
- Dialog de seleção de modelos Ollama
- Salva em `laserflix_config.json`
- 3 papéis: `image_vision`, `text_quality`, `text_fast`

**Arquivos:**
- `ui/model_settings_dialog.py`
- `core/database.py` (`save_config()`, `load_config()`)

---

#### 8. **REMOÇÃO DE PROJETOS (F-02)**
- Botão `🗑️ Remover` no modal
- Confirmação dupla
- NÃO apaga arquivos do disco
- Apenas remove do banco

**Arquivos:**
- `ui/project_modal.py` (linhas 200-250)
- `ui/main_window.py` (`remove_project()` method)

---

#### 9. **PROMPT IA CORRIGIDO (HOT-11)**
- Exige MÍNIMO 10 categorias (3 obrigatórias + 7 opcionais)
- Fallback retorna 12 categorias
- Sistema de limitação por tipo de produto

**Arquivos:**
- `ai/text_generator.py` (prompt system)
- `ai/fallbacks.py` (categorias default)

---

#### 10. **DUPLICATAS CORRIGIDAS (HOT-10/10b)**
- Comparação por nome normalizado
- Detecta duplicatas entre métodos (hybrid → pure → simple)
- Dialog recebe campos corretos (`normalized_name`, `name`)

**Arquivos:**
- `utils/duplicate_detector.py`
- `ui/recursive_import_integration.py` (linhas 100-150)

---

## 🔴 O QUE PRECISA SER IMPLEMENTADO NA v3.4

### 🔴 TAREFA IMEDIATA: **F-06 - Ordenação Configurável**

**Objetivo:**
Menu de ordenação no header (ao lado da busca) com opções:

- 📅 **Recentes** → Data de importação (DESC)
- 📅 **Antigos** → Data de importação (ASC)
- 🔤 **A→Z** → Nome alfabético (ASC)
- 🔥 **Z→A** → Nome alfabético (DESC)
- 🏛️ **Origem** → Agrupa por origem
- 🤖 **Analisados** → Projetos analisados primeiro
- ⏳ **Pendentes** → Projetos não analisados primeiro

**Implementação:**

```python
# ui/main_window.py

class LaserflixMainWindow:
    def __init__(self, root):
        # ...
        self.current_sort = "date_desc"  # Padrão
    
    def _build_ui(self):
        # No header, após o campo de busca:
        sort_frame = tk.Frame(header_frame, bg=BG_PRIMARY)
        sort_frame.pack(side="left", padx=10)
        
        tk.Label(sort_frame, text="📊", bg=BG_PRIMARY, 
                 fg=FG_TERTIARY, font=("Arial", 12)).pack(side="left", padx=5)
        
        self.sort_menu = ttk.Combobox(
            sort_frame,
            values=[
                "📅 Recentes",
                "📅 Antigos",
                "🔤 A→Z",
                "🔥 Z→A",
                "🏛️ Origem",
                "🤖 Analisados",
                "⏳ Pendentes",
            ],
            state="readonly",
            width=12,
            font=("Arial", 9),
        )
        self.sort_menu.set("📅 Recentes")  # Padrão
        self.sort_menu.pack(side="left")
        self.sort_menu.bind("<<ComboboxSelected>>", self._on_sort_change)
    
    def _on_sort_change(self, event=None):
        # Mapeia label → key interno
        label_to_key = {
            "📅 Recentes": "date_desc",
            "📅 Antigos": "date_asc",
            "🔤 A→Z": "name_asc",
            "🔥 Z→A": "name_desc",
            "🏛️ Origem": "origin",
            "🤖 Analisados": "analyzed",
            "⏳ Pendentes": "not_analyzed",
        }
        selected_label = self.sort_menu.get()
        self.current_sort = label_to_key.get(selected_label, "date_desc")
        self.current_page = 1  # Reseta para página 1
        self.display_projects()
    
    def _sort_projects(self, projects):
        """Ordena lista de projetos antes de paginar."""
        if not projects:
            return projects
        
        if self.current_sort == "date_desc":
            return sorted(projects, key=lambda p: p[1].get("added_date", ""), reverse=True)
        
        elif self.current_sort == "date_asc":
            return sorted(projects, key=lambda p: p[1].get("added_date", ""))
        
        elif self.current_sort == "name_asc":
            return sorted(projects, key=lambda p: p[1].get("name", "").lower())
        
        elif self.current_sort == "name_desc":
            return sorted(projects, key=lambda p: p[1].get("name", "").lower(), reverse=True)
        
        elif self.current_sort == "origin":
            return sorted(projects, key=lambda p: (
                p[1].get("origin", "zzz"),
                p[1].get("name", "").lower()
            ))
        
        elif self.current_sort == "analyzed":
            return sorted(projects, key=lambda p: (
                not p[1].get("analyzed", False),  # Analisados primeiro (False < True)
                p[1].get("name", "").lower()
            ))
        
        elif self.current_sort == "not_analyzed":
            return sorted(projects, key=lambda p: (
                p[1].get("analyzed", False),  # Não analisados primeiro
                p[1].get("name", "").lower()
            ))
        
        return projects
    
    def display_projects(self):
        # 1. Obtém projetos filtrados
        all_filtered = [
            (p, self.database[p])
            for p in self.get_filtered_projects()
            if p in self.database
        ]
        
        # 2. ORDENA ANTES DE PAGINAR (CRUCIAL!)
        all_filtered = self._sort_projects(all_filtered)
        
        # 3. Calcula paginação
        total_count = len(all_filtered)
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_count)
        page_items = all_filtered[start_idx:end_idx]
        
        # 4. Renderiza cards...
        # ...
```

**Arquivos a modificar:**
- `ui/main_window.py` (adicionar menu + método `_sort_projects()`)

**Critérios de aceitação:**
- ✅ Dropdown visível no header
- ✅ Ordenação ANTES da paginação
- ✅ Estado persiste ao mudar de página
- ✅ Compatível com filtros ativos
- ✅ Performance: ordenação instantânea até 500 projetos

---

### 🟡 PRÓXIMAS TAREFAS (FILA):

#### **S-03 - Thumbnail Carregamento Assíncrono**

**Problema atual:**
Thumbnails carregam sincronamente na thread principal, travando a UI com muitos projetos.

**Solução:**
```python
import queue
import threading

class ThumbnailPreloader:
    def __init__(self, max_workers=4):
        self.queue = queue.Queue()
        self.cache = {}  # path → PhotoImage
        self.workers = []
        for _ in range(max_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.workers.append(t)
    
    def preload_single(self, project_path, callback):
        """Adiciona thumbnail na fila."""
        if project_path in self.cache:
            callback(project_path, self.cache[project_path])
        else:
            self.queue.put((project_path, callback))
    
    def _worker(self):
        while True:
            project_path, callback = self.queue.get()
            try:
                # Carrega imagem
                cover_path = self._find_cover(project_path)
                img = Image.open(cover_path)
                img = img.resize((220, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.cache[project_path] = photo
                callback(project_path, photo)
            except Exception as e:
                LOGGER.error(f"Erro ao carregar thumbnail: {e}")
            finally:
                self.queue.task_done()
```

**Arquivos a modificar:**
- `core/thumbnail_preloader.py` (criar novo arquivo)
- `ui/project_card.py` (usar `preload_single()` no `build_card()`)

---

#### **F-01 - Modal Completo**

**Recursos a adicionar:**
- Galeria de imagens (thumbs clicáveis)
- Nome PT-BR editável
- Descrição editável (textarea grande)
- Notas do usuário (campo livre)

**Arquivos a modificar:**
- `ui/project_modal.py` (expandir layout)

---

#### **F-03 - Limpeza de Órfãos**

**Objetivo:**
Remover entradas do banco cujo `path` não existe mais em disco.

**Implementação:**
```python
def clean_orphans(self):
    orphans = [p for p in self.database if not os.path.isdir(p)]
    if not orphans:
        messagebox.showinfo("✅ Banco limpo", "Nenhum órfão encontrado!")
        return
    
    if messagebox.askyesno(
        "🗑️ Limpar órfãos",
        f"Encontrados {len(orphans)} projeto(s) com path inválido.\n\nRemover do banco?"
    ):
        for p in orphans:
            self.database.pop(p)
        self.db_manager.save_database()
        self.display_projects()
        messagebox.showinfo("✅", f"{len(orphans)} órfão(s) removido(s)!")
```

**Arquivos a modificar:**
- `ui/main_window.py` (método `clean_orphans()`)
- `ui/header.py` (botão no menu "Dashboard")

---

## 📊 COMPARAÇÃO DE ARQUIVOS

### Arquivos IDÊNTICOS (cópia exata da v3.3):

```
✅ ai/
   └─ analysis_manager.py
   └─ fallbacks.py
   └─ image_analyzer.py
   └─ keyword_maps.py
   └─ ollama_client.py
   └─ text_generator.py

✅ config/
   └─ card_layout.py
   └─ constants.py
   └─ settings.py
   └─ ui_constants.py

✅ core/
   └─ database.py
   └─ project_scanner.py
   └─ thumbnail_cache.py  # Será substituído por thumbnail_preloader.py

✅ ui/
   └─ duplicate_resolution_dialog.py
   └─ edit_modal.py
   └─ header.py
   └─ import_mode_dialog.py
   └─ import_preview_dialog.py
   └─ model_settings_dialog.py
   └─ prepare_folders_dialog.py
   └─ project_card.py
   └─ project_modal.py
   └─ recursive_import_integration.py
   └─ sidebar.py

✅ utils/
   └─ duplicate_detector.py
   └─ logging_setup.py
   └─ platform_utils.py
   └─ recursive_scanner.py

✅ Raiz:
   └─ main.py
   └─ requirements.txt
   └─ backup_manager.py
```

### Arquivos QUE SERÃO MODIFICADOS na v3.4:

```
🔴 ui/main_window.py
   └─ Adicionar menu de ordenação
   └─ Método _sort_projects()

🟡 core/thumbnail_preloader.py (NOVO ARQUIVO)
   └─ Substitui thumbnail_cache.py
   └─ Carregamento assíncrono via queue.Queue

🟡 ui/project_card.py
   └─ Usar thumbnail_preloader ao invés de cache síncrono
```

---

## 🛠️ PROCEDIMENTO DE MIGRAÇÃO

### Passo 1: Verificar cópia

```bash
cd laserflix_v3.4.0.0_Stable
ls -la
# Deve conter TODOS os arquivos da v3.3
```

### Passo 2: Testar compatibilidade

```bash
python main.py
# Deve rodar perfeitamente, idêntico à v3.3
```

### Passo 3: Implementar F-06 (Ordenação)

1. Ler `ui/main_window.py`
2. Adicionar menu de ordenação no `_build_ui()`
3. Criar método `_sort_projects()`
4. Integrar em `display_projects()`
5. Testar

### Passo 4: Commit

```bash
git add .
git commit -m "Laserflix_v3.4.0.0_F-06: Ordenação configurável (7 opções)"
git push
```

---

## ⚠️ BREAKING CHANGES

**NENHUM!** 🎉

A v3.4 é 100% retrocompatível com a v3.3:
- Mesmo formato de banco (`laserflix_database.json`)
- Mesmos arquivos de config (`laserflix_config.json`)
- Mesma estrutura de pastas

---

## 📚 DOCUMENTAÇÃO ATUALIZADA

### Arquivos criados na v3.4:

```
🆕 VERSION_HISTORY.md  ← Este arquivo
🆕 MIGRATION_v3.3_to_v3.4.md  ← Guia de migração
```

### Arquivos atualizados:

```
📝 README.md  ← Atualizado para v3.4
📝 BACKLOG.md  ← Tarefas da v3.4
```

---

## 👥 CRÉDITOS

- **v3.3:** Base sólida com paginação, seleção em massa, import recursivo
- **v3.4:** Evolução com ordenação e thumbnails assíncronos
- **Perplexity (Claude Sonnet 4.6):** Arquitetura e desenvolvimento

---

**Última atualização:** 05/03/2026 19:06 BRT
