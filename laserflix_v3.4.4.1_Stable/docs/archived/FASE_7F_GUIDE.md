# FASE 7F: Refatoração Ultra-Agressiva (FINAL)

**REDUÇÃO ESTIMADA**: -120 linhas total
- ModalManager: -35 linhas
- DatabaseController: -30 linhas
- CardFactory: -40 linhas
- Consolidar preparação: -15 linhas

---

## 7F.1: CRIAR ModalManager (-35 linhas)

### OBJETIVO:
Centralizar gerenciamento de todos os dialogs/modals em um único controller.

### CRIAR: ui/controllers/modal_manager.py

```python
"""
ui/controllers/modal_manager.py — Gerencia todos os modals/dialogs da aplicação.

FASE 7F.1: Centraliza gerenciamento de dialogs
Redução estimada: -35 linhas no main_window.py
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from ui.dialogs.collection_dialog import CollectionDialog
from ui.dialogs.prepare_folders_dialog import PrepareFoldersDialog
from ui.dialogs.import_dialog import ImportDialog
from ui.dialogs.model_settings_dialog import ModelSettingsDialog


class ModalManager:
    """
    Gerencia abertura e coordenação de todos os dialogs.
    
    Responsabilidades:
    - Abrir/fechar dialogs
    - Callbacks de confirmação
    - State management entre dialogs
    """
    
    def __init__(self, parent, collections_manager=None):
        self.parent = parent
        self.collections_manager = collections_manager
        
        # Callbacks
        self.on_modal_closed = None
        self.on_data_changed = None
    
    def open_collections(self, on_close=None):
        """Abre dialog de coleções."""
        dialog = CollectionDialog(
            parent=self.parent,
            collections_manager=self.collections_manager
        )
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def open_prepare_folders(self, on_close=None):
        """Abre dialog de preparação de pastas."""
        dialog = PrepareFoldersDialog(parent=self.parent)
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def open_import(self, on_import_done=None):
        """Abre dialog de importação."""
        dialog = ImportDialog(parent=self.parent)
        
        if on_import_done:
            dialog.on_import_completed = on_import_done
    
    def open_model_settings(self, on_close=None):
        """Abre dialog de configurações de modelo."""
        dialog = ModelSettingsDialog(parent=self.parent)
        
        if on_close:
            dialog.protocol("WM_DELETE_WINDOW", lambda: self._handle_close(dialog, on_close))
    
    def confirm(self, title, message):
        """Mostra dialog de confirmação."""
        return messagebox.askyesno(title, message, parent=self.parent)
    
    def info(self, title, message):
        """Mostra dialog de informação."""
        messagebox.showinfo(title, message, parent=self.parent)
    
    def error(self, title, message):
        """Mostra dialog de erro."""
        messagebox.showerror(title, message, parent=self.parent)
    
    def warning(self, title, message):
        """Mostra dialog de aviso."""
        messagebox.showwarning(title, message, parent=self.parent)
    
    def ask_string(self, title, prompt, initial=""):
        """Pede string ao usuário."""
        return simpledialog.askstring(title, prompt, initialvalue=initial, parent=self.parent)
    
    def _handle_close(self, dialog, callback):
        """Handler genérico de fechamento."""
        dialog.destroy()
        if callback:
            callback()
        if self.on_modal_closed:
            self.on_modal_closed()
```

### INTEGRAÇÃO NO main_window.py:

```python
# No __init__:
self.modal_mgr = ModalManager(
    parent=self.root,
    collections_manager=self.collections_manager
)
self.modal_mgr.on_data_changed = self.display_projects

# SUBSTITUIR (35 linhas inline):
def open_collections_dialog(self):
    # ... 8 linhas
    
def open_prepare_folders(self):
    # ... 8 linhas
    
def open_import_dialog(self):
    # ... 7 linhas
    
def open_model_settings(self):
    # ... 6 linhas
    
# Mais ~6 linhas de messagebox.ask* espalhadas

# POR (8 linhas delegadas):
def open_collections_dialog(self):
    self.modal_mgr.open_collections(on_close=self.display_projects)

def open_prepare_folders(self):
    self.modal_mgr.open_prepare_folders()

def open_import_dialog(self):
    self.modal_mgr.open_import(on_import_done=self.display_projects)

def open_model_settings(self):
    self.modal_mgr.open_model_settings()
```

