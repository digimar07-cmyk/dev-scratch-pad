"""
Configuração de logging com rotação de arquivos
"""
import logging
from logging.handlers import RotatingFileHandler
from config.settings import LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT


def setup_logging():
    """
    Configura logger global com arquivo rotativo e console.
    Retorna instância do logger.
    """
    logger = logging.getLogger("Laserflix")
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Formato de mensagem
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    # Handler de arquivo com rotação
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    
    # Handler de console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger


# Instância global
LOGGER = setup_logging()
