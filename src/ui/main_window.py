from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from src.core.state import VehicleTechState


class KpiTile(QFrame):
    def __init__(self, label: str, unit: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.label = QLabel(label)
        self.label.setObjectName("KpiLabel")
        self.value = QLabel("--")
        self.value.setObjectName("KpiValue")
        self.status = QLabel("OK")
        self.status.setObjectName("StatusOK")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        row = QHBoxLayout()
        row.addWidget(self.value)
        row.addWidget(QLabel(unit))
        row.addStretch(1)
        row.addWidget(self.status)
        layout.addLayout(row)

    def set_data(self, value: str, status: str) -> None:
        self.value.setText(value)
        self.status.setText(status)
        self.status.setObjectName(f"Status{status}")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)


class SectionWidget(QWidget):
    def __init__(self, title: str, tiles: list[KpiTile], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        header = QLabel(title)
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        grid = QGridLayout()
        for idx, tile in enumerate(tiles):
            grid.addWidget(tile, idx // 2, idx % 2)
        layout.addLayout(grid)


class TechMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Informations techniques véhicule — TECH")

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.alert_banner = QFrame()
        self.alert_banner.setObjectName("AlertBanner")
        banner_layout = QHBoxLayout(self.alert_banner)
        self.alert_text = QLabel("Aucune alerte active")
        banner_layout.addWidget(QLabel("ALERT"))
        banner_layout.addWidget(self.alert_text)
        banner_layout.addStretch(1)
        layout.addWidget(self.alert_banner)

        self.kpi = {
            "battery_voltage_V": KpiTile("Tension batterie", "V"),
            "battery_charge_current_A": KpiTile("Courant charge", "A"),
            "charging_state": KpiTile("État charge", ""),
            "station_frequency_Hz": KpiTile("Fréquence borne", "Hz"),
            "station_current_A": KpiTile("Courant borne", "A"),
            "steering_pot_voltage_V": KpiTile("Potentiomètre", "V"),
            "steering_angle_deg": KpiTile("Angle direction", "°"),
            "steering_current_A": KpiTile("Courant direction", "A"),
            "speed_kmh": KpiTile("Vitesse", "km/h"),
            "rpm": KpiTile("RPM", "tr/min"),
            "brake_state": KpiTile("Frein", "%"),
            "motor_temp_C": KpiTile("Temp. moteur", "°C"),
        }

        sections = [
            SectionWidget("Batterie / Charge", [self.kpi["battery_voltage_V"], self.kpi["battery_charge_current_A"], self.kpi["charging_state"]]),
            SectionWidget("Borne", [self.kpi["station_frequency_Hz"], self.kpi["station_current_A"]]),
            SectionWidget("Direction", [self.kpi["steering_pot_voltage_V"], self.kpi["steering_angle_deg"], self.kpi["steering_current_A"]]),
            SectionWidget("Traction / Frein", [self.kpi["speed_kmh"], self.kpi["rpm"], self.kpi["brake_state"]]),
            SectionWidget("Température", [self.kpi["motor_temp_C"]]),
        ]

        sections_grid = QGridLayout()
        for idx, section in enumerate(sections):
            sections_grid.addWidget(section, idx // 2, idx % 2)
        layout.addLayout(sections_grid)

        layout.addWidget(QLabel("Alert Center (historique): à implémenter étape 2"), alignment=Qt.AlignmentFlag.AlignLeft)

    def render(self, state: VehicleTechState) -> None:
        self.kpi["battery_voltage_V"].set_data(f"{state.battery_voltage_V:.2f}", _status_battery(state.battery_voltage_V))
        self.kpi["battery_charge_current_A"].set_data(f"{state.battery_charge_current_A:.2f}", "OK")
        self.kpi["charging_state"].set_data("ON" if state.charging_state else "OFF", "OK")

        self.kpi["station_frequency_Hz"].set_data(f"{state.station_frequency_Hz:.2f}", "OK")
        self.kpi["station_current_A"].set_data(f"{state.station_current_A:.2f}", "OK")

        self.kpi["steering_pot_voltage_V"].set_data(f"{state.steering_pot_voltage_V:.2f}", "OK")
        self.kpi["steering_angle_deg"].set_data(f"{state.steering_angle_deg:.1f}", "OK")
        self.kpi["steering_current_A"].set_data(f"{state.steering_current_A:.2f}", "OK")

        self.kpi["speed_kmh"].set_data(f"{state.speed_kmh:.1f}", "OK")
        self.kpi["rpm"].set_data(f"{state.rpm}", "OK")
        self.kpi["brake_state"].set_data(f"{state.brake_state:.0f}", "OK")

        temp_status = "CRIT" if state.motor_temp_C >= 95 else "WARN" if state.motor_temp_C >= 85 else "OK"
        self.kpi["motor_temp_C"].set_data(f"{state.motor_temp_C:.1f}", temp_status)

        if state.battery_voltage_V < 46.0:
            self.alert_text.setText("CRIT — Battery low")
        elif state.motor_temp_C > 85:
            self.alert_text.setText("WARN — Motor temp élevée")
        else:
            self.alert_text.setText("Aucune alerte active")


def _status_battery(voltage: float) -> str:
    if voltage < 46.0:
        return "CRIT"
    if voltage < 48.0:
        return "WARN"
    return "OK"
