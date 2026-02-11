from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SourceState(str, Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class Alert:
    level: AlertLevel
    code: str
    message: str
    action: str
    created_at: datetime


@dataclass(slots=True)
class TelemetrySample:
    timestamp: datetime
    speed_kph: float = 0.0
    motor_rpm: float = 0.0
    soc_percent: float = 100.0
    pack_voltage_v: float = 52.0
    pack_current_a: float = 0.0
    motor_temp_c: float = 45.0
    controller_temp_c: float = 42.0
    battery_temp_c: float = 35.0
    source_state: SourceState = SourceState.OK

    @property
    def pack_power_kw(self) -> float:
        return (self.pack_voltage_v * self.pack_current_a) / 1000.0

    @property
    def estimated_range_km(self) -> float:
        return max(0.0, (self.soc_percent / 100.0) * 80.0)


@dataclass(slots=True)
class DashboardState:
    sample: TelemetrySample
    active_alerts: list[Alert] = field(default_factory=list)
    alert_history: list[Alert] = field(default_factory=list)
    stale_ms: int = 0


@dataclass(slots=True)
class RollingStats:
    min_value: float
    max_value: float
    avg_value: float


@dataclass(slots=True)
class AppConfig:
    ui_hz: float = 25.0
    data_hz: float = 30.0
    source: str = "demo"
    demo_scenario: str = "normal"
    fullscreen: bool = False
    debug: bool = True
    stale_data_ms: int = 800
    speed_max_kph: float = 140.0
    rpm_max: float = 8500.0
    rpm_redline: float = 7600.0
    battery_warning_v: float = 48.0
    battery_critical_v: float = 46.0
    temp_warning_c: float = 85.0
    temp_critical_c: float = 96.0
