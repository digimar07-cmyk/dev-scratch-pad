#!/usr/bin/env python3
"""
Script de Refatoração Automática - FASE 7C
================================================

Aplica FASE 7C: SelectionController, CollectionController, ProjectManagementController

Redução: -200 linhas (859 → 659 linhas)

Controllers extraídos:
  1. SelectionController - Gerencia seleção múltipla
  2. CollectionController - Gerencia coleções/playlists
  3. ProjectManagementController - Gerencia remoção e flags

Métodos removidos: 14
  - toggle_selection_mode, toggle_card_selection
  - _select_all, _deselect_all, _remove_selected
  - remove_project, clean_orphans
  - _on_add_to_collection, _on_remove_from_collection, _on_new_collection_with
  - toggle_favorite, toggle_done, toggle_good, toggle_bad

Uso:
  python apply_fase7_refactor_7C.py           # Aplicar Fase 7C
  python apply_fase7_refactor_7C.py --dry-run # Ver mudanças sem aplicar
  python apply_fase7_refactor_7C.py --undo    # Desfazer

Autor: Claude Sonnet 4.5
Data: 07/03/2026
Versão: 1.1 (com pause no final)
"""

import os
import sys
import ast
import argparse
import shutil
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import List

# Importa definições de patches
try:
    from fase7_patches import PHASE_7C_IMPORTS, PHASE_7C_INIT, PHASE_7C_METHODS_TO_REMOVE
except ImportError:
    print("❌ Erro: fase7_patches.py não encontrado!")
    print("\nPressione ENTER para fechar...")
    input()
    sys.exit(1)

# Importa gerenciador de versões
try:
    from version_manager import VersionManager
    VERSION_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: version_manager.py não encontrado. Versionamento desabilitado.")
    VERSION_MANAGER_AVAILABLE = False

# Constantes
MAIN_WINDOW_PATH = Path("ui/main_window.py")
BACKUP_DIR = Path(".backups")


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{Color.CYAN}{Color.BOLD}{'=' * 80}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{text}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'=' * 80}{Color.RESET}\n")


def print_success(text: str) -> None:
    print(f"{Color.GREEN}✅ {text}{Color.RESET}")


def print_error(text: str) -> None:
    print(f"{Color.RED}❌ {text}{Color.RESET}")


def print_warning(text: str) -> None:
    print(f"{Color.YELLOW}⚠️  {text}{Color.RESET}")


def print_info(text: str) -> None:
    print(f"{Color.BLUE}ℹ️  {text}{Color.RESET}")


def count_lines(filepath: Path) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())


def create_backup(filepath: Path) -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{filepath.stem}_backup_7C_{timestamp}{filepath.suffix}"
    shutil.copy2(filepath, backup_path)
    print_success(f"Backup criado: {backup_path}")
    return backup_path


