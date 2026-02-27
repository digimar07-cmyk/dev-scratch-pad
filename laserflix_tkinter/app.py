"""LASERFLIX v7.4.0 — Classe Principal
Wrapper temporário que usa o código original
"""

import sys
import os
from pathlib import Path

# Importa o código original
original_file = Path(__file__).parent.parent / "laserflix_v740_Ofline_Stable.py"
exec(open(original_file, encoding='utf-8').read(), globals())

# A classe LaserflixNetflix agora está disponível no namespace global
