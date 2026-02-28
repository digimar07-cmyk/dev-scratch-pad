#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laserflix v740 - Ponto de entrada (main)
Reproduz EXATAMENTE o comportamento do v740 original
"""

from laserflix.app import LaserflixApp

def main():
    """Reproduz o root = tk.Tk() + mainloop() do v740"""
    app = LaserflixApp()
    app.mainloop()

if __name__ == "__main__":
    main()
