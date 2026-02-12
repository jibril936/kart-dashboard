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
        super().__init__("BRAKE", color="#ff6d64", parent=parent)


class DriveTopIndicators(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.mode_label = QLabel("")
        self.mode_label.setStyleSheet(
            "QLabel {"
            "color: #d9e7f5;"
            "font-size: 11px;"
            "font-weight: 800;"
            "letter-spacing: 0.8px;"
            "padding: 2px 2px;"
            "}"
        )
        self.charging_indicator = ChargingIndicator()
        self.brake_indicator = BrakeIndicator()

        layout.addWidget(self.mode_label)
        layout.addStretch(1)
        layout.addWidget(self.charging_indicator)
        layout.addWidget(self.brake_indicator)

    def set_state(self, charging_mode: bool | None, is_charging: bool | None, brake_active: bool | None) -> None:
        if set_visible_if(self.mode_label, value_is_present(charging_mode)):
            self.mode_label.setText("CHARGE" if charging_mode else "DRIVE")

        set_visible_if(self.charging_indicator, bool(is_charging))
        set_visible_if(self.brake_indicator, bool(brake_active))
