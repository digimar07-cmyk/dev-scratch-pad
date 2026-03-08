# FASE 7E+: Simplificação de Callbacks e Métodos

**REDUÇÃO ESTIMADA**: -100 linhas total
- Callbacks de filtro: -30 linhas
- Toggles: -20 linhas
- Código morto: -30 linhas
- Auxiliares: -20 linhas

---

## 7E.1: SIMPLIFICAR CALLBACKS DE FILTRO (-30 linhas)

### ANTES (~108 linhas total):

```python
def set_filter(self, filter_type: str) -> None:
    self.display_ctrl.set_filter(filter_type)
    self.sidebar.set_active_btn(None)
    self.header.set_active_filter(filter_type)
    self._update_chips_bar()
    self.display_projects()

def _on_search(self) -> None:
    query = self.search_var.get()
    self.display_ctrl.set_search_query(query)
    self.display_projects()

def _on_origin_filter(self, origin: str, btn=None) -> None:
    self.display_ctrl.set_origin_filter(origin)
    self.sidebar.set_active_btn(btn)
    self._update_chips_bar()
    count = sum(1 for p in self.database.values() if p.get("origin") == origin)
    self.status_bar.config(text=f"Origem: {origin} ({count} projetos)")
    self.display_projects()

def _on_category_filter(self, category: str, btn=None) -> None:
    self.display_ctrl.set_category_filter(category)
    self.sidebar.set_active_btn(btn)
    self._update_chips_bar()
    count = sum(1 for p in self.database.values() if category in p.get("categories", []))
    self.status_bar.config(text=f"Categoria: {category} ({count} projetos)")
    self.display_projects()

def _on_rating_filter(self, rating: str, btn=None) -> None:
    self.display_ctrl.set_rating_filter(rating)
    self.sidebar.set_active_btn(btn)
    self._update_chips_bar()
    self.display_projects()

def _on_collection_filter(self, collection_name: str) -> None:
    self.display_ctrl.set_collection_filter(collection_name)
    self.display_projects()

def _on_favorite_filter(self) -> None:
    self.display_ctrl.toggle_favorite_filter()
    self.display_projects()

def _on_done_filter(self) -> None:
    self.display_ctrl.toggle_done_filter()
    self.display_projects()
```

### DEPOIS (~78 linhas total):

```python
def set_filter(self, filter_type):
    self.display_ctrl.set_filter(filter_type)
    self.display_projects()

def _on_search(self):
    self.display_ctrl.set_search_query(self.search_var.get())
    self.display_projects()

def _on_origin_filter(self, origin, btn=None):
    self.display_ctrl.set_origin_filter(origin)
    self.sidebar.set_active_btn(btn)
    self.display_projects()

def _on_category_filter(self, category, btn=None):
    self.display_ctrl.set_category_filter(category)
    self.sidebar.set_active_btn(btn)
    self.display_projects()

def _on_rating_filter(self, rating, btn=None):
    self.display_ctrl.set_rating_filter(rating)
    self.sidebar.set_active_btn(btn)
    self.display_projects()

def _on_collection_filter(self, collection_name):
    self.display_ctrl.set_collection_filter(collection_name)
    self.display_projects()

def _on_favorite_filter(self):
    self.display_ctrl.toggle_favorite_filter()
    self.display_projects()

def _on_done_filter(self):
    self.display_ctrl.toggle_done_filter()
    self.display_projects()
```

**EXPLICAÇÃO:**
- Remover chamadas redundantes a `_update_chips_bar()` (já feito em `display_projects()`)
- Remover chamadas redundantes a `header.set_active_filter()` (gerenciado internamente)
- Remover contadores de status inline (podem ser calculados no DisplayController)
- Simplificar assinaturas (remover type hints desnecessários)

**REDUÇÃO: -30 linhas**

---

## 7E.2: SIMPLIFICAR TOGGLES (-20 linhas)

### ANTES (~66 linhas total):

