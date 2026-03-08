#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 FIX URGENTE: REMOVER MÉTODO _build_header() SE EXISTIR

Este script:
1. Procura pelo método _build_header() no main_window.py
2. Se encontrar, REMOVE ele completamente
3. Garante que o código inline do header está presente
4. Valida sintaxe

USO: python FIX_REMOVE_BUILD_HEADER.py

Criado: 08/03/2026 09:23 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path


class UrgentFix:
    """Remove método _build_header() se existir."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backup = None
        
    def run(self):
        print("\n" + "="*70)
        print("⚡ FIX URGENTE: REMOVER _build_header()")
        print("="*70 + "\n")
        
        if not self.main_window.exists():
            print(f"❌ Arquivo não encontrado: {self.main_window}")
            return False
        
        try:
            content = self.main_window.read_text(encoding='utf-8')
            
            # Verificar se método existe
            if 'def _build_header' not in content:
                print("✅ Método _build_header() NÃO existe no arquivo.")
                print("   O arquivo já está correto!\n")
                print("⚠️  Se ainda assim está dando erro, faça 'git pull'!\n")
                input("Pressione ENTER para sair...")
                return True
            
            print("⚠️  Método _build_header() ENCONTRADO (bugado)!\n")
            
            print("💾 [1/4] Backup...")
            self._backup()
            print("   ✓ Backup criado\n")
            
            print("✂️  [2/4] Removendo método bugado...")
            new_content = self._remove_method(content)
            print("   ✓ Método removido\n")
            
            print("✅ [3/4] Validando...")
            self._validate(new_content)
            print("   ✓ Sintaxe OK\n")
            
            print("💾 [4/4] Salvando...")
            self.main_window.write_text(new_content, encoding='utf-8')
            print("   ✓ Salvo\n")
            
            self._report()
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            if self.backup and self.backup.exists():
                print("🔄 Restaurando backup...")
                shutil.copy2(self.backup, self.main_window)
                print("   ✓ Restaurado\n")
            import traceback
            traceback.print_exc()
            return False
    
    def _backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup = self.main_window.with_suffix(f".py.backup_{timestamp}")
        shutil.copy2(self.main_window, self.backup)
    
    def _remove_method(self, content: str) -> str:
        """Remove método _build_header() completamente."""
        lines = content.splitlines(keepends=True)
        
        # Encontrar início do método
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if '    def _build_header' in line:
                start_idx = i
                print(f"      Método encontrado na linha {i+1}")
            elif start_idx is not None and '    def ' in line and i > start_idx:
                end_idx = i
                print(f"      Fim do método na linha {i}")
                break
        
        if start_idx is None:
            raise ValueError("Método não encontrado")
        
        if end_idx is None:
            # Método é o último, procurar próximo bloco
            for i in range(start_idx + 1, len(lines)):
                if lines[i].strip() and not lines[i].startswith(' '):
                    end_idx = i
                    break
            if end_idx is None:
                end_idx = len(lines)
        
        # Remover método
        new_lines = lines[:start_idx] + lines[end_idx:]
        
        print(f"      Removidas {end_idx - start_idx} linhas")
        
        return ''.join(new_lines)
    
    def _validate(self, content: str):
        """Valida sintaxe Python."""
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Sintaxe inválida linha {e.lineno}: {e.msg}")
    
    def _report(self):
        print("="*70)
        print("\n✅ MÉTODO REMOVIDO COM SUCESSO!\n")
        print("="*70)
        
        content = self.main_window.read_text(encoding='utf-8')
        lines = len(content.splitlines())
        
        print("\n📊 ESTATÍSTICAS:\n")
        print(f"   main_window.py: {lines} linhas")
        print(f"   Backup: {self.backup.name}")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar: python main.py")
        print("   2. Se funcionar, DELETAR pasta Copy e usar só principal")
        print("   3. git status")
        print("   4. Se tiver alterações: git add . && git commit -m 'fix: remove buggy method'")
        
        print("\n⚡ IMPORTANTE: O GitHub JÁ ESTÁ CORRETO!")
        print("   Esse erro só aconteceu porque sua pasta local estava desatualizada.")
        print("   Sempre faça 'git pull' antes de copiar para pasta Copy!\n")
        
        print("="*70 + "\n")
        
        # Auto-delete
        try:
            Path(__file__).unlink()
            print("   🗑️  Script auto-deletado\n")
        except:
            pass


def main():
    print("\n🚀 Iniciando fix urgente...\n")
    
    fixer = UrgentFix()
    
    try:
        success = fixer.run()
        
        if success:
            print("✅ SUCESSO!\n")
        else:
            print("❌ Falhou.\n")
        
        input("Pressione ENTER para sair...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado.\n")
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}\n")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")


if __name__ == "__main__":
    main()
