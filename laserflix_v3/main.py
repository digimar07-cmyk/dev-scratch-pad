"""
LASERFLIX v3.0 — Ponto de entrada
Chamada única para manter compatibilidade com v7.4.0
"""

import tkinter as tk
from core.app import LaserflixApp

def main():
    root = tk.Tk()
    app = LaserflixApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