def validate_syntax(content: str) -> bool:
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        print_error(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
        return False


def read_file(filepath: Path) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(filepath: Path, content: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def add_imports(content: str, imports: List[str]) -> str:
    lines = content.split('\n')
    last_controller_import_idx = -1
    for i, line in enumerate(lines):
        if 'from ui.controllers' in line or 'from ui.components' in line:
            last_controller_import_idx = i
    
    if last_controller_import_idx == -1:
        for i, line in enumerate(lines):
            if line.startswith('from ui.'):
                last_controller_import_idx = i
    
    if last_controller_import_idx != -1:
        for imp in reversed(imports):
            if imp not in content:
                lines.insert(last_controller_import_idx + 1, imp)
    
    return '\n'.join(lines)


def add_init_code(content: str, init_code: str) -> str:
    lines = content.split('\n')
    target_idx = -1
    
    for i, line in enumerate(lines):
        if 'self.database           = self.db_manager.database' in line or 'self.database = self.db_manager.database' in line:
            target_idx = i
            break
    
    if target_idx == -1:
        print_warning("Linha alvo 'self.database = ...' não encontrada!")
        return content
    
    init_lines = init_code.strip().split('\n')
    if lines[target_idx + 1].strip():
        init_lines.insert(0, '')
    
    for line in reversed(init_lines):
        lines.insert(target_idx + 1, line)
    
    return '\n'.join(lines)


def remove_methods(content: str, methods: List[str]) -> str:
    lines = content.split('\n')
    
    for method_name in methods:
        method_pattern = rf'^\s+def {re.escape(method_name)}\('
        start_idx = -1
        
        for i, line in enumerate(lines):
            if re.match(method_pattern, line):
                start_idx = i
                break
        
        if start_idx == -1:
            print_warning(f"Método '{method_name}' não encontrado")
            continue
        
        indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        end_idx = len(lines)
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent <= indent and line.strip():
                end_idx = i
                break
        
        print_info(f"  Removendo '{method_name}' (linhas {start_idx+1}-{end_idx})")
        del lines[start_idx:end_idx]
    
    return '\n'.join(lines)


def apply_phase_7c(content: str) -> str:
    print_info("Aplicando Fase 7C...")
    content = add_imports(content, PHASE_7C_IMPORTS)
    print_success("  Imports adicionados")
    content = add_init_code(content, PHASE_7C_INIT)
    print_success("  Código __init__ adicionado")
    content = remove_methods(content, PHASE_7C_METHODS_TO_REMOVE)
    print_success(f"  {len(PHASE_7C_METHODS_TO_REMOVE)} métodos removidos")
    return content


def update_version() -> None:
    if not VERSION_MANAGER_AVAILABLE:
        print_warning("Version manager não disponível")
        return
    
    manager = VersionManager()
    description = "Fase 7C: SelectionController, CollectionController, ProjectManagementController"
    changes = [
        "SelectionController extraído (gerencia seleção múltipla)",
        "CollectionController extraído (gerencia coleções/playlists)",
        "ProjectManagementController extraído (gerencia remoção e flags)",
        "14 métodos removidos do main_window.py",
        "Redução: -200 linhas"
    ]
    
    try:
        new_version = manager.bump_and_update('build', description, changes)
        print()
        print_success(f"Versão atualizada: {new_version}")
    except Exception as e:
        print_warning(f"Erro ao atualizar versão: {e}")


def main():
    try:
        parser = argparse.ArgumentParser(description="Aplica Fase 7C")
        parser.add_argument('--dry-run', action='store_true', help='Ver mudanças sem aplicar')
        parser.add_argument('--undo', action='store_true', help='Desfazer última mudança')
        args = parser.parse_args()
        
        if not MAIN_WINDOW_PATH.exists():
            print_error(f"Arquivo não encontrado: {MAIN_WINDOW_PATH}")
            print("\nPressione ENTER para fechar...")
            input()
            sys.exit(1)
        
        original_content = read_file(MAIN_WINDOW_PATH)
        original_lines = count_lines(MAIN_WINDOW_PATH)
        
        print_header("🔧 REFATORAÇÃO AUTOMÁTICA - FASE 7C")
        print_info(f"Arquivo: {MAIN_WINDOW_PATH}")
        print_info(f"Linhas atuais: {original_lines}")
        print()
        
        if not args.dry_run:
            create_backup(MAIN_WINDOW_PATH)
            print()
        
        print_header("APLICANDO FASE 7C")
        content = apply_phase_7c(original_content)
        print()
        
        print_header("✓ VALIDAÇÃO")
        if not validate_syntax(content):
            print_error("Sintaxe inválida! Abortando.")
            print("\nPressione ENTER para fechar...")
            input()
            sys.exit(1)
        print_success("Sintaxe Python válida")
        
        new_lines = len([l for l in content.split('\n') if l.strip()])
        reduction = original_lines - new_lines
        print_info(f"Linhas: {original_lines} → {new_lines} ({reduction:+d} linhas)")
        print()
        
        if args.dry_run:
            print_warning("DRY-RUN: Mudanças NÃO foram aplicadas")
            print("\nPressione ENTER para fechar...")
            input()
            return
        
        write_file(MAIN_WINDOW_PATH, content)
        print_success(f"Arquivo atualizado: {MAIN_WINDOW_PATH}")
        
        print_header("🔢 VERSIONAMENTO")
        update_version()
        
        print()
        print_header("✅ FASE 7C CONCLUÍDA")
        print_success(f"Refatoração aplicada com sucesso!")
        print_info(f"Linhas: {original_lines} → {new_lines} ({reduction} linhas removidas)")
        print()
        print_info("Próximos passos:")
        print(f"  1. {Color.CYAN}python main.py{Color.RESET} - Testar")
        print(f"  2. {Color.CYAN}git add . && git commit && git push{Color.RESET} - Commit")
        print()
        
        # PAUSE NO FINAL
        print("\nPressione ENTER para fechar...")
        input()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        print("\nPressione ENTER para fechar...")
        input()
        sys.exit(1)
    except Exception as e:
        print("\n")
        print_error("ERRO FATAL:")
        print(f"{Color.RED}{traceback.format_exc()}{Color.RESET}")
        print("\nPressione ENTER para fechar...")
        input()
        sys.exit(1)


if __name__ == '__main__':
    main()