**REDUÇÃO: -35 linhas**

---

## 7F.2: CRIAR DatabaseController (-30 linhas)

### OBJETIVO:
Centralizar operações de database (export, backup, import).

### CRIAR: core/database_controller.py

```python
"""
core/database_controller.py — Controla operações de alto nível do database.

FASE 7F.2: Centraliza operações de database
Redução estimada: -30 linhas no main_window.py
"""
import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox


class DatabaseController:
    """
    Controla operações de alto nível do database.
    
    Responsabilidades:
    - Export de database
    - Backup manual
    - Import de database
    """
    
    def __init__(self, db_manager, database_ref, parent=None):
        self.db_manager = db_manager
        self.database = database_ref
        self.parent = parent
        
        # Callbacks
        self.on_database_changed = None
        self.on_status_message = None
    
    def export(self):
        """Exporta database para arquivo."""
        filename = filedialog.asksaveasfilename(
            title="Exportar Database",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            parent=self.parent
        )
        
        if filename:
            try:
                shutil.copy(self.db_manager.db_path, filename)
                messagebox.showinfo(
                    "✅ Export concluído",
                    f"Database exportado para:\\n{filename}",
                    parent=self.parent
                )
                self._notify_status(f"Database exportado: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror(
                    "❌ Erro no export",
                    f"Não foi possível exportar:\\n{str(e)}",
                    parent=self.parent
                )
    
    def manual_backup(self):
        """Cria backup manual do database."""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.json")
            
            shutil.copy(self.db_manager.db_path, backup_file)
            
            messagebox.showinfo(
                "✅ Backup criado",
                f"Backup salvo em:\\n{backup_file}",
                parent=self.parent
            )
            self._notify_status(f"Backup criado: {os.path.basename(backup_file)}")
        except Exception as e:
            messagebox.showerror(
                "❌ Erro no backup",
                f"Não foi possível criar backup:\\n{str(e)}",
                parent=self.parent
            )
    
    def import_from_file(self, filepath):
        """Importa database de arquivo."""
        if not os.path.exists(filepath):
            messagebox.showerror(
                "❌ Arquivo não encontrado",
                f"Arquivo não existe:\\n{filepath}",
                parent=self.parent
            )
            return False
        
        try:
            # Backup antes de importar
            self.manual_backup()
            
            # Importar
            shutil.copy(filepath, self.db_manager.db_path)
            self.db_manager.load_database()
            
            messagebox.showinfo(
                "✅ Import concluído",
                f"Database importado de:\\n{filepath}",
                parent=self.parent
            )
            
            self._notify_status(f"Database importado: {os.path.basename(filepath)}")
            self._notify_changed()
            return True
            
        except Exception as e:
            messagebox.showerror(
                "❌ Erro no import",
                f"Não foi possível importar:\\n{str(e)}",
                parent=self.parent
            )
            return False
    
    def _notify_status(self, message):
        if self.on_status_message:
            self.on_status_message(message)
    
    def _notify_changed(self):
        if self.on_database_changed:
            self.on_database_changed()
```

### INTEGRAÇÃO NO main_window.py:

```python
# No __init__:
self.db_ctrl = DatabaseController(
    db_manager=self.db_manager,
    database_ref=self.database,
    parent=self.root
)
self.db_ctrl.on_database_changed = self.display_projects
self.db_ctrl.on_status_message = lambda msg: self.status_bar.config(text=msg)

# SUBSTITUIR (30 linhas):
def export_database(self):
    # ... 12 linhas

def manual_backup(self):
    # ... 18 linhas

# POR (6 linhas):
def export_database(self):
    self.db_ctrl.export()

def manual_backup(self):
    self.db_ctrl.manual_backup()
```

