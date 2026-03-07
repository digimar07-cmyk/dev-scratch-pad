#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
version_manager.py - Gerenciador de versões automático do Laserflix
===================================================================

Gerencia versionamento semântico e documentação automática de mudanças.

Uso:
  python version_manager.py bump patch "Descrição da mudança"
  python version_manager.py bump minor "Nova feature"
  python version_manager.py bump major "Breaking change"
  python version_manager.py current

Autor: Claude Sonnet 4.5
Data: 07/03/2026
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

# Arquivos que contêm versão
VERSION_FILE = Path("VERSION")
SETTINGS_FILE = Path("config/settings.py")
CHANGELOG_FILE = Path("CHANGELOG.md")


class VersionManager:
    """Gerencia versionamento semântico (MAJOR.MINOR.PATCH.BUILD)."""
    
    def __init__(self):
        self.version_file = VERSION_FILE
        self.settings_file = SETTINGS_FILE
        self.changelog_file = CHANGELOG_FILE
    
    def get_current_version(self) -> str:
        """Obtém versão atual."""
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        
        # Fallback: ler de settings.py
        if self.settings_file.exists():
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'VERSION\s*=\s*["\']([\d.]+)["\']', content)
            if match:
                version = match.group(1)
                # Criar VERSION file
                with open(self.version_file, 'w', encoding='utf-8') as f:
                    f.write(version)
                return version
        
        # Default
        return "3.4.2.4"
    
    def parse_version(self, version: str) -> Tuple[int, int, int, int]:
        """Parse versão para tupla (major, minor, patch, build)."""
        parts = version.split('.')
        if len(parts) == 3:
            parts.append('0')  # Adicionar build se não existir
        
        return tuple(int(p) for p in parts[:4])
    
    def bump_version(self, bump_type: str) -> str:
        """
        Incrementa versão.
        
        bump_type:
          - 'major': 3.4.2.4 -> 4.0.0.0
          - 'minor': 3.4.2.4 -> 3.5.0.0
          - 'patch': 3.4.2.4 -> 3.4.3.0
          - 'build': 3.4.2.4 -> 3.4.2.5
        """
        current = self.get_current_version()
        major, minor, patch, build = self.parse_version(current)
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
            build = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
            build = 0
        elif bump_type == 'patch':
            patch += 1
            build = 0
        elif bump_type == 'build':
            build += 1
        else:
            raise ValueError(f"Tipo inválido: {bump_type}. Use: major, minor, patch ou build")
        
        new_version = f"{major}.{minor}.{patch}.{build}"
        return new_version
    
    def update_version_file(self, new_version: str) -> None:
        """Atualiza arquivo VERSION."""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(new_version)
        print(f"OK VERSION atualizado: {new_version}")
    
    def update_settings_py(self, new_version: str) -> None:
        """Atualiza VERSION em config/settings.py."""
        if not self.settings_file.exists():
            print(f"AVISO: {self.settings_file} não encontrado")
            return
        
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir VERSION = "..."
        new_content = re.sub(
            r'VERSION\s*=\s*["\'][\d.]+["\']',
            f'VERSION = "{new_version}"',
            content
        )
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"OK config/settings.py atualizado: VERSION = \"{new_version}\"")
    
    def update_changelog(self, new_version: str, description: str, changes: list) -> None:
        """
        Atualiza CHANGELOG.md com nova entrada.
        
        Args:
            new_version: Nova versao (ex: "3.4.2.5")
            description: Descricao da mudanca
            changes: Lista de mudancas detalhadas
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Criar entrada
        entry = f"""## [{new_version}] - {timestamp}

### {description}

"""
        
        if changes:
            entry += "**Mudancas:**\n"
            for change in changes:
                entry += f"- {change}\n"
            entry += "\n"
        
        entry += "---\n\n"
        
        # Ler CHANGELOG existente ou criar novo
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8', errors='replace') as f:
                existing_content = f.read()
            
            # Inserir nova entrada apos o header
            header_end = existing_content.find('\n---\n')
            if header_end != -1:
                new_content = (
                    existing_content[:header_end + 5] + 
                    "\n" + entry + 
                    existing_content[header_end + 5:]
                )
            else:
                new_content = entry + existing_content
        else:
            # Criar CHANGELOG novo
            new_content = f"""# CHANGELOG - Laserflix

Todas as mudancas importantes serao documentadas neste arquivo.

Formato baseado em Keep a Changelog.

---

{entry}"""
        
        with open(self.changelog_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(new_content)
        print(f"OK CHANGELOG.md atualizado")
    
    def bump_and_update(self, bump_type: str, description: str, changes: Optional[list] = None) -> str:
        """
        Incrementa versao e atualiza todos os arquivos.
        
        Args:
            bump_type: 'major', 'minor', 'patch' ou 'build'
            description: Descricao da mudanca
            changes: Lista de mudancas detalhadas (opcional)
        
        Returns:
            Nova versao
        """
        old_version = self.get_current_version()
        new_version = self.bump_version(bump_type)
        
        print(f"\nVERSAO: {old_version} -> {new_version}")
        print(f"DESCRICAO: {description}")
        print()
        
        # Atualizar arquivos
        self.update_version_file(new_version)
        self.update_settings_py(new_version)
        self.update_changelog(new_version, description, changes or [])
        
        print()
        print(f"OK Versionamento completo: v{new_version}")
        
        return new_version


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gerenciador de versoes do Laserflix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s current
  %(prog)s bump build "Corrigido bug X"
  %(prog)s bump patch "Nova feature Y"
  %(prog)s bump minor "Refatoracao Fase 7"
  %(prog)s bump major "Breaking change"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos')
    
    # Comando: current
    subparsers.add_parser('current', help='Mostrar versao atual')
    
    # Comando: bump
    bump_parser = subparsers.add_parser('bump', help='Incrementar versao')
    bump_parser.add_argument(
        'type',
        choices=['major', 'minor', 'patch', 'build'],
        help='Tipo de incremento'
    )
    bump_parser.add_argument(
        'description',
        help='Descricao da mudanca'
    )
    bump_parser.add_argument(
        '--changes',
        nargs='+',
        help='Lista de mudancas detalhadas'
    )
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.command == 'current':
        version = manager.get_current_version()
        print(f"Versao atual: {version}")
    
    elif args.command == 'bump':
        manager.bump_and_update(
            args.type,
            args.description,
            args.changes
        )
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
