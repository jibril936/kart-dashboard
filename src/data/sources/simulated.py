from __future__ import annotations

import math
import random
import time
from datetime import datetime

from src.data.sources.base import DataSource
from src.models.telemetry import SourceState, Telemetry


class SimulatedDataSource(DataSource):
    """Hardware-free telemetry generator with realistic-ish pack dynamics."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._soc = 96.0
        self._last_t = self._start
        self._startup_alert: str | None = None

    def inject_startup_alert(self, message: str) -> None:
        self._startup_alert = message

    def read(self) -> Telemetry:
        now = time.monotonic()
        elapsed = now - self._start
        dt = max(now - self._last_t, 0.001)
        self._last_t = now

        throttle = max(0.0, min(100.0, 48 + 44 * math.sin(elapsed / 4.2) + random.uniform(-8, 8)))
        brake = max(0.0, min(100.0, 8 + 12 * math.sin(elapsed / 6.5 + 1.0) + random.uniform(-4, 4)))

        speed = max(0.0, 0.95 * throttle - 0.55 * brake + 38 + 14 * math.sin(elapsed / 8.0) + random.uniform(-2, 2))
        rpm = max(0.0, speed * 95 + random.uniform(-120, 120))

        current = max(-30.0, 0.9 * throttle - 0.6 * brake + random.uniform(-6, 6))
        voltage = max(44.0, 54.6 - (100 - self._soc) * 0.06 + random.uniform(-0.3, 0.3))
        power_kw = (voltage * current) / 1000

        self._soc = max(0.0, self._soc - max(current, 0.0) * dt * 0.00045)

        battery_temp = 29 + 0.06 * max(current, 0) + 4 * math.sin(elapsed / 25) + random.uniform(-0.4, 0.4)
        motor_temp = 45 + 0.13 * max(current, 0) + 7 * math.sin(elapsed / 18) + random.uniform(-0.8, 0.8)
        inverter_temp = 40 + 0.1 * max(current, 0) + 5 * math.sin(elapsed / 20) + random.uniform(-0.8, 0.8)

        alerts: list[str] = []
        if self._startup_alert:
            alerts.append(self._startup_alert)
            self._startup_alert = None

        return Telemetry(
            timestamp=datetime.utcnow(),
            speed_kph=speed,
            soc_percent=self._soc,
            pack_voltage_v=voltage,
            pack_current_a=current,
            pack_power_kw=power_kw,
            motor_temp_c=motor_temp,
            inverter_temp_c=inverter_temp,
            battery_temp_c=battery_temp,
            motor_rpm=rpm,
            throttle_percent=throttle,
            brake_percent=brake,
            source_state=SourceState.OK,
            alerts=alerts,
        )
