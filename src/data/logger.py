from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from src.models.telemetry import Telemetry


class TelemetryLogger:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        if self._file.tell() == 0:
            self._writer.writerow(["timestamp", "speed_kph", "rpm", "temp_c", "battery_v", "status"])

    def log(self, telemetry: Telemetry) -> None:
        self._writer.writerow(
            [
                telemetry.timestamp.isoformat(),
                telemetry.speed_kph,
                telemetry.rpm,
                telemetry.temp_c,
                telemetry.battery_v,
                telemetry.status,
            ]
        )
        self._file.flush()

    def close(self) -> None:
        self._file.close()
