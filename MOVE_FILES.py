#!/usr/bin/env python3
"""
Script temporário para mover arquivos de laserflix/* para raiz
"""

import os
import shutil
from pathlib import Path

def move_structure():
    base = Path('.')
    laserflix = base / 'laserflix'
    
    if not laserflix.exists():
        print('Pasta laserflix não encontrada!')
        return
    
    # Move cada subpasta
    for folder in ['core', 'ollama', 'media', 'ui', 'workers']:
        src = laserflix / folder
        dst = base / folder
        
        if src.exists():
            print(f'Movendo {src} → {dst}')
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(src), str(dst))
    
    # Remove pasta laserflix vazia
    if laserflix.exists():
        shutil.rmtree(laserflix)
        print('Pasta laserflix removida')
    
    print('✅ Estrutura reorganizada!')

if __name__ == '__main__':
    move_structure()
