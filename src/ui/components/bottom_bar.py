from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #141b24;
                border: 1px solid #2c3e50;
                border-radius: 12px;
            }
            QLabel {
                color: #D8F7FF;
                background: transparent;
                border: none;
                font-family: Arial, sans-serif;
                font-size: 22px;
                font-weight: 700;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(14)

        self.motor_temp_label = QLabel("MOTEUR : --°C")
        self.motor_temp_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.battery_temp_label = QLabel("BATTERIE : --°C")
        self.battery_temp_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.motor_temp_label, 1)
        layout.addWidget(self.battery_temp_label, 1)
        layout.addWidget(self.warning_label, 2)

    def update_temperatures(self, motor_temp: float, battery_temp: float) -> None:
        motor = float(motor_temp)
        battery = float(battery_temp)

        self.motor_temp_label.setText(f"MOTEUR : {motor:.0f}°C")
        self.battery_temp_label.setText(f"BATTERIE : {battery:.0f}°C")

        motor_color = "#FF3333" if motor > 90.0 else "#D8F7FF"
        self.motor_temp_label.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {motor_color};")

    def update_warning(self, warnings: list[str]) -> None:
        if warnings:
            self.warning_label.setText(" | ".join(warnings).upper())
            self.warning_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #FF3333;")
        else:
            self.warning_label.setText("")
            self.warning_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #D8F7FF;")

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(motor_temp_c, 0.0)


BottomBarStrip = BottomBar
