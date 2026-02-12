from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBar, CenterPanel, CircularGauge, IndicatorRow, IndicatorSpec

MAX_SPEED_KMH = 200
MAX_RPM = 8000
SPEED_MAJOR_TICK = 20
RPM_MAJOR_TICK = 1000


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 12)
        root.setSpacing(8)

        self.indicators = IndicatorRow(
            [
                IndicatorSpec("battery_low", "battery", "BATT", active_color="#ffb347"),
                IndicatorSpec("overheat", "temp", "TEMP", active_color="#ff6d64"),
                IndicatorSpec("charging", "charging", "CHG", active_color="#5ea9ff"),
                IndicatorSpec("brake", "brake", "BRAKE", active_color="#ff6d64"),
                IndicatorSpec("steering", "steer", "STEER", active_color="#ffb347"),
                IndicatorSpec("station", "station", "EVSE", active_color="#6da8ff"),
                IndicatorSpec("rpm_high", "rpm", "RPM", active_color="#ffb347"),
                IndicatorSpec("speed_high", "speed", "SPEED", active_color="#ffb347"),
                IndicatorSpec("sensor", "sensor", "SENS", active_color="#ff6d64"),
                IndicatorSpec("ready", "ready", "READY", active_color="#63c6a8"),
            ]
        )
        root.addWidget(self.indicators)

        middle = QHBoxLayout()
        middle.setSpacing(16)

        self.speed_gauge = CircularGauge(
            "SPEED",
            "km/h",
            0,
            MAX_SPEED_KMH,
            warning_value=120,
            critical_value=160,
            red_zone_start=170,
            major_tick_step=SPEED_MAJOR_TICK,
            minor_ticks_per_major=1,
            label_formatter=lambda v: f"{int(v):d}",
        )
        self.center_panel = CenterPanel()
        self.rpm_gauge = CircularGauge(
            "RPM",
            "x1000",
            0,
            MAX_RPM,
            warning_value=6200,
            critical_value=7200,
            red_zone_start=6500,
            major_tick_step=RPM_MAJOR_TICK,
            minor_ticks_per_major=1,
            label_formatter=lambda v: f"{max(0, int(v // 1000))}",
        )

        middle.addWidget(self.speed_gauge, 1)
        middle.addWidget(self.center_panel, 1)
        middle.addWidget(self.rpm_gauge, 1)
        root.addLayout(middle, 1)

        self.bottom_bar = BottomBar()
        root.addWidget(self.bottom_bar)

        nav = QHBoxLayout()
        nav.addStretch(1)
        self.tech_button = QPushButton("TECH")
        self.tech_button.setObjectName("NavButton")
        self.tech_button.clicked.connect(self.tech_requested.emit)
        nav.addWidget(self.tech_button)
        root.addLayout(nav)

    def render(self, state: VehicleTechState) -> None:
        self.speed_gauge.set_value(state.speed_kmh)
        self.rpm_gauge.set_value(float(state.rpm))
        self.center_panel.set_state(state.steering_angle_deg, mode="CHARGE" if state.charging_state else "SPORT")

        battery_pct = (state.battery_voltage_V - 42.0) / 12.0 * 100.0
        power_ratio = min(1.0, max(0.0, state.speed_kmh / 120.0))
        regen_ratio = min(1.0, max(0.0, state.brake_state / 25.0))
        self.bottom_bar.set_values(state.battery_voltage_V, battery_pct, power_ratio, regen_ratio, state.motor_temp_C)

        indicators = {
            "battery_low": state.battery_voltage_V < 48,
            "overheat": state.motor_temp_C >= 85,
            "charging": state.charging_state,
            "brake": state.brake_state > 10,
            "steering": abs(state.steering_angle_deg) > 25,
            "station": state.station_current_A > 0.1,
            "rpm_high": state.rpm > 6200,
            "speed_high": state.speed_kmh > 110,
            "sensor": state.steering_pot_voltage_V < 0.5 or state.steering_pot_voltage_V > 4.5,
            "ready": state.battery_voltage_V >= 48 and state.motor_temp_C < 90,
        }
        self.indicators.update_status(indicators)
