import logging
from datetime import datetime
import sys

def get_logger(name="ingest"):
    logger = logging.getLogger(name)
    logger.propagate = False  # prevent duplicate logs
    if not logger.handlers:
        # File Handler
        file_handler = logging.FileHandler(f"logs_{datetime.now().date()}.log")
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # Console Handler for Docker logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

    return logger
