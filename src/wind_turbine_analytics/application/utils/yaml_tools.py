import yaml
from typing import Any, Dict
from pathlib import Path


def build_client_config_from_scada_yaml(root: Path) -> Dict[str, Any]:
    config_path = root / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Expected config.yml in {root}, but not found.")
    with open(config_path, "r", encoding="utf-8") as f:
        docs = yaml.safe_load(f)
    if not isinstance(docs, dict):
        raise ValueError(
            "Invalid config.yml format: expected a YAML mapping at the root."
        )
    return docs
