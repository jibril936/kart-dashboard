from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

from src.core.model import KartDataModel
from src.ui.components.modern_battery import ModernBattery
from src.ui.components.modern_dynamics import ModernDynamics
from src.ui.components.speed_gauge_oem import SpeedGaugeOEM
from src.ui.components.status_strip import StatusStrip


class DrivingScreen(QWidget):
    def __init__(self, model: KartDataModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = model
        self.setStyleSheet("background-color: #04070A;")

        layout = QGridLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.battery_widget = ModernBattery(self)
        self.dynamics_widget = ModernDynamics(self)
        self.status_strip = StatusStrip(self)

        self.speed_gauge = SpeedGaugeOEM(
            title="SPEED",
            unit="km/h",
            min_value=0,
            max_value=120,
            major_tick_step=10,
            minor_ticks_per_major=1,
        )

        layout.addWidget(self.battery_widget, 0, 0)
        layout.addWidget(self.speed_gauge, 0, 1)
        layout.addWidget(self.dynamics_widget, 0, 2)
        layout.addWidget(self.status_strip, 1, 0, 1, 3)

        layout.setRowStretch(0, 4)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)

        self._voltage = self.model.battery_pack_voltage
        self._current = self.model.battery_pack_current

        speed_signal = getattr(self.model, "speedChanged", None)
        if speed_signal is None:
            speed_signal = self.model.speed_changed
        speed_signal.connect(self.update_gauge)

        self.model.battery_pack_voltage_changed.connect(self._on_voltage_changed)
        self.model.battery_pack_current_changed.connect(self._on_current_changed)
        self.model.motor_temperature_changed.connect(self._on_motor_temp_changed)
        self.model.battery_temperature_changed.connect(self._on_battery_temp_changed)
        self.model.mode_changed.connect(self.dynamics_widget.set_mode)

        brake_signal = getattr(self.model, "brakeActive", None)
        if brake_signal is None:
            brake_signal = getattr(self.model, "brake_state_changed", None)
        if brake_signal is not None:
            brake_signal.connect(self.dynamics_widget.set_brake_state)

        radar_signal = getattr(self.model, "ultrasonicDistances", None)
        if radar_signal is None:
            radar_signal = getattr(self.model, "ultrasonic_distances_changed", None)
        if radar_signal is not None:
            radar_signal.connect(self.dynamics_widget.update_radars)

        self._motor_temp = self.model.motor_temperature
        self._battery_temp = self.model.battery_temperature

        self.update_gauge(self.model.speed)
        self._refresh_energy_widgets()
        self.status_strip.update_temperatures(self._motor_temp, self._battery_temp)

        self.battery_widget.set_voltage(self.model.battery_pack_voltage)
        self.dynamics_widget.set_mode(self.model.mode)
        self.dynamics_widget.set_current(self.model.battery_pack_current)
        self.dynamics_widget.set_brake_state(bool(getattr(self.model, "brake_state", False)))
        self.dynamics_widget.update_radars(list(getattr(self.model, "ultrasonic_distances", [400.0, 400.0, 400.0])))

    def _refresh_energy_widgets(self) -> None:
        self.battery_widget.set_voltage(self._voltage)
        self.dynamics_widget.set_current(self._current)

    def _on_voltage_changed(self, voltage: float) -> None:
        self._voltage = float(voltage)
        self._refresh_energy_widgets()

    def _on_current_changed(self, current: float) -> None:
        self._current = float(current)
        self._refresh_energy_widgets()

    def _on_motor_temp_changed(self, value: float) -> None:
        self._motor_temp = float(value)
        self.status_strip.update_temperatures(self._motor_temp, self._battery_temp)

    def _on_battery_temp_changed(self, value: float) -> None:
        self._battery_temp = float(value)
        self.status_strip.update_temperatures(self._motor_temp, self._battery_temp)

    def update_gauge(self, value: float) -> None:
        self.speed_gauge.set_value(value)


class TechScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #091530;")

        layout = QGridLayout(self)
        label = QLabel("TECH")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)


class GraphsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

        layout = QGridLayout(self)
        label = QLabel("GRAPHS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)
