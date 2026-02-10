from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SourceState(str, Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass(slots=True)
class Telemetry:
    timestamp: datetime
    speed_kph: float | None = None
    soc_percent: float | None = None
    pack_voltage_v: float | None = None
    pack_current_a: float | None = None
    pack_power_kw: float | None = None
    motor_temp_c: float | None = None
    inverter_temp_c: float | None = None
    battery_temp_c: float | None = None
    motor_rpm: float | None = None
    throttle_percent: float | None = None
    brake_percent: float | None = None
    source_state: SourceState = SourceState.OK
    alerts: list[str] = field(default_factory=list)

    @staticmethod
    def format_value(value: float | None, unit: str, precision: int = 1) -> str:
        if value is None:
            return "—"
        return f"{value:.{precision}f} {unit}"
