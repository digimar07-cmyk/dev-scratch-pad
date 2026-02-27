#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Refatoração do app.py
Extrai a classe LaserflixNetflix do monolito para app.py modular

USO:
  python refactor_app_py.py
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
TARGET_DIR = BASE_DIR / "laserflix_tkinter"
SOURCE_FILE = BASE_DIR / "laserflix_v740_Ofline_Stable.py"
APP_FILE = TARGET_DIR / "app.py"

print("🚀 Refactor app.py Tool v1.0")
print("=" * 50)

if not SOURCE_FILE.exists():
    print(f"❌ ERRO: Arquivo fonte não encontrado: {SOURCE_FILE}")
    exit(1)

if not TARGET_DIR.exists():
    print(f"❌ ERRO: Pasta laserflix_tkinter não existe. Execute refactor_laserflix.py primeiro.")
    exit(1)

print(f"✅ Lendo arquivo fonte: {SOURCE_FILE.name}")

with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    original_code = f.read()

print(f"   Tamanho: {len(original_code)} caracteres")

# Extrai a classe LaserflixNetflix completa
print("\n🔍 Extraindo classe LaserflixNetflix...")

# Padrão: da definição da classe até o próximo 'if __name__' ou fim do arquivo
class_match = re.search(
    r'(class LaserflixNetflix:.*?)(?=\nif __name__|\Z)',
    original_code,
    re.DOTALL
)

if not class_match:
    print("❌ ERRO: Não foi possível encontrar a classe LaserflixNetflix")
    exit(1)

class_code = class_match.group(1)
print(f"✅ Classe extraída: {len(class_code)} caracteres")

# Identifica imports necessários
print("\n📦 Identificando imports...")
import_section = re.search(r'^(import .*?\n\n)', original_code, re.MULTILINE | re.DOTALL)
if import_section:
    imports = import_section.group(1)
else:
    imports = ""

print(f"   Imports encontrados: {len(imports.split('\n'))-1} linhas")

# Cria novo app.py
print("\n✏️  Criando novo app.py...")

new_app_content = '''"""LASERFLIX v7.4.0 — Classe Principal
Classe LaserflixNetflix extraída e adaptada para estrutura modular
"""

''' + imports + '''
# Importa módulos core (quando estiverem prontos para uso)
# from core.database_manager import DatabaseManager
# from core.backup_manager import BackupManager
# from core.config_manager import ConfigManager
# from core.ollama_client import OllamaClient
# from core.ollama_text import OllamaTextGenerator
# from core.ollama_vision import OllamaVision
# from core.ai_analyzer import AIAnalyzer
# from core.ai_description import AIDescriptionGenerator

''' + class_code

# Salva backup do app.py antigo
if APP_FILE.exists():
    backup_file = TARGET_DIR / "app.py.backup"
    print(f"   💾 Backup: {backup_file.name}")
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        old_content = f.read()
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(old_content)

# Salva novo app.py
with open(APP_FILE, 'w', encoding='utf-8') as f:
    f.write(new_app_content)

print(f"\n✅ Novo app.py criado: {APP_FILE}")
print(f"   Linhas: {len(new_app_content.split(chr(10)))}")

print("\n" + "=" * 50)
print("✅ REFATORAÇÃO CONCLUÍDA!")
print("\n📍 Para testar:")
print(f"   cd {TARGET_DIR.name}")
print("   python main.py")
print("\n⚠️  IMPORTANTE:")
print("   O app.py agora contém a classe completa extraída.")
print("   Se der erro, use: app.py.backup para restaurar.")
print("=" * 50)
