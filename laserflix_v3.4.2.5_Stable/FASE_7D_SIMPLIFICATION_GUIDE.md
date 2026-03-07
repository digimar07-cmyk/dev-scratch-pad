# FASE 7D.4 e 7D.5: Simplificação de _build_ui() e display_projects()

**REDUÇÃO ESTIMADA**: -103 linhas total
- _build_ui(): -89 linhas (129 → 40)
- display_projects(): -14 linhas (usando components)

---

## FASE 7D.4: SIMPLIFICAR _build_ui()

### ANTES (129 linhas - TUDO INLINE):

```python
def _build_ui(self):
    # Header
    self.header = HeaderBar(
        root=self.root,
        on_search=self._on_search,
        on_scan=self.scanner.scan_for_projects,
        on_collections=self.open_collections_dialog,
        on_prepare=self.open_prepare_folders,
        on_export=self.export_database,
        on_import=self.open_import_dialog,
        on_backup=self.manual_backup,
        on_clean=self.clean_orphans,
        on_model_settings=self.open_model_settings,
        on_selection_mode=self.toggle_selection_mode
    )
    self.header.frame.pack(fill="x")
    self.search_var = self.header.search_var
    
    # Main container
    main_container = tk.Frame(self.root, bg=BG_PRIMARY)
    main_container.pack(fill="both", expand=True)
    
    # Sidebar
    self.sidebar = SidebarPanel(
        parent=main_container,
        on_filter=self.set_filter,
        on_origin_filter=self._on_origin_filter,
        on_category_filter=self._on_category_filter,
        on_rating_filter=self._on_rating_filter,
        on_collection_filter=self._on_collection_filter,
        on_favorite_filter=self._on_favorite_filter,
        on_done_filter=self._on_done_filter,
        collections_manager=self.collections_manager
    )
    self.sidebar.frame.pack(side="left", fill="y")
    
    # Content frame
    content_frame = tk.Frame(main_container, bg=BG_PRIMARY)
    content_frame.pack(side="left", fill="both", expand=True)
    
    # Chips bar (AQUI SERÁ SIMPLIFICADO)
    self._chips_bar_frame = tk.Frame(content_frame, bg=BG_PRIMARY, height=50)
    self._chips_bar_frame.pack_propagate(False)
    self._chips_bar_container = tk.Frame(self._chips_bar_frame, bg=BG_PRIMARY)
    self._chips_bar_container.pack(side="left", fill="both", expand=True, padx=10, pady=8)
    
    # Canvas + Scrollbar (50 linhas de setup)
    self.content_canvas = tk.Canvas(content_frame, bg=BG_PRIMARY, highlightthickness=0)
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
    self.scrollable_frame = tk.Frame(self.content_canvas, bg=BG_PRIMARY)
    # ... 40 linhas de configuração de canvas/scroll
    
    # Selection bar (SERÁ SUBSTITUÍDO POR COMPONENT)
    self._sel_bar = tk.Frame(self.root, bg="#1A1A00", height=48)
    self._sel_bar.pack_propagate(False)
    # ... 40 linhas construindo botões inline
    
    # Status bar
    self.status_bar_component = StatusBar(self.root)
```

### DEPOIS (40 linhas - DELEGADO):

