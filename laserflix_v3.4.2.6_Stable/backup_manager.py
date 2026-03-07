#!/usr/bin/env python3
"""
🔐 Sistema de Backup Local Automático - Laserflix v3.1
Mantém até 10 versões anteriores para restauração rápida
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib


class BackupManager:
    """Gerenciador de backups locais automáticos"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = Path(__file__).parent.resolve()
        else:
            project_root = Path(project_root).resolve()
            
        self.project_root = project_root
        self.backup_dir = project_root / ".backups"
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.max_backups = 10
        
        # Pastas/arquivos a serem excluídos do backup
        self.exclude_patterns = {
            ".backups",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "*.log"
        }
        
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Cria diretório de backups se não existir"""
        self.backup_dir.mkdir(exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata([])
    
    def _load_metadata(self) -> List[Dict]:
        """Carrega metadados dos backups"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_metadata(self, metadata: List[Dict]):
        """Salva metadados dos backups"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _calculate_hash(self, directory: Path) -> str:
        """Calcula hash único do estado atual do projeto"""
        hasher = hashlib.sha256()
        
        for root, dirs, files in os.walk(directory):
            # Remove pastas excluídas da busca
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
            
            for file in sorted(files):
                # Ignora arquivos excluídos
                if any(file.endswith(pattern.replace("*", "")) 
                       for pattern in self.exclude_patterns if "*" in pattern):
                    continue
                if file in self.exclude_patterns:
                    continue
                
                filepath = Path(root) / file
                try:
                    with open(filepath, 'rb') as f:
                        hasher.update(f.read())
                except:
                    pass
        
        return hasher.hexdigest()[:16]
    
    def _should_ignore(self, path: Path, base_path: Path) -> bool:
        """Verifica se arquivo/pasta deve ser ignorado"""
        relative = path.relative_to(base_path)
        parts = relative.parts
        
        # Verifica cada parte do caminho
        for part in parts:
            if part in self.exclude_patterns:
                return True
        
        # Verifica padrões com wildcard
        name = path.name
        for pattern in self.exclude_patterns:
            if "*" in pattern:
                ext = pattern.replace("*", "")
                if name.endswith(ext):
                    return True
        
        return False
    
    def create_backup(self, description: str = "") -> Dict:
        """
        Cria novo backup do estado atual
        
        Args:
            description: Descrição opcional do backup
            
        Returns:
            Dict com informações do backup criado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_hash = self._calculate_hash(self.project_root)
        
        # Verifica se já existe backup com mesmo hash (nada mudou)
        metadata = self._load_metadata()
        if metadata and metadata[0].get('hash') == project_hash:
            print("⚠️ Nenhuma alteração detectada desde último backup")
            return metadata[0]
        
        backup_name = f"backup_{timestamp}_{project_hash}"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Criando backup: {backup_name}")
        
        # Copia arquivos (exceto os excluídos)
        shutil.copytree(
            self.project_root,
            backup_path,
            ignore=lambda src, names: [
                n for n in names 
                if self._should_ignore(Path(src) / n, self.project_root)
            ]
        )
        
        # Atualiza metadados
        backup_info = {
            "name": backup_name,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "description": description,
            "hash": project_hash,
            "size_mb": round(self._get_dir_size(backup_path) / (1024 * 1024), 2)
        }
        
        metadata.insert(0, backup_info)
        
        # Remove backups excedentes
        if len(metadata) > self.max_backups:
            old_backups = metadata[self.max_backups:]
            for old in old_backups:
                old_path = self.backup_dir / old['name']
                if old_path.exists():
                    shutil.rmtree(old_path)
                    print(f"🗑️ Removido backup antigo: {old['name']}")
            
            metadata = metadata[:self.max_backups]
        
        self._save_metadata(metadata)
        print(f"✅ Backup criado: {backup_info['size_mb']} MB")
        
        return backup_info
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        return self._load_metadata()
    
    def restore_backup(self, backup_index: int = 0, target_dir: str = None) -> bool:
        """
        Restaura um backup específico
        
        Args:
            backup_index: Índice do backup (0 = mais recente)
            target_dir: Diretório alvo (None = projeto atual)
            
        Returns:
            True se restaurado com sucesso
        """
        metadata = self._load_metadata()
        
        if not metadata:
            print("❌ Nenhum backup disponível")
            return False
        
        if backup_index >= len(metadata):
            print(f"❌ Backup #{backup_index} não existe (máximo: {len(metadata)-1})")
            return False
        
        backup = metadata[backup_index]
        backup_path = self.backup_dir / backup['name']
        
        if not backup_path.exists():
            print(f"❌ Backup corrompido: {backup['name']}")
            return False
        
        # Define diretório alvo
        if target_dir:
            target = Path(target_dir)
        else:
            # Cria backup de segurança antes de restaurar
            print("🔄 Criando backup de segurança antes de restaurar...")
            self.create_backup(description="Auto-backup antes de restauração")
            target = self.project_root
        
        print(f"♻️ Restaurando backup: {backup['name']}")
        print(f"📅 Data: {backup['datetime']}")
        if backup['description']:
            print(f"📝 Descrição: {backup['description']}")
        
        # Remove conteúdo atual (exceto .backups)
        for item in target.iterdir():
            if item.name == ".backups":
                continue
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)
        
        # Copia backup para target
        for item in backup_path.iterdir():
            if item.is_file():
                shutil.copy2(item, target / item.name)
            else:
                shutil.copytree(item, target / item.name)
        
        print("✅ Backup restaurado com sucesso!")
        return True
    
    def get_backup_info(self, backup_index: int = 0) -> Optional[Dict]:
        """Retorna informações de um backup específico"""
        metadata = self._load_metadata()
        if 0 <= backup_index < len(metadata):
            return metadata[backup_index]
        return None
    
    def delete_backup(self, backup_index: int) -> bool:
        """Remove um backup específico"""
        metadata = self._load_metadata()
        
        if not (0 <= backup_index < len(metadata)):
            print(f"❌ Backup #{backup_index} não existe")
            return False
        
        backup = metadata[backup_index]
        backup_path = self.backup_dir / backup['name']
        
        if backup_path.exists():
            shutil.rmtree(backup_path)
        
        metadata.pop(backup_index)
        self._save_metadata(metadata)
        
        print(f"🗑️ Backup removido: {backup['name']}")
        return True
    
    def _get_dir_size(self, path: Path) -> int:
        """Calcula tamanho total do diretório em bytes"""
        total = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                filepath = Path(root) / file
                try:
                    total += filepath.stat().st_size
                except:
                    pass
        return total
    
    def auto_backup_wrapper(self, func):
        """
        Decorator para criar backup automático antes de executar função
        
        Usage:
            @backup_manager.auto_backup_wrapper
            def risky_operation():
                # código que pode quebrar
                pass
        """
        def wrapper(*args, **kwargs):
            self.create_backup(description=f"Auto-backup antes de {func.__name__}")
            return func(*args, **kwargs)
        return wrapper


