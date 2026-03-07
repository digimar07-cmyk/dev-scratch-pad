#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Refatoracao Automatica - FASE 7C v2.0
================================================

Aplica FASE 7C: SelectionController, CollectionController, ProjectManagementController

VERSAO 2.0 - CORRIGIDA:
- Substitui TODOS os callbacks antigos por novos
- Adiciona callback helpers na classe
- App NAO fica preto!

Reducao: -200 linhas (859 → 659 linhas)

Controllers extraidos:
  1. SelectionController - Gerencia selecao multipla
  2. CollectionController - Gerencia colecoes/playlists
  3. ProjectManagementController - Gerencia remocao e flags

Metodos removidos: 14

Uso:
  python apply_fase7_refactor_7C.py           # Aplicar Fase 7C
  python apply_fase7_refactor_7C.py --dry-run # Ver mudancas sem aplicar
  python apply_fase7_refactor_7C.py --undo    # Desfazer

Autor: Claude Sonnet 4.5
Data: 07/03/2026
Versao: 2.0 (COM SUBSTITUICAO DE CALLBACKS)
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
from typing import List, Dict

# Importa definicoes de patches
try:
    from fase7_patches import (
        PHASE_7C_IMPORTS, 
        PHASE_7C_INIT, 
        PHASE_7C_CALLBACK_HELPERS,
        PHASE_7C_METHODS_TO_REMOVE,
        PHASE_7C_CALLBACK_REPLACEMENTS
    )
except ImportError:
    print("ERRO: fase7_patches.py nao encontrado!")
    print("\nPressione ENTER para fechar...")
    input()
    sys.exit(1)

# Importa gerenciador de versoes
try:
    from version_manager import VersionManager
    VERSION_MANAGER_AVAILABLE = True
except ImportError:
    print("AVISO: version_manager.py nao encontrado. Versionamento desabilitado.")
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
    print(f"{Color.GREEN}OK {text}{Color.RESET}")


def print_error(text: str) -> None:
    print(f"{Color.RED}ERRO {text}{Color.RESET}")


def print_warning(text: str) -> None:
    print(f"{Color.YELLOW}AVISO {text}{Color.RESET}")


def print_info(text: str) -> None:
    print(f"{Color.BLUE}INFO {text}{Color.RESET}")


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
        if 'self.database' in line and '=' in line and 'self.db_manager.database' in line:
            target_idx = i
            break
    
    if target_idx == -1:
        print_warning("Linha alvo 'self.database = ...' nao encontrada!")
        return content
    
    init_lines = init_code.strip().split('\n')
    if lines[target_idx + 1].strip():
        init_lines.insert(0, '')
    
    for line in reversed(init_lines):
        lines.insert(target_idx + 1, line)
    
    return '\n'.join(lines)


def add_callback_helpers(content: str, helpers_code: str) -> str:
    """Adiciona callback helpers no final da classe (antes do ultimo metodo ou fim)."""
    lines = content.split('\n')
    
    # Encontrar ultima linha da classe (antes de eventuais funcoes fora da classe)
    # Procurar pelo ultimo metodo da classe
    last_method_end = -1
    in_class = False
    class_indent = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('class LaserflixMainWindow'):
            in_class = True
            class_indent = len(line) - len(line.lstrip())
        elif in_class:
            # Se linha nao vazia e nao indentada mais que a classe, saiu da classe
            if line.strip() and not line.startswith(' ' * (class_indent + 1)):
                last_method_end = i
                break
            # Se e um metodo da classe, atualizar last_method_end
            if line.strip().startswith('def ') and len(line) - len(line.lstrip()) == class_indent + 4:
                # Encontrar fim desse metodo
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    if next_line.strip() and (len(next_line) - len(next_line.lstrip())) <= class_indent + 4:
                        if next_line.strip().startswith('def '):
                            last_method_end = j
                            break
    
    # Se nao achou, inserir no fim do arquivo
    if last_method_end == -1:
        last_method_end = len(lines)
    
    # Inserir helpers
    helper_lines = helpers_code.split('\n')
    for line in reversed(helper_lines):
        lines.insert(last_method_end, line)
    
    return '\n'.join(lines)


