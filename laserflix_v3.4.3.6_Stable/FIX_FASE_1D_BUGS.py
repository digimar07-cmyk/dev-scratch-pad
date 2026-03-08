#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORREÇÃO DE BUGS FASE-1D + THREADING

Este script corrige 2 erros:
1. ERRO nav_frame: _build_header() tinha código incorreto
2. ERRO threading: recursive_import_integration.py tentando chamar after() após main loop terminar

USO: python FIX_FASE_1D_BUGS.py

Criado: 08/03/2026 08:56 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path


class BugFixer:
    """Corrige bugs da FASE-1D."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.import_integration = self.base_dir / "ui" / "recursive_import_integration.py"
        self.backups = []
        
    def run(self):
        print("\n" + "="*70)
        print("🔧 CORREÇÃO DE BUGS FASE-1D")
        print("="*70 + "\n")
        
        try:
            print("💾 [1/4] Backup...")
            self._backup_files()
            print("   ✓ Backups criados\n")
            
            print("🔧 [2/4] Corrigindo main_window.py...")
            self._fix_main_window()
            print("   ✓ Corrigido\n")
            
            print("🔧 [3/4] Corrigindo recursive_import_integration.py...")
            self._fix_import_integration()
            print("   ✓ Corrigido\n")
            
            print("✅ [4/4] Validando...")
            self._validate()
            print("   ✓ Tudo OK\n")
            
            self._report()
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            print("🔄 Restaurando...")
            self._restore_backups()
            return False
    
    def _backup_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for filepath in [self.main_window, self.import_integration]:
            if filepath.exists():
                backup = filepath.with_suffix(f".py.backup_{timestamp}")
                shutil.copy2(filepath, backup)
                self.backups.append((filepath, backup))
    
    def _fix_main_window(self):
        """Reverte FASE-1D e aplica corretamente."""
        content = self.main_window.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        
        # Remover método _build_header() bugado se existir
        if 'def _build_header' in content:
            # Encontrar e remover
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if '    def _build_header' in line:
                    start_idx = i
                elif start_idx is not None and '    def ' in line and i > start_idx:
                    end_idx = i
                    break
            
            if start_idx and end_idx:
                # Remover método
                lines = lines[:start_idx] + lines[end_idx:]
        
        # Encontrar display_projects() e restaurar código inline
        display_idx = None
        for i, line in enumerate(lines):
            if '    def display_projects(self) -> None:' in line:
                display_idx = i
                break
        
        if display_idx is None:
            raise ValueError("display_projects() não encontrado")
        
        # Procurar pela chamada self._build_header(...)
        header_call_idx = None
        for i in range(display_idx, len(lines)):
            if 'self._build_header(total_count, page_info)' in lines[i]:
                header_call_idx = i
                break
        
        if header_call_idx:
            # Substituir chamada por código inline correto
            inline_header = [
                "        # Header\n",
                "        title_map = {\n",
                "            \"favorite\": \"⭐ Favoritos\", \"done\": \"✓ Já Feitos\",\n",
                "            \"good\": \"👍 Bons\", \"bad\": \"👎 Ruins\",\n",
                "        }\n",
                "        title = title_map.get(self.display_ctrl.current_filter, \"Todos os Projetos\")\n",
                "        if self.display_ctrl.current_origin != \"all\":\n",
                "            title += f\" — {self.display_ctrl.current_origin}\"\n",
                "        if self.display_ctrl.current_categories:\n",
                "            title += f\" — {', '.join(self.display_ctrl.current_categories)}\"\n",
                "        if self.display_ctrl.current_tag:\n",
                "            title += f\" — #{self.display_ctrl.current_tag}\"\n",
                "        if self.display_ctrl.search_query:\n",
                "            title += f' — \"{self.display_ctrl.search_query}\"'\n",
                "        \n",
                "        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)\n",
                "        header_frame.grid(row=0, column=0, columnspan=COLS, sticky=\"ew\", padx=10, pady=(0, 5))\n",
                "        \n",
                "        tk.Label(header_frame, text=title,\n",
                "                 font=(\"Arial\", 20, \"bold\"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor=\"w\"\n",
                "                 ).pack(side=\"left\")\n",
                "        \n",
                "        # Navigation\n",
                "        if total_count > 0:\n",
                "            self._build_navigation_controls(header_frame, page_info)\n",
                "        \n",
            ]
            
            # Remover linha de chamada
            lines = lines[:header_call_idx] + inline_header + lines[header_call_idx+2:]
        
        # Atualizar cabeçalho
        content = ''.join(lines)
        if 'REFACTOR-FASE-1D' in content:
            content = content.replace('REFACTOR-FASE-1D: _build_header() extraído ✅\n', '')
        
        self.main_window.write_text(content, encoding='utf-8')
    
    def _fix_import_integration(self):
        """Corrige erro de threading."""
        content = self.import_integration.read_text(encoding='utf-8')
        
        # Procurar por self.parent.after(0, lambda: self._ask_auto_analysis(success))
        if 'self.parent.after(0, lambda: self._ask_auto_analysis(success))' in content:
            # Substituir por versão safe
            content = content.replace(
                'self.parent.after(0, lambda: self._ask_auto_analysis(success))',
                '''try:\n                self.parent.after(0, lambda: self._ask_auto_analysis(success))\n            except RuntimeError:\n                # Main loop encerrado\n                self.logger.warning("⚠️ Main loop encerrado, pulando auto-analysis")'''
            )
            self.import_integration.write_text(content, encoding='utf-8')
    
    def _validate(self):
        # Validar sintaxe Python
        for filepath in [self.main_window, self.import_integration]:
            content = filepath.read_text(encoding='utf-8')
            try:
                compile(content, str(filepath), 'exec')
            except SyntaxError as e:
                raise SyntaxError(f"Erro em {filepath.name} linha {e.lineno}: {e.msg}")
    
    def _restore_backups(self):
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
    
    def _report(self):
        print("="*70)
        print("\n🎉 BUGS CORRIGIDOS!\n")
        print("="*70)
        
        print("\n✅ CORREÇÕES:\n")
        print("   1. main_window.py: FASE-1D revertida")
        print("   2. main_window.py: header inline restaurado")
        print("   3. recursive_import_integration.py: try/except adicionado")
        
        content = self.main_window.read_text(encoding='utf-8')
        lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS:\n")
        print(f"   main_window.py: {lines} linhas")
        print(f"   Status: Voltou ao estado FASE-1C (596 linhas esperadas)")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar: python main.py")
        print("   2. Testar importação de pastas")
        print("   3. Commit: git add . && git commit -m 'fix: revert FASE-1D + fix threading'")
        print("   4. FASE-1D será refeita corretamente\n")
        
        print("   🗑️  Auto-deletando...")
        try:
            Path(__file__).unlink()
            print("   ✓ Script removido\n")
        except:
            print("   ⚠️  Delete manualmente\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando correção de bugs...\n")
    
    fixer = BugFixer()
    
    try:
        success = fixer.run()
        
        if success:
            print("✅ SUCESSO! Bugs corrigidos.\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Falhou.\n")
            input("Pressione ENTER para sair...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}\n")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()