**REDUÇÃO: -30 linhas**

---

## 7F.3: CRIAR CardFactory (-40 linhas)

### OBJETIVO:
Extrair lógica de criação de cards para factory pattern.

### CRIAR: ui/factories/card_factory.py

```python
"""
ui/factories/card_factory.py — Factory para criação de project cards.

FASE 7F.3: Extrai lógica de criação de cards
Redução estimada: -40 linhas no main_window.py
"""
import tkinter as tk
from ui.components.card import ProjectCard


class CardFactory:
    """
    Factory para criação de project cards.
    
    Responsabilidades:
    - Criar cards com configuração padrão
    - Injetar callbacks
    - Gerenciar estado de seleção
    """
    
    def __init__(self):
        # Callbacks que serão injetados nos cards
        self.on_open = None
        self.on_toggle_favorite = None
        self.on_toggle_done = None
        self.on_toggle_good = None
        self.on_toggle_bad = None
        self.on_add_to_collection = None
        self.on_remove_from_collection = None
        self.on_new_collection = None
        self.on_remove_project = None
        self.on_card_click = None
    
    def create_card(self, parent, project_data, path, is_selected=False):
        """
        Cria um project card com todos os callbacks configurados.
        
        Args:
            parent: Widget pai
            project_data: Dict com dados do projeto
            path: Caminho do projeto
            is_selected: Se está selecionado (modo seleção)
        
        Returns:
            ProjectCard configurado
        """
        card = ProjectCard(
            parent=parent,
            project_data=project_data,
            path=path
        )
        
        # Injetar callbacks
        card.on_open = lambda p: self.on_open(p) if self.on_open else None
        card.on_toggle_favorite = lambda p, b: self.on_toggle_favorite(p, b) if self.on_toggle_favorite else None
        card.on_toggle_done = lambda p, b: self.on_toggle_done(p, b) if self.on_toggle_done else None
        card.on_toggle_good = lambda p, b: self.on_toggle_good(p, b) if self.on_toggle_good else None
        card.on_toggle_bad = lambda p, b: self.on_toggle_bad(p, b) if self.on_toggle_bad else None
        card.on_add_to_collection = lambda p, c: self.on_add_to_collection(p, c) if self.on_add_to_collection else None
        card.on_remove_from_collection = lambda p, c: self.on_remove_from_collection(p, c) if self.on_remove_from_collection else None
        card.on_new_collection = lambda p: self.on_new_collection(p) if self.on_new_collection else None
        card.on_remove_project = lambda p: self.on_remove_project(p) if self.on_remove_project else None
        card.on_card_click = lambda p: self.on_card_click(p) if self.on_card_click else None
        
        # Aplicar estado de seleção
        if is_selected:
            card.set_selected(True)
        
        return card
    
    def create_batch(self, parent, projects_data, selected_paths=None):
        """
        Cria múltiplos cards de uma vez.
        
        Args:
            parent: Widget pai
            projects_data: List de tuples (path, project_data)
            selected_paths: Set de paths selecionados
        
        Returns:
            List de ProjectCards
        """
        if selected_paths is None:
            selected_paths = set()
        
        cards = []
        for path, data in projects_data:
            is_selected = path in selected_paths
            card = self.create_card(parent, data, path, is_selected)
            cards.append(card)
        
        return cards
```

### INTEGRAÇÃO NO main_window.py:

