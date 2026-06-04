from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
TEMPLATES_DIR = ROOT_DIR / "templates"
DB_PATH = DATA_DIR / "radar.sqlite"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_sources() -> dict[str, list[dict[str, Any]]]:
    return load_yaml(CONFIG_DIR / "sources.yaml")


def load_keywords() -> dict[str, list[str]]:
    data = load_yaml(CONFIG_DIR / "keywords.yaml")
    return {
        "include": [str(item).lower() for item in data.get("include", [])],
        "exclude": [str(item).lower() for item in data.get("exclude", [])],
    }


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
