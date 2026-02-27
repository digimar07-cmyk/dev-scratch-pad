"""LASERFLIX v7.4.0 — Entry Point
Ponto de entrada minimalista
"""

import tkinter as tk
from app import LaserflixNetflix


def main():
    root = tk.Tk()
    app = LaserflixNetflix(root)
    root.mainloop()


if __name__ == "__main__":
    main()
