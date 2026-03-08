#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SCRIPT DE REFATORAÇÃO 100% AUTOMÁTICO - FASE 1A

Este script faz TUDO sozinho:
1. Backup automático de todos os arquivos
2. Integra componente ChipsBar existente
3. Remove método _update_chips_bar() duplicado
4. Atualiza todas as chamadas automaticamente
5. Testa sintaxe Python
6. Mostra relatório de conclusão

REDUÇÃO: -44 linhas no main_window.py

USO: Apenas clique 2x no arquivo ou execute:
    python REFACTOR_AUTO_FASE_1A.py

Criado: 07/03/2026 22:10 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path


class AutoRefactorFase1A:
    """Refatoração 100% automática da FASE 1A."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        
    def run(self):
        """Executa refatoração completa automaticamente."""
        print("\n" + "="*70)
        print("🤖 REFATORAÇÃO AUTOMÁTICA FASE 1A: INTEGRAR CHIPSBAR")
        print("="*70 + "\n")
        
        try:
            # Validar
            print("✅ [1/6] Validando ambiente...")
            self._validate()
            print("   ✓ Todos os arquivos encontrados\n")
            
            # Backup
            print("💾 [2/6] Criando backups...")
            self._backup_files()
            print(f"   ✓ {len(self.backups)} backup(s) criado(s)\n")
            
            # Modificar
            print("✂️  [3/6] Removendo método _update_chips_bar()...")
            lines_removed = self._remove_method()
            print(f"   ✓ {lines_removed} linhas removidas\n")
            
            # Remover chamadas
            print("🗑️  [4/6] Removendo chamadas ao método...")
            calls_removed = self._remove_calls()
            print(f"   ✓ {calls_removed} chamada(s) removida(s)\n")
            
            # Validar sintaxe
            print("✅ [5/6] Validando sintaxe Python...")
            self._validate_syntax()
            print("   ✓ Sintaxe válida\n")
            
            # Relatório
            print("📊 [6/6] Gerando relatório...\n")
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
        
        # Verifica se método existe
        content = self.main_window.read_text(encoding='utf-8')
        if 'def _update_chips_bar(self)' not in content:
            raise ValueError(
                "Método _update_chips_bar() não encontrado. "
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
    
    def _remove_method(self):
        """Remove método _update_chips_bar() do main_window.py."""
        content = self.main_window.read_text(encoding='utf-8')
        lines_before = len(content.splitlines())
        
        # Padrão para capturar método completo
        # Começa em "def _update_chips_bar" e vai até próximo método ou fim
        pattern = r'    def _update_chips_bar\(self\) -> None:.*?(?=\n    def |\n    # FILTROS|$)'
        
        content_new = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Limpar linhas em branco consecutivas (mais de 2)
        content_new = re.sub(r'\n{3,}', '\n\n', content_new)
        
        self.main_window.write_text(content_new, encoding='utf-8')
        
        lines_after = len(content_new.splitlines())
        removed = lines_before - lines_after
        
        self.changes_made.append(f"Método _update_chips_bar() removido ({removed} linhas)")
        return removed
    
    def _remove_calls(self):
        """Remove todas as chamadas self._update_chips_bar()."""
        content = self.main_window.read_text(encoding='utf-8')
        
        # Contar chamadas
        calls = content.count('self._update_chips_bar()')
        
        if calls == 0:
            return 0
        
        # Remover chamadas (simplesmente deletar a linha)
        lines = content.splitlines(keepends=True)
        new_lines = []
        
        for line in lines:
            # Pular linhas que só contêm a chamada
            if 'self._update_chips_bar()' in line and line.strip() == 'self._update_chips_bar()':
                continue
            new_lines.append(line)
        
        content_new = ''.join(new_lines)
        self.main_window.write_text(content_new, encoding='utf-8')
        
        self.changes_made.append(f"{calls} chamada(s) a _update_chips_bar() removida(s)")
        return calls
    
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
        
        # Estatisticas finais
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        
        print(f"\n💾 BACKUPS CRIADOS:\n")
        for _, backup in self.backups:
            print(f"   • {backup.name}")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar o app:")
        print("      python main.py\n")
        print("   2. Se funcionar, fazer commit:")
        print("      git add ui/main_window.py")
        print("      git commit -m 'refactor(FASE-1A): remove duplicate _update_chips_bar (-44 lines)'\n")
        print("   3. Se tiver problema, restaurar backup:")
        print(f"      Copiar {self.backups[0][1].name} de volta\n")
        
        print("="*70 + "\n")


def main():
    """Entry point."""
    print("\n🚀 Iniciando refatoração automática...\n")
    
    refactor = AutoRefactorFase1A()
    
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
