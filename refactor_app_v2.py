#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactor app.py v2.0
Extrai a classe LaserflixNetflix do arquivo monolítico de forma correta
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
TARGET_DIR = BASE_DIR / "laserflix_tkinter"
SOURCE_FILE = BASE_DIR / "laserflix_v740_Ofline_Stable.py"

print("🚀 Refactor app.py v2.0")
print("=" * 60)

if not SOURCE_FILE.exists():
    print(f"❌ Arquivo fonte não encontrado: {SOURCE_FILE}")
    exit(1)

if not TARGET_DIR.exists():
    print(f"❌ Pasta laserflix_tkinter não existe.")
    print("Execute: python refactor_laserflix.py")
    exit(1)

print(f"📚 Lendo {SOURCE_FILE.name}...")

with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"   Total: {len(lines)} linhas")

# Encontra onde começa a classe LaserflixNetflix
class_start = None
for i, line in enumerate(lines):
    if line.strip().startswith('class LaserflixNetflix:'):
        class_start = i
        break

if class_start is None:
    print("❌ Classe LaserflixNetflix não encontrada!")
    exit(1)

print(f"✅ Classe encontrada na linha {class_start + 1}")

# Encontra onde termina (antes do if __name__)
main_start = None
for i in range(class_start + 1, len(lines)):
    if lines[i].startswith('def main():'):
        main_start = i
        break

if main_start is None:
    # Se não tem def main, procura if __name__
    for i in range(class_start + 1, len(lines)):
        if lines[i].startswith('if __name__'):
            main_start = i
            break

if main_start is None:
    print("⚠️  Não encontrou fim da classe, usando arquivo inteiro")
    main_start = len(lines)

print(f"✅ Fim da classe na linha {main_start}")

# Extrai imports (tudo antes da classe)
imports_lines = lines[:class_start]

# Extrai a classe completa
class_lines = lines[class_start:main_start]

print(f"\n📦 Extraído:")
print(f"   Imports: {len(imports_lines)} linhas")
print(f"   Classe:  {len(class_lines)} linhas")

# Cria backup
app_file = TARGET_DIR / "app.py"
if app_file.exists():
    backup = TARGET_DIR / "app.py.backup"
    shutil.copy2(app_file, backup)
    print(f"\n💾 Backup: {backup}")

# Monta novo app.py
new_content = (
    '"""LASERFLIX v7.4.0 \u2014 Classe Principal\n'
    'Classe LaserflixNetflix extraída do monolito v7.4.0\n'
    '"""\n\n'
)

# Adiciona imports
new_content += ''.join(imports_lines)

# Adiciona a classe
new_content += '\n'.join(line.rstrip() for line in class_lines)

# Salva
with open(app_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Novo app.py criado!")
print(f"   Tamanho: {len(new_content)} caracteres")
print(f"   Linhas: {len(new_content.splitlines())}")

print("\n" + "=" * 60)
print("✅ REFATORAÇÃO CONCLUÍDA!")
print("\n📍 Para testar:")
print(f"   cd {TARGET_DIR.name}")
print("   python main.py")
print("\n⚠️  Se der erro, restaure:")
print("   cd laserflix_tkinter")
print("   copy app.py.backup app.py")
print("=" * 60)