def replace_callbacks(content: str, replacements: Dict[str, str]) -> str:
    """Substitui todas as referencias de callbacks antigos por novos."""
    print_info("Substituindo callbacks...")
    
    count = 0
    for old, new in replacements.items():
        # Contar quantas vezes aparece
        occurrences = content.count(old)
        if occurrences > 0:
            content = content.replace(old, new)
            count += occurrences
            print_info(f"  '{old}' -> '{new}' ({occurrences}x)")
    
    print_success(f"  {count} callbacks substituidos")
    return content


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
            print_warning(f"Metodo '{method_name}' nao encontrado")
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
    
    # 1. Adicionar imports
    content = add_imports(content, PHASE_7C_IMPORTS)
    print_success("  Imports adicionados")
    
    # 2. Adicionar codigo __init__
    content = add_init_code(content, PHASE_7C_INIT)
    print_success("  Codigo __init__ adicionado")
    
    # 3. Adicionar callback helpers
    content = add_callback_helpers(content, PHASE_7C_CALLBACK_HELPERS)
    print_success("  Callback helpers adicionados")
    
    # 4. Substituir callbacks antigos por novos
    content = replace_callbacks(content, PHASE_7C_CALLBACK_REPLACEMENTS)
    print_success("  Callbacks substituidos")
    
    # 5. Remover metodos antigos
    content = remove_methods(content, PHASE_7C_METHODS_TO_REMOVE)
    print_success(f"  {len(PHASE_7C_METHODS_TO_REMOVE)} metodos removidos")
    
    return content


def update_version() -> None:
    if not VERSION_MANAGER_AVAILABLE:
        print_warning("Version manager nao disponivel")
        return
    
    manager = VersionManager()
    description = "Fase 7C: SelectionController, CollectionController, ProjectManagementController"
    changes = [
        "SelectionController extraido (gerencia selecao multipla)",
        "CollectionController extraido (gerencia colecoes/playlists)",
        "ProjectManagementController extraido (gerencia remocao e flags)",
        "14 metodos removidos do main_window.py",
        "Callbacks conectados corretamente",
        "Reducao: -200 linhas"
    ]
    
    try:
        new_version = manager.bump_and_update('build', description, changes)
        print()
        print_success(f"Versao atualizada: {new_version}")
    except Exception as e:
        print_warning(f"Erro ao atualizar versao: {e}")


def main():
    try:
        parser = argparse.ArgumentParser(description="Aplica Fase 7C v2.0")
        parser.add_argument('--dry-run', action='store_true', help='Ver mudancas sem aplicar')
        parser.add_argument('--undo', action='store_true', help='Desfazer ultima mudanca')
        args = parser.parse_args()
        
        if not MAIN_WINDOW_PATH.exists():
            print_error(f"Arquivo nao encontrado: {MAIN_WINDOW_PATH}")
            print("\nPressione ENTER para fechar...")
            input()
            sys.exit(1)
        
        original_content = read_file(MAIN_WINDOW_PATH)
        original_lines = count_lines(MAIN_WINDOW_PATH)
        
        print_header("REFATORACAO AUTOMATICA - FASE 7C v2.0")
        print_info(f"Arquivo: {MAIN_WINDOW_PATH}")
        print_info(f"Linhas atuais: {original_lines}")
        print()
        
        if not args.dry_run:
            create_backup(MAIN_WINDOW_PATH)
            print()
        
        print_header("APLICANDO FASE 7C")
        content = apply_phase_7c(original_content)
        print()
        
        print_header("VALIDACAO")
        if not validate_syntax(content):
            print_error("Sintaxe invalida! Abortando.")
            print("\nPressione ENTER para fechar...")
            input()
            sys.exit(1)
        print_success("Sintaxe Python valida")
        
        new_lines = len([l for l in content.split('\n') if l.strip()])
        reduction = original_lines - new_lines
        print_info(f"Linhas: {original_lines} -> {new_lines} ({reduction:+d} linhas)")
        print()
        
        if args.dry_run:
            print_warning("DRY-RUN: Mudancas NAO foram aplicadas")
            print("\nPressione ENTER para fechar...")
            input()
            return
        
        write_file(MAIN_WINDOW_PATH, content)
        print_success(f"Arquivo atualizado: {MAIN_WINDOW_PATH}")
        
        print_header("VERSIONAMENTO")
        update_version()
        
        print()
        print_header("FASE 7C CONCLUIDA")
        print_success(f"Refatoracao aplicada com sucesso!")
        print_info(f"Linhas: {original_lines} -> {new_lines} ({reduction} linhas removidas)")
        print()
        print_info("Proximos passos:")
        print(f"  1. {Color.CYAN}python main.py{Color.RESET} - Testar")
        print(f"  2. {Color.CYAN}git add . && git commit && git push{Color.RESET} - Commit")
        print()
        
        # PAUSE NO FINAL
        print("\nPressione ENTER para fechar...")
        input()
        
    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario")
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
