"""
LASERFLIX v3.0.0
Arquitetura modular — Entry point
"""
import tkinter as tk
from ui.main_window import LaserflixMainWindow

VERSION = "3.0.0"

def main():
    root = tk.Tk()
    app = LaserflixMainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
