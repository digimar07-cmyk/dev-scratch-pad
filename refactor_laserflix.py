#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Refatoração Automática do Laserflix v7.4.0
Execute este script UMA VEZ para dividir o código monolítico em módulos.

USO:
  python refactor_laserflix.py
"""

import os
import shutil
from pathlib import Path

# Caminho base
BASE_DIR = Path(__file__).parent
TARGET_DIR = BASE_DIR / "laserflix_tkinter"
SOURCE_FILE = BASE_DIR / "laserflix_v740_Ofline_Stable.py"

print("🚀 Laserflix Refactor Tool v1.0")
print("=" * 50)

if not SOURCE_FILE.exists():
    print(f"❌ ERRO: Arquivo fonte não encontrado: {SOURCE_FILE}")
    print("   Certifique-se de estar na pasta raiz do repositório.")
    exit(1)

print(f"✅ Arquivo fonte encontrado: {SOURCE_FILE.name}")
print(f"📁 Pasta destino: {TARGET_DIR}")

# Cria estrutura de pastas
print("\n📂 Criando estrutura de pastas...")
folders = [
    TARGET_DIR,
    TARGET_DIR / "core",
    TARGET_DIR / "ui",
    TARGET_DIR / "ui" / "sidebar",
    TARGET_DIR / "ui" / "project_grid",
    TARGET_DIR / "ui" / "modals",
    TARGET_DIR / "ui" / "dashboard",
    TARGET_DIR / "ui" / "menus",
    TARGET_DIR / "actions",
    TARGET_DIR / "utils",
    TARGET_DIR / "assets",
    TARGET_DIR / "data",
]

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)
    init_file = folder / "__init__.py"
    if not init_file.exists() and folder != TARGET_DIR and folder != TARGET_DIR / "assets" and folder != TARGET_DIR / "data":
        init_file.write_text('"""\n' + folder.name.capitalize() + ' module\n"""\n', encoding='utf-8')

print("✅ Estrutura de pastas criada!")

# Copia assets
print("\n🖼️  Copiando assets...")
assets_files = ["icon2.ico", "icon2.png", "Logo quadrado.jpg"]
for asset in assets_files:
    src = BASE_DIR / asset
    dst = TARGET_DIR / "assets" / asset
    if src.exists():
        shutil.copy2(src, dst)
        print(f"   ✓ {asset}")

print("\n📝 Criando arquivos principais...")

# main.py
(TARGET_DIR / "main.py").write_text(
'''"""LASERFLIX v7.4.0 — Entry Point
Ponto de entrada minimalista
"""

import tkinter as tk
import sys
import os

# Adiciona pasta raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from app import LaserflixNetflix

def main():
    root = tk.Tk()
    app = LaserflixNetflix(root)
    root.mainloop()

if __name__ == "__main__":
    main()
''', encoding='utf-8')
print("   ✓ main.py")

# Lê o arquivo original
print("\n📖 Lendo arquivo original...")
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    original_code = f.read()

print(f"   Tamanho: {len(original_code)} caracteres")

# Por enquanto, cria um app.py que importa tudo do monolito
print("\n⚙️  Criando app.py temporário (wrapper)...")
(TARGET_DIR / "app.py").write_text(
'''"""LASERFLIX v7.4.0 — Classe Principal
Wrapper temporário que usa o código original
"""

import sys
import os
from pathlib import Path

# Importa o código original
original_file = Path(__file__).parent.parent / "laserflix_v740_Ofline_Stable.py"
exec(open(original_file, encoding='utf-8').read(), globals())

# A classe LaserflixNetflix agora está disponível no namespace global
''', encoding='utf-8')
print("   ✓ app.py (wrapper)")

# requirements.txt
(TARGET_DIR / "requirements.txt").write_text(
'''# LASERFLIX v7.4.0 — Dependências

# Core
Pillow>=10.0.0
requests>=2.31.0

# Opcional (para exportação futura)
# reportlab>=4.0.0
# openpyxl>=3.1.0
''', encoding='utf-8')
print("   ✓ requirements.txt")

# README.md
(TARGET_DIR / "README.md").write_text(
'''# Laserflix v7.4.0 — Refatorado

## Como rodar

```bash
cd laserflix_tkinter
python main.py
```

## Estrutura

- `main.py` — Entry point
- `app.py` — Classe principal (temporariamente usando código original)
- `core/` — Módulos de lógica (em desenvolvimento)
- `ui/` — Componentes de interface (em desenvolvimento)
- `actions/` — Ações e filtros (em desenvolvimento)
- `utils/` — Utilitários (em desenvolvimento)

## Status

✅ Estrutura criada
⏳ Modularização em progresso
''', encoding='utf-8')
print("   ✓ README.md")

print("\n" + "=" * 50)
print("✅ REFATORAÇÃO CONCLUÍDA!")
print("\n📍 Para rodar o app:")
print(f"   cd {TARGET_DIR.name}")
print("   python main.py")
print("\n💡 O app está funcional usando o código original.")
print("   A modularização será feita incrementalmente.")
print("=" * 50)
