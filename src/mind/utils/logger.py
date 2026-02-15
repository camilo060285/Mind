import logging

from mind.config.settings import Settings


def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(Settings.LOG_LEVEL)
        logger.addHandler(handler)
    logger.setLevel(Settings.LOG_LEVEL)
    logger.propagate = False
    return logger
