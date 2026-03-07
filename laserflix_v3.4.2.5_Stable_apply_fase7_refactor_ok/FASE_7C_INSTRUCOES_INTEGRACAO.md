# 🔧 INSTRUÇÕES DE INTEGRAÇÃO - FASE 7C+

## PASSO 1: Adicionar imports no topo do main_window.py

Adicionar após os imports existentes de controllers:

```python
from ui.controllers.selection_controller import SelectionController
from ui.controllers.collection_controller import CollectionController
from ui.controllers.project_management_controller import ProjectManagementController
```

## PASSO 2: Instanciar controllers no __init__

Adicionar no __init__ após a criação do display_ctrl:

```python
# Controllers de gerenciamento (FASE 7C+)
self.selection_ctrl = SelectionController(
    database=self.database,
    db_manager=self.db_manager,
    collections_manager=self.collections_manager
)
self.selection_ctrl.on_mode_changed = self._on_selection_mode_changed
self.selection_ctrl.on_selection_changed = self._on_selection_changed
self.selection_ctrl.on_projects_removed = lambda n: messagebox.showinfo(
    "✅ Projetos removidos",
    f"{n} projeto(s) removido(s) do banco.",
    parent=self.root
)
self.selection_ctrl.on_refresh_needed = self.display_projects

self.collection_ctrl = CollectionController(
    collections_manager=self.collections_manager,
    database=self.database,
    db_manager=self.db_manager
)
self.collection_ctrl.on_collection_changed = self.display_projects
self.collection_ctrl.on_status_message = lambda msg: self.status_bar.config(text=msg)

self.project_mgmt_ctrl = ProjectManagementController(
    database=self.database,
    db_manager=self.db_manager,
    collections_manager=self.collections_manager
)
self.project_mgmt_ctrl.on_project_removed = lambda name: None
self.project_mgmt_ctrl.on_orphans_cleaned = lambda n: None
self.project_mgmt_ctrl.on_status_message = lambda msg: self.status_bar.config(text=msg)
self.project_mgmt_ctrl.on_refresh_needed = self.display_projects
```

## PASSO 3: Substituir métodos existentes

### 3.1 SELEÇÃO (substituir completamente):

**DELETAR:**
```python
def toggle_selection_mode(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def toggle_card_selection(self, path: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _select_all(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _deselect_all(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _remove_selected(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
```

**SUBSTITUIR POR:**
```python
def toggle_selection_mode(self):
    self.selection_ctrl.toggle_mode()

def toggle_card_selection(self, path):
    self.selection_ctrl.toggle_project(path)
    self.display_projects()

def _select_all(self):
    visible_paths = self.display_ctrl.get_filtered_projects()
    self.selection_ctrl.select_all(visible_paths)
    self.display_projects()

def _deselect_all(self):
    self.selection_ctrl.deselect_all()
    self.display_projects()

def _remove_selected(self):
    if self.selection_ctrl.remove_selected(self.root):
        self.display_projects()
```

### 3.2 COLEÇÕES (substituir completamente):

**DELETAR:**
```python
def open_collections_dialog(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _on_collection_filter(self, collection_name: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _on_add_to_collection(self, project_path: str, collection_name: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _on_remove_from_collection(self, project_path: str, collection_name: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def _on_new_collection_with(self, project_path: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
```

**SUBSTITUIR POR:**
```python
def open_collections_dialog(self):
    self.collection_ctrl.open_dialog(self.root)

def _on_collection_filter(self, collection_name):
    # O filtro ainda usa display_ctrl
    self.display_ctrl.set_collection_filter(collection_name)

def _on_add_to_collection(self, project_path, collection_name):
    self.collection_ctrl.add_project(collection_name, project_path)

def _on_remove_from_collection(self, project_path, collection_name):
    self.collection_ctrl.remove_project(collection_name, project_path)

def _on_new_collection_with(self, project_path):
    self.collection_ctrl.create_with_project(project_path, self.root)
```

### 3.3 GERENCIAMENTO DE PROJETOS (substituir completamente):

**DELETAR:**
```python
def remove_project(self, path: str) -> None:
    # ... TODO O CÓDIGO EXISTENTE
    
def clean_orphans(self) -> None:
    # ... TODO O CÓDIGO EXISTENTE
```

