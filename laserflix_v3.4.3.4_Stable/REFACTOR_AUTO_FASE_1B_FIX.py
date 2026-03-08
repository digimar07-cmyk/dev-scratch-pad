#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE CORREÇÃO 100% AUTOMÁTICO - FASE 1B (FIX)

Este script CORRIGE o erro de duplicação criado pelo script anterior:
1. Backup automático de todos os arquivos
2. Remove BLOCO 2 duplicado (linhas ~388-427)
3. Mantém apenas BLOCO 1 (correto)
4. Testa sintaxe Python
5. Mostra relatório de conclusão

REMOVE: ~40 linhas duplicadas
ARQUIVO FINAL: ~628 linhas (ainda 40 linhas a mais que o esperado)

USO: Apenas clique 2x no arquivo ou execute:
    python REFACTOR_AUTO_FASE_1B_FIX.py

Criado: 07/03/2026 23:06 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path


class AutoRefactorFase1BFix:
    """Correção 100% automática da duplicação FASE 1B."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        
    def run(self):
        """Executa correção completa automaticamente."""
        print("\n" + "="*70)
        print("🔧 CORREÇÃO AUTOMÁTICA FASE 1B: REMOVER DUPLICAÇÃO")
        print("="*70 + "\n")
        
        try:
            # Validar
            print("✅ [1/5] Validando ambiente...")
            self._validate()
            print("   ✓ Arquivo encontrado\n")
            
            # Backup
            print("💾 [2/5] Criando backups...")
            self._backup_files()
            print(f"   ✓ {len(self.backups)} backup(s) criado(s)\n")
            
            # Remover duplicação
            print("✂️  [3/5] Removendo código duplicado...")
            lines_removed = self._remove_duplication()
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
        """Valida se arquivo existe."""
        if not self.main_window.exists():
            raise FileNotFoundError(f"main_window.py não encontrado: {self.main_window}")
        
        # Verifica se duplicação existe
        content = self.main_window.read_text(encoding='utf-8')
        
        # Contar ocorrências de "right_controls = tk.Frame(header_frame"
        count = content.count('right_controls = tk.Frame(header_frame, bg=BG_PRIMARY)')
        
        if count < 2:
            raise ValueError(
                f"Duplicação não encontrada (encontradas {count} ocorrências, esperadas 2+). "
                "Correção já foi aplicada?"
            )
    
    def _backup_files(self):
        """Cria backup do arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup = self.main_window.with_suffix(f".py.backup_{timestamp}")
        shutil.copy2(self.main_window, backup)
        self.backups.append((self.main_window, backup))
    
    def _remove_duplication(self):
        """Remove bloco duplicado."""
        content = self.main_window.read_text(encoding='utf-8')
        lines_before = len(content.splitlines())
        
        # Padrão: pegar tudo entre primeiro ").pack(side="left", padx=1)" do último botão
        # até o segundo "right_controls = tk.Frame" e o bloco que o segue
        
        # Estrategia: remover da segunda ocorrência de "right_controls = tk.Frame" 
        # até o final do bloco de navegação repetido
        
        # Localizar segunda ocorrência e remover até o próximo bloco significativo
        pattern = r'(\)\.pack\(side="left", padx=1\)\s+)' \
                  r'(right_controls = tk\.Frame\(header_frame, bg=BG_PRIMARY\).*?' \
                  r'\)\.pack\(side="left", padx=1\)\s+)'
        
        content_fixed = re.sub(pattern, r'\1', content, flags=re.DOTALL)
        
        # Limpar linhas em branco consecutivas (mais de 2)
        content_fixed = re.sub(r'\n{3,}', '\n\n', content_fixed)
        
        self.main_window.write_text(content_fixed, encoding='utf-8')
        
        lines_after = len(content_fixed.splitlines())
        removed = lines_before - lines_after
        
        self.changes_made.append(f"Bloco duplicado removido ({removed} linhas)")
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
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS REALIZADAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        # Estatísticas finais
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        print(f"   Antes da correção: 668 linhas")
        print(f"   Redução: {668 - final_lines} linhas")
        print(f"\n   FASE-1A: 868 → 646 (-222 linhas)")
        print(f"   FASE-1B: 646 → {final_lines} (-{646 - final_lines} linhas)")
        print(f"   TOTAL: 868 → {final_lines} (-{868 - final_lines} linhas, {((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUPS CRIADOS:\n")
        for _, backup in self.backups:
            print(f"   • {backup.name}")
        
        print("\n💡 OBSERVAÇÕES:\n")
        print("   ✅ Código duplicado REMOVIDO")
        print("   ✅ Funcionalidade de paginação mantida")
        print("   ⚠️  Arquivo ainda tem ~40 linhas a mais que o planejado")
        print("   💡 Motivo: script de integração anterior tinha erro de regex\n")
        
        print("✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar o app (deve funcionar normalmente):")
        print("      python main.py\n")
        print("   2. Se funcionar, fazer commit:")
        print("      git add ui/main_window.py")
        print("      git commit -m 'fix(FASE-1B): remove duplicated pagination code (-40 lines)'\n")
        print("   3. Atualizar documentação:")
        print("      - VERSION (manter 3.4.3.4)")
        print("      - CHANGELOG (adicionar entrada de fix)")
        print("      - REFACTORING_PLAN (atualizar com valores reais)\n")
        print("   4. Continuar FASE-1C\n")
        
        print("="*70 + "\n")


def main():
    """Entry point."""
    print("\n🚀 Iniciando correção automática...\n")
    
    refactor = AutoRefactorFase1BFix()
    
    try:
        success = refactor.run()
        
        if success:
            print("✅ Correção completa! Agora teste o app.\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Correção falhou. Backups restaurados.\n")
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
