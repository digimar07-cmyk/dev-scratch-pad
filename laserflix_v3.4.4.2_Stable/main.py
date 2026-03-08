"""
LASERFLIX v3.3
Entry point
"""
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import LaserflixMainWindow
from utils.logging_setup import LOGGER


def main():
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
