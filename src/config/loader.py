from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import os

import yaml


@dataclass(slots=True)
class I2CConfig:
    bus: int = 1
    address: int = 0x10


@dataclass(slots=True)
class LoggingConfig:
    enabled: bool = False
    path: str = "logs/telemetry.csv"


@dataclass(slots=True)
class AlertThresholds:
    low_soc_percent: float = 20.0
    high_motor_temp_c: float = 95.0
    high_inverter_temp_c: float = 85.0
    high_battery_temp_c: float = 60.0


@dataclass(slots=True)
class AppConfig:
    source: str = "simulated"
    refresh_hz: float = 20.0
    fullscreen: bool = True
    debug: bool = False
    i2c: I2CConfig = field(default_factory=I2CConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    alerts: AlertThresholds = field(default_factory=AlertThresholds)


DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or Path(os.environ.get("KART_CONFIG", DEFAULT_CONFIG_PATH))
    debug_env = os.environ.get("DEBUG")

    if not config_path.exists():
        config = AppConfig()
    else:
        with config_path.open("r", encoding="utf-8") as handle:
            raw: dict[str, Any] = yaml.safe_load(handle) or {}

        i2c_raw = raw.get("i2c", {})
        logging_raw = raw.get("logging", {})
        alerts_raw = raw.get("alerts", {})

        config = AppConfig(
            source=str(raw.get("source", "simulated")).strip().lower(),
            refresh_hz=float(raw.get("refresh_hz", 20.0)),
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
            alerts=AlertThresholds(
                low_soc_percent=float(alerts_raw.get("low_soc_percent", 20.0)),
                high_motor_temp_c=float(alerts_raw.get("high_motor_temp_c", 95.0)),
                high_inverter_temp_c=float(alerts_raw.get("high_inverter_temp_c", 85.0)),
                high_battery_temp_c=float(alerts_raw.get("high_battery_temp_c", 60.0)),
            ),
        )

    if debug_env and debug_env != "0":
        config.debug = True
        config.fullscreen = False

    return config
