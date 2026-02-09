from __future__ import annotations

import math
import random
import time
from datetime import datetime

from src.data.sources.base import DataSource
from src.models.telemetry import Telemetry


class SimulatedSource(DataSource):
    """Source simulée pour développement sans matériel."""

    def __init__(self) -> None:
        self._start_time = time.monotonic()

    def read(self) -> Telemetry:
        elapsed = time.monotonic() - self._start_time
        speed = 40 + 20 * math.sin(elapsed / 3.0) + random.uniform(-2, 2)
        rpm = 3500 + 1200 * math.sin(elapsed / 2.0) + random.uniform(-150, 150)
        temp = 65 + 10 * math.sin(elapsed / 6.0) + random.uniform(-1, 1)
        battery = 12.6 - 0.01 * elapsed + random.uniform(-0.05, 0.05)
        return Telemetry(
            timestamp=datetime.utcnow(),
            speed_kph=max(speed, 0.0),
            rpm=max(rpm, 0.0),
            temp_c=temp,
            battery_v=max(battery, 0.0),
            status="OK",
        )
