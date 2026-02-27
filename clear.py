#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEAR.PY - Reset completo do Laserflix
Zera todos os bancos de dados, configs e backups
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
TARGET_DIR = BASE_DIR / "laserflix_tkinter"

# Arquivos e pastas a serem removidos
FILES_TO_REMOVE = [
    "laserflix_database.json",
    "laserflix_database.json.bak",
    "laserflix_database.json.tmp",
    "laserflix_database.json.pre-import.backup",
    "laserflix_config.json",
    "laserflix.log",
]

FOLDERS_TO_REMOVE = [
    "laserflix_backups",
    "__pycache__",
]

print("🧹" * 30)
print("  LASERFLIX - CLEAR DATABASE & CONFIG")
print("🧹" * 30)
print()
print("⚠️  ATENÇÃO: Este script irá DELETAR:")
print()
print("   📁 Banco de dados (database.json)")
print("   ⚙️ Configurações (config.json)")
print("   💾 Todos os backups")
print("   📝 Logs")
print("   📂 Cache (__pycache__)")
print()
confirm = input("🔴 Deseja continuar? Digite 'SIM' para confirmar: ")

if confirm.upper() != "SIM":
    print("\n❌ Operação cancelada.")
    exit(0)

print("\n" + "=" * 60)
print("🛠️ Iniciando limpeza...")
print("=" * 60)

deleted_files = 0
deleted_folders = 0
failed = []

# Remove arquivos
for filename in FILES_TO_REMOVE:
    file_path = TARGET_DIR / filename
    if file_path.exists():
        try:
            os.remove(file_path)
            print(f"   ✓ Removido: {filename}")
            deleted_files += 1
        except Exception as e:
            print(f"   ✗ Falha ao remover {filename}: {e}")
            failed.append(filename)

# Remove pastas
for foldername in FOLDERS_TO_REMOVE:
    folder_path = TARGET_DIR / foldername
    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
            print(f"   ✓ Removido: {foldername}/")
            deleted_folders += 1
        except Exception as e:
            print(f"   ✗ Falha ao remover {foldername}: {e}")
            failed.append(foldername)

# Remove backups no diretório principal também
for backup_file in BASE_DIR.glob("laserflix_*.backup"):
    try:
        os.remove(backup_file)
        print(f"   ✓ Removido: {backup_file.name}")
        deleted_files += 1
    except Exception as e:
        print(f"   ✗ Falha ao remover {backup_file.name}: {e}")
        failed.append(backup_file.name)

print("\n" + "=" * 60)
print("📊 RESUMO DA LIMPEZA")
print("=" * 60)
print(f"\n   📄 Arquivos removidos: {deleted_files}")
print(f"   📂 Pastas removidas: {deleted_folders}")

if failed:
    print(f"\n   ⚠️ Falhas: {len(failed)}")
    for item in failed:
        print(f"      - {item}")
else:
    print(f"\n   ✅ Nenhuma falha!")

print("\n" + "=" * 60)
print("✅ LIMPEZA CONCLUÍDA!")
print("=" * 60)
print("\n🚀 O Laserflix agora está limpo e pronto para rodar do zero.")
print("\n📝 Para iniciar:")
print("   cd laserflix_tkinter")
print("   python main.py")
print("\n📁 Configure as pastas de projetos no primeiro uso.")
print("=" * 60)
