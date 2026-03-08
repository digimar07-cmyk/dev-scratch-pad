#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SINCRONIZAR PASTA COPY COM CORREÇÕES

Este script copia os arquivos corrigidos da pasta principal
para a pasta "laserflix_v3.4.3.7_Stable - Copy".

USO: python SYNC_COPY_FOLDER.py

Criado: 08/03/2026 09:15 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import shutil
from pathlib import Path


class FolderSyncer:
    """Sincroniza pasta Copy com correções."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.copy_dir = self.base_dir.parent / f"{self.base_dir.name} - Copy"
        
    def run(self):
        print("\n" + "="*70)
        print("🔄 SINCRONIZANDO PASTA COPY")
        print("="*70 + "\n")
        
        if not self.copy_dir.exists():
            print(f"❌ Pasta Copy não encontrada: {self.copy_dir}")
            print("\n⚠️  Rode o app na pasta correta sem ' - Copy'!\n")
            input("Pressione ENTER para sair...")
            return False
        
        print(f"✅ Pasta Copy encontrada: {self.copy_dir.name}\n")
        
        try:
            print("📋 [1/3] Copiando main_window.py...")
            self._copy_file("ui/main_window.py")
            print("   ✓ Copiado\n")
            
            print("📋 [2/3] Copiando recursive_import_integration.py...")
            self._copy_file("ui/recursive_import_integration.py")
            print("   ✓ Copiado\n")
            
            print("📋 [3/3] Removendo scripts antigos...")
            self._clean_old_scripts()
            print("   ✓ Limpo\n")
            
            self._report()
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            import traceback
            traceback.print_exc()
            return False
    
    def _copy_file(self, relative_path: str):
        """Copia arquivo da pasta principal para Copy."""
        source = self.base_dir / relative_path
        dest = self.copy_dir / relative_path
        
        if not source.exists():
            raise FileNotFoundError(f"Arquivo fonte não encontrado: {source}")
        
        # Criar diretório de destino se não existir
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar
        shutil.copy2(source, dest)
    
    def _clean_old_scripts(self):
        """Remove scripts de refatoração da pasta Copy."""
        patterns = [
            "REFACTOR_*.py",
            "FIX_*.py",
            "SYNC_*.py"
        ]
        
        for pattern in patterns:
            for script in self.copy_dir.glob(pattern):
                try:
                    script.unlink()
                    print(f"      Removido: {script.name}")
                except:
                    pass
    
    def _report(self):
        print("="*70)
        print("\n✅ SINCRONIZAÇÃO CONCLUÍDA!\n")
        print("="*70)
        
        print("\n📋 ARQUIVOS SINCRONIZADOS:\n")
        print("   1. ✅ ui/main_window.py (596 linhas, FASE-1C)")
        print("   2. ✅ ui/recursive_import_integration.py (com try/except)")
        
        print("\n🎯 PRÓXIMOS PASSOS:\n")
        print(f"   1. Rodar app na pasta Copy:")
        print(f"      cd \"{self.copy_dir}\"")
        print(f"      python main.py")
        print("   2. OU melhor ainda, rodar na pasta principal SEM Copy!")
        
        print("\n⚠️  RECOMENDAÇÃO: Delete a pasta Copy e trabalhe só na principal!\n")
        
        print("="*70 + "\n")
        
        # Auto-delete
        try:
            Path(__file__).unlink()
            print("   🗑️  Script auto-deletado\n")
        except:
            pass


def main():
    print("\n🚀 Iniciando sincronização...\n")
    
    syncer = FolderSyncer()
    
    try:
        success = syncer.run()
        
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
