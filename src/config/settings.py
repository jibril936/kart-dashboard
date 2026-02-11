from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class AppSettings:
    ui_hz: int = 25



def load_settings(path: str = "config/config.yaml") -> AppSettings:
    p = Path(path)
    if not p.exists():
        return AppSettings()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return AppSettings(ui_hz=int(raw.get("ui_hz", 25)))
