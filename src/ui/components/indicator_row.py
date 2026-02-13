from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.ui.visibility import set_visible_if, value_is_present


class StateIndicator(QLabel):
    def __init__(self, text: str, *, color: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "QLabel {"
            "background: rgba(18, 28, 42, 0.92);"
            "border: 1px solid #2a3f59;"
            "border-radius: 10px;"
            "padding: 3px 10px;"
            "font-size: 10px;"
            "font-weight: 700;"
            f"color: {color};"
            "letter-spacing: 0.5px;"
            "}"
        )


class ChargingIndicator(StateIndicator):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("⚡ CHG", color="#5ea9ff", parent=parent)


class BrakeIndicator(StateIndicator):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BRAKE", color="#88bfff", parent=parent)


class DriveTopIndicators(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.battery_label = StateIndicator("", color="#8dc4ff")
        self.temp_label = StateIndicator("", color="#ffc67a")
        self.charging_indicator = ChargingIndicator()
        self.brake_indicator = BrakeIndicator()

        layout.addWidget(self.battery_label)
        layout.addWidget(self.temp_label)
        layout.addStretch(1)
        layout.addWidget(self.charging_indicator)
        layout.addWidget(self.brake_indicator)

    def set_state(
        self,
        *,
        battery_voltage_v: float | None,
        motor_temp_c: float | None,
        is_charging: bool | None,
        brake_active: bool | None,
    ) -> None:
        if set_visible_if(self.battery_label, value_is_present(battery_voltage_v)):
            self.battery_label.setText(f"BAT {battery_voltage_v:.1f}V")

        if set_visible_if(self.temp_label, value_is_present(motor_temp_c)):
            self.temp_label.setText(f"MTR {motor_temp_c:.0f}°C")

        set_visible_if(self.charging_indicator, bool(is_charging))
        set_visible_if(self.brake_indicator, False)
