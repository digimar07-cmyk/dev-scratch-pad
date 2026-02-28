#!/usr/bin/env python3
"""
Script para corrigir imports relativos depois de mover para raiz
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Corrige imports em um arquivo Python"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Substitui imports relativos
    # from ..ollama import X -> from ollama import X
    content = re.sub(r'from \.\.\.?(\w+)', r'from \1', content)
    # from .database import X -> from core.database import X (dentro de core/)
    if 'core' in str(filepath) and 'from .' in content:
        content = re.sub(r'from \.(\w+)', r'from core.\1', content)
    elif 'ollama' in str(filepath) and 'from .' in content:
        content = re.sub(r'from \.(\w+)', r'from ollama.\1', content)
    elif 'media' in str(filepath) and 'from .' in content:
        content = re.sub(r'from \.(\w+)', r'from media.\1', content)
    elif 'ui' in str(filepath) and 'from .' in content:
        content = re.sub(r'from \.(\w+)', r'from ui.\1', content)
    elif 'workers' in str(filepath) and 'from .' in content:
        content = re.sub(r'from \.(\w+)', r'from workers.\1', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ Corrigido: {filepath}')
        return True
    return False

def main():
    base = Path('.')
    fixed = 0
    
    for folder in ['core', 'ollama', 'media', 'ui', 'workers']:
        folder_path = base / folder
        if not folder_path.exists():
            continue
        
        for pyfile in folder_path.glob('*.py'):
            if pyfile.name == '__init__.py':
                continue
            if fix_imports_in_file(pyfile):
                fixed += 1
    
    print(f'\n✅ {fixed} arquivos corrigidos!')

if __name__ == '__main__':
    main()
