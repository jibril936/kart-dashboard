from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import os

import yaml


@dataclass
class I2CConfig:
    bus: int = 1
    address: int = 0x10


@dataclass
class LoggingConfig:
    enabled: bool = False
    path: str = "logs/telemetry.csv"


@dataclass
class AppConfig:
    source: str = "simulated"
    refresh_hz: float = 10.0
    fullscreen: bool = True
    debug: bool = False
    i2c: I2CConfig = field(default_factory=I2CConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or Path(os.environ.get("KART_CONFIG", DEFAULT_CONFIG_PATH))
    debug_env = os.environ.get("DEBUG")
    if not config_path.exists():
        config = AppConfig()
    else:
        raw: Dict[str, Any]
        with config_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}

        i2c_raw = raw.get("i2c", {})
        logging_raw = raw.get("logging", {})

        config = AppConfig(
            source=raw.get("source", "simulated"),
            refresh_hz=float(raw.get("refresh_hz", 10.0)),
            fullscreen=bool(raw.get("fullscreen", True)),
            debug=bool(raw.get("debug", False)),
            i2c=I2CConfig(
                bus=int(i2c_raw.get("bus", 1)),
                address=int(i2c_raw.get("address", 0x10)),
            ),
            logging=LoggingConfig(
                enabled=bool(logging_raw.get("enabled", False)),
                path=str(logging_raw.get("path", "logs/telemetry.csv")),
            ),
        )

    if debug_env and debug_env != "0":
        config.debug = True
        config.fullscreen = False

    return config
