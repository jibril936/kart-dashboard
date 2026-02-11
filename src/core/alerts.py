from __future__ import annotations

from datetime import datetime

from src.core.types import Alert, AlertLevel, AppConfig, DashboardState, TelemetrySample


class AlertEngine:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def evaluate(self, sample: TelemetrySample, stale_ms: int, previous_history: list[Alert]) -> DashboardState:
        alerts: list[Alert] = []

        if sample.pack_voltage_v < self._config.battery_critical_v:
            alerts.append(self._alert(AlertLevel.CRITICAL, "BATTERY_CRITICAL", f"Battery very low ({sample.pack_voltage_v:.1f}V)", "Reduce load immediately"))
        elif sample.pack_voltage_v < self._config.battery_warning_v:
            alerts.append(self._alert(AlertLevel.WARNING, "BATTERY_LOW", f"Battery low ({sample.pack_voltage_v:.1f}V)", "Return to pit soon"))

        hottest = max(sample.motor_temp_c, sample.controller_temp_c, sample.battery_temp_c)
        if hottest >= self._config.temp_critical_c:
            alerts.append(self._alert(AlertLevel.CRITICAL, "TEMP_CRITICAL", f"High temp ({hottest:.1f}°C)", "Cool down drivetrain"))
        elif hottest >= self._config.temp_warning_c:
            alerts.append(self._alert(AlertLevel.WARNING, "TEMP_WARNING", f"Temp rising ({hottest:.1f}°C)", "Monitor thermal load"))

        if stale_ms > self._config.stale_data_ms:
            level = AlertLevel.CRITICAL if stale_ms > self._config.stale_data_ms * 2 else AlertLevel.WARNING
            alerts.append(self._alert(level, "DATA_STALE", f"Data stale ({stale_ms}ms)", "Check sensor link"))

        if sample.source_state.value != "OK":
            alerts.append(self._alert(AlertLevel.WARNING, "SOURCE_STATE", f"Source state: {sample.source_state.value}", "Inspect source"))

        history = previous_history + alerts
        history = history[-200:]
        return DashboardState(sample=sample, active_alerts=alerts, alert_history=history, stale_ms=stale_ms)

    @staticmethod
    def _alert(level: AlertLevel, code: str, message: str, action: str) -> Alert:
        return Alert(level=level, code=code, message=message, action=action, created_at=datetime.utcnow())
