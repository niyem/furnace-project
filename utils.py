"""
Utility functions for the furnace efficiency ML pipeline.

This module provides common utilities including logging setup and JSON serialization.
"""

import logging
import os
import sys
import json
from datetime import datetime


def get_logger(name: str = "furnace") -> logging.Logger:
    """
    Get or create a logger with consistent formatting.

    Creates a logger with INFO level and timestamp formatting. If the logger
    already exists with handlers, returns the existing logger to avoid
    duplicate log messages.

    Parameters
    ----------
    name : str, optional
        Logger name, by default "furnace".

    Returns
    -------
    logging.Logger
        Configured logger instance.

    Examples
    --------
    >>> logger = get_logger("my_module")
    >>> logger.info("Processing data...")
    [2025-11-16 10:30:45] INFO - Processing data...
    """
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


def save_json(obj: dict, path: str) -> None:
    """
    Save a Python object to a JSON file with pretty formatting.

    Parameters
    ----------
    obj : dict
        Object to serialize (must be JSON-serializable).
    path : str
        Output file path.

    Examples
    --------
    >>> results = {'r2': 0.95, 'mae': 0.02}
    >>> save_json(results, 'outputs/results.json')
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
