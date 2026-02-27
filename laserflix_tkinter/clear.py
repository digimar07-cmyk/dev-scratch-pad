#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEAR.PY LOCAL - Reset dentro do diretório laserflix_tkinter
Versão local que roda de dentro da pasta do app
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

# Arquivos e pastas a serem removidos
FILES_TO_REMOVE = [
    "laserflix_database.json",
    "laserflix_database.json.bak",
    "laserflix_database.json.tmp",
    "laserflix_database.json.pre-import.backup",
    "laserflix_config.json",
    "laserflix.log",
    "laserflix.log.1",
    "laserflix.log.2",
    "laserflix.log.3",
]

FOLDERS_TO_REMOVE = [
    "laserflix_backups",
    "__pycache__",
]

print("🧹" * 30)
print("  LASERFLIX - CLEAR LOCAL")
print("🧹" * 30)
print()
print(f"📍 Diretório: {BASE_DIR}")
print()
print("⚠️  Este script irá DELETAR:")
print()
print("   📁 Banco de dados completo")
print("   ⚙️ Todas as configurações")
print("   💾 Todos os backups")
print("   📝 Todos os logs")
print("   📂 Cache Python")
print()

# Lista o que será removido
print("🔍 Encontrado para remoção:")
found_items = []

for filename in FILES_TO_REMOVE:
    file_path = BASE_DIR / filename
    if file_path.exists():
        size = file_path.stat().st_size / 1024  # KB
        print(f"   📄 {filename} ({size:.1f} KB)")
        found_items.append(filename)

for foldername in FOLDERS_TO_REMOVE:
    folder_path = BASE_DIR / foldername
    if folder_path.exists():
        # Conta arquivos na pasta
        file_count = sum(1 for _ in folder_path.rglob('*') if _.is_file())
        print(f"   📂 {foldername}/ ({file_count} arquivos)")
        found_items.append(foldername)

if not found_items:
    print("   ✅ Nada para remover - já está limpo!")
    print()
    input("Pressione ENTER para sair...")
    exit(0)

print()
print(f"📄 Total de itens: {len(found_items)}")
print()
confirm = input("🔴 Confirma DELEÇÃO permanente? Digite 'SIM': ")

if confirm.upper() != "SIM":
    print("\n❌ Operação cancelada.")
    input("Pressione ENTER para sair...")
    exit(0)

print("\n" + "=" * 60)
print("🛠️ Executando limpeza...")
print("=" * 60)

deleted_files = 0
deleted_folders = 0
failed = []

# Remove arquivos
for filename in FILES_TO_REMOVE:
    file_path = BASE_DIR / filename
    if file_path.exists():
        try:
            os.remove(file_path)
            print(f"   ✓ {filename}")
            deleted_files += 1
        except Exception as e:
            print(f"   ✗ {filename}: {e}")
            failed.append((filename, str(e)))

# Remove pastas
for foldername in FOLDERS_TO_REMOVE:
    folder_path = BASE_DIR / foldername
    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
            print(f"   ✓ {foldername}/")
            deleted_folders += 1
        except Exception as e:
            print(f"   ✗ {foldername}: {e}")
            failed.append((foldername, str(e)))

print("\n" + "=" * 60)
print("📊 RESUMO")
print("=" * 60)
print(f"\n   ✅ Arquivos: {deleted_files}")
print(f"   ✅ Pastas: {deleted_folders}")

if failed:
    print(f"\n   ⚠️ Falhas ({len(failed)}):")
    for item, error in failed:
        print(f"      ✗ {item}")
        print(f"        Erro: {error}")
else:
    print(f"\n   ✨ Sem falhas - tudo limpo!")

timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print(f"\n   🕒 {timestamp}")

print("\n" + "=" * 60)
print("✅ LIMPEZA CONCLUÍDA")
print("=" * 60)
print("\n🚀 Laserflix resetado com sucesso!")
print("\n🏁 Para iniciar do zero:")
print("   python main.py")
print("\n📝 Lembre-se:")
print("   1. Adicionar pastas de projetos")
print("   2. Escanear projetos")
print("   3. Analisar com IA")
print("\n" + "=" * 60)
print()
input("Pressione ENTER para sair...")