```python
def toggle_favorite(self, path: str, btn=None) -> None:
    if path in self.database:
        current = self.database[path].get("favorite", False)
        new_value = not current
        self.database[path]["favorite"] = new_value
        self.db_manager.save_database()
        self._invalidate_cache()
        
        if btn:
            btn.config(
                text="⭐" if new_value else "☆",
                fg=ACCENT_GOLD if new_value else FG_TERTIARY
            )

def toggle_done(self, path: str, btn=None) -> None:
    if path in self.database:
        current = self.database[path].get("done", False)
        new_value = not current
        self.database[path]["done"] = new_value
        self.db_manager.save_database()
        self._invalidate_cache()
        
        if btn:
            btn.config(
                text="✓" if new_value else "○",
                fg=ACCENT_GREEN if new_value else FG_TERTIARY
            )

def toggle_good(self, path: str, btn=None) -> None:
    if path in self.database:
        current = self.database[path].get("good", False)
        new_value = not current
        self.database[path]["good"] = new_value
        if new_value:
            self.database[path]["bad"] = False
        self.db_manager.save_database()
        self._invalidate_cache()
        
        if btn:
            btn.config(
                text="👍" if new_value else "○",
                fg=ACCENT_GREEN if new_value else FG_TERTIARY
            )

def toggle_bad(self, path: str, btn=None) -> None:
    if path in self.database:
        current = self.database[path].get("bad", False)
        new_value = not current
        self.database[path]["bad"] = new_value
        if new_value:
            self.database[path]["good"] = False
        self.db_manager.save_database()
        self._invalidate_cache()
        
        if btn:
            btn.config(
                text="👎" if new_value else "○",
                fg=ACCENT_RED if new_value else FG_TERTIARY
            )
```

### DEPOIS (~46 linhas total):

```python
def toggle_favorite(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "favorite")
    if btn and new_value is not None:
        self._update_toggle_btn(btn, "favorite", new_value)
    self._invalidate_cache()

def toggle_done(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "done")
    if btn and new_value is not None:
        self._update_toggle_btn(btn, "done", new_value)
    self._invalidate_cache()

def toggle_good(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "good")
    if btn and new_value is not None:
        self._update_toggle_btn(btn, "good", new_value)
    self._invalidate_cache()

def toggle_bad(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "bad")
    if btn and new_value is not None:
        self._update_toggle_btn(btn, "bad", new_value)
    self._invalidate_cache()

def _update_toggle_btn(self, btn, flag, value):
    """Helper para atualizar visual de botões toggle."""
    configs = {
        "favorite": ("⭐" if value else "☆", ACCENT_GOLD if value else FG_TERTIARY),
        "done": ("✓" if value else "○", ACCENT_GREEN if value else FG_TERTIARY),
        "good": ("👍" if value else "○", ACCENT_GREEN if value else FG_TERTIARY),
        "bad": ("👎" if value else "○", ACCENT_RED if value else FG_TERTIARY)
    }
    
    if flag in configs:
        text, fg = configs[flag]
        btn.config(text=text, fg=fg)
```

**EXPLICAÇÃO:**
- Usar `project_mgmt_ctrl.toggle_flag()` criado na Fase 7C+
- Consolidar lógica de UI update em helper method `_update_toggle_btn()`
- Remover duplicação de código

**REDUÇÃO: -20 linhas**

---

## 7E.3: REMOVER CÓDIGO MORTO E OTIMIZAR (-30 linhas)

### AÇÕES:

#### 1. Remover comentários obsoletos/verbosos
```python
# DELETAR comentários como:
# ============================================================================
# FILTROS
# ============================================================================
# Método para aplicar filtro de tipo
# Atualiza o display após aplicar o filtro
# etc...
```

#### 2. Remover imports não usados
```python
# Verificar e remover imports que não são mais usados após extrações:
# - tkinter.messagebox (se já importado em controllers)
# - tkinter.simpledialog (se já importado em controllers)
# - Qualquer outro import órfão
```

