import logging, os, sys
from datetime import datetime

def get_logger(name: str = "furnace"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger

def save_json(obj, path):
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
