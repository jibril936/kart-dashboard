from __future__ import annotations

from dataclasses import replace

from PyQt6.QtCore import QObject, pyqtSignal

from src.config.loader import AlertThresholds
from src.models.telemetry import SourceState, Telemetry


class TelemetryModel(QObject):
    telemetry_updated = pyqtSignal(Telemetry)

    def __init__(self, thresholds: AlertThresholds) -> None:
        super().__init__()
        self._thresholds = thresholds

    def process(self, telemetry: Telemetry) -> None:
        alerts = list(telemetry.alerts)

        if telemetry.soc_percent is not None and telemetry.soc_percent <= self._thresholds.low_soc_percent:
            alerts.append(f"SOC low ({telemetry.soc_percent:.0f}%)")
        if telemetry.motor_temp_c is not None and telemetry.motor_temp_c >= self._thresholds.high_motor_temp_c:
            alerts.append(f"Motor temp high ({telemetry.motor_temp_c:.1f}°C)")
        if telemetry.inverter_temp_c is not None and telemetry.inverter_temp_c >= self._thresholds.high_inverter_temp_c:
            alerts.append(f"Inverter temp high ({telemetry.inverter_temp_c:.1f}°C)")
        if telemetry.battery_temp_c is not None and telemetry.battery_temp_c >= self._thresholds.high_battery_temp_c:
            alerts.append(f"Battery temp high ({telemetry.battery_temp_c:.1f}°C)")

        if telemetry.source_state in {SourceState.ERROR, SourceState.TIMEOUT} and not alerts:
            alerts.append(f"Source state: {telemetry.source_state.value}")

        self.telemetry_updated.emit(replace(telemetry, alerts=alerts))
