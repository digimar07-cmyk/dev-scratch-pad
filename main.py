#!/usr/bin/env python3
"""
LASERFLIX v7.4.0 — Stable (Modular)
Gerenciador de projetos de corte laser com IA

Entry point principal
"""

import tkinter as tk
import logging
from logging.handlers import RotatingFileHandler

from laserflix.core.app import LaserflixApp


def setup_logging():
    """Configura logging global"""
    logger = logging.getLogger("Laserflix")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler = RotatingFileHandler(
        "laserflix.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def main():
    """Entry point principal"""
    setup_logging()
    root = tk.Tk()
    app = LaserflixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
