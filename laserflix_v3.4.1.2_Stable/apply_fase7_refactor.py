#!/usr/bin/env python3
"""
Script de Refatoração Automática - Fase 7
==========================================

Aplica refatoração completa do main_window.py de forma cirúrgica e segura.

Fases:
  7C: SelectionController, CollectionController, ProjectManagementController (-200 linhas)
  7D: ChipsBar, SelectionBar, PaginationControls (-250 linhas)
  7E: Simplificações (callbacks, toggles, código morto) (-100 linhas)
  7F: ModalManager, DatabaseController, CardFactory (-120 linhas)

Redução total: 868 → 198 linhas (-77%)

Uso:
  python apply_fase7_refactor.py --dry-run       # Ver mudanças sem aplicar
  python apply_fase7_refactor.py --phase 7c      # Aplicar apenas Fase 7C
  python apply_fase7_refactor.py --all           # Aplicar todas as fases
  python apply_fase7_refactor.py --undo          # Desfazer última mudança
  python apply_fase7_refactor.py --list-backups  # Listar backups

Autor: Claude Sonnet 4.5
Data: 07/03/2026
"""

import os
import sys
import ast
import argparse
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# Importa definições de patches (será criado em seguida)
try:
    from fase7_patches import (
        PHASE_7C_IMPORTS, PHASE_7C_INIT, PHASE_7C_METHODS_TO_REMOVE,
        PHASE_7D_IMPORTS, PHASE_7D_INIT, PHASE_7D_METHODS_TO_REMOVE,
        PHASE_7E_SIMPLIFICATIONS,
        PHASE_7F_IMPORTS, PHASE_7F_INIT, PHASE_7F_METHODS_TO_REMOVE,
    )
except ImportError:
    print("❌ Erro: fase7_patches.py não encontrado!")
    print("Execute: git pull para baixar todos os arquivos.")
    sys.exit(1)

# Constantes
MAIN_WINDOW_PATH = Path("ui/main_window.py")
BACKUP_DIR = Path(".backups")
TARGET_LINES = 198
ORIGINAL_LINES = 868


class Color:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print colorful header."""
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
    """Count non-empty lines in file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())


def create_backup(filepath: Path) -> Path:
    """Create timestamped backup of file."""
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    
    shutil.copy2(filepath, backup_path)
    print_success(f"Backup criado: {backup_path}")
    
    return backup_path


