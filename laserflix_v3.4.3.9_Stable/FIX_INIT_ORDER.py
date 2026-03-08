#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 FIX RÁPIDO - Corrige ordem de inicialização

Problema: modal_mgr criado ANTES de display_ctrl existir
Solução: Mover criação dos managers para DEPOIS de _setup_controllers()

Criado: 08/03/2026 10:00 BRT
Modelo: Claude Sonnet 4.5
"""

import shutil
from datetime import datetime
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("🔧 FIX RÁPIDO - Ordem de Inicialização")
    print("="*70 + "\n")
    
    base_dir = Path(__file__).parent
    main_window = base_dir / "ui" / "main_window.py"
    
    if not main_window.exists():
        print(f"❌ Arquivo não encontrado: {main_window}")
        input("Pressione ENTER...")
        return
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = main_window.with_suffix(f".py.backup_fix_{timestamp}")
    shutil.copy2(main_window, backup)
    print(f"💾 Backup: {backup.name}\n")
    
    content = main_window.read_text(encoding='utf-8')
    
    # CORREÇÃO: Encontrar bloco problemático
    # Ele está criando modal_mgr COM display_ctrl antes de _setup_controllers
    
    old_block = '''        self.toggle_mgr = ToggleManager(self.database, self.db_manager)
        
        self.modal_mgr = ModalManager(
            self.root, self.database, self.db_manager, self.collections_manager,
            self.display_ctrl, self.thumbnail_preloader, self.scanner, 
            self.text_generator, self.logger
        )
        
        self.collection_dialog_mgr = CollectionDialogManager(
            self.root, self.collections_manager, self.database, None
        )
        
        self._setup_controllers()
        self._setup_callbacks()'''
    
    new_block = '''        # Primeiro: setup controllers (display_ctrl, etc)
        self._setup_controllers()
        self._setup_callbacks()
        
        # Depois: managers que dependem dos controllers
        self.toggle_mgr = ToggleManager(self.database, self.db_manager)
        
        self.modal_mgr = ModalManager(
            self.root, self.database, self.db_manager, self.collections_manager,
            self.display_ctrl, self.thumbnail_preloader, self.scanner, 
            self.text_generator, self.logger
        )
        
        self.collection_dialog_mgr = CollectionDialogManager(
            self.root, self.collections_manager, self.database, None
        )'''
    
    if old_block not in content:
        print("⚠️  Não encontrou bloco problemático (talvez já corrigido?)\n")
        print("Tentando outra estratégia...\n")
        
        # Estratégia alternativa: procurar se existe a criação incorreta
        if "self.modal_mgr = ModalManager(" in content:
            # Verificar se está ANTES de _setup_controllers
            modal_pos = content.find("self.modal_mgr = ModalManager(")
            setup_pos = content.find("self._setup_controllers()")
            
            if modal_pos < setup_pos and modal_pos != -1 and setup_pos != -1:
                print("❌ PROBLEMA DETECTADO: modal_mgr criado antes de _setup_controllers()\n")
                print("🔧 Aplicando correção manual...\n")
                
                # Extrair linha problemática
                lines = content.splitlines(keepends=True)
                new_lines = []
                skip_until = None
                moved_lines = []
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # Se encontrar modal_mgr ANTES de _setup_controllers
                    if "self.modal_mgr = ModalManager(" in line and setup_pos > modal_pos:
                        # Capturar linhas do ModalManager (multilinhas)
                        moved_lines.append(line)
                        i += 1
                        while i < len(lines) and ")" not in lines[i-1]:
                            moved_lines.append(lines[i])
                            i += 1
                        continue
                    
                    # Se encontrar toggle_mgr ANTES
                    if "self.toggle_mgr = ToggleManager(" in line and "self._setup_controllers()" not in content[:content.find(line)]:
                        moved_lines.append(line)
                        i += 1
                        continue
                    
                    # Se encontrar collection_dialog_mgr ANTES
                    if "self.collection_dialog_mgr = CollectionDialogManager(" in line:
                        # Capturar multilinhas
                        moved_lines.append(line)
                        i += 1
                        while i < len(lines) and ")" not in lines[i-1]:
                            moved_lines.append(lines[i])
                            i += 1
                        continue
                    
                    # Se encontrar _setup_callbacks, inserir managers movidos ANTES
                    if "self._setup_callbacks()" in line:
                        new_lines.append(line)
                        new_lines.append("\n")
                        new_lines.append("        # Managers que dependem de controllers\n")
                        new_lines.extend(moved_lines)
                        i += 1
                        continue
                    
                    new_lines.append(line)
                    i += 1
                
                content = "".join(new_lines)
            else:
                print("✅ Ordem já está correta!\n")
                input("Pressione ENTER...")
                return
        else:
            print("✅ modal_mgr não encontrado (arquivo diferente?)\n")
            input("Pressione ENTER...")
            return
    else:
        content = content.replace(old_block, new_block)
        print("✅ Bloco corrigido!\n")
    
    # Validar
    try:
        compile(content, str(main_window), 'exec')
        print("✅ Sintaxe válida\n")
    except SyntaxError as e:
        print(f"\n❌ Erro: {e}")
        print("🔄 Restaurando backup...\n")
        shutil.copy2(backup, main_window)
        input("Pressione ENTER...")
        return
    
    # Salvar
    main_window.write_text(content, encoding='utf-8')
    print("💾 Arquivo salvo!\n")
    
    print("="*70)
    print("✅ CORREÇÃO APLICADA!")
    print("="*70 + "\n")
    
    print("🚀 ORDEM CORRETA:\n")
    print("  1. Core dependencies (db, scanner, ollama...)")
    print("  2. _setup_controllers() ← Cria display_ctrl, etc")
    print("  3. _setup_callbacks()")
    print("  4. Managers (toggle_mgr, modal_mgr, ...) ← DEPOIS")
    print("  5. _build_ui()")
    print("  6. Conectar bridges\n")
    
    print("✅ Agora teste: python main.py\n")
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
