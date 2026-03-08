#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ROLLBACK COMPLETO + REFACTOR CORRETO

Este script:
1. Restaura backup original
2. Aplica refatorações CORRETAMENTE
3. Testa sintaxe
4. Salva versão funcional

Criado: 08/03/2026 10:07 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("🔄 ROLLBACK COMPLETO + REFACTOR CORRETO")
    print("="*70 + "\n")
    
    base_dir = Path(__file__).parent
    main_window = base_dir / "ui" / "main_window.py"
    
    if not main_window.exists():
        print(f"❌ Arquivo não encontrado: {main_window}")
        input("Pressione ENTER...")
        return
    
    # Procurar backup mais recente
    backups = sorted(main_window.parent.glob("main_window.py.backup_*"))
    if not backups:
        print("❌ Nenhum backup encontrado!")
        print("\nO script original deve ter criado: main_window.py.backup_20260308_095756")
        input("Pressione ENTER...")
        return
    
    original_backup = backups[0]  # Primeiro = mais antigo = original
    print(f"📦 Backup original encontrado: {original_backup.name}\n")
    
    # Criar novo backup do estado atual (antes de rollback)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = main_window.with_suffix(f".py.backup_broken_{timestamp}")
    shutil.copy2(main_window, current_backup)
    print(f"💾 Backup do estado quebrado: {current_backup.name}\n")
    
    # ROLLBACK para original
    print("🔄 Restaurando backup original...\n")
    shutil.copy2(original_backup, main_window)
    
    # Ler conteúdo original
    content = main_window.read_text(encoding='utf-8')
    initial_lines = len(content.splitlines())
    print(f"📄 Estado original restaurado: {initial_lines} linhas\n")
    
    print("="*70)
    print("🔧 APLICANDO REFATORAÇÕES CORRETAS")
    print("="*70 + "\n")
    
    # ============================================================
    # REFATORAÇÃO CORRETA - SEM ERROS DE ORDEM
    # ============================================================
    
    # FASE 1: Criar managers (arquivos externos)
    print("📁 [1/4] Criando arquivos de managers...\n")
    
    managers_dir = base_dir / "ui" / "managers"
    managers_dir.mkdir(exist_ok=True)
    
    # 1. CollectionDialogManager
    (managers_dir / "collection_dialog_manager.py").write_text('''# -*- coding: utf-8 -*-
"""
ui/managers/collection_dialog_manager.py

Gerencia diálogos e operações de coleções.
"""
import os
import tkinter as tk
from tkinter import simpledialog


class CollectionDialogManager:
    def __init__(self, parent, collections_manager, database, status_bar):
        self.parent = parent
        self.collections_manager = collections_manager
        self.database = database
        self.status_bar = status_bar
        self.on_collection_changed = None
    
    def add_to_collection(self, project_path: str, collection_name: str) -> None:
        from ui.controllers.collection_controller import CollectionController
        ctrl = CollectionController(self.collections_manager, self.database)
        ctrl.add_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"✅ '{name}' adicionado à coleção '{collection_name}'")
        if self.on_collection_changed:
            self.on_collection_changed()
    
    def remove_from_collection(self, project_path: str, collection_name: str) -> None:
        from ui.controllers.collection_controller import CollectionController
        ctrl = CollectionController(self.collections_manager, self.database)
        ctrl.remove_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"🗑️ '{name}' removido da coleção '{collection_name}'")
        if self.on_collection_changed:
            self.on_collection_changed()
    
    def new_collection_with(self, project_path: str) -> None:
        name = simpledialog.askstring("📁 Nova Coleção", "Nome da nova coleção:", parent=self.parent)
        if not name or not name.strip():
            return
        name = name.strip()
        from ui.controllers.collection_controller import CollectionController
        ctrl = CollectionController(self.collections_manager, self.database)
        ctrl.create_collection_with_project(project_path, name)
        project_name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"📁 Coleção '{name}' criada com '{project_name}'")
        if self.on_collection_changed:
            self.on_collection_changed()
    
    def open_collections_dialog(self) -> None:
        from ui.collections_dialog import CollectionsDialog
        self.parent.wait_window(
            CollectionsDialog(
                parent=self.parent,
                collections_manager=self.collections_manager,
                database=self.database
            )
        )
        if self.on_collection_changed:
            self.on_collection_changed()
''', encoding='utf-8')
    print("   ✓ collection_dialog_manager.py")
    
    # 2. ToggleManager
    (managers_dir / "toggle_manager.py").write_text('''# -*- coding: utf-8 -*-
"""
ui/managers/toggle_manager.py

Gerencia operações de toggle (favorito, done, good, bad).
"""
from config.ui_constants import ACCENT_GOLD, FG_TERTIARY


class ToggleManager:
    def __init__(self, database, db_manager):
        self.database = database
        self.db_manager = db_manager
        self.on_invalidate_cache = None
    
    def toggle_favorite(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(text="⭐" if nv else "☆", fg=ACCENT_GOLD if nv else FG_TERTIARY)
    
    def toggle_done(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(text="✓" if nv else "○", fg="#00FF00" if nv else FG_TERTIARY)
    
    def toggle_good(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv:
                self.database[path]["bad"] = False
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(fg="#00FF00" if nv else FG_TERTIARY)
    
    def toggle_bad(self, path: str, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv:
                self.database[path]["good"] = False
            self.db_manager.save_database()
            if self.on_invalidate_cache:
                self.on_invalidate_cache()
            if btn:
                btn.config(fg="#FF0000" if nv else FG_TERTIARY)
''', encoding='utf-8')
    print("   ✓ toggle_manager.py")
    
    # 3. AnalysisUIBridge
    (managers_dir / "analysis_ui_bridge.py").write_text('''# -*- coding: utf-8 -*-
"""
ui/managers/analysis_ui_bridge.py

Ponte entre AnalysisController e elementos de UI (progress bar, status).
"""


class AnalysisUIBridge:
    def __init__(self, progress_bar, stop_btn, status_bar, root):
        self.progress_bar = progress_bar
        self.stop_btn = stop_btn
        self.status_bar = status_bar
        self.root = root
    
    def show_progress_ui(self) -> None:
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0
    
    def hide_progress_ui(self) -> None:
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()
    
    def update_progress(self, current: int, total: int, message: str = "") -> None:
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.status_bar.config(text=f"{message} ({current}/{total} — {pct:.1f}%)")
        self.root.update_idletasks()
''', encoding='utf-8')
    print("   ✓ analysis_ui_bridge.py\n")
    
    # FASE 2: Modificar main_window.py
    print("🔧 [2/4] Modificando main_window.py...\n")
    
    # Adicionar imports
    content = content.replace(
        'from ui.managers.dialog_manager import DialogManager',
        '''from ui.managers.dialog_manager import DialogManager
from ui.managers.collection_dialog_manager import CollectionDialogManager
from ui.managers.toggle_manager import ToggleManager
from ui.managers.analysis_ui_bridge import AnalysisUIBridge'''
    )
    print("   ✓ Imports adicionados")
    
    # Adicionar managers no __init__ (DEPOIS de _build_ui)
    build_ui_line = '        self._build_ui()'
    if build_ui_line in content:
        content = content.replace(
            build_ui_line,
            '''        self._build_ui()
        
        # Managers criados DEPOIS de UI existir
        self.toggle_mgr = ToggleManager(self.database, self.db_manager)
        self.toggle_mgr.on_invalidate_cache = self._invalidate_cache
        
        self.collection_dialog_mgr = CollectionDialogManager(
            self.root, self.collections_manager, self.database, self.status_bar
        )
        self.collection_dialog_mgr.on_collection_changed = lambda: (
            self.sidebar.refresh(self.database, self.collections_manager),
            self._invalidate_cache(),
            self.display_projects()
        )
        
        self.analysis_ui_bridge = AnalysisUIBridge(
            self.progress_bar, self.stop_btn, self.status_bar, self.root
        )
        self.analysis_ctrl.on_show_progress = self.analysis_ui_bridge.show_progress_ui
        self.analysis_ctrl.on_hide_progress = self.analysis_ui_bridge.hide_progress_ui
        self.analysis_ctrl.on_update_progress = self.analysis_ui_bridge.update_progress'''
        )
        print("   ✓ Managers adicionados DEPOIS de _build_ui()")
    
    # Substituir métodos por delegação
    print("\n🔄 [3/4] Substituindo métodos por delegação...\n")
    
    replacements = [
        # Toggle favorite
        (
            '''    def toggle_favorite(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("favorite", False)
            self.database[path]["favorite"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(text="⭐" if nv else "☆", fg=ACCENT_GOLD if nv else FG_TERTIARY)''',
            '''    def toggle_favorite(self, path, btn=None) -> None:
        self.toggle_mgr.toggle_favorite(path, btn)'''
        ),
        # Toggle done
        (
            '''    def toggle_done(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("done", False)
            self.database[path]["done"] = nv
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(text="✓" if nv else "○", fg="#00FF00" if nv else FG_TERTIARY)''',
            '''    def toggle_done(self, path, btn=None) -> None:
        self.toggle_mgr.toggle_done(path, btn)'''
        ),
        # Toggle good
        (
            '''    def toggle_good(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("good", False)
            self.database[path]["good"] = nv
            if nv: self.database[path]["bad"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(fg="#00FF00" if nv else FG_TERTIARY)''',
            '''    def toggle_good(self, path, btn=None) -> None:
        self.toggle_mgr.toggle_good(path, btn)'''
        ),
        # Toggle bad
        (
            '''    def toggle_bad(self, path, btn=None) -> None:
        if path in self.database:
            nv = not self.database[path].get("bad", False)
            self.database[path]["bad"] = nv
            if nv: self.database[path]["good"] = False
            self.db_manager.save_database()
            self._invalidate_cache()
            if btn: btn.config(fg="#FF0000" if nv else FG_TERTIARY)''',
            '''    def toggle_bad(self, path, btn=None) -> None:
        self.toggle_mgr.toggle_bad(path, btn)'''
        ),
        # Add to collection
        (
            '''    def _on_add_to_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_ctrl.add_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"✅ '{name}' adicionado à coleção '{collection_name}'")''',
            '''    def _on_add_to_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_dialog_mgr.add_to_collection(project_path, collection_name)'''
        ),
        # Remove from collection
        (
            '''    def _on_remove_from_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_ctrl.remove_project(project_path, collection_name)
        name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"🗑️ '{name}' removido da coleção '{collection_name}'")''',
            '''    def _on_remove_from_collection(self, project_path: str, collection_name: str) -> None:
        self.collection_dialog_mgr.remove_from_collection(project_path, collection_name)'''
        ),
        # New collection with
        (
            '''    def _on_new_collection_with(self, project_path: str) -> None:
        name = simpledialog.askstring("📁 Nova Coleção", "Nome da nova coleção:", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        self.collection_ctrl.create_collection_with_project(project_path, name)
        project_name = self.database.get(project_path, {}).get("name", os.path.basename(project_path))
        self.status_bar.config(text=f"📁 Coleção '{name}' criada com '{project_name}'")''',
            '''    def _on_new_collection_with(self, project_path: str) -> None:
        self.collection_dialog_mgr.new_collection_with(project_path)'''
        ),
        # Open collections dialog
        (
            '''    def open_collections_dialog(self) -> None:
        from ui.collections_dialog import CollectionsDialog
        self.root.wait_window(
            CollectionsDialog(
                parent=self.root,
                collections_manager=self.collections_manager,
                database=self.database
            )
        )
        self.sidebar.refresh(self.database, self.collections_manager)
        self._invalidate_cache()''',
            '''    def open_collections_dialog(self) -> None:
        self.collection_dialog_mgr.open_collections_dialog()'''
        ),
        # Progress methods
        (
            '''    def show_progress_ui(self) -> None:
        self.progress_bar.pack(side="left", padx=10)
        self.stop_btn.pack(side="right", padx=10)
        self.progress_bar["value"] = 0''',
            '''    # Delegado para analysis_ui_bridge'''
        ),
        (
            '''    def hide_progress_ui(self) -> None:
        self.progress_bar.pack_forget()
        self.stop_btn.pack_forget()''',
            ''
        ),
        (
            '''    def update_progress(self, current, total, message="") -> None:
        pct = (current / total) * 100 if total else 0
        self.progress_bar["value"] = pct
        self.status_bar.config(text=f"{message} ({current}/{total} — {pct:.1f}%)")
        self.root.update_idletasks()''',
            ''
        ),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"   ✓ Substituído")
    
    # Validar sintaxe
    print("\n✅ [4/4] Validando sintaxe...\n")
    try:
        compile(content, str(main_window), 'exec')
        print("   ✓ Sintaxe válida!\n")
    except SyntaxError as e:
        print(f"\n❌ ERRO DE SINTAXE: {e}")
        print("\n🔄 Restaurando backup original...\n")
        shutil.copy2(original_backup, main_window)
        input("Pressione ENTER...")
        return
    
    # Salvar
    main_window.write_text(content, encoding='utf-8')
    final_lines = len(content.splitlines())
    reduction = initial_lines - final_lines
    
    print("="*70)
    print("\n🎉 REFATORAÇÃO CONCLUÍDA COM SUCESSO!\n")
    print("="*70 + "\n")
    
    print(f"📊 RESULTADO:\n")
    print(f"  Inicial:  {initial_lines} linhas")
    print(f"  Final:    {final_lines} linhas")
    print(f"  Redução:  -{reduction} linhas\n")
    
    print("📁 ARQUIVOS CRIADOS:\n")
    print("  ✓ ui/managers/collection_dialog_manager.py")
    print("  ✓ ui/managers/toggle_manager.py")
    print("  ✓ ui/managers/analysis_ui_bridge.py\n")
    
    print("✅ PRÓXIMOS PASSOS:\n")
    print("  1. python main.py (testar)")
    print("  2. Importar pasta")
    print("  3. Se OK: git add . && git commit && git push\n")
    
    print("="*70 + "\n")
    
    # Auto-delete
    try:
        Path(__file__).unlink()
        print("   🗑️  Script auto-deletado\n")
    except:
        pass
    
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