**SUBSTITUIR POR:**
```python
def remove_project(self, path):
    self.project_mgmt_ctrl.remove_project(path)

def clean_orphans(self):
    self.project_mgmt_ctrl.clean_orphans(self.root)
```

### 3.4 TOGGLES (simplificar):

**SUBSTITUIR** os métodos toggle_favorite, toggle_done, toggle_good, toggle_bad:

```python
def toggle_favorite(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "favorite")
    if btn and new_value is not None:
        btn.config(
            text="⭐" if new_value else "☆",
            fg=ACCENT_GOLD if new_value else FG_TERTIARY
        )
    self._invalidate_cache()

def toggle_done(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "done")
    if btn and new_value is not None:
        btn.config(
            text="✓" if new_value else "○",
            fg=ACCENT_GREEN if new_value else FG_TERTIARY
        )
    self._invalidate_cache()

def toggle_good(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "good")
    if btn and new_value is not None:
        btn.config(
            text="👍" if new_value else "○",
            fg=ACCENT_GREEN if new_value else FG_TERTIARY
        )
    self._invalidate_cache()

def toggle_bad(self, path, btn=None):
    new_value = self.project_mgmt_ctrl.toggle_flag(path, "bad")
    if btn and new_value is not None:
        btn.config(
            text="👎" if new_value else "○",
            fg=ACCENT_RED if new_value else FG_TERTIARY
        )
    self._invalidate_cache()
```

## PASSO 4: Atualizar referências internas

Procurar por todas as ocorrências de:
- `self._selection_mode` → substituir por `self.selection_ctrl.is_mode_active()`
- `self._selected_paths` → substituir por `self.selection_ctrl.selected_paths`
- `len(self._selected_paths)` → substituir por `self.selection_ctrl.get_selection_count()`

No método display_projects(), onde verifica seleção:
```python
# ANTES:
if self._selection_mode and path in self._selected_paths:
    card_frame.config(bg="#3A3A4E")

# DEPOIS:
if self.selection_ctrl.is_selected(path):
    card_frame.config(bg="#3A3A4E")
```

## PASSO 5: Callback _on_selection_mode_changed

Adicionar método callback:
```python
def _on_selection_mode_changed(self, is_active):
    if is_active:
        # Mostrar selection bar
        if hasattr(self, '_sel_bar'):
            self._sel_bar.pack(fill="x", after=self.header.frame)
    else:
        # Esconder selection bar
        if hasattr(self, '_sel_bar'):
            self._sel_bar.pack_forget()
    self.display_projects()

def _on_selection_changed(self, count):
    if hasattr(self, '_sel_count_lbl'):
        self._sel_count_lbl.config(text=f"{count} selecionado(s)")
```

## PASSO 6: Testar funcionalidades

Após fazer as alterações, testar:
1. ✅ Modo seleção (ativar/desativar)
2. ✅ Selecionar múltiplos projetos
3. ✅ Selecionar todos
4. ✅ Deselecionar todos
5. ✅ Remover selecionados (com confirmações duplas)
6. ✅ Abrir dialog de coleções
7. ✅ Adicionar projeto a coleção
8. ✅ Remover projeto de coleção
9. ✅ Criar nova coleção com projeto
10. ✅ Remover projeto individual
11. ✅ Limpar órfãos
12. ✅ Toggle favorite/done/good/bad

## RESUMO DE LINHAS

DELETAR (estimado):
- toggle_selection_mode: ~15 linhas
- toggle_card_selection: ~12 linhas
- _select_all: ~8 linhas
- _deselect_all: ~6 linhas
- _remove_selected: ~40 linhas
- open_collections_dialog: ~8 linhas
- _on_add_to_collection: ~10 linhas
- _on_remove_from_collection: ~15 linhas
- _on_new_collection_with: ~25 linhas
- remove_project: ~12 linhas
- clean_orphans: ~50 linhas
- toggle_* (simplificação): ~20 linhas

TOTAL DELETADO: ~221 linhas

ADICIONAR (estimado):
- Imports: 3 linhas
- Setup controllers: 25 linhas
- Novos métodos simplificados: 50 linhas

TOTAL ADICIONADO: ~78 linhas

REDUÇÃO LÍQUIDA: ~143 linhas

Resultado esperado: 868 - 143 = 725 linhas (estimativa conservadora)
Projeção otimista: 868 - 200 = 668 linhas

---

PRÓXIMA AÇÃO:
Aplicar estas mudanças manualmente no main_window.py e testar!
