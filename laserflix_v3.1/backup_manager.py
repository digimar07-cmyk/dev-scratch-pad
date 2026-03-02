#!/usr/bin/env python3
"""
Backup Manager - Sistema de Versionamento Local para Laserflix v3.1

Garante recuperação rápida das últimas 10 versões do projeto,
independente do Git. Protege contra commits acidentais que quebram o app.

Modo Akita:
- Small releases com segurança
- Backup automático antes de mudanças
- Restore instantâneo em caso de problema
- Independente de GitHub (funciona offline)

Uso:
    python backup_manager.py create "descrição da versão"
    python backup_manager.py list
    python backup_manager.py restore 5
    python backup_manager.py clean
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import hashlib


class BackupManager:
    """Gerenciador de backups locais com rotação automática."""
    
    MAX_BACKUPS = 10
    BACKUP_DIR = ".backups"
    METADATA_FILE = "backup_metadata.json"
    
    # Arquivos/pastas a ignorar no backup
    IGNORE_PATTERNS = {
        "__pycache__",
        ".backups",
        "*.pyc",
        ".git",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "*.tmp",
        ".pytest_cache",
        ".coverage"
    }
    
    def __init__(self, project_root=None):
        """Inicializa o gerenciador de backups.
        
        Args:
            project_root: Caminho raiz do projeto (default: pasta atual)
        """
        if project_root is None:
            # Assume que o script está em laserflix_v3.1/
            self.project_root = Path(__file__).parent.resolve()
        else:
            self.project_root = Path(project_root).resolve()
        
        self.backup_dir = self.project_root / self.BACKUP_DIR
        self.metadata_path = self.backup_dir / self.METADATA_FILE
        
        # Garante que pasta de backups existe
        self.backup_dir.mkdir(exist_ok=True)
    
    def _load_metadata(self):
        """Carrega metadata dos backups existentes."""
        if not self.metadata_path.exists():
            return {"backups": [], "next_id": 1}
        
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Erro ao ler metadata: {e}")
            return {"backups": [], "next_id": 1}
    
    def _save_metadata(self, metadata):
        """Salva metadata dos backups."""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ Erro ao salvar metadata: {e}")
    
    def _should_ignore(self, path):
        """Verifica se arquivo/pasta deve ser ignorado."""
        path_str = str(path)
        name = path.name
        
        for pattern in self.IGNORE_PATTERNS:
            if pattern.startswith("*"):
                ext = pattern[1:]
                if path_str.endswith(ext):
                    return True
            elif name == pattern or pattern in path_str:
                return True
        
        return False
    
    def _calculate_hash(self, file_path):
        """Calcula hash SHA256 de um arquivo."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()[:16]  # Primeiros 16 chars
        except IOError:
            return "unknown"
    
    def _get_project_hash(self):
        """Gera hash representativo do estado atual do projeto."""
        # Hash baseado nos arquivos Python principais
        main_files = list(self.project_root.glob("**/*.py"))
        main_files = [f for f in main_files if not self._should_ignore(f)]
        main_files = sorted(main_files)[:10]  # Primeiros 10 arquivos
        
        combined = "".join(str(f.stat().st_mtime) for f in main_files if f.exists())
        return hashlib.sha256(combined.encode()).hexdigest()[:8]
    
    def create_backup(self, description="Manual backup"):
        """Cria novo backup do projeto.
        
        Args:
            description: Descrição da versão
            
        Returns:
            Path do arquivo de backup criado ou None se erro
        """
        print(f"\n📦 Criando backup: {description}")
        
        metadata = self._load_metadata()
        backup_id = metadata["next_id"]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        project_hash = self._get_project_hash()
        
        backup_filename = f"backup_{backup_id:03d}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Cria arquivo ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                file_count = 0
                
                for root, dirs, files in os.walk(self.project_root):
                    root_path = Path(root)
                    
                    # Remove pastas ignoradas da busca
                    dirs[:] = [d for d in dirs if not self._should_ignore(root_path / d)]
                    
                    for file in files:
                        file_path = root_path / file
                        
                        if self._should_ignore(file_path):
                            continue
                        
                        # Caminho relativo para manter estrutura
                        arcname = file_path.relative_to(self.project_root)
                        zipf.write(file_path, arcname)
                        file_count += 1
            
            # Calcula tamanho do backup
            backup_size = backup_path.stat().st_size
            size_mb = backup_size / (1024 * 1024)
            
            # Atualiza metadata
            backup_info = {
                "id": backup_id,
                "filename": backup_filename,
                "timestamp": timestamp,
                "description": description,
                "size_mb": round(size_mb, 2),
                "file_count": file_count,
                "hash": project_hash
            }
            
            metadata["backups"].append(backup_info)
            metadata["next_id"] += 1
            
            # Rotação: mantém apenas últimos MAX_BACKUPS
            if len(metadata["backups"]) > self.MAX_BACKUPS:
                old_backups = metadata["backups"][:-self.MAX_BACKUPS]
                metadata["backups"] = metadata["backups"][-self.MAX_BACKUPS:]
                
                # Remove arquivos antigos
                for old_backup in old_backups:
                    old_path = self.backup_dir / old_backup["filename"]
                    if old_path.exists():
                        old_path.unlink()
                        print(f"🗑️  Backup antigo removido: {old_backup['filename']}")
            
            self._save_metadata(metadata)
            
            print(f"✅ Backup criado: {backup_filename}")
            print(f"   📊 Tamanho: {size_mb:.2f} MB ({file_count} arquivos)")
            print(f"   🔖 ID: {backup_id} | Hash: {project_hash}")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def list_backups(self):
        """Lista todos os backups disponíveis."""
        metadata = self._load_metadata()
        backups = metadata.get("backups", [])
        
        if not backups:
            print("\n📂 Nenhum backup encontrado.")
            return
        
        print(f"\n📂 Backups disponíveis ({len(backups)}/{self.MAX_BACKUPS}):")
        print("=" * 80)
        
        for backup in reversed(backups):  # Mais recente primeiro
            backup_id = backup["id"]
            timestamp = backup["timestamp"]
            description = backup["description"]
            size_mb = backup["size_mb"]
            file_count = backup["file_count"]
            
            print(f"\n🔖 ID: {backup_id:03d}")
            print(f"   📅 Data: {timestamp}")
            print(f"   📝 Descrição: {description}")
            print(f"   📊 Tamanho: {size_mb:.2f} MB ({file_count} arquivos)")
        
        print("\n" + "=" * 80)
        print(f"\n💡 Restaurar: python backup_manager.py restore <ID>")
    
    def restore_backup(self, backup_id):
        """Restaura um backup específico.
        
        Args:
            backup_id: ID do backup a restaurar
            
        Returns:
            True se restaurado com sucesso, False caso contrário
        """
        metadata = self._load_metadata()
        backups = metadata.get("backups", [])
        
        # Busca backup pelo ID
        backup_info = None
        for backup in backups:
            if backup["id"] == backup_id:
                backup_info = backup
                break
        
        if not backup_info:
            print(f"❌ Backup ID {backup_id} não encontrado.")
            return False
        
        backup_path = self.backup_dir / backup_info["filename"]
        
        if not backup_path.exists():
            print(f"❌ Arquivo de backup não encontrado: {backup_info['filename']}")
            return False
        
        print(f"\n⚠️  ATENÇÃO: Restaurar backup ID {backup_id}?")
        print(f"   📅 Data: {backup_info['timestamp']}")
        print(f"   📝 Descrição: {backup_info['description']}")
        print(f"\n   ⚠️  Arquivos atuais serão SUBSTITUÍDOS!")
        
        confirm = input("\n   Confirmar? (sim/não): ").strip().lower()
        if confirm not in ["sim", "s", "yes", "y"]:
            print("\n❌ Restauração cancelada.")
            return False
        
        print(f"\n🔄 Restaurando backup {backup_id}...")
        
        try:
            # Cria backup de segurança do estado atual
            print("   📦 Criando backup do estado atual...")
            self.create_backup(f"Auto-backup antes de restore {backup_id}")
            
            # Extrai arquivos do backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Remove arquivos existentes (exceto .backups)
                for item in self.project_root.iterdir():
                    if item.name == self.BACKUP_DIR:
                        continue
                    
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                
                # Extrai todos os arquivos
                zipf.extractall(self.project_root)
            
            print(f"\n✅ Backup {backup_id} restaurado com sucesso!")
            print(f"   📂 Localização: {self.project_root}")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao restaurar backup: {e}")
            return False
    
    def clean_old_backups(self, keep=None):
        """Remove backups antigos além do limite.
        
        Args:
            keep: Quantos backups manter (default: MAX_BACKUPS)
        """
        if keep is None:
            keep = self.MAX_BACKUPS
        
        metadata = self._load_metadata()
        backups = metadata.get("backups", [])
        
        if len(backups) <= keep:
            print(f"\n✅ Apenas {len(backups)} backups - nada a limpar.")
            return
        
        to_remove = backups[:-keep]
        metadata["backups"] = backups[-keep:]
        
        print(f"\n🗑️  Removendo {len(to_remove)} backups antigos...")
        
        for backup in to_remove:
            backup_path = self.backup_dir / backup["filename"]
            if backup_path.exists():
                backup_path.unlink()
                print(f"   ❌ {backup['filename']}")
        
        self._save_metadata(metadata)
        print(f"\n✅ Limpeza concluída - mantidos {keep} backups.")


def main():
    """Função principal - CLI do backup manager."""
    if len(sys.argv) < 2:
        print("""
Backup Manager - Laserflix v3.1

Uso:
    python backup_manager.py create "descrição"  - Criar novo backup
    python backup_manager.py list                 - Listar backups
    python backup_manager.py restore <ID>         - Restaurar backup
    python backup_manager.py clean                - Limpar backups antigos

Exemplos:
    python backup_manager.py create "antes de fix do scroll"
    python backup_manager.py restore 5
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = BackupManager()
    
    if command == "create":
        description = sys.argv[2] if len(sys.argv) > 2 else "Manual backup"
        manager.create_backup(description)
    
    elif command == "list":
        manager.list_backups()
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Erro: ID do backup não fornecido.")
            print("   Uso: python backup_manager.py restore <ID>")
            sys.exit(1)
        
        try:
            backup_id = int(sys.argv[2])
            manager.restore_backup(backup_id)
        except ValueError:
            print(f"❌ Erro: ID inválido '{sys.argv[2]}' (deve ser número).")
            sys.exit(1)
    
    elif command == "clean":
        manager.clean_old_backups()
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("   Comandos disponíveis: create, list, restore, clean")
        sys.exit(1)


if __name__ == "__main__":
    main()
