"""
LASERFLIX v7.4.0 — Modular
Entry point
"""

import tkinter as tk
from core.app import LaserflixNetflix


def main():
    root = tk.Tk()
    app = LaserflixNetflix(root)
    root.mainloop()


if __name__ == "__main__":
    main()
