#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 REFACTOR MANUAL - FASES 1D + 1E + 1F

Este script é mais SEGURO que o automático.
Ele faz busca/substituição de blocos completos sem manipular indentação.

USO: python REFACTOR_MANUAL_1D_1E_1F.py

Criado: 08/03/2026 09:36 BRT
Modelo: Claude Sonnet 4.5
"""

import shutil
from datetime import datetime
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("🔧 REFACTOR MANUAL - FASES 1D + 1E + 1F")
    print("="*70 + "\n")
    
    base_dir = Path(__file__).parent
    main_window = base_dir / "ui" / "main_window.py"
    
    if not main_window.exists():
        print(f"❌ Arquivo não encontrado: {main_window}")
        input("\nPressione ENTER para sair...")
        return
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = main_window.with_suffix(f".py.backup_{timestamp}")
    shutil.copy2(main_window, backup)
    print(f"💾 Backup criado: {backup.name}\n")
    
    content = main_window.read_text(encoding='utf-8')
    initial_lines = len(content.splitlines())
    print(f"📄 Estado inicial: {initial_lines} linhas\n")
    
    # FASE 1D: _build_header
    print("🔧 [1/3] FASE-1D: Adicionando _build_header()...")
    
    # Adicionar método ANTES do comentário # DISPLAY
    header_method = '''    def _build_header(self, total_count: int, page_info: dict) -> None:
        """Constrói cabeçalho com título e navegação (FASE-1D)."""
        title_map = {
            "favorite": "⭐ Favoritos", "done": "✓ Já Feitos",
            "good": "👍 Bons", "bad": "👎 Ruins",
        }
        title = title_map.get(self.display_ctrl.current_filter, "Todos os Projetos")
        if self.display_ctrl.current_origin != "all":
            title += f" — {self.display_ctrl.current_origin}"
        if self.display_ctrl.current_categories:
            title += f" — {', '.join(self.display_ctrl.current_categories)}"
        if self.display_ctrl.current_tag:
            title += f" — #{self.display_ctrl.current_tag}"
        if self.display_ctrl.search_query:
            title += f' — "{self.display_ctrl.search_query}"'
        
        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=COLS, sticky="ew", padx=10, pady=(0, 5))
        
        tk.Label(header_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).pack(side="left")
        
        if total_count > 0:
            self._build_navigation_controls(header_frame, page_info)

'''
    
    content = content.replace('    # DISPLAY\n', header_method + '    # DISPLAY\n')
    
    # Substituir bloco do header inline por chamada
    old_header_block = '''        # Header
        title_map = {
            "favorite": "⭐ Favoritos", "done": "✓ Já Feitos",
            "good": "👍 Bons", "bad": "👎 Ruins",
        }
        title = title_map.get(self.display_ctrl.current_filter, "Todos os Projetos")
        if self.display_ctrl.current_origin != "all":
            title += f" — {self.display_ctrl.current_origin}"
        if self.display_ctrl.current_categories:
            title += f" — {', '.join(self.display_ctrl.current_categories)}"
        if self.display_ctrl.current_tag:
            title += f" — #{self.display_ctrl.current_tag}"
        if self.display_ctrl.search_query:
            title += f' — "{self.display_ctrl.search_query}"'
        
        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)
        header_frame.grid(row=0, column=0, columnspan=COLS, sticky="ew", padx=10, pady=(0, 5))
        
        tk.Label(header_frame, text=title,
                 font=("Arial", 20, "bold"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor="w"
                 ).pack(side="left")
        
        # Navigation
        if total_count > 0:
            self._build_navigation_controls(header_frame, page_info)
        '''
    
    new_header_call = '''        self._build_header(total_count, page_info)
        '''
    
    content = content.replace(old_header_block, new_header_call)
    print("   ✓ Método extraído\n")
    
    # FASE 1E: _build_empty_state
    print("🔧 [2/3] FASE-1E: Adicionando _build_empty_state()...")
    
    empty_method = '''    def _build_empty_state(self) -> None:
        """Exibe mensagem quando não há projetos (FASE-1E)."""
        tk.Label(self.scrollable_frame,
                 text="Nenhum projeto.\\nClique em 'Importar Pastas' para adicionar.",
                 font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                 ).grid(row=2, column=0, columnspan=COLS, pady=80)

'''
    
    content = content.replace('    def _get_thumbnail_async', empty_method + '    def _get_thumbnail_async')
    
    old_empty_block = '''        if not all_filtered:
            tk.Label(self.scrollable_frame,
                     text="Nenhum projeto.\\nClique em 'Importar Pastas' para adicionar.",
                     font=("Arial", 14), bg=BG_PRIMARY, fg=FG_TERTIARY, justify="center"
                     ).grid(row=2, column=0, columnspan=COLS, pady=80)
            return
        '''
    
    new_empty_call = '''        if not all_filtered:
            self._build_empty_state()
            return
        '''
    
    content = content.replace(old_empty_block, new_empty_call)
    print("   ✓ Método extraído\n")
    
    # FASE 1F: _build_cards_grid
    print("🔧 [3/3] FASE-1F: Adicionando _build_cards_grid()...")
    
    cards_method = '''    def _build_cards_grid(self, page_items: list) -> None:
        """Constrói grid de cards com callbacks (FASE-1F)."""
        card_cb = {
            "on_open_modal": self.open_project_modal,
            "on_toggle_favorite": self.toggle_favorite,
            "on_toggle_done": self.toggle_done,
            "on_toggle_good": self.toggle_good,
            "on_toggle_bad": self.toggle_bad,
            "on_analyze_single": self.analyze_single_project,
            "on_open_folder": open_folder,
            "on_set_category": lambda c: self.display_ctrl.add_filter_chip("category", c),
            "on_set_tag": lambda t: self.display_ctrl.add_filter_chip("tag", t),
            "on_set_origin": lambda o: self.display_ctrl.add_filter_chip("origin", o),
            "on_set_collection": lambda c: self.display_ctrl.add_filter_chip("collection", c),
            "get_cover_image_async": self._get_thumbnail_async,
            "selection_mode": self.selection_ctrl.selection_mode,
            "selected_paths": self.selection_ctrl.selected_paths,
            "on_toggle_select": self.selection_ctrl.toggle_project,
            "on_add_to_collection": self._on_add_to_collection,
            "on_remove_from_collection": self._on_remove_from_collection,
            "on_new_collection_with": self._on_new_collection_with,
            "get_collections": lambda: list(self.collections_manager.collections.keys()),
            "get_project_collections": lambda p: self.collections_manager.get_project_collections(p),
        }
        
        for i, (project_path, project_data) in enumerate(page_items):
            row = (i // COLS) + 2
            col = i % COLS
            build_card(self.scrollable_frame, project_path, project_data, card_cb, row, col)
        
        self.content_canvas.yview_moveto(0)

'''
    
    content = content.replace('    def _build_empty_state', cards_method + '    def _build_empty_state')
    
    old_cards_block = '''        # CARDS
        card_cb = {
            "on_open_modal": self.open_project_modal,
            "on_toggle_favorite": self.toggle_favorite,
            "on_toggle_done": self.toggle_done,
            "on_toggle_good": self.toggle_good,
            "on_toggle_bad": self.toggle_bad,
            "on_analyze_single": self.analyze_single_project,
            "on_open_folder": open_folder,
            "on_set_category": lambda c: self.display_ctrl.add_filter_chip("category", c),
            "on_set_tag": lambda t: self.display_ctrl.add_filter_chip("tag", t),
            "on_set_origin": lambda o: self.display_ctrl.add_filter_chip("origin", o),
            "on_set_collection": lambda c: self.display_ctrl.add_filter_chip("collection", c),
            "get_cover_image_async": self._get_thumbnail_async,
            "selection_mode": self.selection_ctrl.selection_mode,
            "selected_paths": self.selection_ctrl.selected_paths,
            "on_toggle_select": self.selection_ctrl.toggle_project,
            "on_add_to_collection": self._on_add_to_collection,
            "on_remove_from_collection": self._on_remove_from_collection,
            "on_new_collection_with": self._on_new_collection_with,
            "get_collections": lambda: list(self.collections_manager.collections.keys()),
            "get_project_collections": lambda p: self.collections_manager.get_project_collections(p),
        }
        
        for i, (project_path, project_data) in enumerate(page_items):
            row = (i // COLS) + 2
            col = i % COLS
            build_card(self.scrollable_frame, project_path, project_data, card_cb, row, col)
        
        self.content_canvas.yview_moveto(0)'''
    
    new_cards_call = '''        self._build_cards_grid(page_items)'''
    
    content = content.replace(old_cards_block, new_cards_call)
    print("   ✓ Método extraído\n")
    
    # Validar
    print("✅ Validando sintaxe...")
    try:
        compile(content, str(main_window), 'exec')
        print("   ✓ Sintaxe OK\n")
    except SyntaxError as e:
        print(f"\n❌ ERRO de sintaxe linha {e.lineno}: {e.msg}")
        print("🔄 Restaurando backup...\n")
        shutil.copy2(backup, main_window)
        input("Pressione ENTER para sair...")
        return
    
    # Salvar
    print("💾 Salvando...")
    main_window.write_text(content, encoding='utf-8')
    final_lines = len(content.splitlines())
    print(f"   ✓ Salvo: {final_lines} linhas\n")
    
    # Relatório
    reduction = initial_lines - final_lines
    pct = (reduction / initial_lines) * 100
    
    print("="*70)
    print("\n✅ REFATORAÇÃO CONCLUÍDA!\n")
    print("="*70)
    print(f"\n📊 Inicial: {initial_lines} linhas")
    print(f"   Final: {final_lines} linhas")
    print(f"   Redução: -{reduction} linhas ({pct:.1f}%)\n")
    
    total_reduction = 868 - final_lines
    total_pct = (total_reduction / 868) * 100
    print(f"🎯 TOTAL desde v3.4.3.0:")
    print(f"   868 → {final_lines} linhas")
    print(f"   -{total_reduction} linhas ({total_pct:.1f}%)\n")
    
    if total_pct >= 40:
        print("⭐ META DE 40% ALCANÇADA!\n")
    
    print("✅ PRÓXIMOS PASSOS:\n")
    print("   1. python main.py (testar app)")
    print("   2. Importar pastas")
    print("   3. Navegar páginas")
    print("   4. Se OK: commit!\n")
    
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
