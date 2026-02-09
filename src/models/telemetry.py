from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Telemetry:
    timestamp: datetime
    speed_kph: Optional[float]
    rpm: Optional[float]
    temp_c: Optional[float]
    battery_v: Optional[float]
    status: str = "OK"

    def formatted(self, value: Optional[float], unit: str, precision: int = 1) -> str:
        if value is None:
            return "—"
        return f"{value:.{precision}f} {unit}"
