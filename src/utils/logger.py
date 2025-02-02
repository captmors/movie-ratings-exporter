import sys
from loguru import logger
from src.config import LOG_DIR


def setup_logger(log_file='app.log') -> None:
    logger.remove()
    logger.add(LOG_DIR / log_file, rotation="1 MB", level="INFO", backtrace=True, diagnose=True)
    logger.add(sys.stderr, level="DEBUG", backtrace=True, diagnose=True)
