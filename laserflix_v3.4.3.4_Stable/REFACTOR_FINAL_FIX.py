#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE CORREÇÃO DEFINITIVO - FASE 1B

Este script FAZ TUDO DE UMA VEZ:
1. Backup automático
2. Remove duplicação CORRETAMENTE (linhas 398-413)
3. LIMPA scripts antigos da pasta
4. Testa sintaxe Python
5. Mostra relatório

REMOVE: ~16 linhas duplicadas
LIMPA: 4 scripts antigos
ARQUIVO FINAL: ~640 linhas

USO: python REFACTOR_FINAL_FIX.py

Criado: 07/03/2026 23:17 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path


class FinalFix:
    """Correção definitiva + limpeza."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        self.scripts_to_remove = [
            "REFACTOR_AUTO_FASE_1B.py",
            "REFACTOR_AUTO_FASE_1B_INTEGRATE.py",
            "REFACTOR_AUTO_FASE_1B_FIX.py",
        ]
        
    def run(self):
        print("\n" + "="*70)
        print("🔧 CORREÇÃO DEFINITIVA + LIMPEZA")
        print("="*70 + "\n")
        
        try:
            print("✅ [1/6] Validando...")
            self._validate()
            print("   ✓ Arquivo encontrado\n")
            
            print("💾 [2/6] Backup...")
            self._backup_files()
            print(f"   ✓ Backup criado\n")
            
            print("✂️  [3/6] Removendo duplicação...")
            lines_removed = self._remove_duplication()
            print(f"   ✓ {lines_removed} linhas removidas\n")
            
            print("🧹 [4/6] Limpando scripts antigos...")
            cleaned = self._clean_old_scripts()
            print(f"   ✓ {cleaned} scripts removidos\n")
            
            print("✅ [5/6] Validando sintaxe...")
            self._validate_syntax()
            print("   ✓ Sintaxe válida\n")
            
            print("📊 [6/6] Relatório...\n")
            self._report()
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            print("🔄 Restaurando backup...")
            self._restore_backups()
            print("   ✓ Restaurado\n")
            return False
    
    def _validate(self):
        if not self.main_window.exists():
            raise FileNotFoundError(f"main_window.py não encontrado")
        
        content = self.main_window.read_text(encoding='utf-8')
        
        # Procurar padrão exato da duplicação (linhas 398-413)
        pattern = r'tk\.Label\(nav_frame, text=f"Pág.*?\)\.pack\(side="left", padx=8\)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if len(matches) < 2:
            raise ValueError(
                f"Duplicação não encontrada (encontradas {len(matches)} ocorrências). "
                "Já foi corrigida?"
            )
    
    def _backup_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.main_window.with_suffix(f".py.backup_{timestamp}")
        shutil.copy2(self.main_window, backup)
        self.backups.append((self.main_window, backup))
    
    def _remove_duplication(self):
        content = self.main_window.read_text(encoding='utf-8')
        lines_before = len(content.splitlines())
        
        # Localizar e remover segunda ocorrência dos 3 últimos botões
        # Padrão: do segundo "tk.Label(nav_frame, text=f\"Pág" até o último ").pack(side=\"left\", padx=1)"
        
        # Primeiro: dividir no primeiro bloco de botões
        parts = content.split('tk.Button(nav_frame, text="⏭"', 1)
        if len(parts) != 2:
            raise ValueError("Padrão de navegação não encontrado")
        
        before_first = parts[0]
        after_first = parts[1]
        
        # Encontrar final do primeiro bloco (até primeiro ").pack(side=\"left\", padx=1)")
        end_first_block = after_first.find(').pack(side="left", padx=1)')
        if end_first_block == -1:
            raise ValueError("Final do primeiro bloco não encontrado")
        
        first_block_end = after_first[:end_first_block + len(').pack(side="left", padx=1)')]
        remainder = after_first[end_first_block + len(').pack(side="left", padx=1)'):]
        
        # Agora remover bloco duplicado (começa com tk.Label e termina com último botão)
        # Padrão da duplicação:
        duplicate_pattern = r'\s+tk\.Label\(nav_frame, text=f"Pág.*?tk\.Button\(nav_frame, text="⏭".*?\)\.pack\(side="left", padx=1\)'
        
        remainder_cleaned = re.sub(duplicate_pattern, '', remainder, count=1, flags=re.DOTALL)
        
        # Reconstruir
        content_fixed = before_first + 'tk.Button(nav_frame, text="⏭"' + first_block_end + remainder_cleaned
        
        # Limpar linhas em branco consecutivas
        content_fixed = re.sub(r'\n{3,}', '\n\n', content_fixed)
        
        self.main_window.write_text(content_fixed, encoding='utf-8')
        
        lines_after = len(content_fixed.splitlines())
        removed = lines_before - lines_after
        
        self.changes_made.append(f"Duplicação removida ({removed} linhas)")
        return removed
    
    def _clean_old_scripts(self):
        cleaned = 0
        for script_name in self.scripts_to_remove:
            script_path = self.base_dir / script_name
            if script_path.exists():
                script_path.unlink()
                cleaned += 1
                self.changes_made.append(f"Script {script_name} removido")
        return cleaned
    
    def _validate_syntax(self):
        content = self.main_window.read_text(encoding='utf-8')
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
    
    def _restore_backups(self):
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
    
    def _report(self):
        print("="*70)
        print("\n🎉 CORREÇÃO COMPLETA!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        print(f"   FASE-1A: 868 → 646 (-222)")
        print(f"   FASE-1B: 646 → {final_lines} (-{646 - final_lines})")
        print(f"   TOTAL: 868 → {final_lines} (-{868 - final_lines}, {((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUP:\n")
        for _, backup in self.backups:
            print(f"   • {backup.name}")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar: python main.py")
        print("   2. Commit: git add . && git commit -m 'fix(FASE-1B): clean duplication'")
        print("   3. Documentar: atualizar CHANGELOG e REFACTORING_PLAN")
        print("   4. Este script IRÁ SE AUTO-DELETAR após sucesso\n")
        
        # Auto-delete
        print("   🗑️  Auto-deletando este script...")
        try:
            Path(__file__).unlink()
            print("   ✓ REFACTOR_FINAL_FIX.py removido\n")
        except:
            print("   ⚠️  Não foi possível auto-deletar (delete manualmente)\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando correção definitiva...\n")
    
    fix = FinalFix()
    
    try:
        success = fix.run()
        
        if success:
            print("✅ SUCESSO TOTAL! Pasta limpa, duplicação corrigida.\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Falhou. Backup restaurado.\n")
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
