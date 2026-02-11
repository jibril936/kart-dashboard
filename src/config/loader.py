from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from src.core.types import AppConfig

DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or Path(os.environ.get("KART_CONFIG", DEFAULT_CONFIG_PATH))
    if not config_path.exists():
        config = AppConfig()
    else:
        raw = _read_yaml(config_path)
        alerts = raw.get("alerts", {})
        display = raw.get("display", {})
        demo = raw.get("demo", {})
        config = AppConfig(
            ui_hz=float(raw.get("ui_hz", 25.0)),
            data_hz=float(raw.get("data_hz", 30.0)),
            source=str(raw.get("source", "demo")).lower(),
            demo_scenario=str(demo.get("scenario", "normal")).lower(),
            fullscreen=bool(display.get("fullscreen", False)),
            debug=bool(display.get("debug", True)),
            stale_data_ms=int(alerts.get("stale_data_ms", 800)),
            speed_max_kph=float(display.get("speed_max_kph", 140.0)),
            rpm_max=float(display.get("rpm_max", 8500.0)),
            rpm_redline=float(display.get("rpm_redline", 7600.0)),
            battery_warning_v=float(alerts.get("battery_warning_v", 48.0)),
            battery_critical_v=float(alerts.get("battery_critical_v", 46.0)),
            temp_warning_c=float(alerts.get("temp_warning_c", 85.0)),
            temp_critical_c=float(alerts.get("temp_critical_c", 96.0)),
        )

    if os.environ.get("DEBUG") in {"1", "true", "True"}:
        config.debug = True
        config.fullscreen = False
    if os.environ.get("KART_DEMO_SCENARIO"):
        config.demo_scenario = os.environ["KART_DEMO_SCENARIO"].lower()
    return config


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
