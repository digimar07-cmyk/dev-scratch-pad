"""LASERFLIX v7.4.0 — Entry Point
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
