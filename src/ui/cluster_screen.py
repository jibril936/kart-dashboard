from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBarStrip, CenterPanel, CircularGauge, DriveTopIndicators

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

        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)
        self.top_indicators = DriveTopIndicators()
        top_bar.addWidget(self.top_indicators)
        root.addLayout(top_bar)

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

        self.bottom_bar = BottomBarStrip()
        root.addWidget(self.bottom_bar)

    def render(self, state: VehicleTechState) -> None:
        speed = state.speed_kmh
        rpm = state.rpm
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        brake = state.brake_state
        motor_temp = state.motor_temp_C

        self.speed_gauge.set_value(float(speed) if speed is not None else 0.0)
        self.rpm_gauge.set_value(float(rpm) if rpm is not None else 0.0)

        self.center_panel.set_state(float(steering_angle) if steering_angle is not None else 0.0, mode="CHARGE" if charging else "DRIVE")

        brake_active = None if brake is None else brake > 10.0
        self.top_indicators.set_state(charging, charging, brake_active)

        self.bottom_bar.set_values(
            battery_voltage=battery_v,
            battery_soc_percent=None,
            motor_temp_c=motor_temp,
        )
