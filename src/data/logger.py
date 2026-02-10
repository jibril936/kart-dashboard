from __future__ import annotations

import csv
from pathlib import Path

from src.models.telemetry import Telemetry


class TelemetryLogger:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        if self._file.tell() == 0:
            self._writer.writerow(
                [
                    "timestamp",
                    "speed_kph",
                    "soc_percent",
                    "pack_voltage_v",
                    "pack_current_a",
                    "pack_power_kw",
                    "motor_temp_c",
                    "inverter_temp_c",
                    "battery_temp_c",
                    "motor_rpm",
                    "throttle_percent",
                    "brake_percent",
                    "source_state",
                    "alerts",
                ]
            )

    def log(self, telemetry: Telemetry) -> None:
        self._writer.writerow(
            [
                telemetry.timestamp.isoformat(),
                telemetry.speed_kph,
                telemetry.soc_percent,
                telemetry.pack_voltage_v,
                telemetry.pack_current_a,
                telemetry.pack_power_kw,
                telemetry.motor_temp_c,
                telemetry.inverter_temp_c,
                telemetry.battery_temp_c,
                telemetry.motor_rpm,
                telemetry.throttle_percent,
                telemetry.brake_percent,
                telemetry.source_state.value,
                " | ".join(telemetry.alerts),
            ]
        )
        self._file.flush()

    def close(self) -> None:
        self._file.close()
