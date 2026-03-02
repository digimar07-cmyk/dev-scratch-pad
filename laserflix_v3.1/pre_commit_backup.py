#!/usr/bin/env python3
"""
Pre-Commit Backup Hook - Backup Automático Antes de Commits

Executa backup automático do projeto antes de cada commit,
garantindo que você sempre tenha uma versão de segurança.

Modo Akita:
- Backup automático antes de mudanças
- Protege contra commits que quebram o app
- Independente do Git (funciona offline)
- Zero intervenção manual necessária

Instalação:
    1. Torne executável:
       chmod +x pre_commit_backup.py
    
    2. Configure Git hook (opcional):
       cp pre_commit_backup.py .git/hooks/pre-commit
       chmod +x .git/hooks/pre-commit
    
    3. OU rode manualmente antes de commits:
       python pre_commit_backup.py

Uso Manual:
    python pre_commit_backup.py
    python pre_commit_backup.py --description "antes de fix"
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Import do backup manager
try:
    from backup_manager import BackupManager
except ImportError:
    print("❌ Erro: backup_manager.py não encontrado.")
    sys.exit(1)


def get_git_status():
    """Verifica se há mudanças para commitar.
    
    Returns:
        tuple: (has_changes, changed_files)
    """
    try:
        # Verifica se estamos em um repo Git
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout.strip()
        if not output:
            return False, []
        
        # Lista arquivos modificados
        changed_files = []
        for line in output.split("\n"):
            if line.strip():
                # Formato: XY filename
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    changed_files.append(parts[1])
        
        return True, changed_files
    
    except subprocess.CalledProcessError:
        # Não é um repo Git ou erro
        return False, []
    except FileNotFoundError:
        # Git não instalado
        return False, []


def get_last_commit_message():
    """Obtém mensagem do último commit.
    
    Returns:
        str: Mensagem do último commit ou None
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def create_pre_commit_backup(description=None):
    """Cria backup antes de commit.
    
    Args:
        description: Descrição customizada (opcional)
        
    Returns:
        bool: True se backup criado com sucesso
    """
    # Determina pasta do projeto
    script_dir = Path(__file__).parent.resolve()
    
    # Verifica se há mudanças
    has_changes, changed_files = get_git_status()
    
    if not has_changes:
        print("\n✅ Nenhuma mudança detectada - backup não necessário.")
        return True
    
    # Gera descrição automática
    if description is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        file_count = len(changed_files)
        
        # Resume arquivos modificados
        if file_count <= 3:
            files_summary = ", ".join(Path(f).name for f in changed_files[:3])
        else:
            files_summary = f"{file_count} arquivos"
        
        description = f"Pre-commit {timestamp} ({files_summary})"
    
    print(f"\n🔒 Criando backup de segurança antes do commit...")
    print(f"   📝 {len(changed_files)} arquivo(s) modificado(s)")
    
    # Cria backup
    manager = BackupManager(script_dir)
    backup_path = manager.create_backup(description)
    
    if backup_path:
        print(f"\n✅ Backup criado com sucesso!")
        print(f"   💡 Restaurar: python backup_manager.py restore <ID>")
        return True
    else:
        print(f"\n⚠️  Backup falhou - prosseguir mesmo assim? (s/n): ", end="")
        response = input().strip().lower()
        return response in ["s", "sim", "y", "yes"]


def main():
    """Função principal - Hook de pre-commit."""
    # Parse argumentos
    description = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1] in ["-d", "--description"]:
            if len(sys.argv) > 2:
                description = sys.argv[2]
    
    # Cria backup
    success = create_pre_commit_backup(description)
    
    if not success:
        print("\n❌ Pre-commit backup cancelado.")
        sys.exit(1)
    
    # Git hooks: retorna 0 para permitir commit
    sys.exit(0)


if __name__ == "__main__":
    main()
