from __future__ import annotations

from src.core.types import AppConfig, DashboardState
from src.qt_compat import ALIGN_CENTER, FONT_BOLD, QFont, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, pyqtSignal
from src.ui.components import AlertBanner, BatteryWidget, GaugeNeedle, TempCard


class DriveScreen(QWidget):
    details_requested = pyqtSignal()

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        self._alert_banner = AlertBanner()
        root.addWidget(self._alert_banner)

        center = QHBoxLayout()
        speed_wrap = QVBoxLayout()
        self._speed = QLabel("0")
        self._speed.setFont(QFont("Inter", 112, FONT_BOLD))
        self._speed.setAlignment(ALIGN_CENTER)
        self._unit = QLabel("km/h")
        self._unit.setAlignment(ALIGN_CENTER)
        self._unit.setProperty("kpi", True)
        speed_wrap.addWidget(self._speed)
        speed_wrap.addWidget(self._unit)

        self._rpm_gauge = GaugeNeedle(0, config.rpm_max, config.rpm_redline)

        center.addLayout(speed_wrap, 2)
        center.addWidget(self._rpm_gauge, 3)
        root.addLayout(center)

        metrics = QGridLayout()
        self._battery = BatteryWidget()
        self._temp_motor = TempCard("Motor")
        self._temp_controller = TempCard("Controller")
        self._temp_battery = TempCard("Battery")
        metrics.addWidget(self._battery, 0, 0)
        metrics.addWidget(self._temp_motor, 0, 1)
        metrics.addWidget(self._temp_controller, 1, 0)
        metrics.addWidget(self._temp_battery, 1, 1)
        root.addLayout(metrics)

        controls = QHBoxLayout()
        controls.addStretch(1)
        btn = QPushButton("Details / Pit")
        btn.setMinimumHeight(52)
        btn.clicked.connect(self.details_requested.emit)
        controls.addWidget(btn)
        root.addLayout(controls)

    def render(self, state: DashboardState) -> None:
        s = state.sample
        self._speed.setText(f"{s.speed_kph:.0f}")
        self._rpm_gauge.set_value(s.motor_rpm)
        self._battery.update_values(s.soc_percent, s.pack_voltage_v, s.estimated_range_km)
        self._temp_motor.set_temp(s.motor_temp_c)
        self._temp_controller.set_temp(s.controller_temp_c)
        self._temp_battery.set_temp(s.battery_temp_c)
        self._alert_banner.update_alerts(state.active_alerts)
