#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SCRIPT DE REFATORAÇÃO 100% AUTOMÁTICO - FASE 1B

Este script faz TUDO sozinho:
1. Backup automático de todos os arquivos
2. Remove código duplicado de paginação inline (~80 linhas)
3. Componente pagination_controls.py já existe - não precisa criar
4. Testa sintaxe Python
5. Mostra relatório de conclusão

REDUÇÃO: ~80 linhas no main_window.py
ARQUIVO FINAL: ~566 linhas

USO: Apenas clique 2x no arquivo ou execute:
    python REFACTOR_AUTO_FASE_1B.py

Criado: 07/03/2026 22:45 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path


class AutoRefactorFase1B:
    """Refatoração 100% automática da FASE 1B."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        
    def run(self):
        """Executa refatoração completa automaticamente."""
        print("\n" + "="*70)
        print("🤖 REFATORAÇÃO AUTOMÁTICA FASE 1B: REMOVER PAGINAÇÃO INLINE")
        print("="*70 + "\n")
        
        try:
            # Validar
            print("✅ [1/5] Validando ambiente...")
            self._validate()
            print("   ✓ Todos os arquivos encontrados\n")
            
            # Backup
            print("💾 [2/5] Criando backups...")
            self._backup_files()
            print(f"   ✓ {len(self.backups)} backup(s) criado(s)\n")
            
            # Remover código inline
            print("✂️  [3/5] Removendo código de paginação inline...")
            lines_removed = self._remove_pagination_code()
            print(f"   ✓ {lines_removed} linhas removidas\n")
            
            # Validar sintaxe
            print("✅ [4/5] Validando sintaxe Python...")
            self._validate_syntax()
            print("   ✓ Sintaxe válida\n")
            
            # Relatório
            print("📊 [5/5] Gerando relatório...\n")
            self._report()
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            print("🔄 Restaurando backups...")
            self._restore_backups()
            print("   ✓ Arquivos restaurados\n")
            return False
    
    def _validate(self):
        """Valida se todos os arquivos existem."""
        if not self.main_window.exists():
            raise FileNotFoundError(f"main_window.py não encontrado: {self.main_window}")
        
        # Verifica se código de paginação existe
        content = self.main_window.read_text(encoding='utf-8')
        if 'sort_frame = tk.Frame(right_controls' not in content:
            raise ValueError(
                "Código de paginação inline não encontrado. "
                "Refatoração já foi aplicada?"
            )
    
    def _backup_files(self):
        """Cria backup dos arquivos que serão modificados."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_to_backup = [self.main_window]
        
        for file in files_to_backup:
            if file.exists():
                backup = file.with_suffix(f".py.backup_{timestamp}")
                shutil.copy2(file, backup)
                self.backups.append((file, backup))
    
    def _remove_pagination_code(self):
        """Remove código de paginação inline do display_projects()."""
        content = self.main_window.read_text(encoding='utf-8')
        lines_before = len(content.splitlines())
        
        # PARTE 1: Remover bloco sort_frame completo (linhas ~354-373)
        # Começa em "sort_frame = tk.Frame(right_controls" até "sort_combo.bind"
        pattern_sort = r'            sort_frame = tk\.Frame\(right_controls.*?sort_combo\.bind\("<<ComboboxSelected>>", on_sort_change\)'
        content = re.sub(pattern_sort, '', content, flags=re.DOTALL)
        
        # PARTE 2: Remover bloco nav_frame completo (linhas ~375-393)
        # Começa em "nav_frame = tk.Frame(right_controls" até último botão
        pattern_nav = r'            nav_frame = tk\.Frame\(right_controls.*?\)\.pack\(side="left", padx=1\)\s*$'
        content = re.sub(pattern_nav, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # Limpar linhas em branco consecutivas (mais de 2)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        self.main_window.write_text(content, encoding='utf-8')
        
        lines_after = len(content.splitlines())
        removed = lines_before - lines_after
        
        self.changes_made.append(f"Código de paginação inline removido ({removed} linhas)")
        return removed
    
    def _validate_syntax(self):
        """Valida sintaxe Python do arquivo modificado."""
        content = self.main_window.read_text(encoding='utf-8')
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(
                f"Erro de sintaxe na linha {e.lineno}: {e.msg}"
            )
    
    def _restore_backups(self):
        """Restaura todos os backups em caso de erro."""
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
    
    def _report(self):
        """Mostra relatório final."""
        print("="*70)
        print("\n🎉 REFATORAÇÃO CONCLUÍDA COM SUCESSO!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS REALIZADAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        # Estatísticas finais
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        print(f"   FASE-1A: 868 → 646 (-222 linhas)")
        print(f"   FASE-1B: 646 → {final_lines} (-{646 - final_lines} linhas)")
        print(f"   TOTAL: 868 → {final_lines} (-{868 - final_lines} linhas, {((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUPS CRIADOS:\n")
        for _, backup in self.backups:
            print(f"   • {backup.name}")
        
        print("\n⚠️  ATENÇÃO IMPORTANTE:\n")
        print("   ⚠️  O componente pagination_controls.py já existe mas usa tema diferente!")
        print("   ⚠️  A UI de paginação foi REMOVIDA mas NÃO SUBSTITUÍDA ainda.")
        print("   ⚠️  Isso é INTENCIONAL - estamos removendo duplicação primeiro.\n")
        print("   💡 Próximo passo: Atualizar pagination_controls.py para usar tema atual")
        print("            e integrar no display_projects()\n")
        
        print("✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar o app (pode NÃO ter paginação ainda):")
        print("      python main.py\n")
        print("   2. Se abrir sem erros, fazer commit:")
        print("      git add ui/main_window.py")
        print("      git commit -m 'refactor(FASE-1B): remove inline pagination code (-80 lines)'\n")
        print("   3. Depois integrar componente pagination_controls.py")
        print("      (será feito em próximo script)\n")
        print("   4. Se tiver erro AGORA, restaurar backup:")
        print(f"      Copiar {self.backups[0][1].name} de volta\n")
        
        print("="*70 + "\n")


def main():
    """Entry point."""
    print("\n🚀 Iniciando refatoração automática...\n")
    
    refactor = AutoRefactorFase1B()
    
    try:
        success = refactor.run()
        
        if success:
            print("✅ Refatoração completa! Agora teste o app.\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Refatoração falhou. Backups restaurados.\n")
            input("Pressione ENTER para sair...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}\n")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()