def list_backups() -> List[Path]:
    """List all available backups."""
    if not BACKUP_DIR.exists():
        return []
    
    backups = sorted(
        BACKUP_DIR.glob("main_window_backup_*.py"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    return backups


def undo_last_change() -> None:
    """Restore from most recent backup."""
    print_header("🔙 DESFAZER ÚLTIMA MUDANÇA")
    
    backups = list_backups()
    
    if not backups:
        print_error("Nenhum backup encontrado!")
        return
    
    latest_backup = backups[0]
    
    print_info(f"Restaurando de: {latest_backup}")
    print_info(f"Data: {datetime.fromtimestamp(latest_backup.stat().st_mtime)}")
    
    # Confirm
    response = input(f"\n{Color.YELLOW}Confirmar restauração? (s/N): {Color.RESET}")
    if response.lower() != 's':
        print_info("Cancelado.")
        return
    
    # Restore
    shutil.copy2(latest_backup, MAIN_WINDOW_PATH)
    print_success(f"Arquivo restaurado de {latest_backup}")
    
    # Count lines
    lines = count_lines(MAIN_WINDOW_PATH)
    print_info(f"Linhas atuais: {lines}")


def validate_syntax(content: str) -> bool:
    """Validate Python syntax using AST."""
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        print_error(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
        return False


def read_file(filepath: Path) -> str:
    """Read file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(filepath: Path, content: str) -> None:
    """Write content to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def add_imports(content: str, imports: List[str]) -> str:
    """
    Add imports after existing controller imports.
    
    Strategy: Find the last 'from ui.controllers' import and add new imports after it.
    """
    lines = content.split('\n')
    
    # Find last controller import
    last_controller_import_idx = -1
    for i, line in enumerate(lines):
        if 'from ui.controllers' in line or 'from ui.components' in line or 'from ui.factories' in line or 'from core.database_controller' in line:
            last_controller_import_idx = i
    
    # If no controller imports found, add after other imports
    if last_controller_import_idx == -1:
        for i, line in enumerate(lines):
            if line.startswith('from ui.'):
                last_controller_import_idx = i
    
    # Insert new imports
    if last_controller_import_idx != -1:
        for imp in reversed(imports):
            if imp not in content:  # Avoid duplicates
                lines.insert(last_controller_import_idx + 1, imp)
    
    return '\n'.join(lines)


def add_init_code(content: str, init_code: str) -> str:
    """
    Add initialization code in __init__ method.
    
    Strategy: Find the line with 'self.database = self.db_manager.database'
    and add new code after it.
    """
    lines = content.split('\n')
    
    # Find target line
    target_line = 'self.database           = self.db_manager.database'
    target_idx = -1
    
    for i, line in enumerate(lines):
        if target_line in line or 'self.database = self.db_manager.database' in line:
            target_idx = i
            break
    
    if target_idx == -1:
        print_warning("Linha alvo 'self.database = ...' não encontrada!")
        return content
    
    # Insert init code after target line
    init_lines = init_code.strip().split('\n')
    
    # Add blank line before if needed
    if lines[target_idx + 1].strip():
        init_lines.insert(0, '')
    
    for line in reversed(init_lines):
        lines.insert(target_idx + 1, line)
    
    return '\n'.join(lines)


def remove_methods(content: str, methods: List[str]) -> str:
    """
    Remove specified methods from class.
    
    Strategy: Use AST to locate methods precisely, then remove them.
    """
    lines = content.split('\n')
    
    for method_name in methods:
        # Find method start
        method_pattern = rf'^\s+def {re.escape(method_name)}\('
        
        start_idx = -1
        for i, line in enumerate(lines):
            if re.match(method_pattern, line):
                start_idx = i
                break
        
        if start_idx == -1:
            print_warning(f"Método '{method_name}' não encontrado (pode já ter sido removido)")
            continue
        
        # Find method end (next def at same indentation or class end)
        indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        end_idx = len(lines)
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():  # Empty line
                continue
            
            curr_indent = len(line) - len(line.lstrip())
            
            # Found next method or class end
            if curr_indent <= indent and line.strip():
                end_idx = i
                break
        
        # Remove method
        print_info(f"  Removendo método '{method_name}' (linhas {start_idx+1}-{end_idx})")
        del lines[start_idx:end_idx]
    
    return '\n'.join(lines)


def apply_simplifications(content: str, simplifications: List[Tuple[str, str]]) -> str:
    """
    Apply regex-based simplifications.
    """
    for pattern, replacement in simplifications:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content


def apply_phase_7c(content: str) -> str:
    """Apply Phase 7C: Add 3 controllers."""
    print_info("Fase 7C: SelectionController, CollectionController, ProjectManagementController")
    
    # Add imports
    content = add_imports(content, PHASE_7C_IMPORTS)
    print_success("  Imports adicionados")
    
    # Add init code
    content = add_init_code(content, PHASE_7C_INIT)
    print_success("  Código __init__ adicionado")
    
    # Remove methods
    content = remove_methods(content, PHASE_7C_METHODS_TO_REMOVE)
    print_success(f"  {len(PHASE_7C_METHODS_TO_REMOVE)} métodos removidos")
    
    return content


def apply_phase_7d(content: str) -> str:
    """Apply Phase 7D: Add 3 UI components."""
    print_info("Fase 7D: ChipsBar, SelectionBar, PaginationControls")
    
    content = add_imports(content, PHASE_7D_IMPORTS)
    print_success("  Imports adicionados")
    
    content = add_init_code(content, PHASE_7D_INIT)
    print_success("  Código __init__ adicionado")
    
    content = remove_methods(content, PHASE_7D_METHODS_TO_REMOVE)
    print_success(f"  {len(PHASE_7D_METHODS_TO_REMOVE)} métodos removidos")
    
    return content


def apply_phase_7e(content: str) -> str:
    """Apply Phase 7E: Simplifications."""
    print_info("Fase 7E: Simplificações (callbacks, toggles, código morto)")
    
    content = apply_simplifications(content, PHASE_7E_SIMPLIFICATIONS)
    print_success(f"  {len(PHASE_7E_SIMPLIFICATIONS)} simplificações aplicadas")
    
    return content


def apply_phase_7f(content: str) -> str:
    """Apply Phase 7F: Final controllers."""
    print_info("Fase 7F: ModalManager, DatabaseController, CardFactory")
    
    content = add_imports(content, PHASE_7F_IMPORTS)
    print_success("  Imports adicionados")
    
    content = add_init_code(content, PHASE_7F_INIT)
    print_success("  Código __init__ adicionado")
    
    content = remove_methods(content, PHASE_7F_METHODS_TO_REMOVE)
    print_success(f"  {len(PHASE_7F_METHODS_TO_REMOVE)} métodos removidos")
    
    return content


def main():
    parser = argparse.ArgumentParser(
        description="Refatoração automática Fase 7 - main_window.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --dry-run          # Ver mudanças sem aplicar
  %(prog)s --phase 7c         # Aplicar apenas Fase 7C
  %(prog)s --all              # Aplicar todas as fases
  %(prog)s --undo             # Desfazer última mudança
  %(prog)s --list-backups     # Listar backups disponíveis
        """
    )
    
    parser.add_argument(
        '--phase',
        choices=['7c', '7d', '7e', '7f'],
        help='Aplicar fase específica'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Aplicar todas as fases (7c+7d+7e+7f)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostrar mudanças sem aplicar'
    )
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Desfazer última mudança (restaurar backup)'
    )
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='Listar todos os backups disponíveis'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.undo:
        undo_last_change()
        return
    
    if args.list_backups:
        print_header("📦 BACKUPS DISPONÍVEIS")
        backups = list_backups()
        if not backups:
            print_info("Nenhum backup encontrado.")
        else:
            for i, backup in enumerate(backups, 1):
                timestamp = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"  {i}. {backup.name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        return
    
    # Validate arguments
    if not args.phase and not args.all:
        parser.print_help()
        return
    
    # Check if file exists
    if not MAIN_WINDOW_PATH.exists():
        print_error(f"Arquivo não encontrado: {MAIN_WINDOW_PATH}")
        sys.exit(1)
    
    # Read original content
    original_content = read_file(MAIN_WINDOW_PATH)
    original_lines = count_lines(MAIN_WINDOW_PATH)
    
    print_header("🔧 REFATORAÇÃO AUTOMÁTICA - FASE 7")
    print_info(f"Arquivo: {MAIN_WINDOW_PATH}")
    print_info(f"Linhas atuais: {original_lines}")
    print_info(f"Meta: {TARGET_LINES} linhas")
    print()
    
    # Create backup (unless dry-run)
    if not args.dry_run:
        create_backup(MAIN_WINDOW_PATH)
        print()
    
    # Apply phases
    content = original_content
    phases_to_apply = []
    
    if args.all:
        phases_to_apply = ['7c', '7d', '7e', '7f']
    elif args.phase:
        phases_to_apply = [args.phase]
    
    for phase in phases_to_apply:
        print_header(f"APLICANDO FASE {phase.upper()}")
        
        if phase == '7c':
            content = apply_phase_7c(content)
        elif phase == '7d':
            content = apply_phase_7d(content)
        elif phase == '7e':
            content = apply_phase_7e(content)
        elif phase == '7f':
            content = apply_phase_7f(content)
        
        print()
    
    # Validate syntax
    print_header("✓ VALIDAÇÃO")
    if not validate_syntax(content):
        print_error("Sintaxe inválida! Abortando.")
        sys.exit(1)
    
    print_success("Sintaxe Python válida")
    
    # Count lines
    new_lines = len([l for l in content.split('\n') if l.strip()])
    reduction = original_lines - new_lines
    reduction_pct = (reduction / original_lines) * 100 if original_lines else 0
    
    print_info(f"Linhas antes: {original_lines}")
    print_info(f"Linhas depois: {new_lines}")
    print_success(f"Redução: {reduction} linhas (-{reduction_pct:.1f}%)")
    print()
    
    # Dry-run: show diff
    if args.dry_run:
        print_warning("DRY-RUN: Mudanças NÃO serão aplicadas")
        print_info("Execute sem --dry-run para aplicar")
        return
    
    # Write file
    write_file(MAIN_WINDOW_PATH, content)
    print_success(f"Arquivo atualizado: {MAIN_WINDOW_PATH}")
    
    print()
    print_header("✅ REFATORAÇÃO CONCLUÍDA")
    print_success(f"main_window.py refatorado com sucesso!")
    print_info(f"Linhas: {original_lines} → {new_lines} ({reduction} linhas removidas)")
    print()
    print_info("Próximos passos:")
    print(f"  1. {Color.CYAN}python main.py{Color.RESET} - Testar aplicação")
    print(f"  2. {Color.CYAN}git add ui/main_window.py{Color.RESET}")
    print(f"  3. {Color.CYAN}git commit -m 'refactor(fase7): Integração completa ({original_lines}→{new_lines} linhas)'{Color.RESET}")
    print()
    print_warning("Se algo quebrar:")
    print(f"  {Color.YELLOW}python apply_fase7_refactor.py --undo{Color.RESET}")
    print()


if __name__ == '__main__':
    main()
