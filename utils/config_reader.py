import json
import os

_config = None


def get_config(key: str):
    global _config
    if _config is None:
        env = os.getenv("ENV", "local")
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", f"{env}.json")
        with open(os.path.normpath(config_path)) as f:
            _config = json.load(f)
    return _config.get(key)