```python
def _build_ui(self):
    self._build_header()
    self._build_main_container()
    self._build_status_bar()
    self._setup_keybindings()

def _build_header(self):
    self.header = HeaderBar(
        root=self.root,
        on_search=self._on_search,
        on_scan=self.scanner.scan_for_projects,
        on_collections=self.open_collections_dialog,
        on_prepare=self.open_prepare_folders,
        on_export=self.export_database,
        on_import=self.open_import_dialog,
        on_backup=self.manual_backup,
        on_clean=self.clean_orphans,
        on_model_settings=self.open_model_settings,
        on_selection_mode=self.toggle_selection_mode
    )
    self.header.frame.pack(fill="x")
    self.search_var = self.header.search_var

def _build_main_container(self):
    main_container = tk.Frame(self.root, bg=BG_PRIMARY)
    main_container.pack(fill="both", expand=True)
    
    self.sidebar = SidebarPanel(
        parent=main_container,
        on_filter=self.set_filter,
        on_origin_filter=self._on_origin_filter,
        on_category_filter=self._on_category_filter,
        on_rating_filter=self._on_rating_filter,
        on_collection_filter=self._on_collection_filter,
        on_favorite_filter=self._on_favorite_filter,
        on_done_filter=self._on_done_filter,
        collections_manager=self.collections_manager
    )
    self.sidebar.frame.pack(side="left", fill="y")
    
    self._build_content_frame(main_container)

def _build_content_frame(self, parent):
    content_frame = tk.Frame(parent, bg=BG_PRIMARY)
    content_frame.pack(side="left", fill="both", expand=True)
    
    # ChipsBar component
    self.chips_bar = ChipsBar(content_frame)
    self.chips_bar.on_chip_removed = lambda f: self.display_ctrl.remove_filter_chip(f)
    self.chips_bar.on_clear_all = self.display_ctrl.clear_all_filters
    
    # SelectionBar component
    self.selection_bar = SelectionBar(self.root)
    self.selection_bar.on_select_all = self._select_all
    self.selection_bar.on_deselect_all = self._deselect_all
    self.selection_bar.on_remove_selected = self._remove_selected
    self.selection_bar.on_cancel = self.toggle_selection_mode
    
    self._build_canvas(content_frame)

def _build_canvas(self, parent):
    self.content_canvas = tk.Canvas(parent, bg=BG_PRIMARY, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.content_canvas.yview)
    self.scrollable_frame = tk.Frame(self.content_canvas, bg=BG_PRIMARY)
    
    self.scrollable_frame.bind(
        "<Configure>",
        lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
    )
    
    self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    self.content_canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    self.content_canvas.pack(side="left", fill="both", expand=True)
    
    self.content_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

def _build_status_bar(self):
    self.status_bar_component = StatusBar(self.root)

def _setup_keybindings(self):
    self.root.bind("<Left>", lambda e: self.display_ctrl.prev_page())
    self.root.bind("<Right>", lambda e: self.display_ctrl.next_page())
    self.root.bind("<Home>", lambda e: self.display_ctrl.first_page())
    self.root.bind("<End>", lambda e: self.display_ctrl.last_page())
```

---

## FASE 7D.5: SIMPLIFICAR display_projects()

### MUDANÇAS PRINCIPAIS:

#### 1. Usar ChipsBar.update() ao invés de _update_chips_bar()

**ANTES:**
```python
def display_projects(self):
    # ... código
    self._update_chips_bar()  # 47 linhas de código inline
    # ... resto
```

**DEPOIS:**
```python
def display_projects(self):
    # ... código
    self.chips_bar.update(self.display_ctrl.active_filters)
    # ... resto
```

#### 2. Usar PaginationControls.render() ao invés de construir inline

**ANTES** (dentro de display_projects - ~60 linhas):
```python
# Header frame
header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
header_frame.pack(fill="x", pady=(0, 10))

# Sort controls
left_controls = tk.Frame(header_frame, bg=BG_PRIMARY)
left_controls.pack(side="left", padx=10)

sort_label = tk.Label(left_controls, text="Ordenar por:", ...)
sort_label.pack(side="left", padx=(0, 5))

sort_combo = ttk.Combobox(left_controls, ...)
sort_combo['values'] = [...]
sort_combo.pack(side="left")

# Navigation buttons
right_controls = tk.Frame(header_frame, bg=BG_PRIMARY)
right_controls.pack(side="right", padx=10)

first_btn = tk.Button(right_controls, text="⏮", ...)
# ... mais 40 linhas
```

**DEPOIS** (~10 linhas):
```python
# Header frame
header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
header_frame.pack(fill="x", pady=(0, 10))

# Pagination controls
pagination = PaginationControls(header_frame)
pagination.on_sort_changed = lambda s: self.display_ctrl.change_sort(s)
pagination.on_first = self.display_ctrl.first_page
pagination.on_prev = self.display_ctrl.prev_page
pagination.on_next = self.display_ctrl.next_page
pagination.on_last = self.display_ctrl.last_page
pagination.render(page_info, self.display_ctrl.get_sort_options())
pagination.pack(fill="x")
```

---

## IMPORTS NECESSÁRIOS

Adicionar no topo do main_window.py:
```python
from ui.components.chips_bar import ChipsBar
from ui.components.selection_bar import SelectionBar
from ui.components.pagination_controls import PaginationControls
```

---

## CALLBACKS ADICIONAIS NECESSÁRIOS

No __init__, após criar selection_ctrl:
```python
def _on_selection_mode_changed(self, is_active):
    if is_active:
        self.selection_bar.show()
    else:
        self.selection_bar.hide()
    self.display_projects()

def _on_selection_changed(self, count):
    self.selection_bar.update_count(count)
```

---

## RESUMO DE REDUÇÃO

### _build_ui():
- **ANTES**: 129 linhas (tudo inline)
- **DEPOIS**: 40 linhas (delegado para métodos)
- **REDUÇÃO**: -89 linhas

### display_projects():
- **ANTES**: ~110 linhas
- **DEPOIS**: ~96 linhas (usando components)
- **REDUÇÃO**: -14 linhas

### TOTAL FASE 7D+: -103 linhas