def main():
    """Interface CLI para gerenciar backups"""
    import sys
    
    manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("🔐 Sistema de Backup Local - Laserflix v3.1\n")
        print("Uso:")
        print("  python backup_manager.py create [descrição]    - Cria novo backup")
        print("  python backup_manager.py list                  - Lista backups")
        print("  python backup_manager.py restore [índice]      - Restaura backup")
        print("  python backup_manager.py info [índice]         - Info do backup")
        print("  python backup_manager.py delete [índice]       - Remove backup")
        print("\nÍndice 0 = backup mais recente")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        manager.create_backup(description)
    
    elif command == "list":
        backups = manager.list_backups()
        if not backups:
            print("📭 Nenhum backup disponível")
            return
        
        print(f"\n📦 Backups disponíveis ({len(backups)}/{manager.max_backups}):\n")
        for i, backup in enumerate(backups):
            print(f"[{i}] {backup['datetime']}")
            print(f"    📝 {backup['description'] or '(sem descrição)'}")
            print(f"    💾 {backup['size_mb']} MB")
            print(f"    🔑 Hash: {backup['hash']}\n")
    
    elif command == "restore":
        index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        
        backup = manager.get_backup_info(index)
        if backup:
            print(f"\n⚠️ ATENÇÃO: Você vai restaurar o backup:")
            print(f"📅 Data: {backup['datetime']}")
            print(f"📝 Descrição: {backup['description'] or '(sem descrição)'}")
            print(f"\n🚨 O estado atual será substituído!")
            
            confirm = input("\nDigite 'SIM' para confirmar: ")
            if confirm.upper() == "SIM":
                manager.restore_backup(index)
            else:
                print("❌ Restauração cancelada")
    
    elif command == "info":
        index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        backup = manager.get_backup_info(index)
        
        if backup:
            print(f"\n📦 Backup #{index}:")
            print(f"📅 Data: {backup['datetime']}")
            print(f"📝 Descrição: {backup['description'] or '(sem descrição)'}")
            print(f"💾 Tamanho: {backup['size_mb']} MB")
            print(f"🔑 Hash: {backup['hash']}")
            print(f"📂 Nome: {backup['name']}")
        else:
            print(f"❌ Backup #{index} não encontrado")
    
    elif command == "delete":
        index = int(sys.argv[2]) if len(sys.argv) > 2 else None
        if index is None:
            print("❌ Especifique o índice do backup")
            return
        
        backup = manager.get_backup_info(index)
        if backup:
            print(f"\n⚠️ Você vai deletar o backup:")
            print(f"📅 Data: {backup['datetime']}")
            
            confirm = input("\nDigite 'SIM' para confirmar: ")
            if confirm.upper() == "SIM":
                manager.delete_backup(index)
            else:
                print("❌ Deleção cancelada")
    
    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
