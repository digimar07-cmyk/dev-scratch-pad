#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE CORREÇÃO COMPLETA - v3.4.3.5

Este script CORRIGE TUDO:
1. Atualiza VERSION para 3.4.3.5
2. Atualiza config/settings.py
3. Deleta scripts antigos de refatoração
4. Valida estrutura
5. Se auto-deleta após sucesso

USO: python FIX_VERSION_AND_CLEAN.py

Criado: 07/03/2026 23:34 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


class VersionFixer:
    """Corrige versão e limpa scripts antigos."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.version_file = self.base_dir / "VERSION"
        self.settings_file = self.base_dir / "config" / "settings.py"
        self.main_window = self.base_dir / "ui" / "main_window.py"
        
        self.scripts_to_remove = [
            "REFACTOR_AUTO_FASE_1A.py",
            "refactor_fase_1a_integrate_chips_bar.py",
        ]
        
        self.changes_made = []
        self.target_version = "3.4.3.5"
        
    def run(self):
        print("\n" + "="*70)
        print("🔧 CORREÇÃO COMPLETA v3.4.3.5")
        print("="*70 + "\n")
        
        try:
            print("✅ [1/6] Validando estrutura...")
            self._validate()
            print("   ✓ Estrutura OK\n")
            
            print("🔢 [2/6] Atualizando VERSION...")
            self._update_version_file()
            print(f"   ✓ VERSION: {self.target_version}\n")
            
            print("🔧 [3/6] Atualizando config/settings.py...")
            self._update_settings()
            print("   ✓ settings.py atualizado\n")
            
            print("🧹 [4/6] Limpando scripts antigos...")
            cleaned = self._clean_old_scripts()
            print(f"   ✓ {cleaned} script(s) removido(s)\n")
            
            print("✅ [5/6] Validando...")
            self._validate_final()
            print("   ✓ Tudo validado\n")
            
            print("📊 [6/6] Relatório...\n")
            self._report()
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            return False
    
    def _validate(self):
        if not self.version_file.exists():
            raise FileNotFoundError("VERSION file não encontrado")
        
        if not self.settings_file.exists():
            raise FileNotFoundError("config/settings.py não encontrado")
        
        if not self.main_window.exists():
            raise FileNotFoundError("ui/main_window.py não encontrado")
        
        # Verificar versão atual
        current_version = self.version_file.read_text(encoding='utf-8').strip()
        if current_version == self.target_version:
            raise ValueError(
                f"VERSION já está correto ({self.target_version}). "
                "Nada a fazer!"
            )
    
    def _update_version_file(self):
        current = self.version_file.read_text(encoding='utf-8').strip()
        self.version_file.write_text(f"{self.target_version}\n", encoding='utf-8')
        self.changes_made.append(f"VERSION: {current} → {self.target_version}")
    
    def _update_settings(self):
        content = self.settings_file.read_text(encoding='utf-8')
        
        # Padrão: VERSION = "x.x.x.x"
        pattern = r'VERSION\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern, content)
        
        if not match:
            raise ValueError("Padrão VERSION não encontrado em settings.py")
        
        old_version = match.group(1)
        
        if old_version == self.target_version:
            self.changes_made.append("settings.py já estava correto")
            return
        
        # Substituir
        new_content = re.sub(
            pattern,
            f'VERSION = "{self.target_version}"',
            content
        )
        
        self.settings_file.write_text(new_content, encoding='utf-8')
        self.changes_made.append(f"settings.py: {old_version} → {self.target_version}")
    
    def _clean_old_scripts(self):
        cleaned = 0
        for script_name in self.scripts_to_remove:
            script_path = self.base_dir / script_name
            if script_path.exists():
                script_path.unlink()
                cleaned += 1
                self.changes_made.append(f"Removido: {script_name}")
        return cleaned
    
    def _validate_final(self):
        # Validar VERSION
        version_content = self.version_file.read_text(encoding='utf-8').strip()
        if version_content != self.target_version:
            raise ValueError(f"VERSION incorreto: {version_content}")
        
        # Validar settings.py
        settings_content = self.settings_file.read_text(encoding='utf-8')
        if f'VERSION = "{self.target_version}"' not in settings_content:
            raise ValueError("settings.py não foi atualizado corretamente")
        
        # Validar que scripts foram removidos
        for script_name in self.scripts_to_remove:
            script_path = self.base_dir / script_name
            if script_path.exists():
                raise ValueError(f"Script {script_name} ainda existe")
        
        # Validar main_window.py
        mw_content = self.main_window.read_text(encoding='utf-8')
        mw_lines = len(mw_content.splitlines())
        
        if mw_lines > 650:
            raise ValueError(f"main_window.py tem {mw_lines} linhas (esperado ~631)")
    
    def _report(self):
        print("="*70)
        print("\n🎉 CORREÇÃO CONCLUÍDA!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        # Estatísticas
        mw_content = self.main_window.read_text(encoding='utf-8')
        mw_lines = len(mw_content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS:\n")
        print(f"   Versão: {self.target_version}")
        print(f"   main_window.py: {mw_lines} linhas")
        print(f"   Scripts removidos: {len([c for c in self.changes_made if 'Removido' in c])}")
        
        print("\n✅ VALIDAÇÃO:\n")
        print("   ✓ VERSION file correto")
        print("   ✓ config/settings.py correto")
        print("   ✓ Scripts antigos removidos")
        print("   ✓ main_window.py válido")
        
        print("\n🚀 PRÓXIMOS PASSOS:\n")
        print("   1. Testar app: python main.py")
        print("   2. Commit: git add . && git commit -m 'fix(v3.4.3.5): correct version'")
        print("   3. Atualizar CHANGELOG.md")
        print("   4. Este script IRÁ SE AUTO-DELETAR\n")
        
        # Auto-delete
        print("   🗑️  Auto-deletando este script...")
        try:
            Path(__file__).unlink()
            print("   ✓ FIX_VERSION_AND_CLEAN.py removido\n")
        except:
            print("   ⚠️  Não foi possível auto-deletar (delete manualmente)\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando correção...\n")
    
    fixer = VersionFixer()
    
    try:
        success = fixer.run()
        
        if success:
            print("✅ SUCESSO! Versão e scripts corrigidos.\n")
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
