from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBar, CenterPanel, CircularGauge, IndicatorRow, IndicatorSpec
from src.ui.visibility import set_visible_if, value_is_present

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
        self.vehicle_state = QLabel("")
        self.vehicle_state.setObjectName("TopStatusState")
        self.indicators = IndicatorRow(
            [
                IndicatorSpec("vehicle_charging", "charging", "CHG", active_color="#5ea9ff"),
                IndicatorSpec("overheat", "temp", "TEMP", active_color="#ff6d64"),
                IndicatorSpec("battery_low", "battery", "BATT", active_color="#ffb347"),
                IndicatorSpec("brake", "brake", "BRAKE", active_color="#ff6d64"),
                IndicatorSpec("abs_fault", "abs", "ABS", active_color="#ff8f66"),
            ]
        )
        top_bar.addWidget(self.vehicle_state, 0)
        top_bar.addWidget(self.indicators, 1)
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
        speed = state.speed_kmh
        rpm = state.rpm
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        brake = state.brake_state
        motor_temp = state.motor_temp_C

        self.speed_gauge.set_value(float(speed) if speed is not None else 0.0)
        self.rpm_gauge.set_value(float(rpm) if rpm is not None else 0.0)

        if set_visible_if(self.vehicle_state, value_is_present(charging)):
            self.vehicle_state.setText("CHARGE" if charging else "DRIVE")

        self.center_panel.set_state(float(steering_angle) if steering_angle is not None else 0.0, mode="CHARGE" if charging else "DRIVE")

        battery_pct = None if battery_v is None else (battery_v - 42.0) / 12.0 * 100.0
        station_current = state.station_current_A
        brake_percent = None if brake is None else min(100.0, max(0.0, brake * 4.0))
        self.bottom_bar.set_values(
            battery_v,
            battery_pct,
            charging,
            station_current,
            steering_angle,
            motor_temp,
            brake_percent,
            temperature_label="MOTOR",
        )

        indicators = {
            "vehicle_charging": charging,
            "overheat": None if motor_temp is None else motor_temp >= 85,
            "battery_low": None if battery_v is None else battery_v < 48,
            "brake": None if brake is None else brake > 10,
            "abs_fault": None,
        }
        self.indicators.update_status(indicators)
