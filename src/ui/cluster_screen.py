from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import CarSimulationWidget, CircularGauge, IndicatorRow, IndicatorSpec, MiniGauge


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 16)
        root.setSpacing(12)

        self.indicators = IndicatorRow(
            [
                IndicatorSpec("battery_low", "🔋", "BATT"),
                IndicatorSpec("overheat", "🌡", "TEMP"),
                IndicatorSpec("charging", "⚡", "CHG"),
                IndicatorSpec("brake", "🛑", "BRAKE"),
                IndicatorSpec("steering", "🛞", "STEER"),
                IndicatorSpec("station", "🔌", "EVSE"),
                IndicatorSpec("rpm_high", "⟳", "RPM"),
                IndicatorSpec("speed_high", "➤", "SPEED"),
                IndicatorSpec("sensor", "📡", "SENS"),
                IndicatorSpec("ready", "✔", "READY"),
            ]
        )
        root.addWidget(self.indicators)

        middle = QHBoxLayout()
        middle.setSpacing(16)

        self.speed_gauge = CircularGauge("SPEED", "km/h", 0, 140, warning_value=90, critical_value=120)
        self.car_sim = CarSimulationWidget()
        self.rpm_gauge = CircularGauge("RPM", "tr/min", 0, 7000, warning_value=5200, critical_value=6200, red_zone_start=5600)

        middle.addWidget(self.speed_gauge, 1)
        middle.addWidget(self.car_sim, 1)
        middle.addWidget(self.rpm_gauge, 1)
        root.addLayout(middle, 1)

        bottom = QHBoxLayout()
        self.battery_mini = MiniGauge("Batterie", "V")
        self.temp_mini = MiniGauge("Temp. moteur", "°C")
        bottom.addWidget(self.battery_mini)
        bottom.addStretch(1)
        bottom.addWidget(self.temp_mini)
        root.addLayout(bottom)

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
        self.car_sim.set_state(state.steering_angle_deg, mode="CHARGE" if state.charging_state else "DRIVE")

        battery_status = "CRIT" if state.battery_voltage_V < 46 else "WARN" if state.battery_voltage_V < 48 else "OK"
        temp_status = "CRIT" if state.motor_temp_C >= 95 else "WARN" if state.motor_temp_C >= 85 else "OK"
        self.battery_mini.set_value(state.battery_voltage_V, (state.battery_voltage_V - 42) / 12, battery_status)
        self.temp_mini.set_value(state.motor_temp_C, state.motor_temp_C / 120, temp_status)

        indicators = {
            "battery_low": state.battery_voltage_V < 48,
            "overheat": state.motor_temp_C >= 85,
            "charging": state.charging_state,
            "brake": state.brake_state > 10,
            "steering": abs(state.steering_angle_deg) > 25,
            "station": state.station_current_A > 0.1,
            "rpm_high": state.rpm > 5200,
            "speed_high": state.speed_kmh > 90,
            "sensor": state.steering_pot_voltage_V < 0.5 or state.steering_pot_voltage_V > 4.5,
            "ready": state.battery_voltage_V >= 48 and state.motor_temp_C < 90,
        }
        self.indicators.update_status(indicators)
