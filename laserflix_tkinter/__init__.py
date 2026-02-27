"""LASERFLIX - Netflix-style project manager for laser cutting designs.

Modular architecture following Fowler/Beck refactoring principles:
- config: Centralized settings and configuration
- models: Data models (Project, DatabaseManager)
- services: Business logic (Ollama, Image, Analysis)
- ui: User interface components
- utils: Utility functions
"""
import logging
from logging.handlers import RotatingFileHandler

__version__ = "7.4.0"
__app_name__ = "LASERFLIX"


def setup_logging():
    """Setup application logging."""
    logger = logging.getLogger("Laserflix")
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        "laserflix.log", 
        maxBytes=5 * 1024 * 1024,
        backupCount=3, 
        encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    
    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger


__all__ = ["__version__", "__app_name__", "setup_logging"]
