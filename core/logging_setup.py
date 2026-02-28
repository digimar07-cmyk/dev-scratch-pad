"""Setup de logging."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Configura sistema de logs."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger("laserflix")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = RotatingFileHandler(
            os.path.join(log_dir, "laserflix.log"),
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
