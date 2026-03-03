"""
LASERFLIX v3.0
Entry point - Usa main_window_FIXED (layout exato v740)
"""
import tkinter as tk
import sys
import os

# Adiciona pasta raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window_FIXED import LaserflixMainWindow
from utils.logging_setup import LOGGER


def main():
    """Ponto de entrada."""
    try:
        root = tk.Tk()
        app = LaserflixMainWindow(root)
        root.mainloop()
    except Exception as e:
        LOGGER.exception("Erro fatal: %s", e)
        input("\nPressione Enter para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()