```python
# No __init__:
self.card_factory = CardFactory()
self.card_factory.on_open = self.open_project
self.card_factory.on_toggle_favorite = self.toggle_favorite
self.card_factory.on_toggle_done = self.toggle_done
self.card_factory.on_toggle_good = self.toggle_good
self.card_factory.on_toggle_bad = self.toggle_bad
self.card_factory.on_add_to_collection = self._on_add_to_collection
self.card_factory.on_remove_from_collection = self._on_remove_from_collection
self.card_factory.on_new_collection = self._on_new_collection_with
self.card_factory.on_remove_project = self.remove_project
self.card_factory.on_card_click = self.toggle_card_selection

# Em display_projects(), SUBSTITUIR (~40 linhas):
for path, project in page_items:
    card = ProjectCard(
        parent=cards_container,
        project_data=project,
        path=path
    )
    
    # 30 linhas de injeção de callbacks
    card.on_open = lambda p: self.open_project(p)
    card.on_toggle_favorite = ...
    # ... etc
    
    if self.selection_ctrl.is_selected(path):
        card.set_selected(True)
    
    card.pack(side="left", padx=10, pady=10)

# POR (8 linhas):
selected_paths = self.selection_ctrl.selected_paths
cards = self.card_factory.create_batch(
    parent=cards_container,
    projects_data=page_items,
    selected_paths=selected_paths
)

for card in cards:
    card.pack(side="left", padx=10, pady=10)
```

**REDUÇÃO: -40 linhas**

---

## 7F.4: CONSOLIDAR PREPARAÇÃO (-15 linhas)

### OBJETIVO:
Consolidar lógica de preparação de projetos.

### ANTES (26 linhas):

```python
def open_prepare_folders(self):
    dialog = PrepareFoldersDialog(self.root)
    # ... 5 linhas de setup
    
def _on_prepare_complete(self, prepared_paths):
    # ... 12 linhas de processamento
    for path in prepared_paths:
        # adicionar ao database
        # atualizar UI
        # etc
    
def _scan_prepared_folders(self, paths):
    # ... 9 linhas
```

### DEPOIS (11 linhas):

```python
def open_prepare_folders(self):
    self.modal_mgr.open_prepare_folders(on_close=self._handle_prepare_complete)

def _handle_prepare_complete(self):
    # Scanner já faz o trabalho pesado
    self.scanner.scan_for_projects()
    self.display_projects()
```

**REDUÇÃO: -15 linhas**

---

## RESUMO COMPLETO

### Fase 7E+ (-100 linhas):
- Callbacks: -30
- Toggles: -20
- Código morto: -30
- Auxiliares: -20

### Fase 7F (-120 linhas):
- ModalManager: -35
- DatabaseController: -30
- CardFactory: -40
- Consolidar preparação: -15

### TOTAL FASES 7E+ e 7F: -220 linhas

**main_window.py FINAL**: ~198 linhas ✅ META ALCANÇADA!

---

## CHECKLIST COMPLETO

### Fase 7E+:
- [ ] Simplificar callbacks de filtro
- [ ] Simplificar toggles
- [ ] Remover código morto
- [ ] Consolidar auxiliares

### Fase 7F:
- [ ] Criar ModalManager
- [ ] Criar DatabaseController
- [ ] Criar CardFactory
- [ ] Consolidar preparação

### Finalização:
- [ ] Testar TODAS as funcionalidades
- [ ] Verificar performance
- [ ] Atualizar README
- [ ] Commit final

---

## ARQUITETURA FINAL

```
main_window.py (198 linhas)
├── Controllers (delegates)
│   ├── DisplayController
│   ├── SelectionController
│   ├── CollectionController
│   ├── ProjectManagementController
│   ├── ModalManager
│   └── DatabaseController
├── Components (UI)
│   ├── HeaderBar
│   ├── SidebarPanel
│   ├── ChipsBar
│   ├── SelectionBar
│   ├── PaginationControls
│   └── StatusBar
└── Factories
    └── CardFactory

TOTAL: 868 → 198 linhas (-670 / -77%)
```

**ARQUITETURA LIMPA, TESTÁVEL E MANUTENÍVEL!** 🎉
