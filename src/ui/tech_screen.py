from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState


class KpiLine(QFrame):
    def __init__(self, label: str, unit: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("KpiLine")
        self.unit = unit

        self.label = QLabel(label)
        self.value = QLabel("--")
        self.value.setObjectName("KpiValue")
        self.status = QLabel("OK")
        self.status.setObjectName("StatusOK")

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.addWidget(self.label)
        row.addStretch(1)
        row.addWidget(self.value)
        row.addWidget(QLabel(unit))
        row.addSpacing(10)
        row.addWidget(self.status)

    def set_data(self, value: str, status: str) -> None:
        self.value.setText(value)
        self.status.setText(status)
        self.status.setObjectName(f"Status{status}")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def set_scale(self, ui_scale: float) -> None:
        base = max(9, int(12 * ui_scale))
        self.label.setFont(QFont("Segoe UI", base, QFont.Weight.Medium))
        self.value.setFont(QFont("Segoe UI", base + 1, QFont.Weight.Bold))
        self.status.setFont(QFont("Segoe UI", base, QFont.Weight.Bold))


class KpiSection(QFrame):
    def __init__(self, title: str, lines: list[KpiLine], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SectionPanel")
        self.lines = lines
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.head = QLabel(title)
        self.head.setObjectName("SectionTitle")
        layout.addWidget(self.head)
        for line in lines:
            layout.addWidget(line)

    def set_scale(self, ui_scale: float) -> None:
        self.head.setFont(QFont("Segoe UI", max(11, int(15 * ui_scale)), QFont.Weight.Bold))
        cast_layout = self.layout()
        if cast_layout is not None:
            cast_layout.setContentsMargins(int(10 * ui_scale), int(8 * ui_scale), int(10 * ui_scale), int(8 * ui_scale))
            cast_layout.setSpacing(int(5 * ui_scale))
        for line in self.lines:
            line.set_scale(ui_scale)


class TechScreen(QWidget):
    cluster_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(14, 10, 14, 10)
        self.root.setSpacing(8)

        self.kpi = {
            "battery_voltage_V": KpiLine("Tension batterie", "V"),
            "battery_charge_current_A": KpiLine("Courant charge", "A"),
            "charging_state": KpiLine("État charge", ""),
            "station_frequency_Hz": KpiLine("Fréquence borne", "Hz"),
            "station_current_A": KpiLine("Courant borne", "A"),
            "steering_pot_voltage_V": KpiLine("Potentiomètre", "V"),
            "steering_angle_deg": KpiLine("Angle direction", "°"),
            "steering_current_A": KpiLine("Courant direction", "A"),
            "speed_kmh": KpiLine("Vitesse", "km/h"),
            "rpm": KpiLine("RPM", "tr/min"),
            "brake_state": KpiLine("Frein", ""),
            "motor_temp_C": KpiLine("Température moteur", "°C"),
        }

        self.sections = [
            KpiSection("Batterie / Charge", [self.kpi["battery_voltage_V"], self.kpi["battery_charge_current_A"], self.kpi["charging_state"]]),
            KpiSection("Borne", [self.kpi["station_frequency_Hz"], self.kpi["station_current_A"]]),
            KpiSection("Direction", [self.kpi["steering_pot_voltage_V"], self.kpi["steering_angle_deg"], self.kpi["steering_current_A"]]),
            KpiSection("Traction / Frein", [self.kpi["speed_kmh"], self.kpi["rpm"], self.kpi["brake_state"]]),
            KpiSection("Température", [self.kpi["motor_temp_C"]]),
        ]

        for sec in self.sections:
            self.root.addWidget(sec)

        nav = QHBoxLayout()
        nav.addStretch(1)
        btn = QPushButton("CLUSTER")
        btn.setObjectName("NavButton")
        btn.clicked.connect(self.cluster_requested.emit)
        nav.addWidget(btn)
        self.root.addLayout(nav)

        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        compact = self.width() < 1100 or self.height() < 650
        ui_scale = 0.9 if compact else 1.0
        self.root.setContentsMargins(int(12 * ui_scale), int(8 * ui_scale), int(12 * ui_scale), int(8 * ui_scale))
        self.root.setSpacing(int(6 * ui_scale))
        for sec in self.sections:
            sec.set_scale(ui_scale)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_responsive_layout()

    def render(self, state: VehicleTechState) -> None:
        self.kpi["battery_voltage_V"].set_data(f"{state.battery_voltage_V:.2f}", "OK")
        self.kpi["battery_charge_current_A"].set_data(f"{state.battery_charge_current_A:.2f}", "OK")
        self.kpi["charging_state"].set_data("ON" if state.charging_state else "OFF", "OK")

        self.kpi["station_frequency_Hz"].set_data(f"{state.station_frequency_Hz:.2f}", "OK")
        self.kpi["station_current_A"].set_data(f"{state.station_current_A:.2f}", "OK")

        self.kpi["steering_pot_voltage_V"].set_data(f"{state.steering_pot_voltage_V:.2f}", "OK")
        self.kpi["steering_angle_deg"].set_data(f"{state.steering_angle_deg:.1f}", "OK")
        self.kpi["steering_current_A"].set_data(f"{state.steering_current_A:.2f}", "OK")

        self.kpi["speed_kmh"].set_data(f"{state.speed_kmh:.1f}", "OK")
        self.kpi["rpm"].set_data(f"{state.rpm}", "OK")
        brake_active = (state.brake_state or 0.0) >= 0.5
        self.kpi["brake_state"].set_data("ON" if brake_active else "OFF", "OK")

        self.kpi["motor_temp_C"].set_data(f"{state.motor_temp_C:.1f}", "OK")
