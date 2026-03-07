#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_fix_fase7c.py - Corrige e aplica Fase 7C automaticamente
==============================================================

Este script:
1. Detecta se main_window.py ja foi modificado pela Fase 7C
2. Se sim, restaura do backup automaticamente
3. Verifica se controllers existem
4. Se nao, cria os controllers corretos
5. Aplica a Fase 7C v2.0

SOLUCAO DEFINITIVA - SEM QUESTIONAMENTOS!

Uso:
  python auto_fix_fase7c.py

Autor: Claude Sonnet 4.5
Data: 2026-03-07
"""

import os
import sys
import shutil
from pathlib import Path

# Cores
class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def print_header(text):
    print(f"\n{Color.CYAN}{Color.BOLD}{'=' * 80}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{text}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'=' * 80}{Color.RESET}\n")

def print_ok(text):
    print(f"{Color.GREEN}OK {text}{Color.RESET}")

def print_erro(text):
    print(f"{Color.RED}ERRO {text}{Color.RESET}")

def print_info(text):
    print(f"{Color.BLUE}INFO {text}{Color.RESET}")

def check_fase7c_applied():
    """Verifica se Fase 7C ja foi aplicada."""
    main_window = Path("ui/main_window.py")
    
    if not main_window.exists():
        return False
    
    content = main_window.read_text(encoding='utf-8')
    
    # Se tem imports dos controllers, Fase 7C foi aplicada
    if "from ui.controllers.selection_controller import SelectionController" in content:
        return True
    
    return False

def find_latest_backup():
    """Encontra o backup mais recente."""
    backup_dir = Path(".backups")
    
    if not backup_dir.exists():
        return None
    
    backups = list(backup_dir.glob("main_window_backup_*.py"))
    
    if not backups:
        return None
    
    # Ordenar por data de modificacao (mais recente primeiro)
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return backups[0]

def restore_backup():
    """Restaura backup automaticamente."""
    print_info("Fase 7C ja foi aplicada anteriormente")
    print_info("Procurando backup...")
    
    backup = find_latest_backup()
    
    if not backup:
        print_erro("Nenhum backup encontrado!")
        print_info("Nao e possivel desfazer automaticamente")
        print_info("Por favor, restaure manualmente ou use a versao do Git")
        return False
    
    print_ok(f"Backup encontrado: {backup}")
    
    # Restaurar
    main_window = Path("ui/main_window.py")
    shutil.copy2(backup, main_window)
    
    print_ok("Backup restaurado!")
    return True

def check_controllers_exist():
    """Verifica se controllers existem."""
    controllers = [
        "ui/controllers/selection_controller.py",
        "ui/controllers/collection_controller.py",
        "ui/controllers/project_management_controller.py"
    ]
    
    missing = []
    for controller in controllers:
        if not Path(controller).exists():
            missing.append(controller)
    
    return missing

def create_controllers():
    """Cria os 3 controllers."""
    print_info("Criando controllers...")
    
    # Criar diretorio se nao existir
    controllers_dir = Path("ui/controllers")
    controllers_dir.mkdir(parents=True, exist_ok=True)
    
    # Controller 1: SelectionController
    selection = controllers_dir / "selection_controller.py"
    if not selection.exists():
        selection.write_text(SELECTION_CONTROLLER, encoding='utf-8')
        print_ok("  selection_controller.py criado")
    
    # Controller 2: CollectionController
    collection = controllers_dir / "collection_controller.py"
    if not collection.exists():
        collection.write_text(COLLECTION_CONTROLLER, encoding='utf-8')
        print_ok("  collection_controller.py criado")
    
    # Controller 3: ProjectManagementController
    project = controllers_dir / "project_management_controller.py"
    if not project.exists():
        project.write_text(PROJECT_CONTROLLER, encoding='utf-8')
        print_ok("  project_management_controller.py criado")

def apply_fase7c():
    """Aplica Fase 7C usando o script existente."""
    print_info("Aplicando Fase 7C v2.0...")
    
    if not Path("apply_fase7_refactor_7C.py").exists():
        print_erro("apply_fase7_refactor_7C.py nao encontrado!")
        return False
    
    # Importar e executar
    import apply_fase7_refactor_7C
    return True

# ============================================================================
# CONTROLLERS (conteudo completo)
# ============================================================================

SELECTION_CONTROLLER = '''"""\nui/controllers/selection_controller.py - Gerencia selecao multipla de projetos.\n"""\n\nimport os\nfrom tkinter import messagebox\n\n\nclass SelectionController:\n    def __init__(self, database, db_manager, collections_manager):\n        self.database = database\n        self.db_manager = db_manager\n        self.collections_manager = collections_manager\n        self.selection_mode = False\n        self.selected_paths = set()\n        self.on_mode_changed = None\n        self.on_selection_changed = None\n        self.on_projects_removed = None\n        self.on_refresh_needed = None\n    \n    def toggle_mode(self):\n        self.selection_mode = not self.selection_mode\n        if not self.selection_mode:\n            self.selected_paths.clear()\n        if self.on_mode_changed:\n            self.on_mode_changed(self.selection_mode)\n        if self.on_selection_changed:\n            self.on_selection_changed(len(self.selected_paths))\n    \n    def toggle_project(self, path):\n        if not self.selection_mode:\n            return\n        if path in self.selected_paths:\n            self.selected_paths.remove(path)\n        else:\n            self.selected_paths.add(path)\n        if self.on_selection_changed:\n            self.on_selection_changed(len(self.selected_paths))\n    \n    def select_all(self, paths):\n        if not self.selection_mode:\n            return\n        self.selected_paths = set(paths)\n        if self.on_selection_changed:\n            self.on_selection_changed(len(self.selected_paths))\n    \n    def deselect_all(self):\n        self.selected_paths.clear()\n        if self.on_selection_changed:\n            self.on_selection_changed(0)\n    \n    def remove_selected(self, parent_window):\n        if not self.selected_paths:\n            messagebox.showwarning("Nenhum projeto selecionado", "Selecione ao menos um projeto.", parent=parent_window)\n            return\n        count = len(self.selected_paths)\n        if not messagebox.askyesno("Confirmar", f"Remover {count} projeto(s)?", parent=parent_window):\n            return\n        for path in self.selected_paths:\n            if path in self.database:\n                del self.database[path]\n            for coll in list(self.collections_manager.collections.keys()):\n                if path in self.collections_manager.collections[coll]:\n                    self.collections_manager.collections[coll].remove(path)\n        self.db_manager.save()\n        self.collections_manager.save()\n        removed = len(self.selected_paths)\n        self.selected_paths.clear()\n        self.selection_mode = False\n        if self.on_mode_changed:\n            self.on_mode_changed(False)\n        if self.on_projects_removed:\n            self.on_projects_removed(removed)\n        if self.on_refresh_needed:\n            self.on_refresh_needed()\n'''

COLLECTION_CONTROLLER = '''"""\nui/controllers/collection_controller.py - Gerencia colecoes/playlists.\n"""\n\nfrom tkinter import messagebox\n\n\nclass CollectionController:\n    def __init__(self, collections_manager, database):\n        self.collections_manager = collections_manager\n        self.database = database\n        self.on_collection_changed = None\n    \n    def add_project(self, path, collection_name):\n        if collection_name not in self.collections_manager.collections:\n            self.collections_manager.collections[collection_name] = []\n        if path not in self.collections_manager.collections[collection_name]:\n            self.collections_manager.collections[collection_name].append(path)\n            self.collections_manager.save()\n            if self.on_collection_changed:\n                self.on_collection_changed()\n    \n    def remove_project(self, path, collection_name):\n        if collection_name in self.collections_manager.collections:\n            if path in self.collections_manager.collections[collection_name]:\n                self.collections_manager.collections[collection_name].remove(path)\n                if not self.collections_manager.collections[collection_name]:\n                    del self.collections_manager.collections[collection_name]\n                self.collections_manager.save()\n                if self.on_collection_changed:\n                    self.on_collection_changed()\n    \n    def create_collection_with_project(self, path, collection_name):\n        if not collection_name:\n            return\n        if collection_name in self.collections_manager.collections:\n            messagebox.showwarning("Colecao existente", f"A colecao \'{collection_name}\' ja existe.")\n            return\n        self.collections_manager.collections[collection_name] = [path]\n        self.collections_manager.save()\n        if self.on_collection_changed:\n            self.on_collection_changed()\n'''

PROJECT_CONTROLLER = '''"""\nui/controllers/project_management_controller.py - Gerencia remocao e flags.\n"""\n\nimport os\nfrom tkinter import messagebox\n\n\nclass ProjectManagementController:\n    def __init__(self, database, db_manager, collections_manager):\n        self.database = database\n        self.db_manager = db_manager\n        self.collections_manager = collections_manager\n        self.on_project_removed = None\n        self.on_orphans_cleaned = None\n        self.on_flag_toggled = None\n    \n    def remove_project(self, path, parent_window):\n        if path not in self.database:\n            return\n        name = os.path.basename(path)\n        if not messagebox.askyesno("Confirmar", f"Remover \'{name}\'?", parent=parent_window):\n            return\n        del self.database[path]\n        for coll in list(self.collections_manager.collections.keys()):\n            if path in self.collections_manager.collections[coll]:\n                self.collections_manager.collections[coll].remove(path)\n                if not self.collections_manager.collections[coll]:\n                    del self.collections_manager.collections[coll]\n        self.db_manager.save()\n        self.collections_manager.save()\n        if self.on_project_removed:\n            self.on_project_removed(name)\n    \n    def clean_orphans(self, parent_window):\n        orphans = [p for p in self.database.keys() if not os.path.exists(p)]\n        if not orphans:\n            messagebox.showinfo("Nenhum orfao", "Nao ha orfaos.", parent=parent_window)\n            return\n        count = len(orphans)\n        if not messagebox.askyesno("Confirmar", f"Remover {count} orfao(s)?", parent=parent_window):\n            return\n        for path in orphans:\n            del self.database[path]\n            for coll in list(self.collections_manager.collections.keys()):\n                if path in self.collections_manager.collections[coll]:\n                    self.collections_manager.collections[coll].remove(path)\n                    if not self.collections_manager.collections[coll]:\n                        del self.collections_manager.collections[coll]\n        self.db_manager.save()\n        self.collections_manager.save()\n        if self.on_orphans_cleaned:\n            self.on_orphans_cleaned(count)\n    \n    def toggle_flag(self, path, flag_name, button=None):\n        if path not in self.database:\n            return\n        current = self.database[path].get(flag_name, False)\n        self.database[path][flag_name] = not current\n        self.db_manager.save()\n        if button:\n            new_state = self.database[path][flag_name]\n            if flag_name == \'favorite\':\n                button.config(text="\\u2605" if new_state else "\\u2606")\n            elif flag_name == \'done\':\n                button.config(text="\\u2713" if new_state else "\\u25cb")\n            elif flag_name == \'good\':\n                button.config(text="\\ud83d\\udc4d" if new_state else "\\u25cb")\n            elif flag_name == \'bad\':\n                button.config(text="\\ud83d\\udc4e" if new_state else "\\u25cb")\n        if self.on_flag_toggled:\n            self.on_flag_toggled()\n'''

# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("AUTO FIX FASE 7C v2.0")
    
    # 1. Verificar se Fase 7C ja foi aplicada
    if check_fase7c_applied():
        if not restore_backup():
            print("\nPressione ENTER para sair...")
            input()
            sys.exit(1)
    else:
        print_ok("main_window.py esta no estado original")
    
    print()
    
    # 2. Verificar controllers
    missing = check_controllers_exist()
    
    if missing:
        print_info(f"{len(missing)} controller(s) faltando:")
        for m in missing:
            print(f"  - {m}")
        print()
        create_controllers()
    else:
        print_ok("Todos os controllers existem")
    
    print()
    
    # 3. Aplicar Fase 7C
    print_header("APLICANDO FASE 7C v2.0")
    
    os.system("python apply_fase7_refactor_7C.py")
    
    print()
    print_header("CONCLUIDO!")
    print_ok("Fase 7C aplicada com sucesso!")
    print()
    print_info("Agora teste:")
    print(f"  {Color.CYAN}python main.py{Color.RESET}")
    print()
    
    print("\nPressione ENTER para fechar...")
    input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuario")
        sys.exit(1)
    except Exception as e:
        print_erro(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("\nPressione ENTER para sair...")
        input()
        sys.exit(1)
