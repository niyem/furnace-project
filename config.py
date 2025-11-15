import yaml, os

class Config:
    def __init__(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.cfg = yaml.safe_load(f)
        self._ensure_paths()

    def _ensure_paths(self):
        for key in ["outputs", "figures", "models", "reports"]:
            p = self.cfg.get("paths", {}).get(key)
            if p:
                os.makedirs(p, exist_ok=True)

    def get(self, *keys, default=None):
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
        return self.cfg[item]
