"""
Configuration management module for the furnace efficiency ML pipeline.

This module provides a configuration class that loads and manages settings
from a YAML configuration file, with automatic directory creation and
flexible key access patterns.
"""

import yaml
import os


class Config:
    """
    Configuration loader and manager for the ML pipeline.

    This class loads configuration from a YAML file and provides convenient
    access methods with automatic directory creation for output paths.

    Parameters
    ----------
    path : str
        Path to the YAML configuration file.

    Attributes
    ----------
    cfg : dict
        Loaded configuration dictionary.

    Examples
    --------
    >>> config = Config('config.yaml')
    >>> data_path = config.get('data', 'path')
    >>> test_size = config.get('regression', 'test_size', default=0.2)
    """

    def __init__(self, path: str):
        """
        Initialize configuration from YAML file.

        Parameters
        ----------
        path : str
            Path to the YAML configuration file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            self.cfg = yaml.safe_load(f)
        self._ensure_paths()

    def _ensure_paths(self):
        """
        Create all output directories specified in the configuration.

        Checks for 'outputs', 'figures', 'models', and 'reports' paths
        and creates them if they don't exist.
        """
        for key in ["outputs", "figures", "models", "reports"]:
            p = self.cfg.get("paths", {}).get(key)
            if p:
                os.makedirs(p, exist_ok=True)

    def get(self, *keys, default=None):
        """
        Get a configuration value by nested keys.

        Supports flexible key access patterns:
        - get("a", "b") for nested keys
        - get(["a", "b"]) for list/tuple of keys
        - get("a", "b", default=value) for default values

        Parameters
        ----------
        *keys : str or list/tuple
            Sequence of keys to navigate the configuration.
        default : any, optional
            Default value if key path doesn't exist.

        Returns
        -------
        any
            Configuration value at the specified key path, or default.

        Examples
        --------
        >>> config.get('data', 'path')
        'ml_ready_data.csv'
        >>> config.get('regression', 'test_size', default=0.2)
        0.2
        """
        # Support either get("a", "b") or get(("a","b")) or get(["a","b"])
        if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
            keys = tuple(keys[0])
        node = self.cfg
        for k in keys:
            if not isinstance(node, dict):
                return default
            if k not in node:
                return default
            node = node[k]
        return node

    def __getitem__(self, item):
        """
        Dictionary-style access to top-level configuration keys.

        Parameters
        ----------
        item : str
            Top-level configuration key.

        Returns
        -------
        any
            Configuration value.
        """
        return self.cfg[item]