#### 3. Consolidar variáveis temporárias
```python
# ANTES:
filtered = self.display_ctrl.get_filtered_projects()
all_items = [(p, self.database[p]) for p in filtered if p in self.database]
sorted_items = self.display_ctrl.apply_sorting(all_items)
page_data = self.display_ctrl.get_page_info(len(sorted_items))

# DEPOIS:
filtered = self.display_ctrl.get_filtered_projects()
all_items = self.display_ctrl.apply_sorting(
    [(p, self.database[p]) for p in filtered if p in self.database]
)
page_data = self.display_ctrl.get_page_info(len(all_items))
```

#### 4. Simplificar condicionais
```python
# ANTES:
if self._selection_mode == True:
    if path in self._selected_paths:
        return True
    else:
        return False
else:
    return False

# DEPOIS:
return self.selection_ctrl.is_selected(path)
```

#### 5. Remover métodos wrapper desnecessários
```python
# DELETAR se existir:
def refresh(self):
    self.display_projects()

def reload(self):
    self.display_projects()

# Usar diretamente display_projects() nos callbacks
```

**REDUÇÃO: -30 linhas**

---

## 7E.4: CONSOLIDAR MÉTODOS AUXILIARES (-20 linhas)

### ANTES:

```python
def _should_rebuild(self):
    # 20 linhas verificando cache, filtros, etc.
    if self._force_rebuild:
        self._force_rebuild = False
        return True
    
    if self._last_filter != self.display_ctrl.active_filters:
        self._last_filter = self.display_ctrl.active_filters.copy()
        return True
    
    if self._last_database_size != len(self.database):
        self._last_database_size = len(self.database)
        return True
    
    # ... mais condições
    return False

def _invalidate_cache(self):
    self._force_rebuild = True

def _get_thumbnail_async(self, path, callback):
    # 9 linhas de threading
    def load():
        thumb = self._load_thumbnail(path)
        callback(thumb)
    threading.Thread(target=load, daemon=True).start()
```

### DEPOIS:

```python
def _should_rebuild(self):
    # 12 linhas simplificadas
    if self._force_rebuild:
        self._force_rebuild = False
        return True
    
    current_state = (
        tuple(self.display_ctrl.active_filters.items()),
        len(self.database)
    )
    
    if current_state != self._last_state:
        self._last_state = current_state
        return True
    
    return False

def _invalidate_cache(self):
    self._force_rebuild = True

# _get_thumbnail_async movido para ThumbnailHelper ou mantido inline
```

**REDUÇÃO: -20 linhas**

---

## CHECKLIST DE EXECUÇÃO

### Passo 1: Callbacks de filtro
- [ ] Simplificar `set_filter()`
- [ ] Simplificar `_on_search()`
- [ ] Simplificar `_on_origin_filter()`
- [ ] Simplificar `_on_category_filter()`
- [ ] Simplificar `_on_rating_filter()`
- [ ] Simplificar `_on_collection_filter()`
- [ ] Simplificar `_on_favorite_filter()`
- [ ] Simplificar `_on_done_filter()`

### Passo 2: Toggles
- [ ] Criar `_update_toggle_btn()` helper
- [ ] Simplificar `toggle_favorite()`
- [ ] Simplificar `toggle_done()`
- [ ] Simplificar `toggle_good()`
- [ ] Simplificar `toggle_bad()`

### Passo 3: Código morto
- [ ] Remover comentários obsoletos
- [ ] Remover imports não usados
- [ ] Consolidar variáveis temporárias
- [ ] Simplificar condicionais
- [ ] Remover métodos wrapper

### Passo 4: Auxiliares
- [ ] Simplificar `_should_rebuild()`
- [ ] Manter `_invalidate_cache()`
- [ ] Decidir sobre `_get_thumbnail_async()`

---

## RESUMO

**REDUÇÃO TOTAL FASE 7E+**: -100 linhas

| Componente | Antes | Depois | Redução |
|------------|-------|--------|---------||
| Callbacks  | 108   | 78     | -30     |
| Toggles    | 66    | 46     | -20     |
| Código morto | -   | -      | -30     |
| Auxiliares | -     | -      | -20     |
| **TOTAL**  | -     | -      | **-100**|

**main_window.py após 7E+**: ~318 linhas (de 418)
