from __future__ import annotations

import math
import random
import time
from datetime import datetime

from src.core.types import SourceState, TelemetrySample
from src.services.base import DataService


class FakeDataService(DataService):
    def __init__(self, scenario: str = "normal") -> None:
        self._scenario = scenario
        self._start = time.monotonic()
        self._last = self._start
        self._soc = 93.0
        self._voltage = 52.2

    def read(self) -> TelemetrySample:
        now = time.monotonic()
        t = now - self._start
        dt = max(0.01, now - self._last)
        self._last = now

        speed = max(0.0, 65 + 20 * math.sin(t * 0.8) + random.uniform(-2, 2))
        rpm = max(800.0, speed * 85 + random.uniform(-120, 120))
        current = 15 + speed * 1.8 + random.uniform(-4, 4)
        motor_temp = 56 + speed * 0.12 + 4 * math.sin(t * 0.15)
        controller_temp = 51 + speed * 0.09 + 3 * math.sin(t * 0.17 + 0.4)
        battery_temp = 43 + speed * 0.05 + 2 * math.sin(t * 0.08 + 0.2)
        source_state = SourceState.OK

        if self._scenario == "acceleration":
            speed = min(128.0, 25 + t * 7.2)
            rpm = min(8450, 1000 + speed * 90)
            current += 40
        elif self._scenario == "battery_drop":
            self._voltage -= 0.03 * dt
            self._soc -= 0.07 * dt
        elif self._scenario == "overheat":
            motor_temp += 28
            controller_temp += 24
            battery_temp += 17
        elif self._scenario == "sensor_ko":
            source_state = SourceState.TIMEOUT if int(t) % 4 < 2 else SourceState.OK
            if source_state == SourceState.TIMEOUT:
                current = 0.0

        self._soc = max(2.0, self._soc - (speed / 40000.0))
        self._voltage = min(self._voltage, 45.0 + self._soc * 0.08)

        return TelemetrySample(
            timestamp=datetime.utcnow(),
            speed_kph=speed,
            motor_rpm=rpm,
            soc_percent=self._soc,
            pack_voltage_v=self._voltage,
            pack_current_a=current,
            motor_temp_c=motor_temp,
            controller_temp_c=controller_temp,
            battery_temp_c=battery_temp,
            source_state=source_state,
        )
