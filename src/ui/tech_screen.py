from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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
        row.addSpacing(14)
        row.addWidget(self.status)

    def set_data(self, value: str, status: str) -> None:
        self.value.setText(value)
        self.status.setText(status)
        self.status.setObjectName(f"Status{status}")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)


class KpiSection(QFrame):
    def __init__(self, title: str, lines: list[KpiLine], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SectionPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        head = QLabel(title)
        head.setObjectName("SectionTitle")
        layout.addWidget(head)
        for line in lines:
            layout.addWidget(line)


class TechScreen(QWidget):
    cluster_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 16)
        root.setSpacing(10)

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
            "brake_state": KpiLine("Frein", "%"),
            "motor_temp_C": KpiLine("Température moteur", "°C"),
        }

        sections = [
            KpiSection("Batterie / Charge", [self.kpi["battery_voltage_V"], self.kpi["battery_charge_current_A"], self.kpi["charging_state"]]),
            KpiSection("Borne", [self.kpi["station_frequency_Hz"], self.kpi["station_current_A"]]),
            KpiSection("Direction", [self.kpi["steering_pot_voltage_V"], self.kpi["steering_angle_deg"], self.kpi["steering_current_A"]]),
            KpiSection("Traction / Frein", [self.kpi["speed_kmh"], self.kpi["rpm"], self.kpi["brake_state"]]),
            KpiSection("Température", [self.kpi["motor_temp_C"]]),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for idx, sec in enumerate(sections):
            grid.addWidget(sec, idx // 2, idx % 2)
        root.addLayout(grid)

        alert_section = QFrame()
        alert_section.setObjectName("SectionPanel")
        alert_layout = QVBoxLayout(alert_section)
        title = QLabel("Alert Center")
        title.setObjectName("SectionTitle")
        alert_layout.addWidget(title)
        self.alert_list = QListWidget()
        self.alert_list.setObjectName("AlertList")
        alert_layout.addWidget(self.alert_list)
        root.addWidget(alert_section, 1)

        nav = QHBoxLayout()
        nav.addStretch(1)
        btn = QPushButton("CLUSTER")
        btn.setObjectName("NavButton")
        btn.clicked.connect(self.cluster_requested.emit)
        nav.addWidget(btn)
        root.addLayout(nav)

    def render(self, state: VehicleTechState) -> None:
        self.kpi["battery_voltage_V"].set_data(f"{state.battery_voltage_V:.2f}", status_battery(state.battery_voltage_V))
        self.kpi["battery_charge_current_A"].set_data(f"{state.battery_charge_current_A:.2f}", "OK")
        self.kpi["charging_state"].set_data("ON" if state.charging_state else "OFF", "OK" if state.charging_state else "WARN")

        self.kpi["station_frequency_Hz"].set_data(f"{state.station_frequency_Hz:.2f}", "OK")
        self.kpi["station_current_A"].set_data(f"{state.station_current_A:.2f}", "OK" if state.station_current_A > 1 else "WARN")

        steering_status = "WARN" if abs(state.steering_angle_deg) > 25 else "OK"
        self.kpi["steering_pot_voltage_V"].set_data(f"{state.steering_pot_voltage_V:.2f}", "OK")
        self.kpi["steering_angle_deg"].set_data(f"{state.steering_angle_deg:.1f}", steering_status)
        self.kpi["steering_current_A"].set_data(f"{state.steering_current_A:.2f}", "OK")

        self.kpi["speed_kmh"].set_data(f"{state.speed_kmh:.1f}", "WARN" if state.speed_kmh > 90 else "OK")
        self.kpi["rpm"].set_data(f"{state.rpm}", "WARN" if state.rpm > 5200 else "OK")
        self.kpi["brake_state"].set_data(f"{state.brake_state:.0f}", "WARN" if state.brake_state > 0 else "OK")

        temp_status = "CRIT" if state.motor_temp_C >= 95 else "WARN" if state.motor_temp_C >= 85 else "OK"
        self.kpi["motor_temp_C"].set_data(f"{state.motor_temp_C:.1f}", temp_status)

        self._update_alert_center(state, temp_status)

    def _update_alert_center(self, state: VehicleTechState, temp_status: str) -> None:
        alerts: list[tuple[str, str]] = []
        if status_battery(state.battery_voltage_V) == "CRIT":
            alerts.append(("CRIT", "Battery voltage critically low"))
        elif status_battery(state.battery_voltage_V) == "WARN":
            alerts.append(("WARN", "Battery voltage below nominal"))

        if temp_status == "CRIT":
            alerts.append(("CRIT", "Motor overheat risk"))
        elif temp_status == "WARN":
            alerts.append(("WARN", "Motor temperature elevated"))

        if abs(state.steering_angle_deg) > 28:
            alerts.append(("WARN", "Steering angle near limit"))

        if state.brake_state > 10:
            alerts.append(("INFO", "Brake pressure event"))

        ts = datetime.fromtimestamp(state.sample_timestamp_ms / 1000).strftime("%H:%M:%S")
        if not alerts:
            alerts = [("OK", "No active alert")]

        self.alert_list.clear()
        for severity, message in alerts:
            item = QListWidgetItem(f"[{ts}] {severity} — {message}")
            if severity == "CRIT":
                item.setForeground(Qt.GlobalColor.red)
            elif severity == "WARN":
                item.setForeground(Qt.GlobalColor.yellow)
            elif severity == "OK":
                item.setForeground(Qt.GlobalColor.green)
            self.alert_list.addItem(item)


def status_battery(voltage: float) -> str:
    if voltage < 46.0:
        return "CRIT"
    if voltage < 48.0:
        return "WARN"
    return "OK"
