#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_folders.py — Prepara pastas para importação gerando folder.jpg.

Gera automaticamente folder.jpg em pastas de produtos usando a primeira imagem.

MODOS:
  --smart: Apenas pastas com arquivos de projeto (.svg, .pdf, .dxf)
  --all: TODAS as pastas com imagens
  --list: Apenas lista, não cria nada (dry-run)

USO:
    python prepare_folders.py <pasta_base> [--smart|--all|--list]
    python prepare_folders.py "D:/PROJETOS" --smart
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple

# Configura encoding para UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Extensões suportadas
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
PROJECT_EXTENSIONS = {'.svg', '.pdf', '.dxf', '.ai', '.eps'}


def find_first_image(folder: Path) -> Path | None:
    """
    Encontra a primeira imagem na pasta.
    
    Args:
        folder: Pasta para buscar
    
    Returns:
        Path da primeira imagem ou None
    """
    try:
        for file in sorted(folder.iterdir()):
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
                if file.name.lower() != 'folder.jpg':
                    return file
    except (PermissionError, OSError):
        return None
    return None


def has_project_files(folder: Path) -> bool:
    """
    Verifica se pasta contém arquivos de projeto.
    
    Args:
        folder: Pasta para verificar
    
    Returns:
        True se contém arquivos de projeto
    """
    try:
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in PROJECT_EXTENSIONS:
                return True
    except (PermissionError, OSError):
        return False
    return False


def scan_folders(
    base_path: Path,
    mode: str = 'smart'
) -> List[Tuple[Path, Path]]:
    """
    Escaneia pastas e identifica onde criar folder.jpg.
    
    Args:
        base_path: Pasta base para escanear
        mode: 'smart', 'all', ou 'list'
    
    Returns:
        Lista de tuplas (pasta, imagem_origem)
    """
    results = []
    
    print(f"\n==> Escaneando: {base_path}")
    print(f"==> Modo: {mode.upper()}\n")
    
    total_scanned = 0
    
    for root, dirs, files in os.walk(base_path):
        folder = Path(root)
        total_scanned += 1
        
        # Ignora pastas de sistema
        folder_name = folder.name.lower()
        if folder_name.startswith(('.', '__')):
            continue
        
        # Verifica se já tem folder.jpg
        folder_jpg = folder / 'folder.jpg'
        if folder_jpg.exists():
            continue
        
        # Verifica modo
        if mode == 'smart':
            if not has_project_files(folder):
                continue
        
        # Busca primeira imagem
        first_image = find_first_image(folder)
        if first_image:
            results.append((folder, first_image))
    
    print(f"\n==> Pastas escaneadas: {total_scanned}")
    print(f"==> Pastas para processar: {len(results)}\n")
    
    return results


def create_folder_jpg(
    folder: Path,
    source_image: Path,
    dry_run: bool = False
) -> bool:
    """
    Cria folder.jpg copiando a imagem fonte.
    
    Args:
        folder: Pasta destino
        source_image: Imagem a copiar
        dry_run: Se True, apenas simula
    
    Returns:
        True se criado com sucesso
    """
    try:
        target = folder / 'folder.jpg'
        
        if dry_run:
            print(f"[DRY-RUN] {folder.name}/folder.jpg <- {source_image.name}")
            return True
        
        shutil.copy2(source_image, target)
        print(f"[OK] {folder.name}/folder.jpg <- {source_image.name}")
        return True
    
    except Exception as e:
        print(f"[ERRO] {folder.name}: {e}")
        return False


def main():
    """
    Função principal.
    """
    print("="*60)
    print("PREPARADOR DE PASTAS - folder.jpg Generator")
    print("="*60)
    
    # Argumentos
    if len(sys.argv) < 2:
        print("\nUSO: python prepare_folders.py <pasta_base> [--smart|--all|--list]")
        print("\nMODOS:")
        print("  --smart (padr\u00e3o): Apenas pastas com arquivos de projeto")
        print("  --all: TODAS as pastas com imagens")
        print("  --list: Apenas lista, n\u00e3o cria (dry-run)")
        sys.exit(1)
    
    base_path = Path(sys.argv[1])
    
    if not base_path.exists():
        print(f"\n[ERRO] Pasta n\u00e3o existe: {base_path}")
        sys.exit(1)
    
    if not base_path.is_dir():
        print(f"\n[ERRO] N\u00e3o \u00e9 uma pasta: {base_path}")
        sys.exit(1)
    
    # Modo
    mode = 'smart'
    dry_run = False
    
    if len(sys.argv) > 2:
        arg = sys.argv[2].lower().lstrip('-')
        if arg == 'all':
            mode = 'all'
        elif arg == 'list':
            mode = 'list'
            dry_run = True
        elif arg == 'smart':
            mode = 'smart'
    
    # Escaneia
    folders_to_process = scan_folders(base_path, mode)
    
    if not folders_to_process:
        print("\n[INFO] Nenhuma pasta para processar.")
        return
    
    # Processa
    print("\n" + "="*60)
    print("PROCESSANDO...")
    print("="*60 + "\n")
    
    success = 0
    failed = 0
    
    for folder, source_image in folders_to_process:
        if create_folder_jpg(folder, source_image, dry_run):
            success += 1
        else:
            failed += 1
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    print(f"Sucesso: {success}")
    print(f"Falhas: {failed}")
    print(f"Total: {len(folders_to_process)}")
    
    if dry_run:
        print("\n[DRY-RUN] Nenhum arquivo foi criado.")
    
    print("="*60)


if __name__ == '__main__':
    main()
