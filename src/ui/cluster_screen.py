from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBar, CenterPanel, CircularGauge, IndicatorRow, IndicatorSpec
from src.ui.components.status_widgets import AbsBadgeWidget
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
        self.abs_badge = AbsBadgeWidget()
        top_bar.addWidget(self.indicators, 1)
        top_bar.addWidget(self.abs_badge, 0)
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
        self.center_panel.set_state(float(steering_angle) if steering_angle is not None else 0.0, mode="CHARGE" if charging else "SPORT")

        battery_pct = None if battery_v is None else (battery_v - 42.0) / 12.0 * 100.0
        power_ratio = None if speed is None else min(1.0, max(0.0, speed / 120.0))
        regen_ratio = None if brake is None else min(1.0, max(0.0, brake / 25.0))
        self.bottom_bar.set_values(battery_v, battery_pct, power_ratio, regen_ratio, motor_temp, temperature_label="MOTOR")

        indicators = {
            "battery_low": None if battery_v is None else battery_v < 48,
            "overheat": None if motor_temp is None else motor_temp >= 85,
            "charging": charging,
            "brake": None if brake is None else brake > 10,
            "steering": None if steering_angle is None else abs(steering_angle) > 25,
            "station": None if state.station_current_A is None else state.station_current_A > 0.1,
            "rpm_high": None if rpm is None else rpm > 6200,
            "speed_high": None if speed is None else speed > 110,
            "sensor": None if state.steering_pot_voltage_V is None else state.steering_pot_voltage_V < 0.5 or state.steering_pot_voltage_V > 4.5,
            "ready": None if (battery_v is None or motor_temp is None) else battery_v >= 48 and motor_temp < 90,
        }
        self.indicators.update_status(indicators)

        if set_visible_if(self.abs_badge, value_is_present(state.abs_active)):
            self.abs_badge.set_active(bool(state.abs_active))
