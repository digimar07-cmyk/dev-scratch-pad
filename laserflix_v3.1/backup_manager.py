#!/usr/bin/env python3
"""
Sistema de Backup Local - Laserflix v3.1
Mantém últimas 10 versões no disco (independente do Git)
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configurações
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKUP_DIR = PROJECT_ROOT / ".backups"
METADATA_FILE = BACKUP_DIR / "backup_metadata.json"
MAX_BACKUPS = 10

# Pastas/arquivos a incluir no backup
INCLUDE_PATTERNS = [
    "ai/",
    "ui/",
    "core/",
    "config/",
    "utils/",
    "main.py",
    "requirements.txt",
    "*.md"
]

# Excluir do backup
EXCLUDE_PATTERNS = [
    ".backups/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    ".git/",
    "venv/",
    "*.db",
    "*.log"
]


class BackupManager:
    """Gerenciador de backups locais"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.metadata_file = METADATA_FILE
        self.project_root = PROJECT_ROOT
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Cria pasta de backups se não existir"""
        self.backup_dir.mkdir(exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata([])
    
    def _load_metadata(self) -> List[Dict]:
        """Carrega metadata de backups"""
        if not self.metadata_file.exists():
            return []
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: List[Dict]):
        """Salva metadata de backups"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _should_include(self, path: Path) -> bool:
        """Verifica se arquivo/pasta deve ser incluído"""
        rel_path = path.relative_to(self.project_root)
        path_str = str(rel_path)
        
        # Verifica exclusões
        for pattern in EXCLUDE_PATTERNS:
            if pattern.endswith('/'):
                if path_str.startswith(pattern.rstrip('/')):
                    return False
            elif pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return False
            else:
                if pattern in path_str:
                    return False
        
        return True
    
    def _get_next_backup_number(self) -> int:
        """Retorna próximo número de backup"""
        metadata = self._load_metadata()
        if not metadata:
            return 1
        return max(b['number'] for b in metadata) + 1
    
    def _cleanup_old_backups(self):
        """Remove backups excedentes (mantém últimas MAX_BACKUPS)"""
        metadata = self._load_metadata()
        if len(metadata) <= MAX_BACKUPS:
            return
        
        # Ordena por número (mais antigos primeiro)
        metadata.sort(key=lambda x: x['number'])
        
        # Remove os mais antigos
        to_remove = metadata[:-MAX_BACKUPS]
        for backup in to_remove:
            backup_file = self.backup_dir / backup['filename']
            if backup_file.exists():
                backup_file.unlink()
                print(f"  ♻️  Removido backup antigo: {backup['filename']}")
        
        # Atualiza metadata
        remaining = metadata[-MAX_BACKUPS:]
        self._save_metadata(remaining)
    
    def create_backup(self, description: str = "") -> Optional[str]:
        """
        Cria novo backup comprimido
        
        Args:
            description: Descrição do backup (opcional)
        
        Returns:
            Nome do arquivo de backup criado ou None se falhar
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_number = self._get_next_backup_number()
        backup_filename = f"backup_{backup_number:03d}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        print(f"\n🔄 Criando backup #{backup_number}...")
        print(f"📦 {backup_filename}")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                file_count = 0
                
                # Adiciona arquivos recursivamente
                for item in self.project_root.rglob('*'):
                    if item.is_file() and self._should_include(item):
                        arcname = item.relative_to(self.project_root)
                        zipf.write(item, arcname)
                        file_count += 1
            
            # Atualiza metadata
            metadata = self._load_metadata()
            metadata.append({
                'number': backup_number,
                'filename': backup_filename,
                'timestamp': timestamp,
                'description': description,
                'file_count': file_count,
                'size_mb': round(backup_path.stat().st_size / 1024 / 1024, 2)
            })
            self._save_metadata(metadata)
            
            print(f"✅ Backup criado: {file_count} arquivos, {metadata[-1]['size_mb']} MB")
            
            # Limpa backups antigos
            self._cleanup_old_backups()
            
            return backup_filename
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        metadata = self._load_metadata()
        
        if not metadata:
            print("\n📭 Nenhum backup encontrado")
            return
        
        print(f"\n📦 Backups disponíveis ({len(metadata)}/{MAX_BACKUPS}):\n")
        
        # Ordena do mais recente para o mais antigo
        metadata.sort(key=lambda x: x['number'], reverse=True)
        
        for backup in metadata:
            desc = f" - {backup['description']}" if backup['description'] else ""
            print(f"  #{backup['number']:03d} | {backup['timestamp']} | {backup['size_mb']} MB{desc}")
        
        print(f"\n💡 Restaurar: python backup_manager.py restore <número>")
    
    def restore_backup(self, backup_number: int) -> bool:
        """
        Restaura backup específico
        
        Args:
            backup_number: Número do backup a restaurar
        
        Returns:
            True se restaurado com sucesso, False caso contrário
        """
        metadata = self._load_metadata()
        backup_data = next((b for b in metadata if b['number'] == backup_number), None)
        
        if not backup_data:
            print(f"❌ Backup #{backup_number} não encontrado")
            return False
        
        backup_path = self.backup_dir / backup_data['filename']
        
        if not backup_path.exists():
            print(f"❌ Arquivo de backup não existe: {backup_data['filename']}")
            return False
        
        print(f"\n⚠️  ATENÇÃO: Isso vai SUBSTITUIR os arquivos atuais!")
        print(f"📦 Restaurando backup #{backup_number} ({backup_data['timestamp']})")
        
        confirm = input("\n🤔 Confirma? (sim/não): ").strip().lower()
        if confirm not in ['sim', 's', 'yes', 'y']:
            print("❌ Restauração cancelada")
            return False
        
        try:
            # Cria backup de segurança antes de restaurar
            print("\n🔄 Criando backup de segurança antes...")
            safety_backup = self.create_backup(f"AUTO: antes de restaurar #{backup_number}")
            
            # Extrai backup
            print(f"\n📂 Extraindo {backup_data['filename']}...")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.project_root)
            
            print(f"✅ Backup #{backup_number} restaurado com sucesso!")
            print(f"💾 Backup de segurança criado: {safety_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def clean_old_backups(self, keep_last: int = MAX_BACKUPS):
        """
        Remove backups antigos manualmente
        
        Args:
            keep_last: Quantidade de backups a manter
        """
        metadata = self._load_metadata()
        if len(metadata) <= keep_last:
            print(f"\n✅ Apenas {len(metadata)} backups encontrados (limite: {keep_last})")
            return
        
        metadata.sort(key=lambda x: x['number'])
        to_remove = metadata[:-keep_last]
        
        print(f"\n🗑️  Removendo {len(to_remove)} backups antigos...\n")
        for backup in to_remove:
            backup_file = self.backup_dir / backup['filename']
            if backup_file.exists():
                backup_file.unlink()
                print(f"  ✅ Removido: {backup['filename']}")
        
        remaining = metadata[-keep_last:]
        self._save_metadata(remaining)
        print(f"\n✅ Limpeza concluída. Mantidos: {len(remaining)} backups")


def main():
    """CLI do backup manager"""
    manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("""
🔧 Sistema de Backup Local - Laserflix v3.1

USO:
  python backup_manager.py create [descrição]  - Cria novo backup
  python backup_manager.py list                 - Lista backups
  python backup_manager.py restore <número>     - Restaura backup
  python backup_manager.py clean [quantidade]   - Limpa backups antigos

EXEMPLOS:
  python backup_manager.py create "antes de fix modal"
  python backup_manager.py restore 5
  python backup_manager.py clean 10
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        description = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        manager.create_backup(description)
    
    elif command == 'list':
        manager.list_backups()
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Especifique o número do backup: python backup_manager.py restore <número>")
            sys.exit(1)
        try:
            backup_number = int(sys.argv[2])
            manager.restore_backup(backup_number)
        except ValueError:
            print("❌ Número de backup inválido")
            sys.exit(1)
    
    elif command == 'clean':
        keep_last = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_BACKUPS
        manager.clean_old_backups(keep_last)
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
